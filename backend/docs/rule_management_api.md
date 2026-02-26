# 规则管理 API 文档

## 概述

规则管理 API 提供了完整的规则可视化、编辑、测试和批量操作功能，用于优化匹配准确率和诊断匹配问题。

**验证需求:** 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 10.10, 10.11, 10.12, 10.13, 10.14, 10.15

## API 端点

### 1. 规则列表接口

**端点:** `GET /api/rules/management/list`

**功能:** 获取所有设备的匹配规则列表，支持搜索、筛选和分页

**验证需求:** 10.1

**查询参数:**
- `page` (int, 可选): 页码，默认 1
- `page_size` (int, 可选): 每页数量，默认 20
- `search` (string, 可选): 搜索关键词（设备ID、品牌、名称、型号）
- `brand` (string, 可选): 品牌筛选
- `device_type` (string, 可选): 设备类型筛选（模糊匹配设备名称）
- `threshold_min` (float, 可选): 最小阈值
- `threshold_max` (float, 可选): 最大阈值

**响应示例:**
```json
{
  "success": true,
  "total": 719,
  "page": 1,
  "page_size": 20,
  "rules": [
    {
      "rule_id": "R_SENSOR001",
      "device_id": "SENSOR001",
      "brand": "霍尼韦尔",
      "device_name": "温度传感器",
      "spec_model": "HST-RA",
      "match_threshold": 5.0,
      "feature_count": 8
    }
  ]
}
```

**使用示例:**
```bash
# 获取第一页规则
curl "http://localhost:5000/api/rules/management/list?page=1&page_size=20"

# 搜索包含"传感器"的规则
curl "http://localhost:5000/api/rules/management/list?search=传感器"

# 筛选阈值在 3.0-6.0 之间的规则
curl "http://localhost:5000/api/rules/management/list?threshold_min=3.0&threshold_max=6.0"

# 筛选霍尼韦尔品牌的规则
curl "http://localhost:5000/api/rules/management/list?brand=霍尼韦尔"
```

---

### 2. 规则详情接口

**端点:** `GET /api/rules/management/{rule_id}`

**功能:** 获取单个设备的详细匹配规则，包括所有提取的特征及其权重值

**验证需求:** 10.2

**路径参数:**
- `rule_id` (string): 规则ID

**响应示例:**
```json
{
  "success": true,
  "rule": {
    "rule_id": "R_SENSOR001",
    "device_id": "SENSOR001",
    "device_info": {
      "brand": "霍尼韦尔",
      "device_name": "温度传感器",
      "spec_model": "HST-RA",
      "detailed_params": "0-50℃,4-20mA,0-10V",
      "unit_price": 213.0
    },
    "match_threshold": 5.0,
    "features": [
      {
        "feature": "温度传感器",
        "weight": 5.0,
        "type": "device_type"
      },
      {
        "feature": "霍尼韦尔",
        "weight": 3.0,
        "type": "brand"
      },
      {
        "feature": "HST-RA",
        "weight": 3.0,
        "type": "model"
      },
      {
        "feature": "4-20ma",
        "weight": 1.0,
        "type": "parameter"
      },
      {
        "feature": "0-10v",
        "weight": 1.0,
        "type": "parameter"
      }
    ],
    "remark": "霍尼韦尔温度传感器匹配规则"
  }
}
```

**特征类型说明:**
- `brand`: 品牌特征
- `device_type`: 设备类型特征
- `model`: 型号特征
- `parameter`: 参数特征

**使用示例:**
```bash
curl "http://localhost:5000/api/rules/management/R_SENSOR001"
```

---

### 3. 规则更新接口

**端点:** `PUT /api/rules/management/{rule_id}`

**功能:** 更新规则的匹配阈值和特征权重

**验证需求:** 10.3, 10.4, 10.5

**路径参数:**
- `rule_id` (string): 规则ID

**请求体:**
```json
{
  "match_threshold": 8.0,
  "features": [
    {
      "feature": "温度传感器",
      "weight": 6.0
    },
    {
      "feature": "霍尼韦尔",
      "weight": 3.0
    },
    {
      "feature": "4-20ma",
      "weight": 1.0
    }
  ],
  "remark": "优化后的规则"
}
```

**请求参数说明:**
- `match_threshold` (float, 可选): 新的匹配阈值
- `features` (array, 可选): 特征列表，每个特征包含 `feature` 和 `weight`
- `remark` (string, 可选): 备注说明

**响应示例:**
```json
{
  "success": true,
  "message": "规则更新成功",
  "rule_id": "R_SENSOR001"
}
```

**使用示例:**
```bash
# 更新匹配阈值
curl -X PUT "http://localhost:5000/api/rules/management/R_SENSOR001" \
  -H "Content-Type: application/json" \
  -d '{
    "match_threshold": 8.0
  }'

# 更新特征权重
curl -X PUT "http://localhost:5000/api/rules/management/R_SENSOR001" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [
      {"feature": "温度传感器", "weight": 6.0},
      {"feature": "霍尼韦尔", "weight": 3.0},
      {"feature": "4-20ma", "weight": 1.0}
    ]
  }'
```

---

### 4. 匹配测试接口

**端点:** `POST /api/rules/management/test`

**功能:** 实时测试设备描述的匹配效果，返回详细的匹配过程和候选规则得分

**验证需求:** 10.6, 10.7, 10.8

**请求体:**
```json
{
  "description": "温度传感器，0-50℃，4-20mA"
}
```

**响应示例:**
```json
{
  "success": true,
  "preprocessing": {
    "original": "温度传感器，0-50℃，4-20mA",
    "normalized": "温度传感器,0-50,4-20ma",
    "features": ["温度传感器", "0-50", "4-20ma"]
  },
  "candidates": [
    {
      "rank": 1,
      "rule_id": "R_SENSOR001",
      "device_id": "SENSOR001",
      "device_name": "霍尼韦尔 温度传感器 HST-RA",
      "score": 9.0,
      "threshold": 5.0,
      "matched_features": [
        {"feature": "温度传感器", "weight": 5.0},
        {"feature": "霍尼韦尔", "weight": 3.0},
        {"feature": "4-20ma", "weight": 1.0}
      ],
      "is_match": true
    },
    {
      "rank": 2,
      "rule_id": "R_SENSOR002",
      "device_id": "SENSOR002",
      "device_name": "西门子 温度传感器 QAE2120",
      "score": 6.0,
      "threshold": 5.0,
      "matched_features": [
        {"feature": "温度传感器", "weight": 5.0},
        {"feature": "4-20ma", "weight": 1.0}
      ],
      "is_match": true
    }
  ],
  "final_match": {
    "device_id": "SENSOR001",
    "matched_device_text": "霍尼韦尔 温度传感器 HST-RA 0-50℃,4-20mA,0-10V",
    "unit_price": 213.0,
    "match_status": "success",
    "match_score": 9.0,
    "match_reason": "权重得分 9.0 超过阈值 5.0，匹配特征: 温度传感器(5.0), 霍尼韦尔(3.0), 4-20ma(1.0)"
  }
}
```

**响应字段说明:**
- `preprocessing`: 预处理结果
  - `original`: 原始输入
  - `normalized`: 归一化后的文本
  - `features`: 提取的特征列表
- `candidates`: 候选规则列表（按得分降序，最多10个）
  - `rank`: 排名
  - `score`: 权重得分
  - `threshold`: 匹配阈值
  - `matched_features`: 匹配到的特征及其权重
  - `is_match`: 是否达到阈值
- `final_match`: 最终匹配结果

**使用示例:**
```bash
curl -X POST "http://localhost:5000/api/rules/management/test" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "温度传感器，0-50℃，4-20mA"
  }'
```

---

### 5. 匹配日志接口

**端点:** `GET /api/rules/management/logs`

**功能:** 查看历史匹配记录，支持按时间、状态、设备类型筛选

**验证需求:** 10.9, 10.10, 10.11

**查询参数:**
- `start_date` (string, 可选): 开始日期（ISO格式）
- `end_date` (string, 可选): 结束日期（ISO格式）
- `status` (string, 可选): 匹配状态（success/failed/all），默认 all
- `device_type` (string, 可选): 设备类型筛选
- `page` (int, 可选): 页码，默认 1
- `page_size` (int, 可选): 每页数量，默认 50

**响应示例:**
```json
{
  "success": true,
  "total": 1523,
  "page": 1,
  "page_size": 50,
  "logs": [
    {
      "log_id": "LOG_001",
      "timestamp": "2026-02-14T10:30:15",
      "input_description": "温度传感器，0-50℃，4-20mA",
      "extracted_features": ["温度传感器", "0-50", "4-20ma"],
      "match_status": "success",
      "matched_device_id": "SENSOR001",
      "match_score": 9.0,
      "match_threshold": 5.0,
      "match_reason": "权重得分 9.0 超过阈值 5.0"
    }
  ]
}
```

**使用示例:**
```bash
# 获取最近的匹配日志
curl "http://localhost:5000/api/rules/management/logs?page=1&page_size=50"

# 筛选失败的匹配记录
curl "http://localhost:5000/api/rules/management/logs?status=failed"

# 按时间范围筛选
curl "http://localhost:5000/api/rules/management/logs?start_date=2026-02-01T00:00:00&end_date=2026-02-14T23:59:59"

# 筛选特定设备类型
curl "http://localhost:5000/api/rules/management/logs?device_type=传感器"
```

---

### 6. 批量操作接口

**端点:** `POST /api/rules/management/batch-update`

**功能:** 批量调整规则权重、阈值或重置规则

**验证需求:** 10.12, 10.13

**操作类型:**

#### 6.1 按特征类型批量调整权重

**请求体:**
```json
{
  "operation": "update_weights_by_type",
  "feature_type": "parameter",
  "new_weight": 1.0,
  "rule_ids": []
}
```

**参数说明:**
- `operation`: 固定为 `update_weights_by_type`
- `feature_type`: 特征类型（brand/device_type/model/parameter）
- `new_weight`: 新的权重值
- `rule_ids`: 规则ID列表，空数组表示应用到所有规则

#### 6.2 批量调整阈值

**请求体:**
```json
{
  "operation": "update_threshold",
  "new_threshold": 7.0,
  "rule_ids": ["R_SENSOR001", "R_SENSOR002"]
}
```

**参数说明:**
- `operation`: 固定为 `update_threshold`
- `new_threshold`: 新的匹配阈值
- `rule_ids`: 规则ID列表

#### 6.3 批量重置规则

**请求体:**
```json
{
  "operation": "reset_rules",
  "rule_ids": ["R_SENSOR001", "R_SENSOR002"]
}
```

**参数说明:**
- `operation`: 固定为 `reset_rules`
- `rule_ids`: 规则ID列表

**响应示例:**
```json
{
  "success": true,
  "message": "批量操作完成：成功 45 条，失败 0 条",
  "updated_count": 45,
  "failed_count": 0
}
```

**使用示例:**
```bash
# 将所有参数类型的权重降低到 1.0
curl -X POST "http://localhost:5000/api/rules/management/batch-update" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "update_weights_by_type",
    "feature_type": "parameter",
    "new_weight": 1.0,
    "rule_ids": []
  }'

# 批量提高阈值
curl -X POST "http://localhost:5000/api/rules/management/batch-update" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "update_threshold",
    "new_threshold": 7.0,
    "rule_ids": ["R_SENSOR001", "R_SENSOR002"]
  }'

# 批量重置规则
curl -X POST "http://localhost:5000/api/rules/management/batch-update" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "reset_rules",
    "rule_ids": ["R_SENSOR001"]
  }'
```

---

### 7. 统计分析接口

**端点:** `GET /api/rules/management/statistics`

**功能:** 获取权重分布、阈值分布等统计信息

**验证需求:** 10.14, 10.15

**响应示例:**
```json
{
  "success": true,
  "statistics": {
    "total_rules": 719,
    "total_features": 3456,
    "avg_weight": 2.35,
    "avg_threshold": 5.12,
    "weight_distribution": {
      "0-1": 245,
      "1-2": 189,
      "2-3": 156,
      "3-4": 129,
      "4-5": 98,
      "5+": 67
    },
    "threshold_distribution": {
      "2.0": 150,
      "5.0": 450,
      "7.0": 100,
      "10.0": 19
    },
    "match_success_rate": {
      "overall": 0.87
    }
  }
}
```

**响应字段说明:**
- `total_rules`: 总规则数
- `total_features`: 总特征数
- `avg_weight`: 平均权重
- `avg_threshold`: 平均阈值
- `weight_distribution`: 权重分布（按区间统计）
- `threshold_distribution`: 阈值分布（按具体值统计）
- `match_success_rate`: 匹配成功率（如果有日志记录）

**使用示例:**
```bash
curl "http://localhost:5000/api/rules/management/statistics"
```

---

## 错误处理

所有接口都遵循统一的错误响应格式：

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

**常见错误码:**
- `DATABASE_MODE_REQUIRED`: 需要数据库模式
- `RULE_NOT_FOUND`: 规则不存在
- `DEVICE_NOT_FOUND`: 设备不存在
- `MISSING_DATA`: 请求体为空
- `VALIDATION_ERROR`: 数据验证失败
- `INVALID_PARAMETER`: 参数格式错误
- `INVALID_OPERATION`: 不支持的操作类型

---

## 使用场景

### 场景 1: 诊断匹配问题

1. 使用匹配测试接口测试问题描述
2. 查看候选规则得分列表，找出得分最高的规则
3. 查看规则详情，分析特征权重配置
4. 调整权重或阈值，重新测试

### 场景 2: 优化匹配准确率

1. 查看统计分析，识别权重配置问题
2. 使用批量操作降低通用参数权重
3. 使用批量操作提高设备类型权重
4. 使用批量操作提高匹配阈值
5. 查看匹配日志验证优化效果

### 场景 3: 规则维护

1. 使用规则列表接口查找需要调整的规则
2. 使用规则详情接口查看当前配置
3. 使用规则更新接口修改配置
4. 使用匹配测试接口验证修改效果

---

## 注意事项

1. **数据库模式要求**: 所有规则管理接口都需要使用数据库模式，JSON 文件模式不支持
2. **自动重载**: 规则更新后会自动重新加载数据并更新匹配引擎
3. **批量操作**: 批量操作会逐个处理规则，部分失败不影响其他规则
4. **日志记录**: 匹配测试接口不会记录日志，只有实际匹配操作才会记录
5. **权重范围**: 建议权重范围为 0.5-10.0，过高或过低可能影响匹配效果
6. **阈值设置**: 建议阈值范围为 3.0-10.0，过低容易误匹配，过高可能匹配失败

---

## 前端集成示例

### Vue 3 + Axios

```javascript
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api/rules/management'

// 获取规则列表
export async function getRulesList(params) {
  const response = await axios.get(`${API_BASE_URL}/list`, { params })
  return response.data
}

// 获取规则详情
export async function getRuleDetail(ruleId) {
  const response = await axios.get(`${API_BASE_URL}/${ruleId}`)
  return response.data
}

// 更新规则
export async function updateRule(ruleId, data) {
  const response = await axios.put(`${API_BASE_URL}/${ruleId}`, data)
  return response.data
}

// 测试匹配
export async function testMatching(description) {
  const response = await axios.post(`${API_BASE_URL}/test`, { description })
  return response.data
}

// 批量操作
export async function batchUpdate(operation, params) {
  const response = await axios.post(`${API_BASE_URL}/batch-update`, {
    operation,
    ...params
  })
  return response.data
}

// 获取统计信息
export async function getStatistics() {
  const response = await axios.get(`${API_BASE_URL}/statistics`)
  return response.data
}
```

---

## 完整使用示例

### Python 示例

```python
import requests

API_BASE_URL = 'http://localhost:5000/api/rules/management'

# 1. 获取规则列表
def get_rules_list(page=1, page_size=20, search=''):
    response = requests.get(f'{API_BASE_URL}/list', params={
        'page': page,
        'page_size': page_size,
        'search': search
    })
    return response.json()

# 2. 获取规则详情
def get_rule_detail(rule_id):
    response = requests.get(f'{API_BASE_URL}/{rule_id}')
    return response.json()

# 3. 更新规则
def update_rule(rule_id, match_threshold=None, features=None):
    data = {}
    if match_threshold is not None:
        data['match_threshold'] = match_threshold
    if features is not None:
        data['features'] = features
    
    response = requests.put(f'{API_BASE_URL}/{rule_id}', json=data)
    return response.json()

# 4. 测试匹配
def test_matching(description):
    response = requests.post(f'{API_BASE_URL}/test', json={
        'description': description
    })
    return response.json()

# 5. 批量操作
def batch_update_weights(feature_type, new_weight, rule_ids=None):
    response = requests.post(f'{API_BASE_URL}/batch-update', json={
        'operation': 'update_weights_by_type',
        'feature_type': feature_type,
        'new_weight': new_weight,
        'rule_ids': rule_ids or []
    })
    return response.json()

# 使用示例
if __name__ == '__main__':
    # 搜索温度传感器的规则
    rules = get_rules_list(search='温度传感器')
    print(f"找到 {rules['total']} 条规则")
    
    # 查看第一条规则的详情
    if rules['rules']:
        rule_id = rules['rules'][0]['rule_id']
        detail = get_rule_detail(rule_id)
        print(f"规则详情: {detail}")
        
        # 更新匹配阈值
        result = update_rule(rule_id, match_threshold=5.0)
        print(f"更新结果: {result}")
    
    # 测试匹配
    test_result = test_matching('温度传感器，0-50℃，4-20mA')
    print(f"匹配结果: {test_result['final_match']}")
    
    # 批量降低参数权重
    batch_result = batch_update_weights('parameter', 1.0)
    print(f"批量操作结果: {batch_result}")
```

### JavaScript 示例

```javascript
const API_BASE_URL = 'http://localhost:5000/api/rules/management';

// 1. 获取规则列表
async function getRulesList(page = 1, pageSize = 20, search = '') {
  const response = await fetch(`${API_BASE_URL}/list?page=${page}&page_size=${pageSize}&search=${search}`);
  return await response.json();
}

// 2. 获取规则详情
async function getRuleDetail(ruleId) {
  const response = await fetch(`${API_BASE_URL}/${ruleId}`);
  return await response.json();
}

// 3. 更新规则
async function updateRule(ruleId, data) {
  const response = await fetch(`${API_BASE_URL}/${ruleId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  return await response.json();
}

// 4. 测试匹配
async function testMatching(description) {
  const response = await fetch(`${API_BASE_URL}/test`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ description })
  });
  return await response.json();
}

// 5. 批量操作
async function batchUpdateWeights(featureType, newWeight, ruleIds = []) {
  const response = await fetch(`${API_BASE_URL}/batch-update`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      operation: 'update_weights_by_type',
      feature_type: featureType,
      new_weight: newWeight,
      rule_ids: ruleIds
    })
  });
  return await response.json();
}

// 使用示例
async function main() {
  try {
    // 搜索温度传感器的规则
    const rules = await getRulesList(1, 20, '温度传感器');
    console.log(`找到 ${rules.total} 条规则`);
    
    // 查看第一条规则的详情
    if (rules.rules.length > 0) {
      const ruleId = rules.rules[0].rule_id;
      const detail = await getRuleDetail(ruleId);
      console.log('规则详情:', detail);
      
      // 更新匹配阈值
      const result = await updateRule(ruleId, { match_threshold: 5.0 });
      console.log('更新结果:', result);
    }
    
    // 测试匹配
    const testResult = await testMatching('温度传感器，0-50℃，4-20mA');
    console.log('匹配结果:', testResult.final_match);
    
    // 批量降低参数权重
    const batchResult = await batchUpdateWeights('parameter', 1.0);
    console.log('批量操作结果:', batchResult);
  } catch (error) {
    console.error('错误:', error);
  }
}

main();
```

## 性能优化建议

### 1. 分页查询

规则列表和日志查询都支持分页，建议：
- 每页数量不超过 50 条
- 使用筛选条件缩小结果范围
- 避免一次性加载所有数据

### 2. 批量操作

批量操作会逐个处理规则，建议：
- 单次批量操作不超过 100 条规则
- 大量规则分批处理
- 在低峰期执行批量操作

### 3. 缓存策略

规则数据会缓存在内存中，建议：
- 规则更新后会自动刷新缓存
- 无需手动清除缓存
- 如遇问题可重启服务刷新

### 4. 并发控制

API 支持并发请求，但建议：
- 避免同时修改同一条规则
- 批量操作期间避免其他修改
- 使用版本管理避免冲突

## 安全注意事项

### 1. 权限控制

规则管理接口需要管理员权限：
- 生产环境应启用身份验证
- 限制规则管理接口的访问
- 记录所有规则修改操作

### 2. 数据验证

所有输入都会进行验证：
- 权重范围: 0.1-20.0
- 阈值范围: 0.1-50.0
- 特征名称: 不能为空
- 规则ID: 必须存在

### 3. 备份恢复

重要操作前建议备份：
- 使用版本管理功能
- 定期备份数据库
- 保留配置文件副本

### 4. 审计日志

系统会记录所有规则修改：
- 修改时间
- 修改内容
- 操作人员
- 修改原因

## 故障排查

### 问题 1: 规则更新失败

**可能原因**:
- 规则ID不存在
- 数据格式错误
- 数据库连接失败
- 权限不足

**解决方法**:
1. 检查规则ID是否正确
2. 验证请求数据格式
3. 检查数据库连接
4. 查看后端日志

### 问题 2: 批量操作部分失败

**可能原因**:
- 部分规则ID不存在
- 部分规则被锁定
- 数据验证失败

**解决方法**:
1. 查看响应中的失败详情
2. 检查失败的规则ID
3. 修正数据后重试

### 问题 3: 匹配测试结果不一致

**可能原因**:
- 规则未保存
- 缓存未刷新
- 配置文件未更新

**解决方法**:
1. 确认规则已保存
2. 重启后端服务
3. 清除浏览器缓存

### 问题 4: API 响应慢

**可能原因**:
- 数据量过大
- 数据库性能问题
- 网络延迟

**解决方法**:
1. 使用分页和筛选
2. 优化数据库索引
3. 检查网络连接

## 更新日志

### v1.0.0 (2026-02-14)
- 实现规则列表接口
- 实现规则详情接口
- 实现规则更新接口
- 实现匹配测试接口
- 实现匹配日志接口
- 实现批量操作接口
- 实现统计分析接口
- 添加完整的使用示例
- 添加性能优化建议
- 添加安全注意事项
- 添加故障排查指南
