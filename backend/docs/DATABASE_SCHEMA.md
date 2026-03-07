# 数据库结构文档

## 数据库信息

**数据库文件**：`data/devices.db`
**数据库类型**：SQLite 3
**字符编码**：UTF-8

## 表结构

### 1. devices 表（设备表）

**用途**：存储所有设备信息

**表结构**：

| 列名 | 数据类型 | 说明 | 示例 |
|------|---------|------|------|
| device_id | VARCHAR(100) | 设备唯一标识（主键） | 霍尼韦尔_HST-RA_20260306180439234895 |
| brand | VARCHAR(50) | 品牌 | 霍尼韦尔 |
| device_name | VARCHAR(100) | 设备名称 | 室内温度传感器 |
| spec_model | VARCHAR(200) | 规格型号 | HST-RA |
| device_type | VARCHAR(50) | 设备类型 | 温度传感器 |
| detailed_params | TEXT | 详细参数 | （可为空） |
| unit_price | INTEGER | 单价（整数，单位：元） | 213 |
| raw_description | TEXT | 原始描述 | （可为空） |
| key_params | JSON | 关键参数（JSON格式） | {"检测对象": "温度", ...} |
| confidence_score | FLOAT | 置信度评分 | （可为空） |
| input_method | VARCHAR(20) | 录入方式 | excel |
| created_at | DATETIME | 创建时间 | 2026-03-06 10:04:39.237133 |
| updated_at | DATETIME | 更新时间 | 2026-03-06 10:04:39.237137 |

**索引**：
- PRIMARY KEY: device_id
- INDEX: device_type
- INDEX: brand

**统计信息**（截至2026-03-07）：
- 总记录数：137
- 设备类型分布：
  * 温度传感器：22个
  * 温湿度传感器：80个
  * 空气质量传感器：35个

**查询示例**：

```sql
-- 查询所有设备
SELECT * FROM devices;

-- 查询特定类型的设备
SELECT * FROM devices WHERE device_type = '温度传感器';

-- 查询特定品牌的设备
SELECT * FROM devices WHERE brand = '霍尼韦尔';

-- 统计设备类型分布
SELECT device_type, COUNT(*) as count 
FROM devices 
GROUP BY device_type;

-- 查询设备详情（包含JSON参数）
SELECT device_id, device_name, device_type, key_params 
FROM devices 
WHERE device_id = '霍尼韦尔_HST-RA_20260306180439234895';
```

### 2. rules 表（规则表）

**用途**：存储设备匹配规则

**表结构**：

| 列名 | 数据类型 | 说明 |
|------|---------|------|
| rule_id | INTEGER | 规则ID（主键，自增） |
| device_id | VARCHAR(100) | 关联的设备ID（外键） |
| rule_data | JSON | 规则数据（JSON格式） |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**统计信息**：
- 总记录数：137（每个设备一条规则）

**查询示例**：

```sql
-- 查询所有规则
SELECT * FROM rules;

-- 查询特定设备的规则
SELECT * FROM rules WHERE device_id = '霍尼韦尔_HST-RA_20260306180439234895';

-- 统计规则数量
SELECT COUNT(*) FROM rules;
```

### 3. configs 表（配置表）

**用途**：存储系统配置

**表结构**：

| 列名 | 数据类型 | 说明 |
|------|---------|------|
| config_key | VARCHAR(100) | 配置键（主键） |
| config_value | TEXT | 配置值（JSON格式） |
| description | TEXT | 配置描述 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

**配置项列表**（31个）：
1. brand_keywords - 品牌关键词
2. default_feature_weights - 默认特征权重
3. default_match_threshold - 默认匹配阈值
4. device_params - 设备参数
5. device_params_config - 设备参数配置
6. device_row_recognition - 设备行识别
7. device_type_keywords - 设备类型关键词
8. feature_extraction - 特征提取
9. feature_quality - 特征质量
10. feature_quality_scoring - 特征质量评分
11. feature_split_chars - 特征分隔符
12. feature_weight_config - 特征权重配置
13. feature_weight_strategy - 特征权重策略
14. feature_whitelist - 特征白名单
15. global_config - 全局配置
16. ignore_keywords - 忽略关键词
17. intelligent_extraction - 智能提取
18. intelligent_splitting - 智能拆分
19. location_words - 位置词
20. match_threshold_config - 匹配阈值配置
21. medium_keywords - 介质关键词
22. metadata_keywords - 元数据关键词
23. normalization_map - 归一化映射
24. performance_config - 性能配置
25. python_test_config - Python测试配置
26. synonym_map - 同义词映射
27. system_version - 系统版本
28. text_cleaning - 文本清理
29. ui_config - UI配置
30. unit_removal - 单位删除
31. whitelist_features - 白名单特征

**查询示例**：

```sql
-- 查询所有配置
SELECT config_key FROM configs;

-- 查询特定配置
SELECT * FROM configs WHERE config_key = 'brand_keywords';

-- 更新配置
UPDATE configs 
SET config_value = '{"keywords": ["霍尼韦尔", "西门子"]}', 
    updated_at = datetime('now') 
WHERE config_key = 'brand_keywords';
```

### 4. optimization_suggestions 表（优化建议表）

**用途**：存储系统优化建议

**表结构**：

| 列名 | 数据类型 | 说明 |
|------|---------|------|
| suggestion_id | INTEGER | 建议ID（主键，自增） |
| suggestion_type | VARCHAR(50) | 建议类型 |
| suggestion_data | JSON | 建议数据（JSON格式） |
| created_at | DATETIME | 创建时间 |

### 5. config_history 表（配置历史表）

**用途**：存储配置变更历史

**表结构**：

| 列名 | 数据类型 | 说明 |
|------|---------|------|
| history_id | INTEGER | 历史ID（主键，自增） |
| config_key | VARCHAR(100) | 配置键 |
| old_value | TEXT | 旧值 |
| new_value | TEXT | 新值 |
| changed_by | VARCHAR(50) | 修改人 |
| changed_at | DATETIME | 修改时间 |

## Python 查询示例

### 基础查询

```python
import sqlite3
import json

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 查询所有设备
cursor.execute("SELECT * FROM devices")
devices = cursor.fetchall()

# 查询设备表结构
cursor.execute("PRAGMA table_info(devices)")
columns = cursor.fetchall()
print("设备表结构:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# 查询设备类型分布
cursor.execute("SELECT device_type, COUNT(*) FROM devices GROUP BY device_type")
type_distribution = cursor.fetchall()
print("\n设备类型分布:")
for device_type, count in type_distribution:
    print(f"  {device_type}: {count}")

# 关闭连接
conn.close()
```

### 查询设备详情（包含JSON解析）

```python
import sqlite3
import json

conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 查询特定设备
cursor.execute("""
    SELECT device_id, device_name, device_type, brand, 
           spec_model, unit_price, key_params 
    FROM devices 
    WHERE device_type = '温度传感器' 
    LIMIT 5
""")

devices = cursor.fetchall()
for device in devices:
    device_id, name, dtype, brand, model, price, key_params = device
    
    # 解析JSON参数
    params = json.loads(key_params) if key_params else {}
    
    print(f"设备: {name}")
    print(f"  类型: {dtype}")
    print(f"  品牌: {brand}")
    print(f"  型号: {model}")
    print(f"  价格: {price}元")
    print(f"  参数: {params}")
    print()

conn.close()
```

### 查询配置

```python
import sqlite3
import json

conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 查询特定配置
cursor.execute("SELECT config_value FROM configs WHERE config_key = ?", ('brand_keywords',))
result = cursor.fetchone()

if result:
    config_value = json.loads(result[0])
    print("品牌关键词配置:")
    print(json.dumps(config_value, ensure_ascii=False, indent=2))

conn.close()
```

## 注意事项

1. **JSON字段**：`key_params`、`rule_data`、`config_value` 等字段存储的是JSON字符串，需要使用 `json.loads()` 解析

2. **日期时间**：`created_at`、`updated_at` 等字段使用 SQLite 的 DATETIME 格式

3. **字符编码**：数据库使用UTF-8编码，中文字符可以正常存储和查询

4. **主键**：
   - devices 表使用 `device_id` 作为主键（字符串）
   - rules 表使用 `rule_id` 作为主键（自增整数）
   - configs 表使用 `config_key` 作为主键（字符串）

5. **外键关系**：
   - rules.device_id → devices.device_id

## 常用查询脚本

### 快速检查数据库状态

```python
import sqlite3

def check_database_status(db_path='data/devices.db'):
    """快速检查数据库状态"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 80)
    print("数据库状态检查")
    print("=" * 80)
    
    # 1. 检查所有表
    print("\n【表列表】")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  {table[0]}: {count} 条记录")
    
    # 2. 检查设备类型分布
    print("\n【设备类型分布】")
    cursor.execute("SELECT device_type, COUNT(*) FROM devices GROUP BY device_type")
    for dtype, count in cursor.fetchall():
        print(f"  {dtype}: {count}")
    
    # 3. 检查品牌分布
    print("\n【品牌分布】")
    cursor.execute("SELECT brand, COUNT(*) FROM devices GROUP BY brand")
    for brand, count in cursor.fetchall():
        print(f"  {brand}: {count}")
    
    conn.close()
    print("=" * 80)

# 使用
check_database_status()
```

---

**文档版本**：1.0
**创建日期**：2026-03-07
**最后更新**：2026-03-07
**维护人**：开发团队
