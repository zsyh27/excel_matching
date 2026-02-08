# 手动调整功能故障排查

## 问题描述

用户反馈：在设备行智能识别与调整页面，选中设备行后，手动调整和批量标记为设备行都提示"调整失败: Request failed with status code 400"。

## 可能的原因

### 1. excel_id 不匹配或已过期

**症状**: 后端返回400错误，错误信息为"无效的excel_id或分析结果已过期"

**原因**:
- 前端传递的`excel_id`与后端缓存中的不匹配
- 后端服务重启导致内存缓存清空
- 前端页面刷新后`excel_id`丢失

**解决方案**:
1. 检查后端日志，查看收到的`excel_id`和缓存中的`excel_id`列表
2. 确保前端和后端使用相同的`excel_id`
3. 重新上传文件，获取新的`excel_id`

### 2. 请求参数格式不正确

**症状**: 后端返回400错误，错误信息为"请求中缺少 excel_id 参数"或"请求中缺少 adjustments 参数"

**原因**:
- 前端发送的请求体格式不正确
- 缺少必需的参数

**解决方案**:
1. 检查前端发送的请求体格式
2. 确保包含`excel_id`和`adjustments`字段

### 3. 后端服务未运行或端口冲突

**症状**: 前端无法连接到后端，或返回404错误

**原因**:
- 后端服务未启动
- 端口被占用
- CORS配置问题

**解决方案**:
1. 启动后端服务：`cd backend && python app.py`
2. 检查端口5000是否被占用
3. 检查CORS配置

## 调试步骤

### 步骤1: 检查后端服务状态

```bash
# 确保后端服务正在运行
cd backend
python app.py
```

**预期输出**:
```
INFO - 初始化系统组件...
INFO - 系统组件初始化完成
INFO - 启动 Flask 应用...
 * Running on http://0.0.0.0:5000
```

### 步骤2: 运行测试脚本

在**新的终端窗口**中运行测试脚本：

```bash
cd backend
python test_manual_adjust_debug.py
```

### 步骤3: 查看后端日志输出

在后端服务的终端窗口中，查看日志输出。

**正常情况**:
```
INFO - Excel文件上传成功，开始分析: 示例设备清单.xlsx
INFO - 识别到表头行: 第X行
INFO - Excel分析完成: {'high_probability': X, 'medium_probability': X, 'low_probability': X}
INFO - 收到手动调整请求: {'excel_id': 'xxx-xxx-xxx', 'adjustments': [...]}
INFO - 当前缓存的excel_id列表: ['xxx-xxx-xxx']
INFO - 请求的excel_id: xxx-xxx-xxx, 类型: <class 'str'>
INFO - 手动标记为设备行: 第6行
INFO - 成功更新 1 行的调整记录
```

**异常情况1 - 缓存为空**:
```
INFO - 收到手动调整请求: {'excel_id': 'xxx-xxx-xxx', 'adjustments': [...]}
INFO - 当前缓存的excel_id列表: []
ERROR - 无效的excel_id: xxx-xxx-xxx
ERROR - 可用的excel_id: []
```

**异常情况2 - excel_id不匹配**:
```
INFO - 收到手动调整请求: {'excel_id': 'aaa-aaa-aaa', 'adjustments': [...]}
INFO - 当前缓存的excel_id列表: ['bbb-bbb-bbb']
ERROR - 无效的excel_id: aaa-aaa-aaa
ERROR - 可用的excel_id: ['bbb-bbb-bbb']
```

### 步骤4: 检查测试脚本输出

**正常输出**:
```
1. 上传并分析Excel文件...
   状态码: 200
   ✅ 上传分析成功，excel_id: xxx-xxx-xxx
   
2. 测试手动调整（单行）...
   状态码: 200
   ✅ 手动调整成功
   
3. 测试手动调整（批量）...
   状态码: 200
   ✅ 批量调整成功
   
4. 获取最终设备行...
   状态码: 200
   ✅ 获取成功
```

**异常输出**:
```
2. 测试手动调整（单行）...
   状态码: 400
   响应: {
     "success": false,
     "error_code": "INVALID_EXCEL_ID",
     "error_message": "无效的excel_id或分析结果已过期"
   }
   ❌ 手动调整失败
```

## 常见问题

### Q1: 后端缓存为空

**问题**: 日志显示"当前缓存的excel_id列表: []"

**原因**: 
- 后端服务重启，内存缓存被清空
- 文件上传/分析失败

**解决方案**:
1. 重新上传文件
2. 确保文件上传和分析成功
3. 检查`/api/excel/analyze`接口是否正常工作

### Q2: excel_id 不匹配

**问题**: 日志显示请求的`excel_id`不在缓存列表中

**原因**:
- 前端使用了旧的`excel_id`
- 前端和后端的`excel_id`不同步

**解决方案**:
1. 清除浏览器的sessionStorage
2. 重新上传文件
3. 确保前端从上传响应中获取正确的`excel_id`

### Q3: 请求参数缺失

**问题**: 日志显示"请求中缺少 excel_id 参数"

**原因**:
- 前端发送的请求体格式不正确
- API调用代码有误

**解决方案**:
1. 检查前端代码中的API调用
2. 确保请求体包含`excel_id`和`adjustments`字段
3. 使用浏览器开发者工具查看网络请求

## 测试脚本

使用`backend/test_manual_adjust_debug.py`脚本进行完整的流程测试：

```bash
cd backend
python test_manual_adjust_debug.py
```

该脚本会：
1. 上传Excel文件
2. 分析设备行
3. 执行单行手动调整
4. 执行批量手动调整
5. 获取最终设备行

如果脚本运行成功，说明后端API工作正常，问题可能在前端。

## 前端调试

### 检查浏览器控制台

1. 打开浏览器开发者工具（F12）
2. 切换到Console标签
3. 查看是否有JavaScript错误

### 检查网络请求

1. 打开浏览器开发者工具（F12）
2. 切换到Network标签
3. 尝试手动调整
4. 查看`/api/excel/manual-adjust`请求
5. 检查请求头、请求体、响应状态码、响应体

**正常请求体**:
```json
{
  "excel_id": "xxx-xxx-xxx-xxx",
  "adjustments": [
    {
      "row_number": 6,
      "action": "mark_as_device"
    }
  ]
}
```

**正常响应**:
```json
{
  "success": true,
  "message": "已更新 1 行的调整记录",
  "updated_rows": [6]
}
```

**错误响应**:
```json
{
  "success": false,
  "error_code": "INVALID_EXCEL_ID",
  "error_message": "无效的excel_id或分析结果已过期"
}
```

### 检查 sessionStorage

1. 打开浏览器开发者工具（F12）
2. 切换到Application标签（Chrome）或Storage标签（Firefox）
3. 展开Session Storage
4. 查看是否有`analysis_xxx-xxx-xxx`键
5. 检查值是否包含分析结果

## 临时解决方案

如果问题持续存在，可以尝试以下临时解决方案：

### 方案1: 清除缓存并重新开始

1. 清除浏览器缓存和sessionStorage
2. 重启后端服务
3. 重新上传文件
4. 重新进行手动调整

### 方案2: 使用测试脚本验证后端

```bash
cd backend
python test_manual_adjust_debug.py
```

如果测试脚本成功，说明后端正常，问题在前端。

### 方案3: 检查前端路由参数

确保前端路由正确传递`excelId`参数：

```javascript
// FileUploadView.vue
router.push({
  name: 'DeviceRowAdjustment',
  params: { excelId: response.excel_id }  // 确保这里传递了正确的excel_id
})

// DeviceRowAdjustmentView.vue
const props = defineProps({
  excelId: {
    type: String,
    required: true
  }
})
```

## 修改内容

### backend/app.py

在`manual_adjust`函数中添加了详细的调试日志：

```python
# 调试日志
logger.info(f"收到手动调整请求: {data}")
logger.info(f"当前缓存的excel_id列表: {list(excel_analysis_cache.keys())}")
logger.info(f"请求的excel_id: {excel_id}, 类型: {type(excel_id)}")
```

## 下一步

1. **重启后端服务**，使调试日志生效
2. **重新测试**手动调整功能
3. **查看后端日志**，确定具体的错误原因
4. **根据日志输出**，采取相应的解决方案

---

**创建日期**: 2026-02-08  
**状态**: 待用户测试  
**优先级**: 高
