# 数据范围选择页面 - 错误处理改进

## 问题描述

用户访问 `/data-range-selection/:excelId` 时，如果文件ID无效或文件已过期，页面会显示空白，没有任何错误提示或操作按钮。

## 根本原因

1. 当 API 调用失败时，虽然会显示错误消息（ElMessage），但页面数据（`sheets`、`previewData` 等）仍然是空数组
2. 页面模板依赖这些数据来渲染内容，数据为空时页面就会显示空白
3. 没有专门的错误状态UI来处理加载失败的情况

## 解决方案

### 1. 添加错误状态管理

在组件中添加 `error` 状态变量：

```javascript
const error = ref(null)
```

### 2. 改进错误捕获

在 `loadPreview()` 函数中捕获错误并保存到状态：

```javascript
async function loadPreview() {
  loading.value = true
  error.value = null  // 清除之前的错误
  try {
    // ... API 调用
  } catch (err) {
    error.value = err.response?.data?.error_message || err.message || '加载预览失败'
    ElMessage.error('加载预览失败: ' + error.value)
    console.error('加载预览失败:', err)
  } finally {
    loading.value = false
  }
}
```

### 3. 添加错误状态UI

在模板中添加错误卡片，当有错误时显示友好的错误页面：

```vue
<template>
  <div class="data-range-selection">
    <!-- 错误状态显示 -->
    <el-card v-if="error && !loading" class="error-card">
      <el-result
        icon="error"
        title="加载失败"
        :sub-title="error"
      >
        <template #extra>
          <el-space>
            <el-button type="primary" @click="loadPreview">重试</el-button>
            <el-button @click="router.push({ name: 'FileUpload' })">返回上传页面</el-button>
          </el-space>
        </template>
      </el-result>
    </el-card>

    <!-- 正常内容 -->
    <el-card v-else class="selection-card" v-loading="loading">
      <!-- ... 正常内容 -->
    </el-card>
  </div>
</template>
```

## 改进效果

### 之前
- ❌ 页面完全空白
- ❌ 用户不知道发生了什么
- ❌ 没有任何操作选项

### 之后
- ✅ 显示清晰的错误信息
- ✅ 提供"重试"按钮（重新加载预览）
- ✅ 提供"返回上传页面"按钮（重新上传文件）
- ✅ 使用 Element Plus 的 `el-result` 组件，UI 友好美观

## 测试方法

### 方法 1: 使用测试页面

打开 `frontend/test-error-handling.html` 文件，点击各个测试链接：

1. **测试无效文件ID** - 使用不存在的文件ID
2. **测试空文件ID** - 不提供文件ID参数
3. **测试过期文件ID** - 使用已过期的文件ID
4. **测试正常流程** - 上传文件后正常访问

### 方法 2: 手动测试

1. 启动后端服务器：`cd backend && python app.py`
2. 启动前端服务器：`cd frontend && npm run dev`
3. 访问无效的文件ID：`http://localhost:3001/data-range-selection/invalid-id?filename=test.xlsx`
4. 应该看到错误页面，而不是空白页面

### 方法 3: 正常流程测试

1. 访问 `http://localhost:3001/`
2. 上传一个Excel文件
3. 点击"选择数据范围"按钮
4. 应该正常显示数据预览和范围选择界面

## 相关文件

- `frontend/src/views/DataRangeSelectionView.vue` - 主要修改文件
- `frontend/test-error-handling.html` - 错误处理测试页面
- `frontend/ERROR_HANDLING_FIX.md` - 本文档

## 后续建议

1. 考虑在其他页面（如 `DeviceRowAdjustmentView.vue`、`MatchingView.vue`）中应用类似的错误处理模式
2. 可以创建一个通用的错误处理组件，在多个页面中复用
3. 添加更详细的错误类型判断（如网络错误、权限错误、文件不存在等），显示不同的错误提示
