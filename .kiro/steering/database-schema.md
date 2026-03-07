---
inclusion: always
---

# 数据库结构参考

## 数据库位置
- **路径**: `data/devices.db`
- **类型**: SQLite 3

## 设备表（devices）列名

**重要**：主键是 `device_id`（不是 `id`），设备名称是 `device_name`（不是 `name`）

```
device_id        VARCHAR(100)  - 设备ID（主键）
brand            VARCHAR(50)   - 品牌
device_name      VARCHAR(100)  - 设备名称
spec_model       VARCHAR(200)  - 规格型号
device_type      VARCHAR(50)   - 设备类型
detailed_params  TEXT          - 详细参数
unit_price       INTEGER       - 单价
raw_description  TEXT          - 原始描述
key_params       JSON          - 关键参数（JSON字符串）
confidence_score FLOAT         - 置信度
input_method     VARCHAR(20)   - 录入方式
created_at       DATETIME      - 创建时间
updated_at       DATETIME      - 更新时间
```

## 其他表

- **rules**: 规则表（rule_id, device_id, rule_data, created_at, updated_at）
- **configs**: 配置表（config_key, config_value, description, created_at, updated_at）
- **optimization_suggestions**: 优化建议表
- **config_history**: 配置历史表

## 当前数据统计（2026-03-07）

- 总设备数：137
- 设备类型：温度传感器(22)、温湿度传感器(80)、空气质量传感器(35)
- 品牌：主要是霍尼韦尔
- 规则数：137条
- 配置项：31个

## 常用查询模板

```python
# 查询所有设备
cursor.execute("SELECT * FROM devices")

# 查询表结构
cursor.execute("PRAGMA table_info(devices)")

# 查询设备类型分布
cursor.execute("SELECT device_type, COUNT(*) FROM devices GROUP BY device_type")

# 查询特定类型设备（使用正确的列名）
cursor.execute("SELECT device_id, device_name, device_type FROM devices WHERE device_type = ?", ('温度传感器',))
```

## 常见错误

❌ `SELECT id FROM devices` → ✅ `SELECT device_id FROM devices`
❌ `SELECT name FROM devices` → ✅ `SELECT device_name FROM devices`

## 注意事项

1. `key_params` 是 JSON 字符串，需要用 `json.loads()` 解析
2. 主键是 `device_id`（字符串），不是自增的 `id`
3. 使用参数化查询防止 SQL 注入：`cursor.execute("... WHERE x = ?", (value,))`
