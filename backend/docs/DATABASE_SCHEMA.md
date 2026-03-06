# 数据库Schema文档

> DDC设备清单匹配报价系统数据库设计文档

## 目录

1. [概述](#概述)
2. [数据表设计](#数据表设计)
3. [索引设计](#索引设计)
4. [关系设计](#关系设计)
5. [数据类型说明](#数据类型说明)
6. [约束规则](#约束规则)

---

## 概述

### 数据库信息

- **数据库名称**: ddc_devices
- **字符集**: UTF-8 (utf8mb4)
- **排序规则**: utf8mb4_unicode_ci
- **支持的数据库**: SQLite 3.x, MySQL 5.7+

### 设计原则

1. **数据完整性**: 使用外键约束保证数据一致性
2. **性能优化**: 为常用查询字段创建索引
3. **扩展性**: 使用JSON字段存储灵活的配置数据
4. **向后兼容**: 保持与JSON模式的数据结构兼容

---

## 数据表设计

### 1. devices（设备表）

存储设备库的基本信息。

**表结构**:

| 字段名 | 数据类型 | 长度 | 允许NULL | 默认值 | 说明 |
|--------|---------|------|---------|--------|------|
| device_id | VARCHAR | 50 | NO | - | 设备唯一标识（主键） |
| brand | VARCHAR | 100 | NO | - | 品牌 |
| device_name | VARCHAR | 200 | NO | - | 设备名称 |
| spec_model | VARCHAR | 100 | YES | NULL | 规格型号 |
| detailed_params | TEXT | - | YES | NULL | 详细参数 |
| price | DECIMAL | 10,2 | NO | - | 价格 |
| device_type | VARCHAR | 50 | YES | NULL | 设备类型 |
| key_params | JSON | - | YES | NULL | 关键参数（JSON格式） |
| input_method | VARCHAR | 20 | YES | 'manual' | 录入方式 |
| created_at | DATETIME | - | YES | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | - | YES | CURRENT_TIMESTAMP | 更新时间 |

**SQL定义**:

```sql
CREATE TABLE devices (
    device_id VARCHAR(50) PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    device_name VARCHAR(200) NOT NULL,
    spec_model VARCHAR(100),
    detailed_params TEXT,
    price DECIMAL(10, 2) NOT NULL,
    device_type VARCHAR(50),
    key_params JSON,
    input_method VARCHAR(20) DEFAULT 'manual',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**字段说明**:

- `device_id`: 设备唯一标识，格式建议：DEV + 序号（如DEV001）
- `brand`: 设备品牌，如"霍尼韦尔"、"西门子"
- `device_name`: 设备名称，如"电动二通阀"、"温度传感器"
- `spec_model`: 规格型号，如"VC4013"、"QAA2012"
- `detailed_params`: 详细参数描述，如"DN15 AC24V 带反馈"
- `price`: 设备价格，单位：元
- `device_type`: 设备类型，用于动态表单，如"阀门"、"传感器"
- `key_params`: 关键参数，JSON格式，如`{"口径": "DN15", "电压": "AC24V"}`
- `input_method`: 录入方式，可选值：manual（手动）、excel（Excel导入）、api（API创建）
- `created_at`: 记录创建时间
- `updated_at`: 记录最后更新时间

**示例数据**:

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

---

### 2. rules（规则表）

存储设备的匹配规则。

**表结构**:

| 字段名 | 数据类型 | 长度 | 允许NULL | 默认值 | 说明 |
|--------|---------|------|---------|--------|------|
| rule_id | VARCHAR | 50 | NO | - | 规则唯一标识（主键） |
| target_device_id | VARCHAR | 50 | NO | - | 关联的设备ID（外键） |
| auto_extracted_features | JSON | - | NO | - | 自动提取的特征列表 |
| feature_weights | JSON | - | NO | - | 特征权重映射 |
| match_threshold | FLOAT | - | NO | - | 匹配阈值 |

**SQL定义**:

```sql
CREATE TABLE rules (
    rule_id VARCHAR(50) PRIMARY KEY,
    target_device_id VARCHAR(50) NOT NULL,
    auto_extracted_features JSON NOT NULL,
    feature_weights JSON NOT NULL,
    match_threshold FLOAT NOT NULL,
    FOREIGN KEY (target_device_id) REFERENCES devices(device_id) ON DELETE CASCADE
);
```

**字段说明**:

- `rule_id`: 规则唯一标识，格式建议：R_ + device_id（如R_DEV001）
- `target_device_id`: 关联的设备ID，外键关联到devices表
- `auto_extracted_features`: 自动提取的特征列表，如`["霍尼韦尔", "电动", "二通阀", "dn15"]`
- `feature_weights`: 特征权重映射，如`{"霍尼韦尔": 1.0, "电动": 4.0, "二通阀": 4.0, "dn15": 4.0}`
- `match_threshold`: 匹配阈值，通常为5.0

**示例数据**:

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

---

### 3. configs（配置表）

存储系统配置信息。

**表结构**:

| 字段名 | 数据类型 | 长度 | 允许NULL | 默认值 | 说明 |
|--------|---------|------|---------|--------|------|
| key | VARCHAR | 100 | NO | - | 配置键（主键） |
| value | JSON | - | NO | - | 配置值（JSON格式） |

**SQL定义**:

```sql
CREATE TABLE configs (
    key VARCHAR(100) PRIMARY KEY,
    value JSON NOT NULL
);
```

**字段说明**:

- `key`: 配置键，如"feature_weight_config"、"normalization_map"
- `value`: 配置值，JSON格式，结构根据配置类型而定

**示例数据**:

```json
{
  "key": "feature_weight_config",
  "value": {
    "brand_weight": 1,
    "device_type_weight": 4,
    "model_weight": 1,
    "parameter_weight": 4
  }
}
```

**常用配置键**:

| 配置键 | 说明 | 示例值 |
|--------|------|--------|
| feature_weight_config | 特征权重配置 | `{"brand_weight": 1, "device_type_weight": 4}` |
| normalization_map | 归一化映射 | `{"℃": "", "Pa": "pa"}` |
| synonym_map | 同义词映射 | `{"阀": ["阀门"], "传感器": ["探头"]}` |
| ignore_keywords | 忽略关键词 | `["施工要求", "验收"]` |
| brand_keywords | 品牌关键词 | `["霍尼韦尔", "西门子"]` |
| device_type_keywords | 设备类型关键词 | `{"阀门": ["阀", "valve"]}` |
| global_config | 全局配置 | `{"default_match_threshold": 5.0}` |

---

## 索引设计

### devices表索引

| 索引名 | 字段 | 类型 | 说明 |
|--------|------|------|------|
| PRIMARY | device_id | 主键 | 设备ID唯一索引 |
| idx_brand | brand | 普通索引 | 优化品牌筛选查询 |
| idx_device_name | device_name | 普通索引 | 优化设备名称搜索 |
| idx_device_type | device_type | 普通索引 | 优化设备类型筛选 |
| idx_input_method | input_method | 普通索引 | 优化录入方式筛选 |

**创建索引SQL**:

```sql
CREATE INDEX idx_brand ON devices(brand);
CREATE INDEX idx_device_name ON devices(device_name);
CREATE INDEX idx_device_type ON devices(device_type);
CREATE INDEX idx_input_method ON devices(input_method);
```

### rules表索引

| 索引名 | 字段 | 类型 | 说明 |
|--------|------|------|------|
| PRIMARY | rule_id | 主键 | 规则ID唯一索引 |
| idx_target_device | target_device_id | 普通索引 | 优化设备规则关联查询 |

**创建索引SQL**:

```sql
CREATE INDEX idx_target_device ON rules(target_device_id);
```

### configs表索引

| 索引名 | 字段 | 类型 | 说明 |
|--------|------|------|------|
| PRIMARY | key | 主键 | 配置键唯一索引 |

---

## 关系设计

### ER图

```
┌─────────────────┐
│    devices      │
│─────────────────│
│ device_id (PK)  │◄─────┐
│ brand           │      │
│ device_name     │      │
│ spec_model      │      │
│ detailed_params │      │
│ price           │      │
│ device_type     │      │
│ key_params      │      │
│ input_method    │      │
│ created_at      │      │
│ updated_at      │      │
└─────────────────┘      │
                         │
                         │ 1:1
                         │
┌─────────────────────────┐
│        rules            │
│─────────────────────────│
│ rule_id (PK)            │
│ target_device_id (FK)   │──────┘
│ auto_extracted_features │
│ feature_weights         │
│ match_threshold         │
└─────────────────────────┘

┌─────────────────┐
│    configs      │
│─────────────────│
│ key (PK)        │
│ value           │
└─────────────────┘
```

### 关系说明

1. **devices ↔ rules (1:1)**
   - 一个设备对应一条匹配规则
   - 外键：`rules.target_device_id` → `devices.device_id`
   - 级联删除：删除设备时自动删除关联规则

2. **configs (独立表)**
   - 配置表独立存在，不与其他表关联
   - 用于存储系统全局配置

---

## 数据类型说明

### VARCHAR vs TEXT

- **VARCHAR**: 用于长度有限的字符串（如品牌、设备名称）
  - 优点：索引效率高，查询速度快
  - 缺点：长度限制

- **TEXT**: 用于长文本（如详细参数）
  - 优点：无长度限制
  - 缺点：不能创建全文索引（MySQL）

### JSON字段

JSON字段用于存储结构化但灵活的数据：

- **key_params**: 设备的关键参数，结构根据设备类型而定
- **auto_extracted_features**: 规则的特征列表
- **feature_weights**: 规则的特征权重映射
- **value**: 配置的值

**JSON字段优势**:
- ✅ 灵活的数据结构
- ✅ 支持嵌套对象和数组
- ✅ 可以使用JSON函数查询

**JSON字段查询示例**:

```sql
-- MySQL
SELECT * FROM devices WHERE JSON_EXTRACT(key_params, '$.口径') = 'DN15';

-- SQLite
SELECT * FROM devices WHERE json_extract(key_params, '$.口径') = 'DN15';
```

### DECIMAL vs FLOAT

- **DECIMAL(10,2)**: 用于价格字段
  - 优点：精确存储，无浮点误差
  - 格式：10位总长度，2位小数

- **FLOAT**: 用于匹配阈值
  - 优点：存储空间小
  - 缺点：可能有浮点误差

---

## 约束规则

### 主键约束

- `devices.device_id`: 设备ID必须唯一
- `rules.rule_id`: 规则ID必须唯一
- `configs.key`: 配置键必须唯一

### 外键约束

- `rules.target_device_id` → `devices.device_id`
  - 级联删除：`ON DELETE CASCADE`
  - 说明：删除设备时自动删除关联规则

### 非空约束

**devices表**:
- `device_id`, `brand`, `device_name`, `price`: 必填

**rules表**:
- 所有字段必填

**configs表**:
- 所有字段必填

### 默认值

- `devices.input_method`: 默认 'manual'
- `devices.created_at`: 默认当前时间
- `devices.updated_at`: 默认当前时间，更新时自动更新

---

## 数据迁移

### 从JSON迁移到数据库

参考 [DATABASE_MIGRATION_GUIDE.md](DATABASE_MIGRATION_GUIDE.md)

### Schema版本管理

当前Schema版本：v2.1.0

**版本历史**:

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| v2.1.0 | 2026-03-04 | 添加device_type、key_params、input_method字段 |
| v2.0.0 | 2026-02-12 | 初始数据库Schema |

---

## 性能优化建议

### 1. 索引使用

- ✅ 为常用查询字段创建索引
- ✅ 避免在JSON字段上创建索引
- ✅ 定期分析索引使用情况

### 2. 查询优化

```sql
-- 好的做法：使用索引字段
SELECT * FROM devices WHERE brand = '霍尼韦尔';

-- 避免：在TEXT字段上使用LIKE
SELECT * FROM devices WHERE detailed_params LIKE '%DN15%';

-- 好的做法：使用分页
SELECT * FROM devices LIMIT 20 OFFSET 0;
```

### 3. 数据维护

```sql
-- SQLite：压缩数据库
VACUUM;

-- MySQL：优化表
OPTIMIZE TABLE devices;
OPTIMIZE TABLE rules;
```

---

## 附录

### 完整建表SQL

**SQLite**:

```sql
-- 创建devices表
CREATE TABLE devices (
    device_id VARCHAR(50) PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    device_name VARCHAR(200) NOT NULL,
    spec_model VARCHAR(100),
    detailed_params TEXT,
    price DECIMAL(10, 2) NOT NULL,
    device_type VARCHAR(50),
    key_params TEXT,  -- SQLite使用TEXT存储JSON
    input_method VARCHAR(20) DEFAULT 'manual',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_brand ON devices(brand);
CREATE INDEX idx_device_name ON devices(device_name);
CREATE INDEX idx_device_type ON devices(device_type);
CREATE INDEX idx_input_method ON devices(input_method);

-- 创建rules表
CREATE TABLE rules (
    rule_id VARCHAR(50) PRIMARY KEY,
    target_device_id VARCHAR(50) NOT NULL,
    auto_extracted_features TEXT NOT NULL,  -- SQLite使用TEXT存储JSON
    feature_weights TEXT NOT NULL,  -- SQLite使用TEXT存储JSON
    match_threshold FLOAT NOT NULL,
    FOREIGN KEY (target_device_id) REFERENCES devices(device_id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_target_device ON rules(target_device_id);

-- 创建configs表
CREATE TABLE configs (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL  -- SQLite使用TEXT存储JSON
);
```

**MySQL**:

```sql
-- 创建devices表
CREATE TABLE devices (
    device_id VARCHAR(50) PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    device_name VARCHAR(200) NOT NULL,
    spec_model VARCHAR(100),
    detailed_params TEXT,
    price DECIMAL(10, 2) NOT NULL,
    device_type VARCHAR(50),
    key_params JSON,
    input_method VARCHAR(20) DEFAULT 'manual',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_brand (brand),
    INDEX idx_device_name (device_name),
    INDEX idx_device_type (device_type),
    INDEX idx_input_method (input_method)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建rules表
CREATE TABLE rules (
    rule_id VARCHAR(50) PRIMARY KEY,
    target_device_id VARCHAR(50) NOT NULL,
    auto_extracted_features JSON NOT NULL,
    feature_weights JSON NOT NULL,
    match_threshold FLOAT NOT NULL,
    FOREIGN KEY (target_device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
    INDEX idx_target_device (target_device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建configs表
CREATE TABLE configs (
    key VARCHAR(100) PRIMARY KEY,
    value JSON NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

**文档版本**: v2.1.0  
**最后更新**: 2026-03-04  
**维护者**: DDC开发团队
