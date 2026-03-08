# 设计文档：设备数据批量导入系统

## 系统架构

### 核心组件

```
┌─────────────────────────────────────────────────────────┐
│                   Excel Import System                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐      ┌──────────────────────────┐    │
│  │ Excel Parser │─────>│ Device Params Validator  │    │
│  └──────────────┘      └──────────────────────────┘    │
│         │                         │                      │
│         v                         v                      │
│  ┌──────────────────────────────────────────────┐      │
│  │         Device Importer                       │      │
│  │  - Generate device_id                         │      │
│  │  - Map fields to database columns             │      │
│  │  - Handle JSON serialization                  │      │
│  └──────────────────────────────────────────────┘      │
│         │                                                │
│         v                                                │
│  ┌──────────────────────────────────────────────┐      │
│  │         Rule Generator                         │      │
│  │  - Extract features                            │      │
│  │  - Assign weights                              │      │
│  │  - Generate rules                              │      │
│  └──────────────────────────────────────────────┘      │
│         │                                                │
│         v                                                │
│  ┌──────────────────────────────────────────────┐      │
│  │         Database Manager                       │      │
│  │  - Transaction management                      │      │
│  │  - Cascade operations                          │      │
│  └──────────────────────────────────────────────┘      │
│         │                                                │
│         v                                                │
│  ┌──────────────────────────────────────────────┐      │
│  │         Report Generator                       │      │
│  │  - Statistics                                  │      │
│  │  - Examples                                    │      │
│  │  - Markdown output                             │      │
│  └──────────────────────────────────────────────┘      │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## 数据流

### 导入流程

```
Excel File
    │
    v
┌─────────────────────┐
│  1. Parse Excel     │
│  - Read headers     │
│  - Extract rows     │
│  - Map columns      │
└─────────────────────┘
    │
    v
┌─────────────────────┐
│  2. Validate Config │
│  - Check types      │
│  - Check params     │
│  - Auto-add if need │
└─────────────────────┘
    │
    v
┌─────────────────────┐
│  3. Import Devices  │
│  - Generate ID      │
│  - Create ORM obj   │
│  - Save to DB       │
└─────────────────────┘
    │
    v
┌─────────────────────┐
│  4. Generate Rules  │
│  - Extract features │
│  - Assign weights   │
│  - Save rules       │
└─────────────────────┘
    │
    v
┌─────────────────────┐
│  5. Generate Report │
│  - Statistics       │
│  - Examples         │
│  - Save markdown    │
└─────────────────────┘
```

## 数据模型

### Excel文件结构

```
| 品牌 | 设备类型 | 设备名称 | 规格型号 | 单价 | 参数1 | 参数2 | ... |
|------|---------|---------|---------|------|-------|-------|-----|
| 霍尼韦尔 | 座阀 | 水二通调节阀 | V5011N1040/U | 2603 | 2通 | DN15 | ... |
```

**标准字段**（前5列）：
- 品牌（brand）
- 设备类型（device_type）
- 设备名称（device_name）
- 规格型号（spec_model）
- 单价（unit_price）

**参数字段**（第6列起）：
- 动态列，列名即参数名
- 值可以为空
- 存储到key_params JSON字段

### 数据库模型

```python
class Device(Base):
    __tablename__ = 'devices'
    
    device_id = Column(String(100), primary_key=True)
    brand = Column(String(50))
    device_name = Column(String(100))
    spec_model = Column(String(200))
    device_type = Column(String(50))
    unit_price = Column(Integer)
    key_params = Column(JSON)  # SQLAlchemy handles serialization
    detailed_params = Column(Text)
    input_method = Column(String(20))  # 'excel_import'
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    rules = relationship("Rule", back_populates="device", cascade="all, delete-orphan")
```

### key_params结构

```json
{
  "通数": {"value": "2通"},
  "通径": {"value": "DN15"},
  "英制尺寸": {"value": "1/2\""},
  "介质": {"value": "水"},
  "Cv值": {"value": "1.6"},
  "压力等级": {"value": "PN16"}
}
```

### 规则模型

```python
class Rule(Base):
    __tablename__ = 'rules'
    
    rule_id = Column(String(100), primary_key=True)
    target_device_id = Column(String(100), ForeignKey('devices.device_id'))
    auto_extracted_features = Column(JSON)  # List of features
    feature_weights = Column(JSON)  # Dict of feature -> weight
    match_threshold = Column(Float)
    remark = Column(Text)
    
    device = relationship("Device", back_populates="rules")
```

### 规则数据结构

```json
{
  "rule_id": "R_HON_C9C6CCC1",
  "target_device_id": "HON_C9C6CCC1",
  "auto_extracted_features": [
    "霍尼韦尔",
    "座阀",
    "水二通调节阀",
    "v5011n1040/u",
    "2通",
    "dn15",
    "水"
  ],
  "feature_weights": {
    "霍尼韦尔": 10.0,
    "座阀": 20.0,
    "水二通调节阀": 1.0,
    "v5011n1040/u": 5.0,
    "2通": 15.0,
    "dn15": 15.0,
    "水": 15.0
  },
  "match_threshold": 5.0
}
```

## 核心算法

### 1. Excel解析算法

```python
def load_excel_devices(file_path):
    """从Excel加载设备数据"""
    wb = load_workbook(file_path)
    ws = wb.active
    
    # 获取表头
    headers = [cell.value for cell in ws[1]]
    
    # 标准字段索引
    brand_idx = headers.index('品牌')
    device_type_idx = headers.index('设备类型')
    device_name_idx = headers.index('设备名称')
    spec_model_idx = headers.index('规格型号')
    unit_price_idx = headers.index('单价')
    
    # 参数字段（第6列起）
    param_fields = headers[5:]
    
    devices = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        # 提取标准字段
        device = {
            'brand': row[brand_idx],
            'device_type': row[device_type_idx],
            'device_name': row[device_name_idx],
            'spec_model': row[spec_model_idx],
            'unit_price': int(row[unit_price_idx]) if row[unit_price_idx] else 0
        }
        
        # 提取参数（key_params）
        key_params = {}
        for i, param_name in enumerate(param_fields, start=5):
            param_value = row[i]
            if param_value is not None and param_value != '':
                key_params[param_name] = {
                    "value": str(param_value)  # 转换为字符串
                }
        
        device['key_params'] = key_params
        devices.append(device)
    
    return devices, param_fields
```

### 2. 设备导入算法

```python
def import_devices(devices):
    """导入设备到数据库并生成规则"""
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    config = db_loader.load_config()
    
    feature_extractor = DeviceFeatureExtractor(config)
    rule_generator = RuleGenerator(config)
    
    success_count = 0
    error_count = 0
    rule_count = 0
    
    with db_manager.session_scope() as session:
        for device_data in devices:
            try:
                # 生成设备ID
                device_id = f"HON_{uuid.uuid4().hex[:8].upper()}"
                
                # 创建设备ORM对象
                device_orm = DeviceModel(
                    device_id=device_id,
                    brand=device_data['brand'],
                    device_name=device_data['device_name'],
                    spec_model=device_data['spec_model'],
                    device_type=device_data['device_type'],
                    unit_price=device_data['unit_price'],
                    key_params=device_data['key_params'],  # ✅ 直接传递dict
                    input_method='excel_import',
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                # 添加设备到数据库
                session.add(device_orm)
                session.flush()  # 确保设备已保存
                
                # 生成规则
                rule_data = rule_generator.generate_rule(device_orm)
                
                if rule_data:
                    # 转换为ORM模型
                    rule_orm = RuleModel(
                        rule_id=rule_data.rule_id,
                        target_device_id=rule_data.target_device_id,
                        auto_extracted_features=rule_data.auto_extracted_features,
                        feature_weights=rule_data.feature_weights,
                        match_threshold=rule_data.match_threshold,
                        remark=rule_data.remark
                    )
                    session.add(rule_orm)
                    rule_count += 1
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"❌ 导入失败: {device_data.get('spec_model')} - {str(e)}")
    
    return success_count, rule_count, error_count
```

### 3. 规则生成算法

规则生成使用现有的`RuleGenerator`类，遵循设备录入阶段的特征提取规则：

**特征提取**：
1. 品牌（brand） → 权重10.0
2. 设备类型（device_type） → 权重20.0
3. 设备名称（device_name） → 权重1.0
4. 规格型号（spec_model） → 权重5.0
5. 关键参数（key_params） → 权重15.0

**权重分配原则**：
- 只使用设备字段类型，不使用关键词判断
- 不使用元数据关键词（仅在匹配阶段使用）
- 保持字段完整性，不做拆分和清理

## JSON序列化处理

### ⚠️ 关键设计决策

**问题**：SQLAlchemy的JSON列类型会自动处理序列化和反序列化

**错误做法**：
```python
# ❌ 错误：手动序列化导致双重序列化
device_orm.key_params = json.dumps(key_params)
# 结果：数据库中存储的是字符串的JSON，而不是JSON对象
```

**正确做法**：
```python
# ✅ 正确：直接传递dict对象
device_orm.key_params = key_params
# SQLAlchemy会自动调用json.dumps()序列化
```

**原理**：
- SQLAlchemy的`JSON`列类型内部使用`TypeDecorator`
- 写入时自动调用`json.dumps()`
- 读取时自动调用`json.loads()`
- 开发者只需要操作Python的dict对象

## 配置管理

### 设备参数配置文件

**位置**：`backend/config/device_params.yaml`

**结构**：
```yaml
device_types:
  座阀:
    keywords:
      - 座阀
      - 调节阀
      - valve
    params:
      - name: 通径
        pattern: 'DN\s*([0-9]+)'
        required: false
        data_type: string
        unit: null
      - name: 通数
        pattern: '([0-9]+)通'
        required: false
        data_type: string
        unit: null
      - name: 介质
        pattern: null
        required: false
        data_type: string
        unit: null
```

### 配置检查和自动添加

```python
def check_device_params_config(device_types, param_fields):
    """检查设备参数配置"""
    config_path = 'backend/config/device_params.yaml'
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    existing_types = set(config['device_types'].keys())
    missing_types = []
    
    for dtype in device_types:
        if dtype not in existing_types:
            missing_types.append(dtype)
    
    return len(missing_types) == 0
```

## 错误处理策略

### 1. 单设备失败不影响其他设备

```python
for device_data in devices:
    try:
        # 导入设备和生成规则
        ...
    except Exception as e:
        error_count += 1
        print(f"❌ 导入失败: {device_data.get('spec_model')} - {str(e)}")
        # 继续处理下一个设备
```

### 2. 事务管理

```python
with db_manager.session_scope() as session:
    # 所有操作在一个事务中
    # session_scope会自动commit或rollback
```

### 3. 数据验证

```python
# 验证必填字段
if not device_data.get('brand'):
    raise ValueError("品牌不能为空")

# 验证数据类型
unit_price = int(device_data['unit_price']) if device_data['unit_price'] else 0
```

## 报告生成

### 导入报告结构

```markdown
# 座阀设备导入完成报告

## ✅ 导入完成

**导入日期**：2026-03-08
**数据来源**：data/霍尼韦尔座阀设备清单_v2.xlsx
**导入状态**：✅ 成功

## 📊 导入统计

| 项目 | 数量 |
|------|------|
| 总设备数 | 418 |
| 成功导入 | 418 |
| 生成规则 | 418 |
| 失败 | 0 |
| **成功率** | **100%** |

## 📋 设备类型分布

| 设备类型 | 数量 | 占比 |
|---------|------|------|
| 座阀 | 382 | 91.4% |
| 执行器 | 36 | 8.6% |

## 🔧 导入的参数字段

1. Cv值
2. Kvs值
3. 介质
...

## 🎯 规则生成详情

### 规则示例
...
```

## 性能优化

### 1. 批量操作

```python
# 使用session.flush()而不是每次commit
session.add(device_orm)
session.flush()  # 确保设备已保存，获得ID
```

### 2. 进度显示

```python
if i % 50 == 0:
    print(f"  已处理: {i}/{len(devices)}")
```

### 3. 索引优化

```sql
CREATE INDEX idx_device_type ON devices(device_type);
CREATE INDEX idx_brand ON devices(brand);
CREATE INDEX idx_input_method ON devices(input_method);
```

## 清理和重新导入

### 清理脚本

```python
def cleanup_excel_imports():
    """清理Excel导入的设备"""
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    
    with db_manager.session_scope() as session:
        # 查询Excel导入的设备
        devices = session.query(DeviceModel).filter(
            DeviceModel.input_method == 'excel_import'
        ).all()
        
        print(f"找到 {len(devices)} 个Excel导入的设备")
        
        # 删除设备（级联删除规则）
        for device in devices:
            session.delete(device)
        
        print(f"✅ 已删除 {len(devices)} 个设备及其规则")
```

## 测试策略

### 1. 单元测试

- 测试Excel解析功能
- 测试配置检查功能
- 测试设备导入功能
- 测试规则生成功能
- 测试报告生成功能

### 2. 集成测试

- 测试完整的导入流程
- 测试错误处理
- 测试清理和重新导入

### 3. 性能测试

- 测试导入速度（>= 10设备/秒）
- 测试大批量导入（>1000设备）

## 安全考虑

1. **SQL注入防护**：使用ORM，不拼接SQL
2. **文件路径验证**：验证Excel文件路径
3. **数据验证**：验证所有输入数据
4. **事务管理**：确保数据一致性
5. **错误日志**：记录所有错误信息

## 扩展性

### 支持更多Excel格式

```python
# 支持不同的列顺序
def find_column_index(headers, possible_names):
    for name in possible_names:
        if name in headers:
            return headers.index(name)
    raise ValueError(f"找不到列: {possible_names}")
```

### 支持更多设备类型

```python
# 通过配置文件添加新设备类型
device_type_configs = {
    '新设备类型': {
        'keywords': ['关键词1', '关键词2'],
        'params': [...]
    }
}
```

## 依赖关系

```
device-data-import
    ├── database-migration (数据库结构)
    ├── intelligent-device-input (特征提取和规则生成)
    ├── openpyxl (Excel解析)
    ├── SQLAlchemy (ORM)
    └── PyYAML (配置文件)
```

## 参考文档

- 设备录入指南：`.kiro/steering/device-input-guide.md`
- 数据库结构：`.kiro/steering/database-schema.md`
- 智能特征提取：`.kiro/steering/intelligent-extraction-system-guide.md`

