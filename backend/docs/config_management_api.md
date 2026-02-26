# 配置管理 API 文档

## 概述

配置管理 API 提供了完整的配置 CRUD 操作,支持动态管理系统配置。所有配置更新后会自动重新初始化相关组件(预处理器、匹配引擎等)。

**验证需求**: 23.1-23.7

## API 端点

### 1. 获取所有配置

```
GET /api/config
```

**验证需求**: 23.1

**响应示例**:
```json
{
  "success": true,
  "config": {
    "global_config": {
      "default_match_threshold": 0.7,
      "max_match_results": 5
    },
    "text_preprocessing": {
      "feature_split_chars": [",", "，", " "],
      "normalize_chars": {"（": "(", "）": ")"}
    }
  }
}
```

### 2. 获取单个配置

```
GET /api/config/:key
```

**验证需求**: 23.2

**路径参数**:
- `key`: 配置键

**响应示例**:
```json
{
  "success": true,
  "data": {
    "config_key": "global_config",
    "config_value": {
      "default_match_threshold": 0.7,
      "max_match_results": 5
    },
    "description": "全局配置项"
  }
}
```

**错误响应** (404):
```json
{
  "success": false,
  "error_code": "CONFIG_NOT_FOUND",
  "error_message": "配置不存在: invalid_key"
}
```

### 3. 创建新配置

```
POST /api/config
```

**验证需求**: 23.4, 23.7

**请求体**:
```json
{
  "config_key": "custom_settings",
  "config_value": {
    "enable_cache": true,
    "cache_ttl": 3600
  },
  "description": "自定义设置"
}
```

**响应示例** (201):
```json
{
  "success": true,
  "data": {
    "config_key": "custom_settings"
  },
  "message": "配置创建成功"
}
```

**错误响应** (400 - 配置已存在):
```json
{
  "success": false,
  "error_code": "CONFIG_ALREADY_EXISTS",
  "error_message": "配置已存在: custom_settings"
}
```

**错误响应** (400 - 无效 JSON):
```json
{
  "success": false,
  "error_code": "INVALID_JSON_FORMAT",
  "error_message": "无效的 JSON 格式: ..."
}
```

### 4. 更新配置

```
PUT /api/config
```

**验证需求**: 23.3, 23.6

**请求体**:
```json
{
  "updates": {
    "global_config": {
      "default_match_threshold": 0.75,
      "max_match_results": 10
    }
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "配置更新成功"
}
```

**说明**: 配置更新后会自动重新初始化以下组件:
- TextPreprocessor (文本预处理器)
- MatchEngine (匹配引擎)
- DeviceRowClassifier (设备行分类器)

### 5. 删除配置

```
DELETE /api/config/:key
```

**验证需求**: 23.5

**路径参数**:
- `key`: 配置键

**响应示例**:
```json
{
  "success": true,
  "data": {
    "config_key": "custom_settings"
  },
  "message": "配置删除成功"
}
```

**错误响应** (404):
```json
{
  "success": false,
  "error_code": "CONFIG_NOT_FOUND",
  "error_message": "配置不存在: invalid_key"
}
```

## 数据验证

### JSON 格式验证

**验证需求**: 23.7

所有配置值必须是有效的 JSON 格式。系统会在创建和更新配置时验证 JSON 格式:

- ✅ 有效: `{"key": "value"}`, `[1, 2, 3]`, `"string"`, `123`, `true`
- ❌ 无效: `{invalid json}`, `undefined`, `NaN`

如果提供无效的 JSON 格式,API 会返回 400 错误:

```json
{
  "success": false,
  "error_code": "INVALID_JSON_FORMAT",
  "error_message": "无效的 JSON 格式: Expecting property name enclosed in double quotes"
}
```

## 组件重新初始化

**验证需求**: 23.6

当配置更新或删除后,系统会自动重新初始化以下组件以应用新配置:

1. **TextPreprocessor**: 文本预处理器,使用新的预处理规则
2. **MatchEngine**: 匹配引擎,使用新的匹配阈值和规则
3. **DeviceRowClassifier**: 设备行分类器,使用新的分类配置

这确保了配置更改立即生效,无需重启应用。

## 使用示例

### 示例 1: 创建自定义配置

```bash
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "config_key": "my_custom_config",
    "config_value": {
      "feature_enabled": true,
      "max_retries": 3
    },
    "description": "我的自定义配置"
  }'
```

### 示例 2: 获取配置详情

```bash
curl http://localhost:5000/api/config/my_custom_config
```

### 示例 3: 更新配置

```bash
curl -X PUT http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "updates": {
      "my_custom_config": {
        "feature_enabled": false,
        "max_retries": 5
      }
    }
  }'
```

### 示例 4: 删除配置

```bash
curl -X DELETE http://localhost:5000/api/config/my_custom_config
```

## 错误处理

所有 API 端点遵循统一的错误响应格式:

```json
{
  "success": false,
  "error_code": "ERROR_CODE",
  "error_message": "错误描述",
  "details": {
    "error_detail": "详细错误信息"
  }
}
```

### 常见错误码

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-------------|
| `CONFIG_NOT_FOUND` | 配置不存在 | 404 |
| `CONFIG_ALREADY_EXISTS` | 配置已存在 | 400 |
| `INVALID_JSON_FORMAT` | 无效的 JSON 格式 | 400 |
| `VALIDATION_ERROR` | 数据验证失败 | 400 |
| `MISSING_DATA` | 请求体为空 | 400 |
| `DATABASE_MODE_REQUIRED` | 需要数据库模式 | 400 |
| `CREATE_CONFIG_ERROR` | 创建配置失败 | 500 |
| `UPDATE_CONFIG_ERROR` | 更新配置失败 | 500 |
| `DELETE_CONFIG_ERROR` | 删除配置失败 | 500 |
| `GET_CONFIG_ERROR` | 获取配置失败 | 500 |

## 测试

配置管理 API 包含完整的测试套件:

### 运行集成测试

```bash
python -m pytest backend/tests/test_config_api_integration.py -v
```

### 测试覆盖

- ✅ 创建配置 (成功、重复、无效 JSON)
- ✅ 获取配置 (单个、所有、不存在)
- ✅ 更新配置 (成功、不存在、无效 JSON)
- ✅ 删除配置 (成功、不存在)
- ✅ 完整 CRUD 流程
- ✅ JSON 格式验证

## 实现细节

### DatabaseLoader 方法

配置管理 API 使用 `DatabaseLoader` 类的以下方法:

- `load_config()`: 加载所有配置
- `get_config_by_key(config_key)`: 获取配置值
- `get_config_detail_by_key(config_key)`: 获取配置详情(包括描述)
- `add_config(config_key, config_value, description)`: 添加配置
- `update_config(config_key, config_value)`: 更新配置
- `delete_config(config_key)`: 删除配置

### 数据库模式

配置存储在 `configs` 表中:

```sql
CREATE TABLE configs (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value JSON NOT NULL,
    description TEXT
);
```

## 注意事项

1. **数据库模式要求**: 所有配置管理 API 端点都需要系统运行在数据库模式下
2. **JSON 格式**: 配置值必须是有效的 JSON 格式
3. **组件重新初始化**: 配置更新后会自动重新初始化相关组件,可能会有短暂的性能影响
4. **并发安全**: 使用数据库事务确保并发操作的安全性

## 相关文档

- [设备管理 API](./device_management_api.md)
- [规则管理 API](./rule_management_api.md)
- [数据库迁移指南](./MIGRATION_GUIDE.md)
