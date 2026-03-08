---
inclusion: always
---
# 数据库结构和操作参考

## 数据库位置
- **路径**: `data/devices.db`
- **类型**: SQLite 3

---

## 核心表结构

### devices 表（设备表）

**⚠️ 重要**：主键是 `device_id`（不是 `id`），设备名称是 `device_name`（不是 `name`）

```sql
device_id        VARCHAR(100)  PRIMARY KEY  -- 设备ID（主键）
brand            VARCHAR(50)                -- 品牌
device_name      VARCHAR(100)               -- 设备名称
spec_model       VARCHAR(200)               -- 规格型号
device_type      VARCHAR(50)                -- 设备类型
detailed_params  TEXT                       -- 详细参数
unit_price       INTEGER                    -- 单价
key_params       JSON                       -- 关键参数（JSON字符串）
confidence_score FLOAT                      -- 置信度
input_method     VARCHAR(20)                -- 录入方式
created_at       DATETIME                   -- 创建时间
updated_at       DATETIME                   -- 更新时间
```

### rules 表（规则表）

```sql
rule_id                 VARCHAR(100)  PRIMARY KEY
target_device_id        VARCHAR(100)  FOREIGN KEY -> devices.device_id
auto_extracted_features JSON          -- 自动提取的特征
feature_weights         JSON          -- 特征权重
match_threshold         FLOAT         -- 匹配阈值
remark                  TEXT          -- 备注
```

### configs 表（配置表）

```sql
config_key    VARCHAR(100)  PRIMARY KEY
config_value  JSON                      -- 配置值
description   TEXT                      -- 描述
```

**重要配置键**：
- `device_params` - 设备参数配置（原 `backend/config/device_params.yaml`）
- `intelligent_extraction` - 智能提取配置（原 `backend/config/intelligent_extraction_config.json`）
- `device_type_keywords` - 设备类型关键词
- `brand_keywords` - 品牌关键词
- `feature_weight_config` - 特征权重配置
- `synonym_map` - 同义词映射
- 等等...（共31个配置键）

---

## Python数据库操作

### 初始化（标准流程）

```python
import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule, Config

# 1. 创建数据库管理器
db_manager = DatabaseManager("sqlite:///data/devices.db")

# 2. 创建数据库加载器
db_loader = DatabaseLoader(db_manager)

# 3. 加载配置（如需要）
config = db_loader.load_config()

# 4. 访问特定配置
device_params = db_loader.get_config_by_key('device_params')
intelligent_extraction = db_loader.get_config_by_key('intelligent_extraction')
```

### 配置访问（重要！）

#### 访问 device_params 配置（原 device_params.yaml）

```python
# 方法1：获取完整配置
device_params = db_loader.get_config_by_key('device_params')

# 方法2：从所有配置中获取
all_config = db_loader.load_config()
device_params = all_config.get('device_params')

# 访问具体设备类型的参数
if device_params and 'device_types' in device_params:
    sensor_params = device_params['device_types'].get('温度传感器', {})
    params_list = sensor_params.get('params', [])
    
    # 遍历参数
    for param in params_list:
        print(f"参数名: {param['name']}")
        print(f"是否必填: {param['required']}")
        print(f"选项: {param.get('options', [])}")
```

#### 访问 intelligent_extraction 配置（原 intelligent_extraction_config.json）

```python
# 获取智能提取配置
intelligent_extraction = db_loader.get_config_by_key('intelligent_extraction')

if intelligent_extraction:
    # 访问设备类型配置
    device_types = intelligent_extraction.get('device_type', {}).get('device_types', [])
    
    # 访问参数提取配置
    parameter_config = intelligent_extraction.get('parameter', {})
    range_config = parameter_config.get('range', {})
    
    # 访问匹配权重
    matching_weights = intelligent_extraction.get('matching', {}).get('weights', {})
    
    print(f"设备类型列表: {device_types}")
    print(f"匹配权重: {matching_weights}")
```

#### 配置迁移对照表

| 旧文件路径 | 新配置键 | 访问方法 |
|-----------|---------|---------|
| `backend/config/device_params.yaml` | `device_params` | `db_loader.get_config_by_key('device_params')` |
| `backend/config/intelligent_extraction_config.json` | `intelligent_extraction` | `db_loader.get_config_by_key('intelligent_extraction')` |
| `data/static_config.json` 中的配置 | 各自对应的键 | `db_loader.get_config_by_key('config_key')` |

### 查询操作

```python
# 查询所有设备
with db_manager.session_scope() as session:
    devices = session.query(Device).all()

# 按条件查询
with db_manager.session_scope() as session:
    devices = session.query(Device).filter(
        Device.brand == "霍尼韦尔",
        Device.device_type == "压差变送器"
    ).all()

# 查询单个设备
with db_manager.session_scope() as session:
    device = session.query(Device).filter(
        Device.device_id == "HON_12345678"
    ).first()
```

### 插入操作

```python
from datetime import datetime
import uuid

with db_manager.session_scope() as session:
    device = Device(
        device_id=f"DEV_{uuid.uuid4().hex[:8]}",
        brand="霍尼韦尔",
        device_name="测试设备",
        spec_model="TEST-001",
        device_type="压差变送器",
        unit_price=5000,
        key_params={"量程": {"value": "0-4 Bar"}},
        input_method="manual",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(device)
    # session_scope 会自动 commit
```

### 更新操作

```python
with db_manager.session_scope() as session:
    device = session.query(Device).filter(
        Device.device_id == "DEV_12345678"
    ).first()
    
    if device:
        device.unit_price = 6000
        device.updated_at = datetime.now()
        # session_scope 会自动 commit
```

### 删除操作

```python
with db_manager.session_scope() as session:
    device = session.query(Device).filter(
        Device.device_id == "DEV_12345678"
    ).first()
    
    if device:
        session.delete(device)  # 级联删除关联的规则
```

### 生成规则（完整流程）

```python
from modules.device_feature_extractor import DeviceFeatureExtractor
from modules.rule_generator import RuleGenerator
from modules.models import Rule as RuleModel

# 加载配置
config = db_loader.load_config()

# 初始化组件
feature_extractor = DeviceFeatureExtractor(config)
rule_generator = RuleGenerator(config)

with db_manager.session_scope() as session:
    device = session.query(Device).first()
    
    # 生成规则（返回数据类）
    rule_data = rule_generator.generate_rule(device)
    
    if rule_data:
        # ⚠️ 重要：转换为ORM模型
        rule_orm = RuleModel(
            rule_id=rule_data.rule_id,
            target_device_id=rule_data.target_device_id,
            auto_extracted_features=rule_data.auto_extracted_features,
            feature_weights=rule_data.feature_weights,
            match_threshold=rule_data.match_threshold,
            remark=rule_data.remark
        )
        session.add(rule_orm)
```

---

## ⚠️ 常见错误和解决方案

### 错误1：模型导入混淆

```python
# ❌ 错误：混淆了数据类和ORM模型
from modules.data_loader import Device, Rule  # 数据类，用于业务逻辑

# ✅ 正确：使用ORM模型进行数据库操作
from modules.models import Device, Rule  # ORM模型，用于数据库操作
```

**关键区别**：
- `modules.models` → SQLAlchemy ORM模型 → 数据库操作
- `modules.data_loader` → 数据类 → 业务逻辑

### 错误2：初始化顺序错误

```python
# ❌ 错误：缺少 db_manager 参数
db_loader = DatabaseLoader()

# ✅ 正确：先创建 db_manager
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)
```

### 错误3：配置加载方法错误

```python
# ❌ 错误：方法名不存在
config = db_loader.load_all_config()

# ✅ 正确：使用正确的方法名
config = db_loader.load_config()
```

### 错误4：特征提取器初始化错误

```python
# ❌ 错误：缺少 config 参数
feature_extractor = DeviceFeatureExtractor()

# ✅ 正确：传递 config
config = db_loader.load_config()
feature_extractor = DeviceFeatureExtractor(config)
```

### 错误5：规则生成器返回值类型混淆

```python
# ❌ 错误：直接添加数据类到数据库
rule = rule_generator.generate_rule(device)
session.add(rule)  # 错误：返回的是数据类，不是ORM模型

# ✅ 正确：转换为ORM模型
from modules.models import Rule as RuleModel

rule_data = rule_generator.generate_rule(device)  # 返回数据类
if rule_data:
    rule_orm = RuleModel(
        rule_id=rule_data.rule_id,
        target_device_id=rule_data.target_device_id,
        auto_extracted_features=rule_data.auto_extracted_features,
        feature_weights=rule_data.feature_weights,
        match_threshold=rule_data.match_threshold,
        remark=rule_data.remark
    )
    session.add(rule_orm)  # 正确：添加ORM模型
```

### 错误6：规则生成器参数错误

```python
# ❌ 错误：传递了多余的参数
features = feature_extractor.extract_features(device)
rule = rule_generator.generate_rule(device, features)

# ✅ 正确：只传递 device 对象
rule_data = rule_generator.generate_rule(device)
```

### 错误8：配置文件访问错误（已废弃的文件）

```python
# ❌ 错误：尝试读取已删除的 YAML 文件
with open('backend/config/device_params.yaml', 'r') as f:
    device_params = yaml.safe_load(f)

# ✅ 正确：从数据库读取
device_params = db_loader.get_config_by_key('device_params')

# ❌ 错误：尝试读取已删除的 JSON 文件
with open('backend/config/intelligent_extraction_config.json', 'r') as f:
    extraction_config = json.load(f)

# ✅ 正确：从数据库读取
extraction_config = db_loader.get_config_by_key('intelligent_extraction')
```

**配置文件迁移说明**：
- `backend/config/device_params.yaml` → 数据库 `device_params` 键
- `backend/config/intelligent_extraction_config.json` → 数据库 `intelligent_extraction` 键
- 所有配置现在都存储在数据库 `configs` 表中

---

## 快速参考

### 正确的初始化顺序

```python
# 1. DatabaseManager
db_manager = DatabaseManager("sqlite:///data/devices.db")

# 2. DatabaseLoader
db_loader = DatabaseLoader(db_manager)

# 3. 加载配置
config = db_loader.load_config()

# 4. 初始化其他组件
feature_extractor = DeviceFeatureExtractor(config)
rule_generator = RuleGenerator(config)
```

### 数据类 vs ORM模型对照表

| 用途 | 模块 | 类 | 说明 |
|------|------|-----|------|
| 数据库操作 | `modules.models` | `Device`, `Rule`, `Config` | SQLAlchemy ORM模型 |
| 业务逻辑 | `modules.data_loader` | `Device`, `Rule` | Python数据类 |

### 规则生成器返回值

- `rule_generator.generate_rule(device)` 返回 **数据类** (`modules.data_loader.Rule`)
- 需要转换为 **ORM模型** (`modules.models.Rule`) 才能保存到数据库

---

## 测试验证

运行以下命令验证数据库操作：

```bash
python test_database_operations.py
```

预期输出：
```
============================================================
  总计: 7/7 通过
============================================================

🎉 所有测试通过！
```

---

## 参考文档

- 完整指南：`Python数据库操作指南.md`
- 快速参考：`数据库操作快速参考.md`
- 测试结果：`数据库操作测试结果.md`

---

**最后更新**: 2026-03-07  
**测试状态**: ✅ 所有测试通过 (7/7)
