# 设计文档 - 数据库迁移

## 概述

本文档描述了将DDC设备清单匹配报价系统从静态JSON文件存储迁移到关系型数据库存储的设计方案。系统将使用SQLAlchemy ORM框架，支持SQLite和MySQL两种数据库，并保持向后兼容JSON文件模式。

## 架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        应用层                                │
│  (Flask API, MatchEngine, ExcelParser, ExcelExporter)       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      数据访问层                              │
│                    (DataLoader)                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  DatabaseLoader  │         │   JSONLoader     │         │
│  │  (新增)          │         │   (现有)         │         │
│  └──────────────────┘         └──────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ↓                       ↓
┌──────────────────────────┐  ┌──────────────────────┐
│      数据库存储          │  │    JSON文件存储      │
│  (SQLite/MySQL)          │  │  (static_*.json)     │
│  - devices表             │  │  - static_device     │
│  - rules表               │  │  - static_rule       │
│  - configs表             │  │  - static_config     │
└──────────────────────────┘  └──────────────────────┘
```

### 存储模式切换

系统通过配置文件控制存储模式：

```python
# config.py
class Config:
    STORAGE_MODE = 'database'  # 'database' 或 'json'
    DATABASE_TYPE = 'sqlite'   # 'sqlite' 或 'mysql'
    DATABASE_URL = 'sqlite:///data/devices.db'
    FALLBACK_TO_JSON = True    # 数据库失败时是否回退到JSON
```

## 组件和接口

### 1. 数据库模型 (models.py)

使用SQLAlchemy定义ORM模型：

```python
from sqlalchemy import Column, String, Float, Integer, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Device(Base):
    """设备模型"""
    __tablename__ = 'devices'
    
    device_id = Column(String(100), primary_key=True)
    brand = Column(String(50), nullable=False, index=True)
    device_name = Column(String(100), nullable=False, index=True)
    spec_model = Column(String(200), nullable=False)
    detailed_params = Column(Text, nullable=False)
    unit_price = Column(Float, nullable=False)
    
    # 关联规则
    rules = relationship("Rule", back_populates="device", cascade="all, delete-orphan")

class Rule(Base):
    """匹配规则模型"""
    __tablename__ = 'rules'
    
    rule_id = Column(String(100), primary_key=True)
    target_device_id = Column(String(100), ForeignKey('devices.device_id'), nullable=False, index=True)
    auto_extracted_features = Column(JSON, nullable=False)  # 存储为JSON数组
    feature_weights = Column(JSON, nullable=False)          # 存储为JSON对象
    match_threshold = Column(Float, nullable=False)
    remark = Column(Text)
    
    # 关联设备
    device = relationship("Device", back_populates="rules")

class Config(Base):
    """配置模型"""
    __tablename__ = 'configs'
    
    config_key = Column(String(100), primary_key=True)
    config_value = Column(JSON, nullable=False)
    description = Column(Text)
```

### 2. 数据库管理器 (database.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager

class DatabaseManager:
    """数据库连接和会话管理"""
    
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=False)
        self.SessionFactory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.SessionFactory)
    
    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(self.engine)
    
    @contextmanager
    def session_scope(self):
        """提供事务会话上下文"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def close(self):
        """关闭数据库连接"""
        self.Session.remove()
        self.engine.dispose()
```

### 3. 数据库加载器 (database_loader.py)

```python
class DatabaseLoader:
    """数据库数据加载器"""
    
    def __init__(self, db_manager: DatabaseManager, preprocessor=None):
        self.db_manager = db_manager
        self.preprocessor = preprocessor
    
    def load_devices(self) -> Dict[str, Device]:
        """从数据库加载所有设备"""
        with self.db_manager.session_scope() as session:
            devices = session.query(DeviceModel).all()
            return {d.device_id: self._model_to_dataclass(d) for d in devices}
    
    def load_rules(self) -> List[Rule]:
        """从数据库加载所有规则"""
        with self.db_manager.session_scope() as session:
            rules = session.query(RuleModel).all()
            return [self._model_to_rule(r) for r in rules]
    
    def get_device_by_id(self, device_id: str) -> Optional[Device]:
        """根据ID查询设备"""
        with self.db_manager.session_scope() as session:
            device = session.query(DeviceModel).filter_by(device_id=device_id).first()
            return self._model_to_dataclass(device) if device else None
    
    def add_device(self, device: Device) -> bool:
        """添加设备"""
        with self.db_manager.session_scope() as session:
            device_model = self._dataclass_to_model(device)
            session.add(device_model)
            return True
    
    def update_device(self, device: Device) -> bool:
        """更新设备"""
        with self.db_manager.session_scope() as session:
            device_model = session.query(DeviceModel).filter_by(device_id=device.device_id).first()
            if device_model:
                device_model.brand = device.brand
                device_model.device_name = device.device_name
                device_model.spec_model = device.spec_model
                device_model.detailed_params = device.detailed_params
                device_model.unit_price = device.unit_price
                return True
            return False
    
    def delete_device(self, device_id: str) -> bool:
        """删除设备（级联删除规则）"""
        with self.db_manager.session_scope() as session:
            device = session.query(DeviceModel).filter_by(device_id=device_id).first()
            if device:
                session.delete(device)
                return True
            return False
```

### 4. 统一数据加载器 (data_loader.py 重构)

重构现有的DataLoader，支持多种存储模式：

```python
class DataLoader:
    """统一数据加载器 - 支持数据库和JSON两种模式"""
    
    def __init__(self, config: Config, preprocessor=None):
        self.config = config
        self.preprocessor = preprocessor
        self.storage_mode = config.STORAGE_MODE
        
        # 根据配置初始化对应的加载器
        if self.storage_mode == 'database':
            try:
                db_manager = DatabaseManager(config.DATABASE_URL)
                self.loader = DatabaseLoader(db_manager, preprocessor)
                logger.info(f"使用数据库存储模式: {config.DATABASE_TYPE}")
            except Exception as e:
                if config.FALLBACK_TO_JSON:
                    logger.warning(f"数据库连接失败，回退到JSON模式: {e}")
                    self.loader = JSONLoader(config, preprocessor)
                    self.storage_mode = 'json'
                else:
                    raise
        else:
            self.loader = JSONLoader(config, preprocessor)
            logger.info("使用JSON文件存储模式")
    
    def load_devices(self) -> Dict[str, Device]:
        """加载设备 - 委托给具体加载器"""
        return self.loader.load_devices()
    
    def load_rules(self) -> List[Rule]:
        """加载规则 - 委托给具体加载器"""
        return self.loader.load_rules()
    
    # ... 其他方法类似委托
```

## 数据模型

### devices 表结构

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| device_id | VARCHAR(100) | PRIMARY KEY | 设备唯一标识 |
| brand | VARCHAR(50) | NOT NULL, INDEX | 品牌 |
| device_name | VARCHAR(100) | NOT NULL, INDEX | 设备名称 |
| spec_model | VARCHAR(200) | NOT NULL | 规格型号 |
| detailed_params | TEXT | NOT NULL | 详细参数 |
| unit_price | FLOAT | NOT NULL | 不含税单价 |

### rules 表结构

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| rule_id | VARCHAR(100) | PRIMARY KEY | 规则唯一标识 |
| target_device_id | VARCHAR(100) | FOREIGN KEY, NOT NULL, INDEX | 关联设备ID |
| auto_extracted_features | JSON | NOT NULL | 自动提取的特征列表 |
| feature_weights | JSON | NOT NULL | 特征权重映射 |
| match_threshold | FLOAT | NOT NULL | 匹配阈值 |
| remark | TEXT | NULL | 备注说明 |

### configs 表结构

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| config_key | VARCHAR(100) | PRIMARY KEY | 配置键 |
| config_value | JSON | NOT NULL | 配置值（JSON格式） |
| description | TEXT | NULL | 配置说明 |

## 正确性属性

*属性是系统在所有有效执行中应保持为真的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性 1: 数据库连接生命周期管理

*对于任何*数据库操作，当操作完成或失败时，系统应正确关闭数据库会话和连接
**验证需求: 1.3**

### 属性 2: 设备ID唯一性

*对于任何*设备插入操作，如果设备ID已存在，系统应执行更新而不是插入，保持ID唯一性
**验证需求: 2.6**

### 属性 3: 规则与设备关联完整性

*对于任何*规则，其target_device_id必须对应数据库中存在的设备
**验证需求: 3.4, 11.4**

### 属性 4: 设备删除级联

*对于任何*设备删除操作，系统应同时删除所有关联的匹配规则
**验证需求: 9.3**

### 属性 5: 事务原子性

*对于任何*批量数据操作，如果任何一条记录失败，系统应回滚整个事务，保持数据一致性
**验证需求: 7.4, 9.5**

### 属性 6: 存储模式回退

*对于任何*数据库连接失败的情况，如果配置允许回退，系统应自动切换到JSON模式并继续正常工作
**验证需求: 5.3**

### 属性 7: 数据迁移完整性

*对于任何*从JSON迁移到数据库的操作，迁移后的设备ID和规则ID应与原JSON文件中的完全一致
**验证需求: 7.2, 7.3**

### 属性 8: 特征自动生成一致性

*对于任何*设备，使用相同的TextPreprocessor生成的特征应与Excel解析时生成的特征使用相同的规则
**验证需求: 3.1**

### 属性 9: 配置值JSON序列化往返

*对于任何*配置对象，将其序列化为JSON存储到数据库后再反序列化，应得到等价的配置对象
**验证需求: 11.3**

### 属性 10: 查询结果非空处理

*对于任何*数据库查询操作，当结果为空时，系统应返回空列表或None而不是抛出异常
**验证需求: 4.5**

## 错误处理

### 数据库连接错误

- 捕获连接异常并记录详细日志
- 如果配置允许，自动回退到JSON模式
- 提供明确的错误信息给用户

### 数据完整性错误

- 外键约束违反时回滚事务
- 记录违反约束的具体记录
- 提供修复建议

### 数据导入错误

- 跳过格式错误的记录并继续处理
- 记录所有跳过的记录和原因
- 导入完成后提供统计报告

## 测试策略

### 单元测试

- 测试DatabaseManager的连接管理
- 测试ORM模型的CRUD操作
- 测试DataLoader的模式切换逻辑
- 测试数据迁移脚本的正确性

### 集成测试

- 测试完整的数据导入流程
- 测试数据库模式下的匹配功能
- 测试存储模式回退机制
- 测试事务回滚机制

### 端到端测试

- 使用真实设备价格例子.xlsx数据
- 上传(原始表格)建筑设备监控及能源管理报价清单(3).xlsx
- 验证匹配准确率≥85%
- 验证导出功能正常

### 性能测试

- 测试720条设备数据的加载性能
- 测试大批量匹配的性能
- 对比数据库模式和JSON模式的性能差异
