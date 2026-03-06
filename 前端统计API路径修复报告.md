# 前端统计API路径修复报告

## 问题描述

访问 http://localhost:3000/statistics 页面时显示：
- 加载日志失败: Request failed with status code 404
- 加载统计数据失败: Request failed with status code 404

## 问题原因

前端API调用路径错误，导致实际请求路径重复了 `/api` 前缀。

### 错误示例

**前端配置**：
```javascript
// frontend/src/api/index.js
const api = axios.create({
  baseURL: '/api',  // 已经配置了 /api 前缀
  timeout: 30000
})
```

**错误的API调用**：
```javascript
// 错误：使用了 /api/ 前缀
const response = await api.get('/api/statistics/match-logs', { params })
```

**实际请求路径**：
```
baseURL + path = /api + /api/statistics/match-logs = /api/api/statistics/match-logs
```

这导致404错误，因为后端路由是 `/api/statistics/match-logs`，而不是 `/api/api/statistics/match-logs`。

## 修复方案

移除API调用中的 `/api` 前缀，因为 `baseURL` 已经包含了这个前缀。

### 修复的文件

#### 1. frontend/src/components/Statistics/MatchLogs.vue

**修改前**：
```javascript
const response = await api.get('/api/statistics/match-logs', { params })
```

**修改后**：
```javascript
const response = await api.get('/statistics/match-logs', { params })
```

#### 2. frontend/src/components/Statistics/RuleStatistics.vue

**修改前**：
```javascript
const response = await api.get('/api/statistics/rules')
```

**修改后**：
```javascript
const response = await api.get('/statistics/rules')
```

#### 3. frontend/src/components/Statistics/MatchingStatistics.vue

**修改前**：
```javascript
const response = await api.get('/api/statistics/match-success-rate', { params })
```

**修改后**：
```javascript
const response = await api.get('/statistics/match-success-rate', { params })
```

## 正确的API路径规则

### 规则说明

当使用 `api` 实例（已配置 `baseURL: '/api'`）时：

✅ **正确**：
```javascript
api.get('/statistics/match-logs')        // 实际请求: /api/statistics/match-logs
api.get('/database/statistics')          // 实际请求: /api/database/statistics
api.get('/devices')                      // 实际请求: /api/devices
```

❌ **错误**：
```javascript
api.get('/api/statistics/match-logs')    // 实际请求: /api/api/statistics/match-logs
api.get('/api/database/statistics')      // 实际请求: /api/api/database/statistics
api.get('/api/devices')                  // 实际请求: /api/api/devices
```

### 其他正确的API调用示例

**frontend/src/api/database.js** - 这些是正确的：
```javascript
export const getStatistics = () => {
  return api.get('/database/statistics')  // ✅ 正确
}

export const getBrandDistribution = () => {
  return api.get('/database/statistics/brands')  // ✅ 正确
}

export const getPriceDistribution = () => {
  return api.get('/database/statistics/prices')  // ✅ 正确
}
```

## 验证步骤

### 步骤1：重启前端服务
```bash
cd frontend
npm run dev
```

### 步骤2：访问统计页面
打开浏览器访问：http://localhost:3000/statistics

### 步骤3：检查各个标签页
1. **系统概览** - 应该显示统计数据、图表和设备列表
2. **匹配日志** - 应该显示日志列表（如果有数据）
3. **规则统计** - 应该显示规则统计信息
4. **匹配统计** - 应该显示匹配成功率趋势

### 步骤4：检查浏览器控制台
打开浏览器开发者工具（F12），检查：
- Network标签：确认API请求路径正确（应该是 `/api/statistics/...`）
- Console标签：确认没有404错误

## 预期结果

### 修复前
```
❌ GET /api/api/statistics/match-logs 404 (Not Found)
❌ GET /api/api/statistics/rules 404 (Not Found)
❌ GET /api/api/statistics/match-success-rate 404 (Not Found)
```

### 修复后
```
✅ GET /api/statistics/match-logs 200 (OK)
✅ GET /api/statistics/rules 200 (OK)
✅ GET /api/statistics/match-success-rate 200 (OK)
```

## 相关文件

### 修改的文件
- `frontend/src/components/Statistics/MatchLogs.vue` - 匹配日志组件
- `frontend/src/components/Statistics/RuleStatistics.vue` - 规则统计组件
- `frontend/src/components/Statistics/MatchingStatistics.vue` - 匹配统计组件

### 未修改的文件（已经正确）
- `frontend/src/api/database.js` - 数据库API（路径正确）
- `frontend/src/api/index.js` - API配置（配置正确）
- `frontend/vite.config.js` - Vite配置（代理配置正确）

## 注意事项

### API路径规范

在整个前端项目中，使用 `api` 实例时应该遵循以下规范：

1. **不要**在路径前加 `/api` 前缀
2. **直接**使用相对路径，如 `/devices`、`/statistics/rules`
3. `baseURL` 会自动添加 `/api` 前缀

### 检查清单

- [x] MatchLogs组件API路径修复
- [x] RuleStatistics组件API路径修复
- [x] MatchingStatistics组件API路径修复
- [x] 验证其他组件没有类似问题
- [ ] 重启前端服务
- [ ] 测试统计页面各个标签页
- [ ] 确认浏览器控制台无错误

## 总结

问题的根本原因是API调用路径重复了 `/api` 前缀。由于 `axios` 实例已经配置了 `baseURL: '/api'`，所以在调用时不应该再加 `/api` 前缀。

修复后，所有统计API调用都能正确访问后端接口，统计仪表板页面应该能够正常显示数据。
