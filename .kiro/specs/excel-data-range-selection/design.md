# 设计文档 - Excel数据范围选择

## 概述

Excel数据范围选择功能为用户提供了在上传Excel文件后、识别设备行之前精确指定要处理的数据范围的能力。通过让用户选择工作表、行区间和列区间，系统可以从源头上减少噪音数据的干扰，提高后续处理的准确性和效率。

核心设计理念：
- **用户友好**: 提供直观的界面和实时预览，降低使用门槛
- **灵活性**: 支持多种输入方式（列字母/索引），提供合理的默认值
- **性能优先**: 只加载和处理必要的数据，避免内存溢出
- **向后兼容**: 不影响现有流程，范围选择为可选步骤

## 架构设计

系统采用前后端分离架构，在现有上传流程中插入范围选择步骤：

```
┌─────────────────────────────────────────────────────────┐
│                    用户流程                              │
│                                                          │
│  上传文件 → 【范围选择】 → 设备行识别 → 调整确认 → 匹配  │
│              ↑ 新增步骤                                  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    前端层                                │
│  ┌──────────────────────────────────────────────────┐   │
│  │ DataRangeSelectionView.vue                       │   │
│  │ - 工作表选择下拉框                                │   │
│  │ - 行列范围输入表单                                │   │
│  │ - 数据预览表格                                    │   │
│  │ - 范围预览高亮                                    │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────┐
│                     后端层                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │ API Layer (Flask)                                │   │
│  │ - POST /api/excel/preview                        │   │
│  │ - POST /api/excel/parse_range                    │   │
│  └──────────────────────────────────────────────────┘   │
│                            │                             │
│  ┌──────────────────────────────────────────────────┐   │
│  │ ExcelParser (Enhanced)                           │   │
│  │ - get_preview()                                  │   │
│  │ - parse_range()                                  │   │
│  │ - _col_letter_to_index()                         │   │
│  │ - _col_index_to_letter()                         │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 组件设计

### 1. 后端组件

#### 1.1 ExcelParser 增强

在现有的 `ExcelParser` 类中添加新方法：


```python
class ExcelParser:
    """Excel 解析器（增强版）"""
    
    def get_preview(self, file_path: str, sheet_index: int = 0, max_rows: int = 10) -> Dict:
        """
        获取Excel文件预览信息
        
        验证需求: 1.1, 1.2, 1.3, 1.4, 1.5
        
        Args:
            file_path: Excel文件路径
            sheet_index: 工作表索引（默认0）
            max_rows: 最大预览行数（默认10）
            
        Returns:
            {
                'sheets': [{'index': 0, 'name': 'Sheet1', 'rows': 100, 'cols': 20}],
                'preview_data': [[cell1, cell2, ...], ...],
                'total_rows': 100,
                'total_cols': 20,
                'column_letters': ['A', 'B', 'C', ...]
            }
        """
        pass
    
    def parse_range(
        self,
        file_path: str,
        sheet_index: int = 0,
        start_row: int = 1,
        end_row: Optional[int] = None,
        start_col: int = 1,
        end_col: Optional[int] = None
    ) -> ParseResult:
        """
        解析Excel文件的指定范围
        
        验证需求: 8.6, 8.7, 8.8
        
        Args:
            file_path: Excel文件路径
            sheet_index: 工作表索引
            start_row: 起始行号（从1开始）
            end_row: 结束行号（None表示到最后）
            start_col: 起始列号（从1开始）
            end_col: 结束列号（None表示到最后）
            
        Returns:
            ParseResult: 解析结果（只包含指定范围的数据）
        """
        pass
    
    def _col_letter_to_index(self, col_letter: str) -> int:
        """
        将列字母转换为列索引
        
        验证需求: 9.1, 9.2
        
        Examples:
            'A' -> 1
            'Z' -> 26
            'AA' -> 27
            'AZ' -> 52
        """
        pass
    
    def _col_index_to_letter(self, col_index: int) -> str:
        """
        将列索引转换为列字母
        
        验证需求: 9.3, 9.4
        
        Examples:
            1 -> 'A'
            26 -> 'Z'
            27 -> 'AA'
            52 -> 'AZ'
        """
        pass
    
    def _get_column_letters(self, max_cols: int) -> List[str]:
        """
        生成列字母列表
        
        Args:
            max_cols: 最大列数
            
        Returns:
            ['A', 'B', 'C', ..., 'Z', 'AA', 'AB', ...]
        """
        pass
```

#### 1.2 数据模型

```python
@dataclass
class SheetInfo:
    """工作表信息"""
    index: int          # 工作表索引
    name: str           # 工作表名称
    rows: int           # 总行数
    cols: int           # 总列数

@dataclass
class PreviewData:
    """预览数据"""
    sheets: List[SheetInfo]         # 工作表列表
    preview_data: List[List[str]]   # 预览数据（前N行）
    total_rows: int                 # 当前工作表总行数
    total_cols: int                 # 当前工作表总列数
    column_letters: List[str]       # 列字母列表

@dataclass
class RangeSelection:
    """范围选择"""
    sheet_index: int                # 工作表索引
    start_row: int                  # 起始行号
    end_row: Optional[int]          # 结束行号
    start_col: int                  # 起始列号
    end_col: Optional[int]          # 结束列号
```

### 2. API端点

#### 2.1 POST /api/excel/preview

获取Excel文件预览信息：

```python
@app.route('/api/excel/preview', methods=['POST'])
def preview_excel():
    """
    Excel预览接口
    
    验证需求: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7
    
    Request:
        {
            "file_id": "uuid-xxx",
            "sheet_index": 0  # 可选，默认0
        }
    
    Response:
        {
            "success": true,
            "data": {
                "sheets": [
                    {
                        "index": 0,
                        "name": "Sheet1",
                        "rows": 100,
                        "cols": 20
                    }
                ],
                "preview_data": [
                    ["序号", "设备名称", "型号", ...],
                    ["1", "DDC控制器", "ML-5000", ...],
                    ...
                ],
                "total_rows": 100,
                "total_cols": 20,
                "column_letters": ["A", "B", "C", ...]
            }
        }
    
    Error Response:
        {
            "success": false,
            "error_code": "FILE_NOT_FOUND",
            "error_message": "文件不存在或已过期"
        }
    """
    pass
```

#### 2.2 POST /api/excel/parse_range

使用指定范围解析Excel文件：

```python
@app.route('/api/excel/parse_range', methods=['POST'])
def parse_excel_range():
    """
    Excel范围解析接口
    
    验证需求: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8
    
    Request:
        {
            "file_id": "uuid-xxx",
            "sheet_index": 0,      # 可选，默认0
            "start_row": 2,        # 可选，默认1
            "end_row": 50,         # 可选，默认null（到最后）
            "start_col": 1,        # 可选，默认1
            "end_col": 10          # 可选，默认null（到最后）
        }
    
    Response:
        {
            "success": true,
            "file_id": "uuid-xxx",
            "parse_result": {
                "rows": [...],
                "total_rows": 49,
                "filtered_rows": 5,
                "format": "xlsx"
            }
        }
    
    Error Response:
        {
            "success": false,
            "error_code": "INVALID_RANGE",
            "error_message": "行号超出有效范围（1-100）"
        }
    """
    pass
```

### 3. 前端组件

#### 3.1 DataRangeSelectionView.vue

数据范围选择主组件：


```vue
<template>
  <div class="data-range-selection">
    <el-card class="selection-card">
      <template #header>
        <div class="card-header">
          <span>数据范围选择</span>
          <el-tag type="info">{{ filename }}</el-tag>
        </div>
      </template>

      <!-- 工作表选择 -->
      <el-form :model="rangeForm" label-width="100px">
        <el-form-item label="工作表">
          <el-select
            v-model="rangeForm.sheetIndex"
            @change="handleSheetChange"
            :disabled="sheets.length === 1"
            style="width: 300px"
          >
            <el-option
              v-for="sheet in sheets"
              :key="sheet.index"
              :label="`${sheet.name} (${sheet.rows}行 × ${sheet.cols}列)`"
              :value="sheet.index"
            />
          </el-select>
        </el-form-item>

        <!-- 行范围选择 -->
        <el-form-item label="行范围">
          <el-input-number
            v-model="rangeForm.startRow"
            :min="1"
            :max="totalRows"
            placeholder="起始行"
            style="width: 150px"
          />
          <span style="margin: 0 10px">至</span>
          <el-input-number
            v-model="rangeForm.endRow"
            :min="rangeForm.startRow"
            :max="totalRows"
            placeholder="结束行（留空=最后）"
            style="width: 150px"
          />
          <el-tag type="info" size="small" style="margin-left: 10px">
            共 {{ selectedRowCount }} 行
          </el-tag>
        </el-form-item>

        <!-- 列范围选择 -->
        <el-form-item label="列范围">
          <el-input
            v-model="rangeForm.startCol"
            placeholder="起始列（如A或1）"
            style="width: 150px"
            @blur="validateColumn('start')"
          />
          <span style="margin: 0 10px">至</span>
          <el-input
            v-model="rangeForm.endCol"
            placeholder="结束列（留空=最后）"
            style="width: 150px"
            @blur="validateColumn('end')"
          />
          <el-tag type="info" size="small" style="margin-left: 10px">
            共 {{ selectedColCount }} 列
          </el-tag>
        </el-form-item>

        <!-- 快捷选项 -->
        <el-form-item label="快捷选项">
          <el-button size="small" @click="skipFirstRow">跳过第一行</el-button>
          <el-button size="small" @click="selectFirstFiveCols">只选前5列</el-button>
          <el-button size="small" @click="resetRange">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据预览 -->
      <el-divider>数据预览</el-divider>
      <div class="preview-container">
        <el-table
          :data="previewData"
          border
          stripe
          max-height="400"
          :row-class-name="getRowClassName"
          :cell-class-name="getCellClassName"
        >
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
          <el-table-column
            v-for="(col, index) in columnLetters"
            :key="index"
            :label="col"
            :prop="`col_${index}`"
            min-width="120"
          >
            <template #default="{ row }">
              {{ row[index] || '' }}
            </template>
          </el-table-column>
        </el-table>
        <div v-if="totalRows > 10" class="preview-tip">
          <el-alert
            type="info"
            :closable="false"
            show-icon
          >
            仅显示前10行，实际将处理 {{ selectedRowCount }} 行数据
          </el-alert>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleConfirm">
          确认范围并继续
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getExcelPreview, parseExcelRange } from '@/api/excel'

const props = defineProps({
  excelId: {
    type: String,
    required: true
  },
  filename: {
    type: String,
    default: ''
  }
})

const router = useRouter()

// 状态管理
const loading = ref(false)
const sheets = ref([])
const previewData = ref([])
const columnLetters = ref([])
const totalRows = ref(0)
const totalCols = ref(0)

// 范围表单
const rangeForm = ref({
  sheetIndex: 0,
  startRow: 1,
  endRow: null,
  startCol: 'A',
  endCol: null
})

// 计算属性
const selectedRowCount = computed(() => {
  const end = rangeForm.value.endRow || totalRows.value
  return Math.max(0, end - rangeForm.value.startRow + 1)
})

const selectedColCount = computed(() => {
  const startIdx = parseColumnInput(rangeForm.value.startCol)
  const endIdx = rangeForm.value.endCol 
    ? parseColumnInput(rangeForm.value.endCol) 
    : totalCols.value
  return Math.max(0, endIdx - startIdx + 1)
})

// 组件挂载时加载预览
onMounted(async () => {
  await loadPreview()
})

// 加载预览数据
async function loadPreview() {
  loading.value = true
  try {
    const response = await getExcelPreview(props.excelId, rangeForm.value.sheetIndex)
    const data = response.data.data
    
    sheets.value = data.sheets
    previewData.value = data.preview_data
    totalRows.value = data.total_rows
    totalCols.value = data.total_cols
    columnLetters.value = data.column_letters
    
    // 如果只有一个工作表，自动选择
    if (sheets.value.length === 1) {
      rangeForm.value.sheetIndex = 0
    }
  } catch (error) {
    ElMessage.error('加载预览失败')
    console.error('加载预览失败:', error)
  } finally {
    loading.value = false
  }
}

// 工作表切换
async function handleSheetChange() {
  await loadPreview()
  resetRange()
}

// 列输入验证
function validateColumn(type) {
  const col = type === 'start' ? rangeForm.value.startCol : rangeForm.value.endCol
  if (!col) return
  
  const index = parseColumnInput(col)
  if (index < 1 || index > totalCols.value) {
    ElMessage.warning(`无效的列标识: ${col}`)
    if (type === 'start') {
      rangeForm.value.startCol = 'A'
    } else {
      rangeForm.value.endCol = null
    }
  }
}

// 解析列输入（支持字母和数字）
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

// 列字母转索引
function columnLetterToIndex(letter) {
  let index = 0
  for (let i = 0; i < letter.length; i++) {
    index = index * 26 + (letter.charCodeAt(i) - 64)
  }
  return index
}

// 快捷操作
function skipFirstRow() {
  rangeForm.value.startRow = 2
}

function selectFirstFiveCols() {
  rangeForm.value.startCol = 'A'
  rangeForm.value.endCol = 'E'
}

function resetRange() {
  rangeForm.value.startRow = 1
  rangeForm.value.endRow = null
  rangeForm.value.startCol = 'A'
  rangeForm.value.endCol = null
}

// 行/列高亮样式
function getRowClassName({ rowIndex }) {
  const actualRow = rowIndex + 1
  const inRange = actualRow >= rangeForm.value.startRow && 
                  (!rangeForm.value.endRow || actualRow <= rangeForm.value.endRow)
  return inRange ? 'selected-row' : ''
}

function getCellClassName({ columnIndex }) {
  const startIdx = parseColumnInput(rangeForm.value.startCol) - 1
  const endIdx = rangeForm.value.endCol 
    ? parseColumnInput(rangeForm.value.endCol) - 1
    : totalCols.value - 1
  
  const inRange = columnIndex >= startIdx && columnIndex <= endIdx
  return inRange ? 'selected-cell' : ''
}

// 确认范围
async function handleConfirm() {
  try {
    loading.value = true
    
    // 转换列输入为索引
    const startColIndex = parseColumnInput(rangeForm.value.startCol)
    const endColIndex = rangeForm.value.endCol 
      ? parseColumnInput(rangeForm.value.endCol) 
      : null
    
    // 调用范围解析API
    const response = await parseExcelRange(props.excelId, {
      sheet_index: rangeForm.value.sheetIndex,
      start_row: rangeForm.value.startRow,
      end_row: rangeForm.value.endRow,
      start_col: startColIndex,
      end_col: endColIndex
    })
    
    if (response.data.success) {
      // 保存范围选择到sessionStorage
      sessionStorage.setItem(`range_${props.excelId}`, JSON.stringify(rangeForm.value))
      
      // 跳转到设备行识别页面
      router.push({
        name: 'DeviceRowAdjustment',
        params: { excelId: props.excelId }
      })
    }
  } catch (error) {
    ElMessage.error('解析失败: ' + (error.response?.data?.error_message || error.message))
  } finally {
    loading.value = false
  }
}

function handleCancel() {
  router.back()
}
</script>

<style scoped>
.data-range-selection {
  padding: 20px;
}

.selection-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-container {
  margin-top: 20px;
}

.preview-tip {
  margin-top: 10px;
}

.action-buttons {
  margin-top: 20px;
  text-align: right;
}

/* 高亮选中的行和列 */
:deep(.selected-row) {
  background-color: #e3f2fd !important;
}

:deep(.selected-cell) {
  background-color: #bbdefb !important;
  font-weight: 500;
}
</style>
```

### 4. 路由配置

在前端路由中添加新的范围选择页面：

```javascript
// frontend/src/router/index.js

{
  path: '/data-range/:excelId',
  name: 'DataRangeSelection',
  component: () => import('@/views/DataRangeSelectionView.vue'),
  props: true
}
```

### 5. API客户端

添加新的API调用方法：

```javascript
// frontend/src/api/excel.js

import request from './request'

/**
 * 获取Excel预览
 */
export function getExcelPreview(fileId, sheetIndex = 0) {
  return request({
    url: '/api/excel/preview',
    method: 'post',
    data: {
      file_id: fileId,
      sheet_index: sheetIndex
    }
  })
}

/**
 * 使用指定范围解析Excel
 */
export function parseExcelRange(fileId, range) {
  return request({
    url: '/api/excel/parse_range',
    method: 'post',
    data: {
      file_id: fileId,
      ...range
    }
  })
}
```

## 数据流设计

### 1. 完整流程

```
1. 用户上传Excel文件
   ↓
2. 后端返回file_id
   ↓
3. 前端跳转到数据范围选择页面
   ↓
4. 调用 /api/excel/preview 获取预览数据
   ↓
5. 用户选择工作表、行列范围
   ↓
6. 实时更新预览高亮
   ↓
7. 用户点击"确认范围"
   ↓
8. 调用 /api/excel/parse_range 解析指定范围
   ↓
9. 跳转到设备行识别页面
```

### 2. 数据缓存策略

- **预览数据**: 前端缓存在组件state中，切换工作表时重新加载
- **范围选择**: 保存到sessionStorage，支持返回时恢复
- **解析结果**: 后端缓存在excel_analysis_cache中，使用excel_id作为键

### 3. 错误处理



| 错误类型 | 错误码 | 处理方式 |
|---------|--------|---------|
| 文件不存在 | FILE_NOT_FOUND | 提示用户重新上传 |
| 文件格式不支持 | INVALID_FORMAT | 提示支持的格式 |
| 工作表不存在 | SHEET_NOT_FOUND | 重置为第一个工作表 |
| 行号超出范围 | INVALID_ROW_RANGE | 显示有效范围提示 |
| 列标识无效 | INVALID_COL_IDENTIFIER | 显示格式说明 |
| 范围为空 | EMPTY_RANGE | 提示至少选择一行一列 |

## 性能优化

### 1. 后端优化

- **流式读取**: 使用openpyxl的read_only模式，避免加载整个文件到内存
- **按需加载**: 只读取指定范围的单元格，不加载整个工作表
- **预览限制**: 预览最多返回10行数据，减少网络传输
- **缓存策略**: 预览数据缓存5分钟，避免重复读取

```python
# 示例：流式读取指定范围
def _parse_xlsx_range(self, file_path, sheet_index, start_row, end_row, start_col, end_col):
    workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
    sheet = workbook.worksheets[sheet_index]
    
    rows = []
    for row_idx, row in enumerate(sheet.iter_rows(
        min_row=start_row,
        max_row=end_row,
        min_col=start_col,
        max_col=end_col,
        values_only=True
    ), start=start_row):
        # 只处理指定范围内的数据
        row_data = [self._convert_cell_value_openpyxl(cell) for cell in row]
        parsed_row = ParsedRow(...)
        rows.append(parsed_row)
    
    workbook.close()
    return rows
```

### 2. 前端优化

- **防抖处理**: 范围输入变化时，延迟500ms更新预览
- **虚拟滚动**: 如果预览数据超过100行，使用虚拟滚动
- **懒加载**: 只在用户切换工作表时才加载新数据
- **本地验证**: 在前端验证范围有效性，减少无效请求

```javascript
// 示例：防抖处理
import { debounce } from 'lodash-es'

const updatePreview = debounce(() => {
  // 更新预览高亮
}, 500)

watch([() => rangeForm.value.startRow, () => rangeForm.value.endRow], () => {
  updatePreview()
})
```

## 向后兼容性

### 1. 可选步骤

范围选择是可选的，用户可以跳过直接使用默认范围：

- 在上传成功后，提供"跳过范围选择"按钮
- 如果用户跳过，使用默认范围（全部数据）
- 现有的直接调用 `/api/parse` 的流程继续有效

### 2. API兼容

- 新增的API端点不影响现有端点
- `/api/parse` 继续支持，内部调用 `parse_range` 使用默认范围
- 前端可以根据需要选择使用新流程或旧流程

```python
# 示例：parse接口向后兼容
@app.route('/api/parse', methods=['POST'])
def parse_file():
    """文件解析接口（向后兼容）"""
    # 内部调用parse_range，使用默认范围
    return parse_excel_range_internal(
        file_id=data['file_id'],
        sheet_index=0,
        start_row=1,
        end_row=None,
        start_col=1,
        end_col=None
    )
```

## 测试策略

### 1. 单元测试

测试ExcelParser的新方法：

```python
# backend/tests/test_excel_range_selection.py

def test_col_letter_to_index():
    """测试列字母转索引"""
    parser = ExcelParser()
    assert parser._col_letter_to_index('A') == 1
    assert parser._col_letter_to_index('Z') == 26
    assert parser._col_letter_to_index('AA') == 27
    assert parser._col_letter_to_index('AZ') == 52

def test_col_index_to_letter():
    """测试列索引转字母"""
    parser = ExcelParser()
    assert parser._col_index_to_letter(1) == 'A'
    assert parser._col_index_to_letter(26) == 'Z'
    assert parser._col_index_to_letter(27) == 'AA'
    assert parser._col_index_to_letter(52) == 'AZ'

def test_get_preview():
    """测试获取预览"""
    parser = ExcelParser()
    preview = parser.get_preview('test.xlsx')
    assert 'sheets' in preview
    assert 'preview_data' in preview
    assert len(preview['preview_data']) <= 10

def test_parse_range():
    """测试范围解析"""
    parser = ExcelParser()
    result = parser.parse_range(
        'test.xlsx',
        start_row=2,
        end_row=10,
        start_col=1,
        end_col=5
    )
    assert len(result.rows) == 9  # 2-10共9行
```

### 2. 集成测试

测试完整的API流程：

```python
# backend/tests/test_excel_range_api.py

def test_preview_api():
    """测试预览API"""
    response = client.post('/api/excel/preview', json={
        'file_id': 'test-file-id'
    })
    assert response.status_code == 200
    data = response.json['data']
    assert 'sheets' in data
    assert 'preview_data' in data

def test_parse_range_api():
    """测试范围解析API"""
    response = client.post('/api/excel/parse_range', json={
        'file_id': 'test-file-id',
        'start_row': 2,
        'end_row': 10,
        'start_col': 1,
        'end_col': 5
    })
    assert response.status_code == 200
    assert response.json['success'] == True
```

### 3. 端到端测试

测试完整的用户流程：

```javascript
// frontend/tests/e2e/data-range-selection.spec.js

describe('数据范围选择', () => {
  it('应该正确显示预览数据', async () => {
    // 上传文件
    await uploadFile('test.xlsx')
    
    // 进入范围选择页面
    await page.goto('/data-range/test-file-id')
    
    // 验证预览数据显示
    expect(await page.locator('.preview-container').isVisible()).toBe(true)
  })
  
  it('应该正确选择范围', async () => {
    // 输入范围
    await page.fill('input[placeholder="起始行"]', '2')
    await page.fill('input[placeholder="结束行"]', '10')
    
    // 验证高亮
    const selectedRows = await page.locator('.selected-row').count()
    expect(selectedRows).toBe(9)
  })
  
  it('应该正确解析范围', async () => {
    // 点击确认
    await page.click('button:has-text("确认范围并继续")')
    
    // 验证跳转到设备行识别页面
    await page.waitForURL('/device-row-adjustment/*')
  })
})
```

## 安全考虑

### 1. 输入验证

- 验证file_id格式（UUID）
- 验证sheet_index范围（0到工作表数量-1）
- 验证行号范围（1到总行数）
- 验证列标识格式（字母或数字）
- 防止SQL注入（虽然不涉及数据库查询）

### 2. 文件访问控制

- 只允许访问用户自己上传的文件
- 文件ID使用UUID，难以猜测
- 文件缓存设置过期时间（1小时）
- 定期清理过期文件

### 3. 资源限制

- 限制预览行数（最多100行）
- 限制文件大小（最大50MB）
- 限制并发请求数（每用户最多5个）
- 超时保护（请求超时30秒）

## 部署注意事项

### 1. 依赖项

确保安装了必要的Python包：

```bash
pip install openpyxl xlrd
```

### 2. 配置项

在 `config.py` 中添加新配置：

```python
class Config:
    # Excel预览配置
    EXCEL_PREVIEW_MAX_ROWS = 10
    EXCEL_PREVIEW_CACHE_TTL = 300  # 5分钟
    
    # Excel解析配置
    EXCEL_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    EXCEL_PARSE_TIMEOUT = 30  # 30秒
```

### 3. 前端环境变量

```env
# .env.production
VITE_API_BASE_URL=https://api.example.com
VITE_EXCEL_PREVIEW_ENABLED=true
```

## 未来扩展

### 1. 高级功能

- **范围模板**: 保存常用的范围配置为模板
- **批量处理**: 支持一次选择多个范围
- **智能识别**: 自动识别表头和数据区域
- **范围验证**: 检测选择的范围是否包含有效数据

### 2. 用户体验改进

- **拖拽选择**: 支持鼠标拖拽选择范围
- **可视化编辑**: 在预览表格上直接框选范围
- **历史记录**: 记住用户最近使用的范围配置
- **范围建议**: 根据文件内容智能推荐范围

### 3. 性能优化

- **增量加载**: 预览数据分批加载
- **WebWorker**: 在后台线程处理大文件
- **缓存优化**: 使用Redis缓存预览数据
- **CDN加速**: 静态资源使用CDN

## 总结

Excel数据范围选择功能通过在上传和解析之间插入一个范围选择步骤，让用户能够精确控制要处理的数据范围。这个设计：

1. **用户友好**: 提供直观的界面和实时预览
2. **性能优化**: 只加载和处理必要的数据
3. **向后兼容**: 不影响现有流程
4. **可扩展**: 为未来的高级功能预留空间

通过这个功能，用户可以从源头上减少噪音数据，提高后续处理的准确性和效率。
