# 匹配日志记录功能

## 概述

匹配日志记录功能自动记录每次设备匹配操作的详细信息，用于分析匹配准确率、诊断匹配问题和优化匹配规则。

**验证需求:** 10.9, 10.10, 10.11

## 功能特性

### 1. 自动日志记录

每次执行设备匹配时，系统会自动记录以下信息：

- **输入描述**: 原始设备描述文本
- **提取特征**: 从描述中提取的特征列表
- **匹配状态**: success（成功）或 failed（失败）
- **匹配设备**: 匹配到的设备ID（失败时为空）
- **匹配得分**: 权重累计得分
- **匹配阈值**: 使用的匹配阈值
- **匹配原因**: 成功或失败的详细原因
- **时间戳**: 匹配操作的时间

### 2. 日志查询

支持多种查询条件：

- **时间范围**: 按开始日期和结束日期筛选
- **匹配状态**: 筛选成功或失败的匹配
- **设备类型**: 按设备类型关键词筛选
- **分页**: 支持分页查询，避免一次加载过多数据

### 3. 统计分析

提供匹配统计信息：

- 总匹配次数
- 成功匹配次数
- 失败匹配次数
- 匹配准确率

## 数据库表结构

```sql
CREATE TABLE match_logs (
    log_id VARCHAR(50) PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    input_description TEXT NOT NULL,
    extracted_features JSON,
    match_status VARCHAR(20) NOT NULL,
    matched_device_id VARCHAR(100),
    match_score FLOAT,
    match_threshold FLOAT,
    match_reason TEXT
);

CREATE INDEX idx_match_logs_timestamp ON match_logs(timestamp);
CREATE INDEX idx_match_logs_status ON match_logs(match_status);
```

## API 接口

### 1. 获取匹配日志列表

**端点:** `GET /api/match-logs`

**查询参数:**
- `start_date`: 开始日期（ISO格式，可选）
- `end_date`: 结束日期（ISO格式，可选）
- `status`: 匹配状态（success/failed/all，默认all）
- `device_type`: 设备类型筛选（可选）
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认50）

**响应示例:**
```json
{
  "success": true,
  "total": 150,
  "page": 1,
  "page_size": 50,
  "logs": [
    {
      "log_id": "LOG_a1b2c3d4e5f6",
      "timestamp": "2026-02-14T10:30:15",
      "input_description": "温度传感器，0-50℃，4-20mA",
      "extracted_features": ["温度传感器", "0-50℃", "4-20ma"],
      "match_status": "success",
      "matched_device_id": "SENSOR001",
      "match_score": 8.5,
      "match_threshold": 5.0,
      "match_reason": "权重得分 8.5 超过阈值 5.0"
    }
  ]
}
```

### 2. 获取单条日志详情

**端点:** `GET /api/match-logs/<log_id>`

**响应示例:**
```json
{
  "success": true,
  "log": {
    "log_id": "LOG_a1b2c3d4e5f6",
    "timestamp": "2026-02-14T10:30:15",
    "input_description": "温度传感器，0-50℃，4-20mA",
    "extracted_features": ["温度传感器", "0-50℃", "4-20ma"],
    "match_status": "success",
    "matched_device_id": "SENSOR001",
    "match_score": 8.5,
    "match_threshold": 5.0,
    "match_reason": "权重得分 8.5 超过阈值 5.0"
  }
}
```

### 3. 获取匹配统计信息

**端点:** `GET /api/match-logs/statistics`

**查询参数:**
- `start_date`: 开始日期（ISO格式，可选）
- `end_date`: 结束日期（ISO格式，可选）

**响应示例:**
```json
{
  "success": true,
  "total": 1000,
  "success_count": 850,
  "failed_count": 150,
  "accuracy_rate": 85.0
}
```

## 使用示例

### Python 代码示例

```python
from modules.database import DatabaseManager
from modules.match_logger import MatchLogger
from modules.match_engine import MatchEngine

# 初始化数据库和日志记录器
db_manager = DatabaseManager('sqlite:///matching.db')
db_manager.create_tables()
match_logger = MatchLogger(db_manager)

# 初始化匹配引擎（传入日志记录器）
match_engine = MatchEngine(
    rules=rules,
    devices=devices,
    config=config,
    match_logger=match_logger
)

# 执行匹配（自动记录日志）
features = ['温度传感器', '0-50℃', '4-20ma']
result = match_engine.match(
    features,
    input_description="温度传感器，0-50℃，4-20mA"
)

# 查询日志
logs = match_logger.query_logs(
    status='failed',
    page=1,
    page_size=20
)

# 获取统计信息
stats = match_logger.get_statistics()
print(f"匹配准确率: {stats['accuracy_rate']}%")
```

### cURL 示例

```bash
# 获取最近的匹配日志
curl "http://localhost:5000/api/match-logs?page=1&page_size=20"

# 获取失败的匹配日志
curl "http://localhost:5000/api/match-logs?status=failed"

# 获取指定时间范围的日志
curl "http://localhost:5000/api/match-logs?start_date=2026-02-01T00:00:00&end_date=2026-02-14T23:59:59"

# 获取统计信息
curl "http://localhost:5000/api/match-logs/statistics"

# 获取单条日志详情
curl "http://localhost:5000/api/match-logs/LOG_a1b2c3d4e5f6"
```

## 注意事项

1. **数据库模式要求**: 匹配日志功能仅在数据库模式下可用。如果使用JSON文件模式，日志记录功能将被禁用。

2. **性能考虑**: 日志记录是异步的，不会影响匹配性能。即使日志记录失败，匹配操作也会正常完成。

3. **存储空间**: 日志会随时间累积，建议定期清理旧日志或设置自动归档策略。

4. **隐私保护**: 日志中包含原始设备描述，可能包含敏感信息，请注意数据安全。

## 后续扩展

以下功能将在后续任务中实现：

- **日志导出**: 支持将日志导出为CSV或Excel格式
- **日志分析**: 自动分析日志，识别高频误匹配特征
- **优化建议**: 基于日志数据生成规则优化建议
- **可视化**: 提供匹配趋势图表和统计报表

## 相关文档

- [数据库设计文档](../docs/database_design.md)
- [匹配引擎文档](../docs/match_engine.md)
- [API文档](../docs/api_documentation.md)
