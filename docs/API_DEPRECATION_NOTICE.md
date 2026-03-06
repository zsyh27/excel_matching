# API 弃用通知

## 概述

本文档列出了已被弃用的 API 端点，以及推荐使用的替代方案。这些弃用的 API 将在 **3 个月后**（2026年5月14日）完全移除。

## 弃用的 API 端点

### 1. 规则管理 API

以下规则管理相关的 API 端点已被弃用：

#### 1.1 获取规则详情

**弃用的端点**:
```
GET /api/rules/management/<rule_id>
```

**替代方案**:
```
GET /api/devices/<device_id>
```

**说明**: 规则信息现在作为设备详情的一部分返回。

**响应变化**:
- 旧 API 返回独立的规则对象
- 新 API 在设备对象中包含 `rule` 字段

---

#### 1.2 更新规则

**弃用的端点**:
```
PUT /api/rules/management/<rule_id>
```

**替代方案**:
```
PUT /api/devices/<device_id>/rule
```

**说明**: 规则更新现在通过设备规则专用端点进行。

**请求格式变化**:
```json
// 旧格式
{
  "match_threshold": 5.0,
  "features": [
    {"feature": "温度传感器", "weight": 5.0, "type": "device_type"}
  ]
}

// 新格式（相同）
{
  "match_threshold": 5.0,
  "features": [
    {"feature": "温度传感器", "weight": 5.0, "type": "device_type"}
  ]
}
```

---

#### 1.3 获取规则列表

**弃用的端点**:
```
GET /api/rules/management/list
```

**替代方案**:
```
GET /api/devices?include_rules=true
```

**说明**: 规则列表现在作为设备列表的一部分返回，每个设备包含规则摘要。

**响应变化**:
```json
// 旧格式
{
  "success": true,
  "rules": [
    {
      "rule_id": "RULE_001",
      "device_id": "DEV001",
      "brand": "霍尼韦尔",
      "device_name": "温度传感器",
      "match_threshold": 5.0,
      "feature_count": 5
    }
  ]
}

// 新格式
{
  "success": true,
  "devices": [
    {
      "device_id": "DEV001",
      "brand": "霍尼韦尔",
      "device_name": "温度传感器",
      "rule_summary": {
        "has_rule": true,
        "feature_count": 5,
        "match_threshold": 5.0,
        "total_weight": 12.0
      }
    }
  ]
}
```

---

#### 1.4 获取规则统计

**弃用的端点**:
```
GET /api/rules/management/statistics
```

**替代方案**:
```
GET /api/statistics/rules
```

**说明**: 规则统计已迁移到统计 API 命名空间。

**响应格式**: 保持不变

---

#### 1.5 获取匹配日志

**弃用的端点**:
```
GET /api/rules/management/logs
```

**替代方案**:
```
GET /api/statistics/match-logs
```

**说明**: 匹配日志已迁移到统计 API 命名空间。

**响应格式**: 保持不变

---

#### 1.6 匹配测试

**弃用的端点**:
```
POST /api/rules/management/test
```

**替代方案**:
```
POST /api/match/test
```

**说明**: 匹配测试功能已移至独立的匹配测试端点。

**请求/响应格式**: 保持不变

---

## 迁移指南

### 前端代码迁移

#### 示例 1: 获取规则详情

**旧代码**:
```javascript
// 获取规则详情
const response = await fetch(`/api/rules/management/${ruleId}`)
const data = await response.json()
const rule = data.rule
```

**新代码**:
```javascript
// 获取设备详情（包含规则）
const response = await fetch(`/api/devices/${deviceId}`)
const data = await response.json()
const rule = data.device.rule
```

---

#### 示例 2: 更新规则

**旧代码**:
```javascript
// 更新规则
await fetch(`/api/rules/management/${ruleId}`, {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    match_threshold: 5.0,
    features: [...]
  })
})
```

**新代码**:
```javascript
// 更新设备规则
await fetch(`/api/devices/${deviceId}/rule`, {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    match_threshold: 5.0,
    features: [...]
  })
})
```

---

#### 示例 3: 获取规则列表

**旧代码**:
```javascript
// 获取规则列表
const response = await fetch('/api/rules/management/list?page=1&page_size=20')
const data = await response.json()
const rules = data.rules
```

**新代码**:
```javascript
// 获取设备列表（包含规则摘要）
const response = await fetch('/api/devices?page=1&page_size=20')
const data = await response.json()
const devices = data.devices
// 访问规则摘要: devices[0].rule_summary
```

---

#### 示例 4: 获取统计数据

**旧代码**:
```javascript
// 获取规则统计
const response = await fetch('/api/rules/management/statistics')
const data = await response.json()
const stats = data.statistics
```

**新代码**:
```javascript
// 获取规则统计（新端点）
const response = await fetch('/api/statistics/rules')
const data = await response.json()
const stats = data.statistics
```

---

## 弃用警告

当您调用已弃用的 API 时，响应中会包含以下字段：

```json
{
  "success": true,
  "data": { ... },
  "_deprecated": true,
  "_deprecation_message": "此API已被弃用，将在3个月后移除",
  "_new_endpoint": "/api/devices/{device_id}"
}
```

**建议**: 
- 在开发环境中监控这些警告
- 尽快迁移到新的 API 端点
- 在弃用期结束前完成所有迁移

---

## 时间表

| 日期 | 事件 |
|------|------|
| 2026-02-14 | API 标记为弃用，开始弃用期 |
| 2026-03-14 | 第一次提醒（1个月） |
| 2026-04-14 | 第二次提醒（2个月） |
| 2026-05-14 | 弃用的 API 完全移除 |

---

## 常见问题

### Q1: 为什么要弃用这些 API？

**A**: 为了消除功能重复，优化系统架构。规则作为设备的属性，应该在设备管理中统一管理，而不是作为独立的管理对象。

### Q2: 弃用期间旧 API 还能使用吗？

**A**: 是的，在弃用期（3个月）内，旧 API 仍然可以正常使用，但会在响应中包含弃用警告。

### Q3: 新 API 的功能和旧 API 一样吗？

**A**: 是的，新 API 提供了相同的功能，只是端点路径和部分响应格式有所调整。

### Q4: 如何检测代码中是否使用了弃用的 API？

**A**: 
1. 在浏览器开发者工具中查看网络请求
2. 检查响应中是否包含 `_deprecated: true` 字段
3. 查看后端日志中的弃用警告

### Q5: 迁移工作量大吗？

**A**: 迁移工作量较小，主要是更新 API 端点路径和调整部分响应字段的访问方式。大多数情况下只需要修改几行代码。

---

## 联系支持

如果您在迁移过程中遇到问题，请联系技术支持：

- 📧 邮箱: support@example.com
- 📞 电话: 400-xxx-xxxx
- 💬 在线支持: https://support.example.com

---

**文档版本**: v1.0.0  
**发布日期**: 2026-02-14  
**维护者**: DDC 系统开发团队
