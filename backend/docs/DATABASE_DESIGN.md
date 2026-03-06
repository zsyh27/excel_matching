# 数据库设计文档

> DDC设备清单匹配报价系统 - 数据库设计详细说明

## 目录

1. [设计概述](#设计概述)
2. [数据模型](#数据模型)
3. [表结构详解](#表结构详解)
4. [索引策略](#索引策略)
5. [数据完整性](#数据完整性)
6. [性能优化](#性能优化)
7. [扩展性设计](#扩展性设计)

---

## 设计概述

### 设计目标

1. **数据完整性**：通过外键约束和事务保证数据一致性
2. **高性能**：通过索引优化查询性能，支持1000+设备
3. **可扩展性**：使用JSON字段支持灵活的数据结构
4. **向后兼容**：保持与JSON模式的数据结构兼容

### 技术选型

- **ORM框架**：SQLAlchemy 1.4+
- **数据库**：SQLite（开发）/ MySQL（生产）
- **字符集**：UTF-8 (utf8mb4)
- **事务隔离级别**：READ COMMITTED

### 设计原则

1. **单一职责**：每个表只负责一类数据
2. **最小冗余**：避免数据重复，通过关联查询获取
3. **灵活扩展**：使用JSON字段存储可变结构数据
4. **性能优先**：为常用查询创建索引

---

## 数据模型

### ER图

```
┌─────────────────────────┐
│       devices           │
│─────────────────────────│
│ device_id (PK)          │◄──────┐
│ brand                   │       │
│ device_name             │       │
│ spec_model              │       │
│ detailed_params         │       │
│ price                   │       │
│ device_type             │       │ 1:1
│ key_params (JSON)       │       │
│ input_method            │       │
│ created_at              │       │
│ updated_at              │       │
└─────────────────────────┘       │
                                  │
┌─────────────────────────────────┐
│           rules                 │
│─────────────────────────────────│
│ rule_id (PK)                    │
│ target_device_id (FK)           │───────┘
│ auto_extracted_features (JSON)  │
│ feature_weights (JSON)          │
│ match_threshold                 │
└─────────────────────────────────┘

┌─────────────────────────┐
│        configs          │
│─────────────────────────│
│ key (PK)                │
│ value (JSON)            │
└─────────────────────────┘
```

### 关系说明

1. **devices ↔ rules (1:1)**
   - 一个设备对应一条匹配规则
   - 删除设备时级联删除规则
   - 规则必须关联到存在的设备

2. **configs (独立表)**
   - 存储系统全局配置
   - 不与其他表关联
   - 支持动态配置更新

---

## 表结构详解

### 1. devices表

**用途**：存储设备库的基本信息和扩展属性

**字段设计**：

| 字段 | 类型 | 约束 | 说明 | 设计考虑 |
|------|------|------|------|---------|
| device_id | VARCHAR(50) | PK, NOT NULL | 设备唯一标识 | 使用VARCHAR而非INT，支持自定义ID格式 |
| brand | VARCHAR(100) | NOT NULL, INDEX | 品牌 | 索引支持品牌筛选查询 |
| device_name | VARCHAR(200) | NOT NULL, INDEX | 设备名称 | 索引支持名称搜索 |
| spec_model | VARCHAR(100) | NULL | 规格型号 | 可选字段，部分设备无型号 |
| detailed_params | TEXT | NULL | 详细参数 | TEXT类型支持长文本 |
| price | DECIMAL(10,2) | NOT NULL | 价格 | DECIMAL保证精度，避免浮点误差 |
| device_type | VARCHAR(50) | NULL, INDEX | 设备类型 | 用于动态表单，索引支持类型筛选 |
| key_params | JSON | NULL | 关键参数 | JSON格式，结构灵活 |
| input_method | VARCHAR(20) | DEFAULT 'manual', INDEX | 录入方式 | 跟踪数据来源 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 | 自动记录 |
| updated_at | DATETIME | DEFAULT NOW, ON UPDATE NOW | 更新时间 | 自动更新 |

**设计亮点**：

1. **灵活的ID设计**：VARCHAR类型支持DEV001、DEVICE_2024_001等多种格式
2. **JSON字段**：key_params支持不同设备类型的不同参数结构
3. **时间戳**：自动记录创建和更新时间，便于审计
4. **索引优化**：为常用查询字段创建索引

**数据示例**：

```json
{
  "device_id": "DEV001",
  "brand": "霍尼韦尔",
  "device_name": "电动二通阀",
  "spec_model": "VC4013",
  "detailed_params": "DN15 AC24V 带反馈",
  "price": 850.00,
  "device_type": "阀门",
  "key_params": {
    "口径": "DN15",
    "电压": "AC24V",
    "反馈": "有"
  },
  "input_method": "manual",
  "created_at": "2026-03-01 10:00:00",
  "updated_at": "2026-03-01 10:00:00"
}
```

### 2. rules表

**用途**：存储设备的匹配规则，用于Excel设备描述的智能匹配

**字段设计**：

| 字段 | 类型 | 约束 | 说明 | 设计考虑 |
|------|------|------|------|---------|
| rule_id | VARCHAR(50) | PK, NOT NULL | 规则唯一标识 | 格式：R_{device_id} |
| target_device_id | VARCHAR(50) | FK, NOT NULL, INDEX | 关联设备ID | 外键保证数据完整性 |
| auto_extracted_features | JSON | NOT NULL | 提取的特征列表 | 数组格式，存储所有特征 |
| feature_weights | JSON | NOT NULL | 特征权重映射 | 对象格式，特征→权重 |
| match_threshold | FLOAT | NOT NULL | 匹配阈值 | 通常为5.0 |

**设计亮点**：

1. **外键约束**：确保规则必须关联到存在的设备
2. **级联删除**：删除设备时自动删除规则
3. **JSON存储**：灵活存储不同数量的特征和权重
4. **索引优化**：target_device_id索引支持快速查询设备的规则

**数据示例**：

```json
{
  "rule_id": "R_DEV001",
  "target_device_id": "DEV001",
  "auto_extracted_features": [
    "霍尼韦尔",
    "电动",
    "二通阀",
    "dn15",
    "ac24v"
  ],
  "feature_weights": {
    "霍尼韦尔": 1.0,
    "电动": 4.0,
    "二通阀": 4.0,
    "dn15": 4.0,
    "ac24v": 4.0
  },
  "match_threshold": 5.0
}
```

### 3. configs表

**用途**：存储系统配置，支持动态配置更新

**字段设计**：

| 字段 | 类型 | 约束 | 说明 | 设计考虑 |
|------|------|------|------|---------|
| key | VARCHAR(100) | PK, NOT NULL | 配置键 | 唯一标识配置项 |
| value | JSON | NOT NULL | 配置值 | JSON格式，结构灵活 |

**设计亮点**：

1. **键值对设计**：简单灵活，易于扩展
2. **JSON值**：支持复杂的配置结构
3. **无外键**：独立存在，不影响其他表

**常用配置示例**：

```json
// feature_weight_config
{
  "key": "feature_weight_config",
  "value": {
    "brand_weight": 1,
    "device_type_weight": 4,
    "model_weight": 1,
    "parameter_weight": 4
  }
}

// normalization_map
{
  "key": "normalization_map",
  "value": {
    "℃": "",
    "Pa": "pa",
    "~": "-",
    "±": ""
  }
}

// synonym_map
{
  "key": "synonym_map",
  "value": {
    "阀": ["阀门"],
    "传感器": ["探头", "感应器"]
  }
}
```

---

## 索引策略

### 索引设计原则

1. **查询频率**：为常用查询字段创建索引
2. **选择性**：选择性高的字段优先创建索引
3. **复合索引**：考虑多字段组合查询
4. **维护成本**：平衡查询性能和写入性能

### devices表索引

| 索引名 | 字段 | 类型 | 用途 | 选择性 |
|--------|------|------|------|--------|
| PRIMARY | device_id | 主键 | 唯一标识 | 100% |
| idx_brand | brand | 单列 | 品牌筛选 | 高 |
| idx_device_name | device_name | 单列 | 名称搜索 | 中 |
| idx_device_type | device_type | 单列 | 类型筛选 | 高 |
| idx_input_method | input_method | 单列 | 来源筛选 | 低 |

**索引使用场景**：

```sql
-- 使用idx_brand索引
SELECT * FROM devices WHERE brand = '霍尼韦尔';

-- 使用idx_device_type索引
SELECT * FROM devices WHERE device_type = '阀门';

-- 使用idx_brand和idx_device_type索引（索引合并）
SELECT * FROM devices WHERE brand = '霍尼韦尔' AND device_type = '阀门';
```

### rules表索引

| 索引名 | 字段 | 类型 | 用途 | 选择性 |
|--------|------|------|------|--------|
| PRIMARY | rule_id | 主键 | 唯一标识 | 100% |
| idx_target_device | target_device_id | 单列 | 设备规则查询 | 100% |

**索引使用场景**：

```sql
-- 使用idx_target_device索引
SELECT * FROM rules WHERE target_device_id = 'DEV001';
```

### 索引维护

```sql
-- SQLite：分析索引使用情况
ANALYZE;

-- MySQL：分析表和索引
ANALYZE TABLE devices;
ANALYZE TABLE rules;

-- MySQL：优化表
OPTIMIZE TABLE devices;
OPTIMIZE TABLE rules;
```

---

## 数据完整性

### 主键约束

**目的**：确保每条记录唯一可识别

```sql
-- devices表主键
PRIMARY KEY (device_id)

-- rules表主键
PRIMARY KEY (rule_id)

-- configs表主键
PRIMARY KEY (key)
```

### 外键约束

**目的**：保证数据关联的完整性

```sql
-- rules表外键
FOREIGN KEY (target_device_id) 
REFERENCES devices(device_id) 
ON DELETE CASCADE
```

**级联删除行为**：
- 删除设备时，自动删除关联的规则
- 防止孤立规则的产生
- 保持数据一致性

### 非空约束

**目的**：确保关键字段必须有值

```sql
-- devices表非空字段
device_id NOT NULL
brand NOT NULL
device_name NOT NULL
price NOT NULL

-- rules表非空字段
rule_id NOT NULL
target_device_id NOT NULL
auto_extracted_features NOT NULL
feature_weights NOT NULL
match_threshold NOT NULL
```

### 默认值

**目的**：为可选字段提供合理的默认值

```sql
-- devices表默认值
input_method DEFAULT 'manual'
created_at DEFAULT CURRENT_TIMESTAMP
updated_at DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

### 数据验证

**应用层验证**：

```python
# 设备ID格式验证
def validate_device_id(device_id: str) -> bool:
    return len(device_id) <= 50 and device_id.strip() != ''

# 价格验证
def validate_price(price: float) -> bool:
    return price >= 0 and price <= 999999.99

# JSON格式验证
def validate_json_field(value: str) -> bool:
    try:
        json.loads(value)
        return True
    except:
        return False
```

---

## 性能优化

### 查询优化

#### 1. 使用索引

```sql
-- 好的做法：使用索引字段
SELECT * FROM devices WHERE brand = '霍尼韦尔';

-- 避免：在TEXT字段上使用LIKE
SELECT * FROM devices WHERE detailed_params LIKE '%DN15%';
```

#### 2. 分页查询

```sql
-- 好的做法：使用LIMIT和OFFSET
SELECT * FROM devices 
ORDER BY created_at DESC 
LIMIT 20 OFFSET 0;

-- 避免：一次加载所有数据
SELECT * FROM devices;
```

#### 3. 选择必要字段

```sql
-- 好的做法：只选择需要的字段
SELECT device_id, brand, device_name, price 
FROM devices;

-- 避免：使用SELECT *
SELECT * FROM devices;
```

### 写入优化

#### 1. 批量插入

```python
# 好的做法：批量插入
devices = [Device(...) for _ in range(100)]
session.bulk_save_objects(devices)
session.commit()

# 避免：逐条插入
for device_data in devices_data:
    device = Device(**device_data)
    session.add(device)
    session.commit()  # 每次都提交
```

#### 2. 事务管理

```python
# 好的做法：使用事务
with session_scope() as session:
    # 多个操作在一个事务中
    session.add(device)
    session.add(rule)
    # 自动提交或回滚

# 避免：频繁提交
session.add(device)
session.commit()
session.add(rule)
session.commit()
```

### 缓存策略

#### 1. 查询结果缓存

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_device_by_id(device_id: str) -> Device:
    return session.query(Device).filter_by(device_id=device_id).first()
```

#### 2. 配置缓存

```python
# 缓存配置，避免频繁查询
config_cache = {}

def get_config(key: str):
    if key not in config_cache:
        config_cache[key] = load_config_from_db(key)
    return config_cache[key]
```

---

## 扩展性设计

### 水平扩展

**分库分表策略**：

```python
# 按品牌分表
def get_table_name(brand: str) -> str:
    if brand in ['霍尼韦尔', '西门子']:
        return 'devices_premium'
    else:
        return 'devices_standard'
```

### 垂直扩展

**读写分离**：

```python
# 主库（写）
master_db = DatabaseManager('mysql://master:3306/ddc')

# 从库（读）
slave_db = DatabaseManager('mysql://slave:3306/ddc')

# 写操作使用主库
master_db.add_device(device)

# 读操作使用从库
devices = slave_db.load_devices()
```

### 字段扩展

**使用JSON字段**：

```python
# 添加新字段无需修改表结构
device.key_params = {
    "口径": "DN15",
    "电压": "AC24V",
    "新字段": "新值"  # 动态添加
}
```

### 版本管理

**Schema版本控制**：

```python
# migrations/versions/
# - v1_initial_schema.py
# - v2_add_device_type.py
# - v3_add_timestamps.py

def get_schema_version() -> str:
    return session.query(Config).filter_by(key='schema_version').first().value
```

---

## 附录

### 完整建表SQL

参考 [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)

### 性能基准测试

| 操作 | 数据量 | 耗时 | 要求 |
|------|--------|------|------|
| 加载设备 | 100 | 0.050s | < 2s |
| 批量创建 | 50 | 1.397s | < 10s |
| 查询筛选 | 1000 | 0.058s | < 1s |
| 分页查询 | 100 | 0.049s | < 2s |

### 数据库大小估算

```
单个设备记录大小：约1KB
1000个设备：约1MB
10000个设备：约10MB
100000个设备：约100MB

加上索引和规则：
1000个设备：约2-3MB
10000个设备：约20-30MB
100000个设备：约200-300MB
```

---

**文档版本**: v1.0  
**最后更新**: 2026-03-04  
**维护者**: DDC开发团队
