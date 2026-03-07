# 数据库快速参考

## 设备表（devices）列名

```python
# 正确的列名（按顺序）
columns = [
    'device_id',        # VARCHAR(100) - 设备ID（主键）
    'brand',            # VARCHAR(50) - 品牌
    'device_name',      # VARCHAR(100) - 设备名称
    'spec_model',       # VARCHAR(200) - 规格型号
    'device_type',      # VARCHAR(50) - 设备类型
    'detailed_params',  # TEXT - 详细参数
    'unit_price',       # INTEGER - 单价
    'raw_description',  # TEXT - 原始描述
    'key_params',       # JSON - 关键参数
    'confidence_score', # FLOAT - 置信度
    'input_method',     # VARCHAR(20) - 录入方式
    'created_at',       # DATETIME - 创建时间
    'updated_at'        # DATETIME - 更新时间
]
```

## 常用查询模板

### 1. 查询所有设备

```python
cursor.execute("SELECT * FROM devices")
devices = cursor.fetchall()
```

### 2. 查询表结构

```python
cursor.execute("PRAGMA table_info(devices)")
columns = cursor.fetchall()
```

### 3. 查询设备类型分布

```python
cursor.execute("SELECT device_type, COUNT(*) FROM devices GROUP BY device_type")
type_distribution = cursor.fetchall()
```

### 4. 查询特定类型设备

```python
cursor.execute("SELECT * FROM devices WHERE device_type = ?", ('温度传感器',))
devices = cursor.fetchall()
```

### 5. 查询设备详情（指定列）

```python
cursor.execute("""
    SELECT device_id, device_name, device_type, brand, 
           spec_model, unit_price, key_params 
    FROM devices 
    WHERE device_type = ? 
    LIMIT 5
""", ('温度传感器',))
```

### 6. 查询配置

```python
cursor.execute("SELECT config_value FROM configs WHERE config_key = ?", ('brand_keywords',))
result = cursor.fetchone()
```

## 当前数据统计（2026-03-07）

- **总设备数**：137
- **设备类型**：
  * 温度传感器：22个
  * 温湿度传感器：80个
  * 空气质量传感器：35个
- **品牌**：主要是霍尼韦尔
- **规则数**：137条
- **配置项**：31个

## 注意事项

1. ❌ **错误**：`SELECT id, device_name FROM devices` （没有 `id` 列）
2. ✅ **正确**：`SELECT device_id, device_name FROM devices`

3. ❌ **错误**：`SELECT name FROM devices` （没有 `name` 列）
4. ✅ **正确**：`SELECT device_name FROM devices`

5. ⚠️ **JSON字段**：`key_params` 需要用 `json.loads()` 解析
6. ⚠️ **主键**：使用 `device_id`（字符串），不是 `id`
