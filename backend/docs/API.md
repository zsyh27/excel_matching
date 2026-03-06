# DDC 设备清单匹配报价系统 - RESTful API 文档

> 版本: v2.1.0  
> 最后更新: 2026-03-04

## 概述

本文档描述了DDC设备清单匹配报价系统在数据库模式下提供的RESTful API接口。

### 基础信息

- **Base URL**: `http://localhost:5000/api`
- **Content-Type**: `application/json`
- **字符编码**: UTF-8

### 响应格式

所有API响应遵循统一格式：

**成功响应**:
```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "错误信息",
  "code": "ERROR_CODE"
}
```

### HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 设备管理 API

### 1. 获取设备列表

获取设备列表，支持分页和筛选。

**请求**:
```
GET /api/devices
```

**查询参数**:

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| page | integer | 否 | 页码（默认1） | 1 |
| per_page | integer | 否 | 每页数量（默认20） | 20 |
| brand | string | 否 | 品牌筛选 | 霍尼韦尔 |
| name | string | 否 | 设备名称筛选 | 阀门 |
| device_type | string | 否 | 设备类型筛选 | 阀门 |
| min_price | float | 否 | 最低价格 | 100.0 |
| max_price | float | 否 | 最高价格 | 1000.0 |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "devices": [
      {
        "device_id": "DEV001",
        "brand": "霍尼韦尔",
        "device_name": "电动二通阀",
        "spec_model": "VC4013",
        "detailed_params": "DN15 AC24V",
        "price": 850.00,
        "device_type": "阀门",
        "key_params": {"口径": "DN15", "电压": "AC24V"},
        "input_method": "manual",
        "created_at": "2026-03-01T10:00:00",
        "updated_at": "2026-03-01T10:00:00"
      }
    ],
    "total": 720,
    "page": 1,
    "per_page": 20,
    "pages": 36
  }
}
```

### 2. 获取单个设备

获取指定设备的详细信息，包括关联的匹配规则。

**请求**:
```
GET /api/devices/:id
```

**路径参数**:
- `id`: 设备ID

**响应示例**:
```json
{
  "success": true,
  "data": {
    "device": {
      "device_id": "DEV001",
      "brand": "霍尼韦尔",
      "device_name": "电动二通阀",
      "spec_model": "VC4013",
      "detailed_params": "DN15 AC24V",
      "price": 850.00,
      "device_type": "阀门",
      "key_params": {"口径": "DN15", "电压": "AC24V"}
    },
    "rule": {
      "rule_id": "R_DEV001",
      "auto_extracted_features": ["霍尼韦尔", "电动", "二通阀", "dn15"],
      "feature_weights": {"霍尼韦尔": 1.0, "电动": 4.0},
      "match_threshold": 5.0
    }
  }
}
```

### 3. 创建设备

创建新设备，支持自动生成匹配规则。

**请求**:
```
POST /api/devices
Content-Type: application/json
```

**请求体**:
```json
{
  "device_id": "DEV002",
  "brand": "西门子",
  "device_name": "温度传感器",
  "spec_model": "QAA2012",
  "detailed_params": "0-50℃ 4-20mA",
  "price": 320.00,
  "device_type": "传感器",
  "key_params": {
    "测量范围": "0-50℃",
    "输出信号": "4-20mA"
  },
  "auto_generate_rule": true
}
```

**字段说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| device_id | string | 是 | 设备唯一标识 |
| brand | string | 是 | 品牌 |
| device_name | string | 是 | 设备名称 |
| spec_model | string | 否 | 规格型号 |
| detailed_params | string | 否 | 详细参数 |
| price | float | 是 | 价格 |
| device_type | string | 否 | 设备类型（用于动态表单） |
| key_params | object | 否 | 关键参数（JSON格式） |
| auto_generate_rule | boolean | 否 | 是否自动生成规则（默认false） |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "device_id": "DEV002",
    "rule_generated": true,
    "rule_id": "R_DEV002"
  },
  "message": "设备创建成功，规则已自动生成"
}
```

### 4. 更新设备

更新设备信息，支持重新生成匹配规则。

**请求**:
```
PUT /api/devices/:id
Content-Type: application/json
```

**请求体**:
```json
{
  "price": 900.00,
  "detailed_params": "DN15 AC24V 带反馈",
  "regenerate_rule": true
}
```

**字段说明**:
- 所有字段均为可选
- `regenerate_rule`: 是否重新生成规则（默认false）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "device_id": "DEV001",
    "rule_regenerated": true
  },
  "message": "设备更新成功，规则已重新生成"
}
```

### 5. 删除设备

删除设备，自动级联删除关联的匹配规则。

**请求**:
```
DELETE /api/devices/:id
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "device_id": "DEV001",
    "rules_deleted": 1
  },
  "message": "设备删除成功，已级联删除1条规则"
}
```

### 6. 批量导入设备

从Excel文件批量导入设备。

**请求**:
```
POST /api/devices/batch
Content-Type: multipart/form-data
```

**表单数据**:
- `file`: Excel文件（.xlsx, .xls）
- `auto_generate_rules`: 是否自动生成规则（可选，默认true）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total": 100,
    "success": 95,
    "updated": 3,
    "failed": 2,
    "errors": [
      {"row": 10, "error": "缺少必填字段: device_id"},
      {"row": 25, "error": "价格格式错误"}
    ]
  },
  "message": "批量导入完成"
}
```

---

## 规则管理 API

### 1. 获取规则列表

获取匹配规则列表。

**请求**:
```
GET /api/rules
```

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| device_id | string | 否 | 按设备ID筛选 |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "rules": [
      {
        "rule_id": "R_DEV001",
        "target_device_id": "DEV001",
        "auto_extracted_features": ["霍尼韦尔", "电动", "二通阀"],
        "feature_weights": {"霍尼韦尔": 1.0, "电动": 4.0},
        "match_threshold": 5.0
      }
    ]
  }
}
```

### 2. 获取单个规则

获取指定规则的详细信息。

**请求**:
```
GET /api/rules/:id
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "rule": {
      "rule_id": "R_DEV001",
      "target_device_id": "DEV001",
      "auto_extracted_features": ["霍尼韦尔", "电动", "二通阀"],
      "feature_weights": {"霍尼韦尔": 1.0},
      "match_threshold": 5.0
    },
    "device": {
      "device_id": "DEV001",
      "brand": "霍尼韦尔",
      "device_name": "电动二通阀"
    }
  }
}
```

### 3. 创建规则

手动创建匹配规则。

**请求**:
```
POST /api/rules
Content-Type: application/json
```

**请求体**:
```json
{
  "rule_id": "R_DEV003",
  "target_device_id": "DEV003",
  "auto_extracted_features": ["西门子", "温度", "传感器"],
  "feature_weights": {
    "西门子": 1.0,
    "温度": 4.0,
    "传感器": 4.0
  },
  "match_threshold": 5.0
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "rule_id": "R_DEV003"
  },
  "message": "规则创建成功"
}
```

### 4. 更新规则

更新规则信息。

**请求**:
```
PUT /api/rules/:id
Content-Type: application/json
```

**请求体**:
```json
{
  "match_threshold": 6.0,
  "feature_weights": {
    "西门子": 1.5,
    "温度": 4.5
  }
}
```

### 5. 删除规则

删除规则（不影响关联的设备）。

**请求**:
```
DELETE /api/rules/:id
```

### 6. 批量生成规则

为多个设备批量生成或重新生成规则。

**请求**:
```
POST /api/rules/generate
Content-Type: application/json
```

**请求体**:
```json
{
  "device_ids": ["DEV001", "DEV002", "DEV003"],
  "force_regenerate": false
}
```

**字段说明**:
- `device_ids`: 设备ID列表（可选，为空则为所有设备生成）
- `force_regenerate`: 是否强制重新生成已有规则（默认false）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total": 3,
    "generated": 2,
    "updated": 1,
    "failed": 0
  },
  "message": "规则生成完成"
}
```

---

## 配置管理 API

### 1. 获取所有配置

获取系统所有配置项。

**请求**:
```
GET /api/config
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "configs": [
      {
        "key": "feature_weight_config",
        "value": {
          "brand_weight": 1,
          "device_type_weight": 4
        }
      }
    ]
  }
}
```

### 2. 获取单个配置

获取指定配置项的值。

**请求**:
```
GET /api/config/:key
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "key": "feature_weight_config",
    "value": {
      "brand_weight": 1,
      "device_type_weight": 4
    }
  }
}
```

### 3. 创建配置

创建新的配置项。

**请求**:
```
POST /api/config
Content-Type: application/json
```

**请求体**:
```json
{
  "key": "custom_setting",
  "value": {
    "enabled": true,
    "threshold": 0.8
  }
}
```

### 4. 更新配置

更新配置项，系统会自动重新初始化相关组件。

**请求**:
```
PUT /api/config
Content-Type: application/json
```

**请求体**:
```json
{
  "key": "feature_weight_config",
  "value": {
    "brand_weight": 1,
    "device_type_weight": 5
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "key": "feature_weight_config",
    "components_reinitialized": ["preprocessor", "match_engine"]
  },
  "message": "配置更新成功，相关组件已重新初始化"
}
```

### 5. 删除配置

删除配置项。

**请求**:
```
DELETE /api/config/:key
```

---

## 统计信息 API

### 1. 获取数据库统计概览

获取数据库的统计信息概览。

**请求**:
```
GET /api/database/statistics
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_devices": 720,
    "total_rules": 715,
    "total_brands": 15,
    "rule_coverage": 99.3,
    "devices_without_rules": 5
  }
}
```

### 2. 获取品牌分布

获取各品牌的设备数量分布。

**请求**:
```
GET /api/database/statistics/brands
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "brands": [
      {"brand": "霍尼韦尔", "count": 250},
      {"brand": "西门子", "count": 180},
      {"brand": "江森自控", "count": 150}
    ]
  }
}
```

### 3. 获取价格分布

获取设备价格区间分布。

**请求**:
```
GET /api/database/statistics/prices
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "price_ranges": [
      {"range": "0-500", "count": 200},
      {"range": "500-1000", "count": 300},
      {"range": "1000-2000", "count": 150}
    ]
  }
}
```

### 4. 获取最近添加的设备

获取最近添加的设备列表。

**请求**:
```
GET /api/database/statistics/recent?limit=10
```

**查询参数**:
- `limit`: 返回数量（默认10）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "devices": [
      {
        "device_id": "DEV720",
        "brand": "霍尼韦尔",
        "device_name": "电动二通阀",
        "created_at": "2026-03-04T10:00:00"
      }
    ]
  }
}
```

### 5. 获取没有规则的设备

获取没有匹配规则的设备列表。

**请求**:
```
GET /api/database/statistics/without-rules
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "devices": [
      {
        "device_id": "DEV100",
        "brand": "西门子",
        "device_name": "温度传感器"
      }
    ],
    "count": 5
  }
}
```

---

## 数据一致性 API

### 1. 检查数据一致性

检查数据库中的数据一致性问题。

**请求**:
```
GET /api/database/consistency-check
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_devices": 720,
    "total_rules": 715,
    "devices_without_rules": [
      {"device_id": "DEV100", "device_name": "温度传感器"}
    ],
    "orphan_rules": [
      {"rule_id": "R_DEV999", "target_device_id": "DEV999"}
    ],
    "issues_count": 6
  }
}
```

### 2. 修复数据一致性问题

自动修复数据一致性问题。

**请求**:
```
POST /api/database/fix-consistency
Content-Type: application/json
```

**请求体**:
```json
{
  "generate_missing_rules": true,
  "delete_orphan_rules": true
}
```

**字段说明**:
- `generate_missing_rules`: 为没有规则的设备生成规则
- `delete_orphan_rules`: 删除孤立规则（关联设备不存在）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "rules_generated": 5,
    "orphan_rules_deleted": 1
  },
  "message": "数据一致性问题已修复"
}
```

---

## 动态表单 API

### 1. 获取设备类型配置

获取设备类型配置，用于前端动态表单渲染。

**请求**:
```
GET /api/device-types
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "device_types": [
      {
        "type": "阀门",
        "display_name": "阀门",
        "parameters": [
          {
            "name": "口径",
            "type": "string",
            "required": true,
            "unit": "DN",
            "options": ["DN15", "DN20", "DN25"]
          },
          {
            "name": "电压",
            "type": "string",
            "required": true,
            "options": ["AC24V", "AC220V", "DC24V"]
          }
        ]
      }
    ]
  }
}
```

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| DEVICE_NOT_FOUND | 设备不存在 |
| DEVICE_ID_EXISTS | 设备ID已存在 |
| RULE_NOT_FOUND | 规则不存在 |
| RULE_ID_EXISTS | 规则ID已存在 |
| CONFIG_NOT_FOUND | 配置不存在 |
| INVALID_JSON | JSON格式错误 |
| MISSING_REQUIRED_FIELD | 缺少必填字段 |
| FOREIGN_KEY_ERROR | 外键约束错误 |
| DATABASE_ERROR | 数据库错误 |

---

## 使用示例

### Python示例

```python
import requests

# 创建设备
response = requests.post(
    'http://localhost:5000/api/devices',
    json={
        'device_id': 'DEV001',
        'brand': '霍尼韦尔',
        'device_name': '电动二通阀',
        'price': 850.00,
        'auto_generate_rule': True
    }
)
print(response.json())

# 获取设备列表
response = requests.get(
    'http://localhost:5000/api/devices',
    params={'brand': '霍尼韦尔', 'page': 1}
)
print(response.json())
```

### JavaScript示例

```javascript
// 创建设备
fetch('http://localhost:5000/api/devices', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    device_id: 'DEV001',
    brand: '霍尼韦尔',
    device_name: '电动二通阀',
    price: 850.00,
    auto_generate_rule: true
  })
})
.then(res => res.json())
.then(data => console.log(data));

// 获取设备列表
fetch('http://localhost:5000/api/devices?brand=霍尼韦尔&page=1')
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 附录

### 数据模型

#### Device（设备）
```json
{
  "device_id": "string (主键)",
  "brand": "string (必填)",
  "device_name": "string (必填)",
  "spec_model": "string",
  "detailed_params": "string",
  "price": "float (必填)",
  "device_type": "string",
  "key_params": "object (JSON)",
  "input_method": "string (manual/excel/api)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Rule（规则）
```json
{
  "rule_id": "string (主键)",
  "target_device_id": "string (外键)",
  "auto_extracted_features": "array",
  "feature_weights": "object (JSON)",
  "match_threshold": "float"
}
```

#### Config（配置）
```json
{
  "key": "string (主键)",
  "value": "object (JSON)"
}
```

---

**文档版本**: v2.1.0  
**最后更新**: 2026-03-04  
**维护者**: DDC开发团队


---

## 高级功能

### 批量操作

#### 批量创建设备

**请求**:
```bash
POST /api/devices/batch
Content-Type: multipart/form-data
```

**表单数据**:
- `file`: Excel文件（.xlsx, .xls）
- `auto_generate_rules`: 是否自动生成规则（可选，默认true）
- `update_existing`: 是否更新已存在的设备（可选，默认false）

**Excel文件格式**:

| 设备ID | 品牌 | 设备名称 | 规格型号 | 详细参数 | 价格 |
|--------|------|---------|---------|---------|------|
| DEV001 | 霍尼韦尔 | 电动二通阀 | VC4013 | DN15 AC24V | 850.00 |
| DEV002 | 西门子 | 温度传感器 | QAA2012 | 0-50℃ | 320.00 |

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total": 100,
    "success": 95,
    "updated": 3,
    "failed": 2,
    "errors": [
      {
        "row": 10,
        "device_id": "DEV010",
        "error": "缺少必填字段: brand"
      },
      {
        "row": 25,
        "device_id": "DEV025",
        "error": "价格格式错误: abc"
      }
    ],
    "rules_generated": 95
  },
  "message": "批量导入完成：成功95个，更新3个，失败2个"
}
```

#### 批量生成规则

**请求**:
```bash
POST /api/rules/generate
Content-Type: application/json
```

**请求体**:
```json
{
  "device_ids": ["DEV001", "DEV002", "DEV003"],
  "force_regenerate": false
}
```

**字段说明**:
- `device_ids`: 设备ID列表（可选，为空则为所有设备生成）
- `force_regenerate`: 是否强制重新生成已有规则（默认false）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total": 3,
    "generated": 2,
    "updated": 1,
    "failed": 0,
    "skipped": 0,
    "details": [
      {
        "device_id": "DEV001",
        "status": "updated",
        "rule_id": "R_DEV001"
      },
      {
        "device_id": "DEV002",
        "status": "generated",
        "rule_id": "R_DEV002"
      },
      {
        "device_id": "DEV003",
        "status": "generated",
        "rule_id": "R_DEV003"
      }
    ]
  },
  "message": "规则生成完成：生成2条，更新1条"
}
```

### 数据导出

#### 导出设备列表

**请求**:
```bash
GET /api/devices/export?format=excel&brand=霍尼韦尔
```

**查询参数**:
- `format`: 导出格式（excel, csv, json）
- 其他筛选参数同GET /api/devices

**响应**:
- Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
- Content-Disposition: attachment; filename="devices_20260304.xlsx"

### 数据统计

#### 高级统计查询

**请求**:
```bash
GET /api/database/statistics/advanced
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "overview": {
      "total_devices": 720,
      "total_rules": 715,
      "total_brands": 15,
      "rule_coverage": 99.3
    },
    "by_brand": [
      {
        "brand": "霍尼韦尔",
        "device_count": 250,
        "avg_price": 1250.50,
        "min_price": 320.00,
        "max_price": 5800.00
      }
    ],
    "by_device_type": [
      {
        "device_type": "阀门",
        "count": 300,
        "percentage": 41.7
      }
    ],
    "by_input_method": [
      {
        "input_method": "excel",
        "count": 650,
        "percentage": 90.3
      },
      {
        "input_method": "manual",
        "count": 70,
        "percentage": 9.7
      }
    ],
    "price_distribution": {
      "0-500": 200,
      "500-1000": 300,
      "1000-2000": 150,
      "2000+": 70
    },
    "recent_activity": {
      "devices_added_today": 5,
      "devices_added_this_week": 23,
      "devices_added_this_month": 95
    }
  }
}
```

---

## 性能优化建议

### 分页查询

对于大数据量查询，始终使用分页：

```bash
# 好的做法
GET /api/devices?page=1&per_page=20

# 避免
GET /api/devices  # 返回所有数据
```

### 字段选择

只请求需要的字段（如果API支持）：

```bash
# 好的做法
GET /api/devices?fields=device_id,brand,device_name,price

# 避免
GET /api/devices  # 返回所有字段
```

### 缓存策略

对于不常变化的数据，使用缓存：

```javascript
// 客户端缓存示例
const cache = new Map();

async function getDeviceTypes() {
  if (cache.has('device_types')) {
    return cache.get('device_types');
  }
  
  const response = await fetch('/api/device-types');
  const data = await response.json();
  
  cache.set('device_types', data);
  return data;
}
```

### 批量操作

使用批量API而非循环调用：

```javascript
// 好的做法：批量生成规则
await fetch('/api/rules/generate', {
  method: 'POST',
  body: JSON.stringify({
    device_ids: ['DEV001', 'DEV002', 'DEV003']
  })
});

// 避免：循环调用
for (const deviceId of deviceIds) {
  await fetch(`/api/rules/generate/${deviceId}`, {
    method: 'POST'
  });
}
```

---

## 安全性

### 认证和授权

**注意**：当前版本未实现认证，生产环境需要添加：

```javascript
// 建议的认证方式
fetch('/api/devices', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
});
```

### 输入验证

所有API都会验证输入：

- 必填字段检查
- 数据类型验证
- 长度限制检查
- SQL注入防护
- XSS防护

### 错误处理

API使用标准HTTP状态码：

| 状态码 | 说明 | 示例 |
|--------|------|------|
| 200 | 成功 | 查询成功 |
| 201 | 创建成功 | 设备创建成功 |
| 400 | 请求错误 | 缺少必填字段 |
| 404 | 资源不存在 | 设备不存在 |
| 409 | 冲突 | 设备ID已存在 |
| 500 | 服务器错误 | 数据库连接失败 |

---

## 版本控制

### API版本

当前版本：v1

未来版本将通过URL路径区分：

```bash
# v1 (当前)
GET /api/devices

# v2 (未来)
GET /api/v2/devices
```

### 向后兼容

我们承诺：
- 不会删除现有字段
- 不会改变现有字段的含义
- 新增字段为可选
- 废弃功能会提前通知

---

## 限流和配额

### 建议的限流策略

生产环境建议实施：

- 每IP每分钟最多100个请求
- 批量操作每次最多1000条记录
- 文件上传最大10MB

### 响应头

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1709539200
```

---

## 监控和日志

### 请求日志

所有API请求都会记录：

```
2026-03-04 10:00:00 - INFO - GET /api/devices?page=1 - 200 - 0.050s
2026-03-04 10:00:05 - INFO - POST /api/devices - 201 - 0.120s
2026-03-04 10:00:10 - ERROR - GET /api/devices/INVALID - 404 - 0.010s
```

### 性能监控

关键指标：

- 平均响应时间
- 95分位响应时间
- 错误率
- 请求量

---

## 常见问题

### Q1: 如何处理大文件上传？

A: 使用分块上传或流式处理：

```javascript
const formData = new FormData();
formData.append('file', file);

await fetch('/api/devices/batch', {
  method: 'POST',
  body: formData
});
```

### Q2: 如何优化查询性能？

A: 
1. 使用分页
2. 添加适当的索引
3. 只查询需要的字段
4. 使用缓存

### Q3: 如何处理并发更新？

A: 使用乐观锁：

```json
{
  "device_id": "DEV001",
  "version": 1,
  "price": 900.00
}
```

### Q4: 如何批量删除？

A: 使用批量删除API（如果实现）：

```bash
DELETE /api/devices/batch
Content-Type: application/json

{
  "device_ids": ["DEV001", "DEV002"]
}
```

---

## 更新日志

### v1.0.0 (2026-03-04)

- ✅ 初始版本发布
- ✅ 设备管理API
- ✅ 规则管理API
- ✅ 配置管理API
- ✅ 统计信息API
- ✅ 数据一致性API
- ✅ 动态表单API

---

**API文档版本**: v1.0.0  
**最后更新**: 2026-03-04  
**维护者**: DDC开发团队  
**反馈**: 请提交Issue或联系开发团队
