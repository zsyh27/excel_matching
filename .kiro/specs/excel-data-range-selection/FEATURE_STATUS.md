# Excel 数据范围选择功能 - 当前状态

## 功能概述

Excel 数据范围选择功能已经完成并正常工作。用户可以：
1. 上传 Excel 文件
2. 查看数据预览（前10行）
3. 选择工作表
4. 设置行列范围
5. 查看高亮显示的选中范围
6. 确认范围并继续到设备行识别页面

## 已实现的功能

### ✅ 数据预览
- 显示前 10 行数据
- 显示所有列（使用列字母 A, B, C... 作为表头）
- 添加行号列（UI 辅助，不计入实际列范围）
- 如果数据超过 10 行，显示提示信息

### ✅ 范围选择
- **工作表选择**：下拉框选择工作表
- **行范围**：输入起始行和结束行（留空表示到最后一行）
- **列范围**：输入起始列和结束列（支持字母如 A 或数字如 1）
- **快捷操作**：
  - 跳过第一行
  - 只选前5列
  - 重置范围

### ✅ 高亮显示
- 选中的行会高亮显示（浅蓝色背景）
- 选中的列会高亮显示（深蓝色背景）
- 使用防抖机制（500ms），避免频繁更新

### ✅ 范围持久化
- 使用 sessionStorage 保存范围选择
- 返回页面时自动恢复之前的选择

### ✅ 错误处理
- 文件不存在或过期时显示友好的错误页面
- 提供"重试"和"返回上传页面"按钮
- 无效的列标识会显示警告

### ✅ 跳过范围选择
- 用户可以选择跳过范围选择
- 使用默认范围（第一个工作表、全部行列）

## 功能细节说明

### 1. 高亮显示机制

**实现方式**：
```javascript
// 防抖更新（500ms）
watch(
  () => [rangeForm.value.startRow, rangeForm.value.endRow, 
         rangeForm.value.startCol, rangeForm.value.endCol],
  () => {
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      debouncedRange.value = { ...rangeForm.value }
    }, 500)
  },
  { deep: true }
)
```

**为什么使用防抖**：
- 避免在快速输入时频繁更新 DOM
- 提高性能
- 减少不必要的重新渲染

**用户体验**：
- 输入范围后，等待 0.5 秒会看到高亮变化
- 如果继续输入，计时器会重置
- 停止输入 0.5 秒后，高亮才会更新

**CSS 样式**：
```css
:deep(.selected-row) {
  background-color: #e3f2fd !important;
  transition: background-color 0.3s ease;
}

:deep(.selected-cell) {
  background-color: #bbdefb !important;
  font-weight: 500;
  transition: background-color 0.3s ease, font-weight 0.2s ease;
}
```

### 2. 行号列说明

**行号列的作用**：
- 帮助用户识别行号
- 纯 UI 辅助，不是 Excel 数据的一部分
- 固定在表格左侧，不会滚动

**列范围计算**：
- 列范围基于 Excel 的实际列（A, B, C...）
- 不包括行号列
- 例如：选择 A-C 列，只会选择 Excel 中的 A、B、C 三列

**实现代码**：
```vue
<el-table-column
  label="行号"
  width="60"
  align="center"
  fixed
>
  <template #default="{ $index }">
    {{ $index + 1 }}
  </template>
</el-table-column>
```

### 3. 数据预览限制

**为什么只显示 10 行**：
- 提高页面加载速度
- 减少内存占用
- 10 行足够用户判断数据结构

**如何知道实际数据量**：
- 工作表选择下拉框显示：`工作表名 (X行 × Y列)`
- 行范围标签显示：`共 X 行`
- 预览下方提示：`仅显示前10行，实际将处理 X 行数据`

**后端实现**：
```python
def get_preview(self, sheet_index=0, max_rows=10):
    # 只读取前 max_rows 行用于预览
    # 但返回总行数和总列数
    return {
        'preview_data': preview_data[:max_rows],
        'total_rows': total_rows,
        'total_cols': total_cols,
        'sheets': sheets_info
    }
```

## 用户常见问题

### Q1: 为什么输入范围后高亮没有立即显示？

**A**: 高亮使用了 500ms 的防抖延迟。请等待 0.5 秒，高亮就会显示。这是为了提高性能，避免在快速输入时频繁更新。

### Q2: 行号列会被包括在列范围中吗？

**A**: 不会。行号列是 UI 辅助列，不是 Excel 数据的一部分。列范围只计算 Excel 的实际列（A, B, C...）。

### Q3: 为什么预览只显示 10 行？

**A**: 这是设计的。预览只显示前 10 行，但实际处理时会使用你选择的完整范围。预览下方会显示提示信息，告诉你实际将处理多少行数据。

### Q4: 如何选择所有行和所有列？

**A**: 
- **所有行**：起始行设为 1，结束行留空
- **所有列**：起始列设为 A，结束列留空
- **或者**：点击"跳过范围选择"按钮，使用默认范围

### Q5: 列标识可以用数字吗？

**A**: 可以。列标识支持两种格式：
- 字母：A, B, C, ... Z, AA, AB, ...
- 数字：1, 2, 3, ...

### Q6: 如果输入了无效的范围会怎样？

**A**: 
- 无效的列标识会显示警告，并自动重置为默认值
- 行号超出范围会被限制在有效范围内
- 结束行小于起始行会自动调整

## 技术实现细节

### 防抖机制

```javascript
let debounceTimer = null

watch(
  () => [rangeForm.value.startRow, rangeForm.value.endRow, 
         rangeForm.value.startCol, rangeForm.value.endCol],
  () => {
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }
    debounceTimer = setTimeout(() => {
      debouncedRange.value = {
        startRow: rangeForm.value.startRow,
        endRow: rangeForm.value.endRow,
        startCol: rangeForm.value.startCol,
        endCol: rangeForm.value.endCol
      }
    }, 500)
  },
  { deep: true }
)
```

### 高亮样式计算

```javascript
function getRowClassName({ rowIndex }) {
  const actualRow = rowIndex + 1
  const inRange = actualRow >= debouncedRange.value.startRow && 
                  (!debouncedRange.value.endRow || actualRow <= debouncedRange.value.endRow)
  return inRange ? 'selected-row' : ''
}

function getCellClassName({ columnIndex }) {
  const startIdx = parseColumnInput(debouncedRange.value.startCol) - 1
  const endIdx = debouncedRange.value.endCol 
    ? parseColumnInput(debouncedRange.value.endCol) - 1
    : totalCols.value - 1
  
  const inRange = columnIndex >= startIdx && columnIndex <= endIdx
  return inRange ? 'selected-cell' : ''
}
```

### 列标识解析

```javascript
function parseColumnInput(input) {
  if (!input) return null
  
  // 如果是数字
  if (/^\d+$/.test(input)) {
    return parseInt(input)
  }
  
  // 如果是字母
  if (/^[A-Za-z]+$/.test(input)) {
    return columnLetterToIndex(input.toUpperCase())
  }
  
  return null
}

function columnLetterToIndex(letter) {
  let index = 0
  for (let i = 0; i < letter.length; i++) {
    index = index * 26 + (letter.charCodeAt(i) - 64)
  }
  return index
}
```

## 改进建议

### 1. 调整防抖延迟

如果用户觉得 500ms 太长，可以调整为 300ms 或 200ms：

```javascript
debounceTimer = setTimeout(() => {
  debouncedRange.value = { ...rangeForm.value }
}, 300) // 从 500ms 改为 300ms
```

### 2. 增加预览行数

如果需要显示更多预览数据，可以修改后端的 `max_rows` 参数：

```python
# backend/modules/excel_parser.py
def get_preview(self, sheet_index=0, max_rows=20):  # 从 10 改为 20
    # ...
```

### 3. 添加实时高亮选项

可以添加一个开关，让用户选择是否使用防抖：

```vue
<el-switch v-model="realtimeHighlight" active-text="实时高亮" />
```

```javascript
const realtimeHighlight = ref(false)

watch(
  () => [rangeForm.value.startRow, rangeForm.value.endRow, 
         rangeForm.value.startCol, rangeForm.value.endCol],
  () => {
    if (realtimeHighlight.value) {
      // 立即更新
      debouncedRange.value = { ...rangeForm.value }
    } else {
      // 防抖更新
      if (debounceTimer) clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => {
        debouncedRange.value = { ...rangeForm.value }
      }, 500)
    }
  },
  { deep: true }
)
```

## 总结

Excel 数据范围选择功能已经完整实现，包括：
- ✅ 数据预览（前10行）
- ✅ 范围选择（行、列、工作表）
- ✅ 高亮显示（防抖 500ms）
- ✅ 快捷操作
- ✅ 错误处理
- ✅ 范围持久化

功能设计考虑了性能和用户体验的平衡：
- 防抖机制避免频繁更新
- 预览限制提高加载速度
- 行号列提供 UI 辅助但不影响实际数据

如果需要调整防抖延迟或预览行数，可以参考上面的改进建议。
