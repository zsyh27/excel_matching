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
            style="width: 400px"
          >
            <el-option
              v-for="sheet in sheets"
              :key="sheet.index"
              :label="`${sheet.name} (${sheet.rows}行 × ${sheet.cols}列)`"
              :value="sheet.index"
            />
          </el-select>
          <el-text v-if="sheets.length === 1" type="info" size="small" style="margin-left: 10px">
            只有一个工作表，已自动选择
          </el-text>
        </el-form-item>

        <!-- 行范围选择 -->
        <el-form-item label="行范围">
          <el-input-number
            v-model="rangeForm.startRow"
            :min="1"
            :max="totalRows || 999999"
            placeholder="起始行"
            style="width: 150px"
            :disabled="!totalRows"
          />
          <span style="margin: 0 10px">至</span>
          <el-input-number
            v-model="rangeForm.endRow"
            :min="rangeForm.startRow"
            :max="totalRows || 999999"
            placeholder="结束行"
            style="width: 150px"
            clearable
            :disabled="!totalRows"
          />
          <el-tag type="info" size="small" style="margin-left: 10px">
            共 {{ selectedRowCount }} 行
          </el-tag>
          <el-text type="info" size="small" style="margin-left: 10px">
            留空表示到最后一行
          </el-text>
        </el-form-item>

        <!-- 列范围选择 -->
        <el-form-item label="列范围">
          <el-input
            v-model="rangeForm.startCol"
            placeholder="起始列（如A或1）"
            style="width: 150px"
            @blur="validateColumn('start')"
            :disabled="!totalCols"
          />
          <span style="margin: 0 10px">至</span>
          <el-input
            v-model="rangeForm.endCol"
            placeholder="结束列"
            style="width: 150px"
            @blur="validateColumn('end')"
            clearable
            :disabled="!totalCols"
          />
          <el-tag type="info" size="small" style="margin-left: 10px">
            共 {{ selectedColCount }} 列
          </el-tag>
          <el-text type="info" size="small" style="margin-left: 10px">
            留空表示到最后一列
          </el-text>
        </el-form-item>

        <!-- 快捷选项 -->
        <el-form-item label="快捷选项">
          <el-button size="small" @click="skipFirstRow" :disabled="!totalRows">跳过第一行</el-button>
          <el-button size="small" @click="selectFirstFiveCols" :disabled="!totalCols">只选前5列</el-button>
          <el-button size="small" @click="resetRange" :disabled="!totalRows && !totalCols">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据预览 -->
      <el-divider>数据预览</el-divider>
      <transition name="fade" mode="out-in">
        <div v-if="!loading" class="preview-container" key="preview">
          <el-table
            :key="`table-${debouncedRange.startRow}-${debouncedRange.endRow}-${debouncedRange.startCol}-${debouncedRange.endCol}`"
            :data="previewData"
            border
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
        <div v-else class="preview-skeleton" key="skeleton">
          <el-skeleton :rows="10" animated />
        </div>
      </transition>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button @click="handleCancel">取消</el-button>
        <el-button plain @click="handleSkipRangeSelection" :disabled="loading || !!error">
          跳过范围选择
        </el-button>
        <el-button type="primary" @click="handleConfirm" :loading="loading" :disabled="!!error">
          确认范围并继续
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getExcelPreview, parseExcelRange } from '@/api/excel'

const router = useRouter()
const route = useRoute()

// 从路由参数获取excelId和filename
const excelId = ref(route.params.excelId || '')
const filename = ref(route.query.filename || '')

// 状态管理
const loading = ref(false)
const error = ref(null)
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

// 防抖更新的范围值（用于高亮显示）
const debouncedRange = ref({
  startRow: 1,
  endRow: null,
  startCol: 'A',
  endCol: null
})

// 防抖定时器
let debounceTimer = null

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

// 监听范围变化，防抖更新高亮（200ms）
watch(
  () => [rangeForm.value.startRow, rangeForm.value.endRow, rangeForm.value.startCol, rangeForm.value.endCol],
  () => {
    console.log('[watch] 范围变化，准备更新高亮')
    
    // 清除之前的定时器
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }
    
    // 设置新的定时器，200ms后更新高亮
    debounceTimer = setTimeout(() => {
      console.log('[watch] 更新 debouncedRange:', {
        startRow: rangeForm.value.startRow,
        endRow: rangeForm.value.endRow,
        startCol: rangeForm.value.startCol,
        endCol: rangeForm.value.endCol
      })
      
      debouncedRange.value = {
        startRow: rangeForm.value.startRow,
        endRow: rangeForm.value.endRow,
        startCol: rangeForm.value.startCol,
        endCol: rangeForm.value.endCol
      }
    }, 200) // 从 500ms 改为 200ms
  },
  { deep: true }
)

// 组件挂载时加载预览
onMounted(async () => {
  console.log('[DataRangeSelection] 组件已挂载')
  console.log('[DataRangeSelection] excelId:', excelId.value)
  console.log('[DataRangeSelection] filename:', filename.value)
  
  if (!excelId.value) {
    console.error('[DataRangeSelection] 缺少文件ID')
    ElMessage.error('缺少文件ID')
    router.back()
    return
  }
  
  // 尝试从sessionStorage恢复之前的范围选择
  const savedRange = sessionStorage.getItem(`excel_range_${excelId.value}`)
  if (savedRange) {
    try {
      const parsedRange = JSON.parse(savedRange)
      rangeForm.value = {
        sheetIndex: parsedRange.sheetIndex ?? 0,
        startRow: parsedRange.startRow ?? 1,
        endRow: parsedRange.endRow ?? null,
        startCol: parsedRange.startCol ?? 'A',
        endCol: parsedRange.endCol ?? null
      }
      console.log('[DataRangeSelection] 已恢复范围选择:', rangeForm.value)
      ElMessage.success('已恢复之前的范围选择')
    } catch (error) {
      console.error('[DataRangeSelection] 恢复范围选择失败:', error)
    }
  }
  
  console.log('[DataRangeSelection] 开始加载预览...')
  await loadPreview()
  console.log('[DataRangeSelection] 预览加载完成')
  
  // 初始化防抖范围值
  debouncedRange.value = {
    startRow: rangeForm.value.startRow,
    endRow: rangeForm.value.endRow,
    startCol: rangeForm.value.startCol,
    endCol: rangeForm.value.endCol
  }
})

// 加载预览数据
async function loadPreview() {
  console.log('[loadPreview] 开始加载预览')
  console.log('[loadPreview] excelId:', excelId.value)
  console.log('[loadPreview] sheetIndex:', rangeForm.value.sheetIndex)
  
  loading.value = true
  error.value = null
  try {
    console.log('[loadPreview] 调用 getExcelPreview API...')
    const response = await getExcelPreview(excelId.value, rangeForm.value.sheetIndex)
    console.log('[loadPreview] API 响应:', response)
    
    const data = response.data.data
    console.log('[loadPreview] 解析数据:', data)
    
    sheets.value = data.sheets
    previewData.value = data.preview_data
    totalRows.value = data.total_rows
    totalCols.value = data.total_cols
    columnLetters.value = data.column_letters
    
    console.log('[loadPreview] 数据加载成功')
    console.log('[loadPreview] sheets:', sheets.value.length)
    console.log('[loadPreview] previewData:', previewData.value.length)
    
    // 如果只有一个工作表，自动选择
    if (sheets.value.length === 1) {
      rangeForm.value.sheetIndex = 0
    }
  } catch (err) {
    console.error('[loadPreview] 加载失败:', err)
    console.error('[loadPreview] 错误详情:', err.response)
    error.value = err.response?.data?.error_message || err.message || '加载预览失败'
    ElMessage.error('加载预览失败: ' + error.value)
  } finally {
    loading.value = false
    console.log('[loadPreview] loading 状态:', loading.value)
    console.log('[loadPreview] error 状态:', error.value)
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
  
  // 立即更新防抖范围（重置操作不需要防抖）
  debouncedRange.value = {
    startRow: 1,
    endRow: null,
    startCol: 'A',
    endCol: null
  }
}

// 行/列高亮样式（使用防抖后的范围值）
// 只高亮行列交叉的区域
function getRowClassName({ rowIndex }) {
  // 不再单独高亮整行
  return ''
}

function getCellClassName({ row, column, rowIndex, columnIndex }) {
  // 排除行号列（label 为"行号"）
  if (column.label === '行号') {
    return ''
  }
  
  // 检查行是否在范围内
  const actualRow = rowIndex + 1  // rowIndex 是 0-based，actualRow 是 1-based
  const startRow = debouncedRange.value.startRow
  const endRow = debouncedRange.value.endRow || totalRows.value
  const inRowRange = actualRow >= startRow && actualRow <= endRow
  
  if (!inRowRange) {
    return ''
  }
  
  // 检查列是否在范围内
  // columnIndex 是所有列的索引（包括行号列）
  // 行号列是第0列，所以数据列从第1列开始
  const dataColumnIndex = columnIndex - 1
  
  const startColIdx = parseColumnInput(debouncedRange.value.startCol) - 1
  const endColIdx = debouncedRange.value.endCol 
    ? parseColumnInput(debouncedRange.value.endCol) - 1
    : totalCols.value - 1
  
  const inColRange = dataColumnIndex >= startColIdx && dataColumnIndex <= endColIdx
  
  // 只有行列都在范围内才高亮
  return (inRowRange && inColRange) ? 'selected-cell' : ''
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
    const response = await parseExcelRange(excelId.value, {
      sheet_index: rangeForm.value.sheetIndex,
      start_row: rangeForm.value.startRow,
      end_row: rangeForm.value.endRow,
      start_col: startColIndex,
      end_col: endColIndex
    })
    
    if (response.data.success) {
      // 保存范围选择到sessionStorage（使用统一的键名格式）
      sessionStorage.setItem(`excel_range_${excelId.value}`, JSON.stringify(rangeForm.value))
      
      // 保存分析结果到sessionStorage
      const analysisData = {
        filename: response.data.filename,
        analysis_results: response.data.analysis_results,
        statistics: response.data.statistics
      }
      sessionStorage.setItem(`analysis_${excelId.value}`, JSON.stringify(analysisData))
      
      ElMessage.success('范围解析成功')
      
      // 跳转到设备行识别页面
      router.push({
        name: 'DeviceRowAdjustment',
        params: { excelId: excelId.value }
      })
    }
  } catch (error) {
    ElMessage.error('解析失败: ' + (error.response?.data?.error_message || error.message))
    console.error('解析失败:', error)
  } finally {
    loading.value = false
  }
}

// 跳过范围选择，使用默认范围
async function handleSkipRangeSelection() {
  try {
    // 显示确认对话框
    await ElMessageBox.confirm(
      '将使用默认范围（第一个工作表、全部行列）直接进行解析，是否继续？',
      '跳过范围选择',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    loading.value = true
    
    // 使用默认范围：第一个工作表、全部行列
    const response = await parseExcelRange(excelId.value, {
      sheet_index: 0,
      start_row: 1,
      end_row: null,
      start_col: 1,
      end_col: null
    })
    
    if (response.data.success) {
      // 保存默认范围到sessionStorage
      const defaultRange = {
        sheetIndex: 0,
        startRow: 1,
        endRow: null,
        startCol: 'A',
        endCol: null
      }
      sessionStorage.setItem(`excel_range_${excelId.value}`, JSON.stringify(defaultRange))
      
      // 保存分析结果到sessionStorage
      const analysisData = {
        filename: response.data.filename,
        analysis_results: response.data.analysis_results,
        statistics: response.data.statistics
      }
      sessionStorage.setItem(`analysis_${excelId.value}`, JSON.stringify(analysisData))
      
      ElMessage.success('使用默认范围解析成功')
      
      // 跳转到设备行识别页面
      router.push({
        name: 'DeviceRowAdjustment',
        params: { excelId: excelId.value }
      })
    }
  } catch (error) {
    // 用户取消操作
    if (error === 'cancel') {
      return
    }
    
    ElMessage.error('解析失败: ' + (error.response?.data?.error_message || error.message))
    console.error('解析失败:', error)
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
  min-height: 100vh;
  background-color: #f5f7fa;
}

.selection-card {
  max-width: 1200px;
  margin: 0 auto;
}

.error-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: 500;
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

/* 高亮选中的行列交叉区域 */
:deep(.selected-cell) {
  background-color: #ffeb3b !important;  /* 黄色 - 交叉区域 */
  font-weight: 500;
  transition: background-color 0.3s ease, font-weight 0.2s ease;
}

/* 确保 hover 时高亮样式不会消失 */
:deep(.el-table__row:hover > td.selected-cell) {
  background-color: #ffeb3b !important;
}

/* 表格淡入动画 */
.fade-enter-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 骨架屏样式 */
.preview-skeleton {
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
  min-height: 400px;
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  font-weight: 600;
}

/* 表格行过渡效果 */
:deep(.el-table__row) {
  transition: background-color 0.3s ease;
}

/* 表格单元格过渡效果 */
:deep(.el-table__cell) {
  transition: background-color 0.3s ease;
}
</style>
