# 手动调整功能故障排查指南 v2.0

## 问题描述

用户反馈：在设备行智能识别与调整页面，选中设备行后，手动调整和批量标记为设备行都提示"调整失败: Request failed with status code 400"。

## 快速诊断流程

### 第一步：运行测试脚本

```bash
# 确保后端服务正在运行
cd backend
python app.py

# 在新的终端窗口运行测试脚本
cd backend
python test_manual_adjust_debug.py
```

### 第二步：根据测试结果判断问题

- ✅ **测试脚本全部通过** → 问题在前端，跳转到"前端问题排查"
- ❌ **测试脚本失败** → 问题在后端，跳转到"后端问题排查"

---

## 后端问题排查

### 问题1: 后端服务未运行

**症状**: 测试脚本无法连接到后端

**解决方案**:
```bash
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

### 问题2: 端口被占用

**症状**: 后端启动失败，提示端口5000已被占用

**解决方案**:
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <进程ID> /F

# Linux/Mac
lsof -i :5000
kill -9 <进程ID>
```

### 问题3: 依赖包缺失

**症状**: 后端启动时报ImportError

**解决方案**:
```bash
cd backend
pip install -r requirements.txt
```

### 问题4: 数据文件缺失

**症状**: 后端启动时报FileNotFoundError

**解决方案**:
确保以下文件存在：
- `data/static_device.json`
- `data/static_rule.json`
- `data/config.json`

---

## 前端问题排查

### 问题1: excel_id 不匹配或已过期

**症状**: 
- 后端日志显示"无效的excel_id或分析结果已过期"
- 前端收到400错误

**原因**:
1. 后端服务重启，内存缓存被清空
2. 前端使用了旧的excel_id
3. 前端和后端的excel_id不同步

**诊断步骤**:

1. 打开浏览器开发者工具（F12）
2. 切换到Network标签
3. 尝试手动调整
4. 查看`/api/excel/manual-adjust`请求的请求体

**检查点**:
```json
// 请求体应该包含
{
  "excel_id": "xxx-xxx-xxx-xxx",  // 检查这个ID
  "adjustments": [...]
}
```

5. 切换到后端控制台，查看日志：
```
INFO - 收到手动调整请求: {'excel_id': 'xxx-xxx-xxx', ...}
INFO - 当前缓存的excel_id列表: ['yyy-yyy-yyy']  // 对比这两个ID是否一致
```

**解决方案**:

**方案A: 重新上传文件**（推荐）
1. 刷新浏览器页面
2. 重新上传Excel文件
3. 进入设备行调整页面
4. 尝试手动调整

**方案B: 清除缓存**
1. 打开浏览器开发者工具（F12）
2. 切换到Application标签（Chrome）或Storage标签（Firefox）
3. 展开Session Storage
4. 删除所有`analysis_*`键
5. 刷新页面并重新上传文件

### 问题2: 前端路由参数传递错误

**症状**: 
- 前端组件无法获取excelId
- 控制台显示"excelId is required"

**诊断步骤**:

1. 打开浏览器开发者工具（F12）
2. 切换到Console标签
3. 查看是否有错误信息

**检查点**:

检查`FileUploadView.vue`中的路由跳转：
```javascript
// 应该是这样
router.push({
  name: 'DeviceRowAdjustment',
  params: { excelId: response.excel_id }  // 确保传递了excelId
})
```

检查`DeviceRowAdjustmentView.vue`中的props定义：
```javascript
// 应该是这样
const props = defineProps({
  excelId: {
    type: String,
    required: true
  }
})
```

检查`DeviceRowAdjustment.vue`中的API调用：
```javascript
// 应该是这样
const response = await api.post('/excel/manual-adjust', {
  excel_id: props.excelId,  // 使用props.excelId
  adjustments: [...]
})
```

**解决方案**:

如果发现代码不一致，需要修改相应的文件。

### 问题3: sessionStorage 数据丢失

**症状**: 
- 进入调整页面后显示"未找到分析结果"
- 表格为空

**诊断步骤**:

1. 打开浏览器开发者工具（F12）
2. 切换到Application标签（Chrome）或Storage标签（Firefox）
3. 展开Session Storage
4. 查看是否有`analysis_xxx-xxx-xxx`键

**解决方案**:

重新上传文件，确保上传成功后再进入调整页面。

### 问题4: API请求格式错误

**症状**: 
- 后端日志显示"请求中缺少 excel_id 参数"或"请求中缺少 adjustments 参数"

**诊断步骤**:

1. 打开浏览器开发者工具（F12）
2. 切换到Network标签
3. 尝试手动调整
4. 查看`/api/excel/manual-adjust`请求
5. 点击请求，查看Payload（请求体）

**正确的请求体格式**:
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

**解决方案**:

如果请求体格式不正确，需要检查前端代码中的API调用逻辑。

---

## 完整的调试流程

### 1. 后端调试

**启动后端服务**:
```bash
cd backend
python app.py
```

**查看后端日志**:
后端已添加详细的调试日志，会显示：
- 收到的请求数据
- 当前缓存的excel_id列表
- 请求的excel_id及类型
- 操作结果

**正常日志示例**:
```
INFO - Excel文件上传成功，开始分析: 示例设备清单.xlsx
INFO - 识别到表头行: 第3行
INFO - Excel分析完成: {'high_probability': 15, 'medium_probability': 5, 'low_probability': 30}
INFO - 收到手动调整请求: {'excel_id': 'abc-123-def', 'adjustments': [{'row_number': 6, 'action': 'mark_as_device'}]}
INFO - 当前缓存的excel_id列表: ['abc-123-def']
INFO - 请求的excel_id: abc-123-def, 类型: <class 'str'>
INFO - 手动标记为设备行: 第6行
INFO - 成功更新 1 行的调整记录
```

**异常日志示例**:
```
INFO - 收到手动调整请求: {'excel_id': 'abc-123-def', 'adjustments': [...]}
INFO - 当前缓存的excel_id列表: []
ERROR - 无效的excel_id: abc-123-def
ERROR - 可用的excel_id: []
```

### 2. 前端调试

**打开浏览器开发者工具**:
1. 按F12打开开发者工具
2. 切换到Network标签
3. 勾选"Preserve log"（保留日志）

**上传文件并观察**:
1. 上传Excel文件
2. 查看`/api/excel/analyze`请求
3. 确认响应中包含`excel_id`
4. 确认跳转到调整页面

**尝试手动调整并观察**:
1. 选择一行，执行手动调整
2. 查看`/api/excel/manual-adjust`请求
3. 检查请求体中的`excel_id`是否与上传时返回的一致
4. 查看响应状态码和响应体

**检查sessionStorage**:
1. 切换到Application标签
2. 展开Session Storage
3. 查看`analysis_xxx-xxx-xxx`键
4. 确认值包含分析结果

### 3. 运行测试脚本

**运行完整测试**:
```bash
cd backend
python test_manual_adjust_debug.py
```

**测试脚本会执行**:
1. 上传并分析Excel文件
2. 执行单行手动调整
3. 执行批量手动调整
4. 获取最终设备行

**预期输出**:
```
================================================================================
手动调整API调试
================================================================================

⚠️  请确保后端服务正在运行: cd backend && python app.py
⚠️  后端地址: http://localhost:5000

================================================================================

1. 上传并分析Excel文件...
   状态码: 200
   ✅ 上传分析成功，excel_id: xxx-xxx-xxx
   总行数: 50
   高概率设备行: 15
   测试行号: 6

2. 测试手动调整（单行）...
   状态码: 200
   ✅ 手动调整成功

3. 测试手动调整（批量）...
   状态码: 200
   ✅ 批量调整成功

4. 获取最终设备行...
   状态码: 200
   ✅ 获取成功
   总设备行数: 18
   自动识别: 15
   手动调整: 3

================================================================================
调试完成
================================================================================
```

---

## 常见错误代码

### 400 Bad Request

**错误代码**: `INVALID_EXCEL_ID`
**错误信息**: "无效的excel_id或分析结果已过期"
**原因**: excel_id不在后端缓存中
**解决方案**: 重新上传文件

**错误代码**: `MISSING_EXCEL_ID`
**错误信息**: "请求中缺少 excel_id 参数"
**原因**: 请求体中没有excel_id字段
**解决方案**: 检查前端API调用代码

**错误代码**: `MISSING_ADJUSTMENTS`
**错误信息**: "请求中缺少 adjustments 参数"
**原因**: 请求体中没有adjustments字段
**解决方案**: 检查前端API调用代码

### 404 Not Found

**原因**: API路径错误
**解决方案**: 确认API路径为`/api/excel/manual-adjust`

### 500 Internal Server Error

**原因**: 后端代码异常
**解决方案**: 查看后端日志中的错误堆栈信息

---

## 临时解决方案

如果问题持续存在，可以尝试以下临时解决方案：

### 方案1: 完全重置

```bash
# 1. 停止后端服务（Ctrl+C）

# 2. 清除浏览器缓存
# - 打开浏览器开发者工具（F12）
# - 右键点击刷新按钮
# - 选择"清空缓存并硬性重新加载"

# 3. 重启后端服务
cd backend
python app.py

# 4. 刷新前端页面
# 5. 重新上传文件
```

### 方案2: 使用测试脚本验证

```bash
# 运行测试脚本验证后端API
cd backend
python test_manual_adjust_debug.py

# 如果测试脚本成功，说明后端正常，问题在前端
# 如果测试脚本失败，说明后端有问题
```

### 方案3: 检查CORS配置

如果前端和后端在不同的域名或端口，可能是CORS问题。

检查`backend/app.py`中的CORS配置：
```python
from flask_cors import CORS
CORS(app)  # 确保这行代码存在
```

---

## 修改记录

### v2.0 (2026-02-08)
- 修复测试脚本中的API路径错误（`/api/excel/upload` → `/api/excel/analyze`）
- 添加完整的诊断流程
- 添加详细的前端调试步骤
- 添加常见错误代码说明
- 添加临时解决方案

### v1.0 (2026-02-08)
- 初始版本
- 添加调试日志到`backend/app.py`
- 创建测试脚本`backend/test_manual_adjust_debug.py`

---

**创建日期**: 2026-02-08  
**最后更新**: 2026-02-08  
**状态**: 待用户测试  
**优先级**: 高
