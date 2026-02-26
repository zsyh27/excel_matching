# 设备管理 API 文档

本文档描述了设备管理 API 的使用方法。

验证需求: 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7

## 前提条件

设备管理 API 需要系统运行在**数据库模式**下。请确保配置文件中设置了：

```json
{
  "storage_mode": "database",
  "database_url": "sqlite:///data/devices.db"
}
```

## API 端点

### 1. 获取设备列表（增强版）

**端点**: `GET /api/devices`

**功能**: 获取设备列表，支持过滤和分页

**查询参数**:
- `brand` (可选): 按品牌过滤
- `name` (可选): 按名称模糊搜索
- `min_price` (可选): 最低价格
- `max_price` (可选): 最高价格
- `page` (可选): 页码，默认 1
- `page_size` (可选): 每页数量，默认 50

**请求示例**:
```bash
# 获取所有设备
curl http://localhost:5000/api/devices

# 按品牌过滤
curl http://localhost:5000/api/devices?brand=霍尼韦尔

# 按名称搜索
curl http://localhost:5000/api/devices?name=传感器

# 价格范围过滤
curl http://localhost:5000/api/devices?min_price=100&max_price=1000

# 分页查询
curl http://localhost:5000/api/devices?page=2&page_size=20
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "devices": [
      {
        "device_id": "D001",
        "brand": "霍尼韦尔",
        "device_name": "温度传感器",
        "spec_model": "T7350A1008",
        "detailed_params": "测量范围: -40~120℃",
        "unit_price": 450.0,
        "has_rules": true
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 50
  }
}
```

---

### 2. 获取单个设备详情

**端点**: `GET /api/devices/:id`

**功能**: 查询单个设备的详细信息，包含关联的规则

**路径参数**:
- `id`: 设备 ID

**请求示例**:
```bash
curl http://localhost:5000/api/devices/D001
```

**成功响应** (200):
```json
{
  "success": true,
  "data": {
    "device_id": "D001",
    "brand": "霍尼韦尔",
    "device_name": "温度传感器",
    "spec_model": "T7350A1008",
    "detailed_params": "测量范围: -40~120℃",
    "unit_price": 450.0,
    "rules": [
      {
        "rule_id": "R_D001",
        "match_threshold": 0.7
      }
    ]
  }
}
```

**错误响应** (404):
```json
{
  "success": false,
  "error_code": "DEVICE_NOT_FOUND",
  "error_message": "设备不存在: D999"
}
```

---

### 3. 创建新设备

**端点**: `POST /api/devices`

**功能**: 创建新设备，可选自动生成匹配规则

**请求体**:
```json
{
  "device_id": "D002",
  "brand": "西门子",
  "device_name": "压力传感器",
  "spec_model": "QBE2003-P25",
  "detailed_params": "测量范围: 0-25bar",
  "unit_price": 680.0,
  "auto_generate_rule": true
}
```

**字段说明**:
- `device_id` (必需): 设备唯一标识
- `brand` (必需): 品牌
- `device_name` (必需): 设备名称
- `spec_model` (必需): 规格型号
- `detailed_params` (必需): 详细参数
- `unit_price` (必需): 单价
- `auto_generate_rule` (可选): 是否自动生成规则，默认 true

**请求示例**:
```bash
curl -X POST http://localhost:5000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "D002",
    "brand": "西门子",
    "device_name": "压力传感器",
    "spec_model": "QBE2003-P25",
    "detailed_params": "测量范围: 0-25bar",
    "unit_price": 680.0,
    "auto_generate_rule": true
  }'
```

**成功响应** (201):
```json
{
  "success": true,
  "data": {
    "device_id": "D002",
    "rule_generated": true
  },
  "message": "设备创建成功，已自动生成匹配规则"
}
```

**错误响应** (400):
```json
{
  "success": false,
  "error_code": "DEVICE_ALREADY_EXISTS",
  "error_message": "设备已存在: D002"
}
```

---

### 4. 更新设备信息

**端点**: `PUT /api/devices/:id`

**功能**: 更新设备信息，可选重新生成匹配规则

**路径参数**:
- `id`: 设备 ID

**请求体**:
```json
{
  "brand": "西门子",
  "device_name": "压力传感器",
  "spec_model": "QBE2003-P25",
  "detailed_params": "测量范围: 0-25bar, 精度: ±0.5%",
  "unit_price": 720.0,
  "regenerate_rule": true
}
```

**字段说明**:
- 所有设备字段都是可选的，只更新提供的字段
- `regenerate_rule` (可选): 是否重新生成规则，默认 false

**请求示例**:
```bash
curl -X PUT http://localhost:5000/api/devices/D002 \
  -H "Content-Type: application/json" \
  -d '{
    "unit_price": 720.0,
    "regenerate_rule": true
  }'
```

**成功响应** (200):
```json
{
  "success": true,
  "data": {
    "device_id": "D002",
    "rule_regenerated": true
  },
  "message": "设备更新成功，已重新生成匹配规则"
}
```

**错误响应** (404):
```json
{
  "success": false,
  "error_code": "DEVICE_NOT_FOUND",
  "error_message": "设备不存在: D999"
}
```

---

### 5. 删除设备

**端点**: `DELETE /api/devices/:id`

**功能**: 删除设备，自动级联删除关联的规则

**路径参数**:
- `id`: 设备 ID

**请求示例**:
```bash
curl -X DELETE http://localhost:5000/api/devices/D002
```

**成功响应** (200):
```json
{
  "success": true,
  "data": {
    "device_id": "D002",
    "rules_deleted": 1
  },
  "message": "设备删除成功，已级联删除 1 条关联规则"
}
```

**错误响应** (404):
```json
{
  "success": false,
  "error_code": "DEVICE_NOT_FOUND",
  "error_message": "设备不存在: D999"
}
```

---

## 错误处理

所有 API 端点使用统一的错误响应格式：

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

### 错误码列表

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-------------|
| `DEVICE_NOT_FOUND` | 设备不存在 | 404 |
| `DEVICE_ALREADY_EXISTS` | 设备已存在 | 400 |
| `VALIDATION_ERROR` | 数据验证失败 | 400 |
| `MISSING_DATA` | 请求体为空 | 400 |
| `DATABASE_MODE_REQUIRED` | 需要数据库模式 | 400 |
| `DATABASE_ERROR` | 数据库操作失败 | 500 |

---

## 使用示例

### Python 示例

```python
import requests

BASE_URL = "http://localhost:5000"

# 1. 创建设备
device_data = {
    "device_id": "TEST_001",
    "brand": "测试品牌",
    "device_name": "测试设备",
    "spec_model": "TEST-001",
    "detailed_params": "测试参数",
    "unit_price": 999.99,
    "auto_generate_rule": True
}

response = requests.post(f"{BASE_URL}/api/devices", json=device_data)
print(response.json())

# 2. 获取设备详情
response = requests.get(f"{BASE_URL}/api/devices/TEST_001")
print(response.json())

# 3. 更新设备
update_data = {
    "unit_price": 1299.99,
    "regenerate_rule": True
}

response = requests.put(f"{BASE_URL}/api/devices/TEST_001", json=update_data)
print(response.json())

# 4. 删除设备
response = requests.delete(f"{BASE_URL}/api/devices/TEST_001")
print(response.json())
```

### JavaScript 示例

```javascript
const BASE_URL = "http://localhost:5000";

// 1. 创建设备
async function createDevice() {
  const deviceData = {
    device_id: "TEST_001",
    brand: "测试品牌",
    device_name: "测试设备",
    spec_model: "TEST-001",
    detailed_params: "测试参数",
    unit_price: 999.99,
    auto_generate_rule: true
  };

  const response = await fetch(`${BASE_URL}/api/devices`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(deviceData)
  });

  const result = await response.json();
  console.log(result);
}

// 2. 获取设备列表（带过滤）
async function getDevices() {
  const response = await fetch(`${BASE_URL}/api/devices?brand=霍尼韦尔&page=1&page_size=20`);
  const result = await response.json();
  console.log(result);
}

// 3. 更新设备
async function updateDevice(deviceId) {
  const updateData = {
    unit_price: 1299.99,
    regenerate_rule: true
  };

  const response = await fetch(`${BASE_URL}/api/devices/${deviceId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(updateData)
  });

  const result = await response.json();
  console.log(result);
}

// 4. 删除设备
async function deleteDevice(deviceId) {
  const response = await fetch(`${BASE_URL}/api/devices/${deviceId}`, {
    method: 'DELETE'
  });

  const result = await response.json();
  console.log(result);
}
```

---

## 注意事项

1. **数据库模式**: 所有设备管理 API 都需要系统运行在数据库模式下
2. **自动规则生成**: 创建设备时默认会自动生成匹配规则，可以通过 `auto_generate_rule: false` 禁用
3. **级联删除**: 删除设备时会自动删除所有关联的规则
4. **数据重新加载**: 创建、更新或删除设备后，系统会自动重新加载数据并更新匹配引擎
5. **并发安全**: 数据库操作使用事务管理，确保数据一致性

---

## 相关文档

- [数据库迁移规范](../../.kiro/specs/database-migration/requirements.md)
- [设计文档](../../.kiro/specs/database-migration/design.md)
- [任务列表](../../.kiro/specs/database-migration/tasks.md)
