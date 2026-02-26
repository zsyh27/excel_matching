# FileUpload 组件文档

## 概述

FileUpload.vue 是 DDC 设备清单匹配报价系统的文件上传组件，负责处理 Excel 文件的上传、验证和解析。

## 功能特性

### 1. 文件格式验证（需求 1.1, 1.2, 1.3, 1.4）
- 仅接受 `.xls`、`.xlsx`、`.xlsm` 格式的 Excel 文件
- 自动验证文件扩展名
- 拒绝非 Excel 格式文件并显示错误提示

### 2. 文件大小验证（需求 1.4）
- 最大文件大小限制：10MB
- 超过限制时显示友好的错误提示

### 3. 拖拽上传（需求 1.1, 1.2, 1.3）
- 支持拖拽文件到上传区域
- 支持点击选择文件
- 使用 Element Plus 的 el-upload 组件实现

### 4. 上传进度显示（需求 9.1）
- 实时显示上传进度百分比
- 进度条颜色根据状态变化（上传中/成功/失败）
- 显示当前操作状态文本

### 5. 通知提示（需求 9.1, 9.2）
- **上传成功**：显示成功通知，包含文件名
- **上传失败**：显示错误通知，包含失败原因
- **解析成功**：显示解析结果统计
- **解析失败**：显示详细错误信息

### 6. 自动解析（需求 9.2）
- 文件上传成功后自动调用 `/api/parse` 接口
- 显示解析进度和结果
- 解析完成后触发 `parse-complete` 事件

## API 接口

### 上传接口
- **端点**: `POST /api/upload`
- **请求**: multipart/form-data，包含 file 字段
- **响应**:
```json
{
  "success": true,
  "file_id": "uuid-string",
  "filename": "设备清单.xlsx",
  "format": "xlsx"
}
```

### 解析接口
- **端点**: `POST /api/parse`
- **请求**:
```json
{
  "file_id": "uuid-string"
}
```
- **响应**:
```json
{
  "success": true,
  "file_id": "uuid-string",
  "parse_result": {
    "total_rows": 100,
    "valid_rows": 95,
    "device_rows": 85,
    "rows": [...]
  }
}
```

## 组件事件

### upload-success
文件上传成功时触发

**参数**:
```javascript
{
  file_id: string,    // 文件唯一标识
  filename: string,   // 原始文件名
  format: string      // 文件格式（xls/xlsx/xlsm）
}
```

### parse-complete
文件解析完成时触发

**参数**:
```javascript
{
  file_id: string,
  parse_result: {
    total_rows: number,
    valid_rows: number,
    device_rows: number,
    rows: Array
  }
}
```

## 组件方法

### reset()
重置组件状态，清除上传记录和解析结果

**使用示例**:
```vue
<template>
  <FileUpload ref="uploadRef" />
  <el-button @click="resetUpload">重置</el-button>
</template>

<script setup>
import { ref } from 'vue'
import FileUpload from './components/FileUpload.vue'

const uploadRef = ref(null)

const resetUpload = () => {
  uploadRef.value.reset()
}
</script>
```

## 使用示例

### 基础使用
```vue
<template>
  <FileUpload 
    @upload-success="handleUploadSuccess"
    @parse-complete="handleParseComplete"
  />
</template>

<script setup>
import FileUpload from './components/FileUpload.vue'

const handleUploadSuccess = (fileInfo) => {
  console.log('文件上传成功:', fileInfo)
}

const handleParseComplete = (data) => {
  console.log('文件解析完成:', data)
  // 处理解析结果，例如显示在表格中
}
</script>
```

### 完整示例
```vue
<template>
  <div>
    <FileUpload 
      ref="uploadRef"
      @upload-success="handleUploadSuccess"
      @parse-complete="handleParseComplete"
    />
    
    <el-button 
      v-if="parseResult" 
      @click="startMatching"
      type="primary"
    >
      开始匹配
    </el-button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FileUpload from './components/FileUpload.vue'

const uploadRef = ref(null)
const currentFileId = ref(null)
const parseResult = ref(null)

const handleUploadSuccess = (fileInfo) => {
  currentFileId.value = fileInfo.file_id
}

const handleParseComplete = (data) => {
  parseResult.value = data.parse_result
}

const startMatching = () => {
  // 调用匹配接口
  console.log('开始匹配设备...')
}
</script>
```

## 错误处理

组件内置了完善的错误处理机制：

1. **文件格式错误**: 显示支持的格式列表
2. **文件大小超限**: 显示最大文件大小限制
3. **上传失败**: 显示服务器返回的错误信息
4. **解析失败**: 显示详细的错误原因和建议

## 样式定制

组件使用 scoped 样式，可以通过以下方式自定义：

```vue
<style>
/* 修改上传区域高度 */
.upload-area :deep(.el-upload-dragger) {
  height: 250px;
}

/* 修改进度条颜色 */
.progress-container :deep(.el-progress__text) {
  color: #409EFF;
}
</style>
```

## 依赖项

- Vue 3.3+
- Element Plus 2.4+
- Axios 1.6+

## 验证需求

该组件实现并验证了以下需求：

- **需求 1.1**: 接受 xls 格式文件
- **需求 1.2**: 接受 xlsm 格式文件
- **需求 1.3**: 接受 xlsx 格式文件
- **需求 1.4**: 拒绝非 Excel 文件并显示错误消息
- **需求 9.1**: 上传成功时显示成功通知消息
- **需求 9.2**: 上传失败时显示包含失败原因的错误通知消息

## 测试建议

### 手动测试场景

1. **正常上传流程**
   - 上传有效的 xls/xlsx/xlsm 文件
   - 验证进度条显示正确
   - 验证成功通知显示
   - 验证解析结果显示

2. **文件格式验证**
   - 尝试上传 .txt 文件 → 应该被拒绝
   - 尝试上传 .pdf 文件 → 应该被拒绝
   - 尝试上传 .doc 文件 → 应该被拒绝

3. **文件大小验证**
   - 上传超过 10MB 的文件 → 应该被拒绝

4. **拖拽上传**
   - 拖拽文件到上传区域 → 应该触发上传

5. **错误处理**
   - 后端服务未启动时上传 → 应该显示错误通知
   - 上传损坏的 Excel 文件 → 应该显示解析错误

### 自动化测试

可以使用 Vitest 和 Vue Test Utils 编写单元测试：

```javascript
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import FileUpload from './FileUpload.vue'

describe('FileUpload', () => {
  it('should reject non-Excel files', () => {
    const wrapper = mount(FileUpload)
    const file = new File(['content'], 'test.txt', { type: 'text/plain' })
    const result = wrapper.vm.beforeUpload(file)
    expect(result).toBe(false)
  })

  it('should accept Excel files', () => {
    const wrapper = mount(FileUpload)
    const file = new File(['content'], 'test.xlsx', { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const result = wrapper.vm.beforeUpload(file)
    expect(result).toBe(true)
  })
})
```

## 注意事项

1. 确保后端服务运行在 `http://localhost:5000`
2. 确保 Vite 代理配置正确（vite.config.js）
3. 上传的文件会保存在后端的 `temp/uploads` 目录
4. 组件依赖 Element Plus 的图标，确保已正确导入
5. 文件上传使用 FormData，确保后端正确处理 multipart/form-data

## 未来改进

1. 支持批量文件上传
2. 添加文件预览功能
3. 支持断点续传
4. 添加上传历史记录
5. 支持从云存储导入文件
