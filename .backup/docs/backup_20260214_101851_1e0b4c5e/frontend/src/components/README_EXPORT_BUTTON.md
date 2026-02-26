# ExportButton 组件文档

## 概述

ExportButton 是一个独立的导出按钮组件，负责处理报价清单的导出功能。该组件调用后端 `/api/export` 接口，将匹配结果导出为 Excel 文件。

## 功能特性

1. **导出按钮显示**
   - 仅在有数据时显示按钮
   - 显示下载图标和文字
   - 支持加载状态显示

2. **导出功能**
   - 调用后端 `/api/export` 接口
   - 传递文件 ID 和匹配结果数据
   - 自动触发文件下载

3. **文件下载**
   - 创建临时下载链接
   - 自动生成文件名（包含时间戳）
   - 下载完成后清理资源

4. **通知提示**
   - 导出成功时显示成功通知
   - 导出失败时显示错误通知
   - 包含详细的错误信息

## Props

| 属性名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| fileId | String | 是 | null | 上传文件的唯一标识 |
| matchedRows | Array | 是 | [] | 匹配结果数据数组 |
| originalFilename | String | 否 | '' | 原始文件名，用于生成导出文件名 |

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| export-success | { filename, timestamp } | 导出成功时触发 |
| export-error | { message, error } | 导出失败时触发 |

## 使用示例

### 基本使用

```vue
<template>
  <ExportButton
    :file-id="fileId"
    :matched-rows="matchedRows"
    :original-filename="filename"
    @export-success="handleExportSuccess"
    @export-error="handleExportError"
  />
</template>

<script setup>
import { ref } from 'vue'
import ExportButton from './ExportButton.vue'

const fileId = ref('uuid-string')
const matchedRows = ref([
  {
    row_number: 1,
    row_type: 'device',
    device_description: 'CO浓度探测器',
    match_result: {
      device_id: 'SENSOR001',
      matched_device_text: '霍尼韦尔 CO传感器...',
      unit_price: 766.14,
      match_status: 'success'
    }
  }
])
const filename = ref('设备清单.xlsx')

const handleExportSuccess = (data) => {
  console.log('导出成功:', data)
}

const handleExportError = (error) => {
  console.error('导出失败:', error)
}
</script>
```

### 在 ResultTable 中使用

```vue
<template>
  <div class="card-header">
    <span>匹配结果</span>
    <ExportButton
      :file-id="fileId"
      :matched-rows="displayRows"
      :original-filename="originalFilename"
      @export-success="handleExportSuccess"
      @export-error="handleExportError"
    />
  </div>
</template>

<script setup>
import ExportButton from './ExportButton.vue'

const handleExportSuccess = (data) => {
  emit('export-success', data)
}

const handleExportError = (error) => {
  console.error('导出错误:', error)
}
</script>
```

## 导出流程

1. **验证参数**
   - 检查 fileId 是否存在
   - 检查 matchedRows 是否有数据

2. **调用接口**
   - POST `/api/export`
   - 传递 file_id 和 matched_rows
   - 设置 responseType 为 'blob'

3. **处理响应**
   - 创建 Blob 对象
   - 生成下载链接
   - 触发浏览器下载

4. **清理资源**
   - 移除临时链接
   - 释放 URL 对象

5. **显示通知**
   - 成功：显示成功通知，触发 export-success 事件
   - 失败：显示错误通知，触发 export-error 事件

## 文件命名规则

导出的文件名格式：`{原始文件名}_导出_{时间戳}.xlsx`

示例：
- 输入：`设备清单.xlsx`
- 输出：`设备清单_导出_2026-02-07T12-30-45.xlsx`

如果没有提供原始文件名，则使用默认名称：`报价清单_导出_{时间戳}.xlsx`

## 错误处理

### 常见错误

1. **缺少文件 ID**
   - 错误信息：缺少文件 ID，无法导出
   - 处理：显示错误消息，不调用接口

2. **没有数据**
   - 错误信息：没有可导出的数据
   - 处理：显示错误消息，不调用接口

3. **网络错误**
   - 错误信息：从后端响应中提取
   - 处理：显示错误通知，触发 export-error 事件

4. **文件生成失败**
   - 错误信息：导出报价清单失败
   - 处理：显示错误通知，记录详细错误

### 错误响应处理

组件会尝试从 Blob 响应中提取错误信息：

```javascript
if (error.response.data instanceof Blob) {
  const text = await error.response.data.text()
  const errorData = JSON.parse(text)
  errorMessage = errorData.error_message
}
```

## 样式定制

组件使用 Element Plus 的按钮样式，可以通过以下方式定制：

```css
.el-button {
  font-weight: 500;
}

.el-button .el-icon {
  margin-right: 5px;
}
```

## 暴露的方法

组件通过 `defineExpose` 暴露了 `handleExport` 方法，父组件可以通过 ref 调用：

```vue
<template>
  <ExportButton ref="exportButtonRef" ... />
  <el-button @click="triggerExport">手动触发导出</el-button>
</template>

<script setup>
import { ref } from 'vue'

const exportButtonRef = ref(null)

const triggerExport = () => {
  exportButtonRef.value.handleExport()
}
</script>
```

## 验证需求

该组件实现了以下需求：

- **需求 9.4**: 实现导出功能，调用后端接口并触发文件下载
- **需求 9.5**: 实现导出成功/失败的通知提示

## 注意事项

1. **超时设置**：导出接口的超时时间设置为 60 秒，以应对大文件导出
2. **响应类型**：必须设置 `responseType: 'blob'` 以正确接收二进制数据
3. **内存管理**：下载完成后及时清理 URL 对象，避免内存泄漏
4. **文件名编码**：文件名中的特殊字符会被替换，确保跨平台兼容性
5. **错误处理**：Blob 类型的错误响应需要特殊处理才能提取错误信息

## 依赖

- Vue 3
- Element Plus
- Axios
- @element-plus/icons-vue (Download 图标)

## 浏览器兼容性

- Chrome/Edge: 完全支持
- Firefox: 完全支持
- Safari: 完全支持
- IE11: 不支持（需要 polyfill）
