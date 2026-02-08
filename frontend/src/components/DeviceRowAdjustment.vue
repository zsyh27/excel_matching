<template>
  <div class="device-row-adjustment">
    <el-card class="adjustment-card">
      <template #header>
        <div class="card-header">
          <span>设备行智能识别与调整</span>
          <el-tag type="info" size="large">
            文件: {{ filename }}
          </el-tag>
        </div>
      </template>

      <!-- 工具栏 -->
      <div class="toolbar">
        <el-row :gutter="10">
          <el-col :span="6">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索行号或内容"
              clearable
              @input="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>

          <el-col :span="5">
            <el-select
              v-model="filterLevel"
              placeholder="筛选概率等级"
              clearable
              @change="handleFilter"
              style="width: 100%"
            >
              <el-option label="高概率设备行" value="high" />
              <el-option label="中概率可疑行" value="medium" />
              <el-option label="低概率无关行" value="low" />
            </el-select>
          </el-col>

          <el-col :span="13" class="button-group">
            <el-button
              type="primary"
              :disabled="selectedRows.length === 0"
              @click="batchMarkAsDevice"
            >
              批量标记为设备行 ({{ selectedRows.length }})
            </el-button>

            <el-button
              type="warning"
              :disabled="selectedRows.length === 0"
              @click="batchUnmarkAsDevice"
            >
              批量取消设备行 ({{ selectedRows.length }})
            </el-button>

            <el-button
              type="success"
              @click="confirmAndProceed"
            >
              确认调整并进入匹配
            </el-button>
          </el-col>
        </el-row>
      </div>

      <!-- 统计信息 -->
      <div class="statistics-bar">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stat-item">
              <span class="stat-label">总行数:</span>
              <span class="stat-value">{{ allRows.length }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item high">
              <span class="stat-label">高概率:</span>
              <span class="stat-value">{{ statistics.high_probability }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item medium">
              <span class="stat-label">中概率:</span>
              <span class="stat-value">{{ statistics.medium_probability }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item low">
              <span class="stat-label">低概率:</span>
              <span class="stat-value">{{ statistics.low_probability }}</span>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-icon class="is-loading" :size="40">
          <Loading />
        </el-icon>
        <div class="loading-text">正在加载分析结果...</div>
      </div>

      <!-- 数据表格 -->
      <el-table
        v-else-if="filteredRows.length > 0"
        :data="filteredRows"
        @selection-change="handleSelectionChange"
        :row-class-name="getRowClassName"
        stripe
        border
        max-height="600"
        style="width: 100%"
      >
        <el-table-column type="selection" width="55" />

        <el-table-column prop="row_number" label="行号" width="80" align="center" />

        <el-table-column label="概率等级" width="140" align="center">
          <template #default="{ row }">
            <el-tag :type="getProbabilityTagType(row)">
              {{ getProbabilityLabel(row) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="total_score" label="得分" width="80" align="center">
          <template #default="{ row }">
            {{ row.total_score.toFixed(1) }}
          </template>
        </el-table-column>

        <el-table-column label="行内容" min-width="400">
          <template #default="{ row }">
            <el-tooltip
              :content="getFullRowContent(row.row_content)"
              placement="top"
              :disabled="getFullRowContent(row.row_content).length <= 150"
            >
              <div class="row-content">
                {{ formatRowContent(row.row_content) }}
              </div>
            </el-tooltip>
          </template>
        </el-table-column>

        <el-table-column label="判定依据" min-width="300" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.reasoning }}
          </template>
        </el-table-column>

        <el-table-column label="手动调整" width="200" align="center">
          <template #default="{ row }">
            <el-select
              v-model="row.manual_action"
              placeholder="选择操作"
              size="small"
              @change="handleManualAdjust(row)"
              style="width: 100%"
            >
              <el-option label="标记为设备行" value="mark_as_device" />
              <el-option label="取消设备行" value="unmark_as_device" />
              <el-option label="恢复自动判断" value="restore_auto" />
            </el-select>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty
        v-else
        description="没有符合条件的数据"
        :image-size="150"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import { Search, Loading } from '@element-plus/icons-vue'
import api from '../api/index.js'

// 定义 props
const props = defineProps({
  excelId: {
    type: String,
    required: true
  }
})

// 定义 emits
const emit = defineEmits(['proceed-to-matching'])

// 状态管理
const loading = ref(false)
const filename = ref('')
const allRows = ref([])
const filteredRows = ref([])
const selectedRows = ref([])
const searchKeyword = ref('')
const filterLevel = ref(null)
const statistics = ref({
  high_probability: 0,
  medium_probability: 0,
  low_probability: 0
})

/**
 * 组件挂载时加载分析结果
 */
onMounted(async () => {
  await loadAnalysisResults()
})

/**
 * 从缓存加载分析结果
 */
const loadAnalysisResults = async () => {
  try {
    loading.value = true
    
    // 调用后端接口获取缓存的分析结果
    // 注意：这里假设后端提供了一个获取缓存分析结果的接口
    // 如果没有，我们需要在上传成功后将结果存储到 sessionStorage
    
    // 先尝试从 sessionStorage 获取
    const cachedData = sessionStorage.getItem(`analysis_${props.excelId}`)
    
    if (cachedData) {
      const data = JSON.parse(cachedData)
      filename.value = data.filename || ''
      allRows.value = data.analysis_results.map(row => ({
        ...row,
        manual_action: null,
        is_manually_adjusted: false,
        manual_decision: null
      }))
      filteredRows.value = [...allRows.value]
      statistics.value = data.statistics || {
        high_probability: 0,
        medium_probability: 0,
        low_probability: 0
      }
    } else {
      ElMessage.warning('未找到分析结果，请重新上传文件')
    }
    
  } catch (error) {
    ElMessage.error('加载分析结果失败')
    console.error('加载分析结果失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 更新统计信息
 */
const updateStatistics = () => {
  statistics.value = {
    high_probability: allRows.value.filter(r => 
      r.is_manually_adjusted 
        ? r.manual_decision === true 
        : r.probability_level === 'high'
    ).length,
    medium_probability: allRows.value.filter(r => 
      !r.is_manually_adjusted && r.probability_level === 'medium'
    ).length,
    low_probability: allRows.value.filter(r => 
      r.is_manually_adjusted 
        ? r.manual_decision === false 
        : r.probability_level === 'low'
    ).length
  }
}

/**
 * 获取行的 CSS 类名
 * 验证需求: 9.1, 9.2, 9.3, 9.4, 9.5
 */
const getRowClassName = ({ row }) => {
  // 手动调整优先
  if (row.is_manually_adjusted) {
    return row.manual_decision ? 'row-manual-device' : 'row-manual-non-device'
  }

  // 自动判断
  switch (row.probability_level) {
    case 'high':
      return 'row-high-probability'
    case 'medium':
      return 'row-medium-probability'
    case 'low':
      return 'row-low-probability'
    default:
      return ''
  }
}

/**
 * 获取概率等级标签类型
 * 验证需求: 9.1, 9.2, 9.3, 9.4, 9.5
 */
const getProbabilityTagType = (row) => {
  if (row.is_manually_adjusted) {
    return row.manual_decision ? 'success' : 'danger'
  }

  switch (row.probability_level) {
    case 'high':
      return 'primary'
    case 'medium':
      return 'warning'
    case 'low':
      return 'info'
    default:
      return ''
  }
}

/**
 * 获取概率等级标签文本
 * 验证需求: 9.1, 9.2, 9.3, 9.4, 9.5
 */
const getProbabilityLabel = (row) => {
  if (row.is_manually_adjusted) {
    return row.manual_decision ? '手动-设备行' : '手动-非设备'
  }

  switch (row.probability_level) {
    case 'high':
      return '高概率'
    case 'medium':
      return '中概率'
    case 'low':
      return '低概率'
    default:
      return '未知'
  }
}

/**
 * 格式化行内容显示（限制长度）
 */
const formatRowContent = (content) => {
  if (!content || !Array.isArray(content)) {
    return ''
  }
  
  // 过滤空单元格并合并
  const filteredContent = content.filter(cell => cell && cell.trim())
  const fullText = filteredContent.join(' | ')
  
  // 如果内容过长，只显示前150个字符
  const maxLength = 150
  if (fullText.length > maxLength) {
    return fullText.substring(0, maxLength) + '...'
  }
  
  return fullText
}

/**
 * 获取完整的行内容（不截断，用于Tooltip）
 */
const getFullRowContent = (content) => {
  if (!content || !Array.isArray(content)) {
    return ''
  }
  
  // 过滤空单元格并合并
  const filteredContent = content.filter(cell => cell && cell.trim())
  return filteredContent.join(' | ')
}

/**
 * 处理单行手动调整
 * 验证需求: 10.1, 10.2, 10.3, 10.4, 10.5
 */
const handleManualAdjust = async (row) => {
  if (!row.manual_action) {
    return
  }

  try {
    // 调用API保存手动调整
    const response = await api.post('/excel/manual-adjust', {
      excel_id: props.excelId,
      adjustments: [{
        row_number: row.row_number,
        action: row.manual_action
      }]
    })

    if (!response.data.success) {
      throw new Error(response.data.error || '调整失败')
    }

    // 更新本地状态
    if (row.manual_action === 'restore_auto') {
      row.is_manually_adjusted = false
      row.manual_decision = null
      row.manual_action = null
    } else {
      row.is_manually_adjusted = true
      row.manual_decision = row.manual_action === 'mark_as_device'
    }

    // 更新统计信息
    updateStatistics()

    ElMessage.success('调整已保存')

  } catch (error) {
    ElMessage.error(`调整失败: ${error.message}`)
    console.error('手动调整失败:', error)
  }
}

/**
 * 处理表格选择变化
 * 验证需求: 11.1
 */
const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

/**
 * 批量标记为设备行
 * 验证需求: 11.2, 11.3, 11.5
 */
const batchMarkAsDevice = async () => {
  if (selectedRows.value.length === 0) {
    return
  }

  try {
    const adjustments = selectedRows.value.map(row => ({
      row_number: row.row_number,
      action: 'mark_as_device'
    }))

    const response = await api.post('/excel/manual-adjust', {
      excel_id: props.excelId,
      adjustments
    })

    if (!response.data.success) {
      throw new Error(response.data.error || '批量调整失败')
    }

    // 更新本地状态
    selectedRows.value.forEach(row => {
      row.is_manually_adjusted = true
      row.manual_decision = true
      row.manual_action = 'mark_as_device'
    })

    // 更新统计信息
    updateStatistics()

    ElMessage.success(`已标记 ${adjustments.length} 行为设备行`)

  } catch (error) {
    ElMessage.error(`批量调整失败: ${error.message}`)
    console.error('批量标记失败:', error)
  }
}

/**
 * 批量取消设备行
 * 验证需求: 11.2, 11.4, 11.5
 */
const batchUnmarkAsDevice = async () => {
  if (selectedRows.value.length === 0) {
    return
  }

  try {
    const adjustments = selectedRows.value.map(row => ({
      row_number: row.row_number,
      action: 'unmark_as_device'
    }))

    const response = await api.post('/excel/manual-adjust', {
      excel_id: props.excelId,
      adjustments
    })

    if (!response.data.success) {
      throw new Error(response.data.error || '批量调整失败')
    }

    // 更新本地状态
    selectedRows.value.forEach(row => {
      row.is_manually_adjusted = true
      row.manual_decision = false
      row.manual_action = 'unmark_as_device'
    })

    // 更新统计信息
    updateStatistics()

    ElMessage.success(`已取消 ${adjustments.length} 行的设备行标记`)

  } catch (error) {
    ElMessage.error(`批量调整失败: ${error.message}`)
    console.error('批量取消失败:', error)
  }
}

/**
 * 处理搜索
 * 验证需求: 12.1, 12.2
 */
const handleSearch = () => {
  applyFilters()
}

/**
 * 处理筛选
 * 验证需求: 12.3
 */
const handleFilter = () => {
  applyFilters()
}

/**
 * 应用筛选条件
 * 验证需求: 12.1, 12.2, 12.3, 12.4, 12.5
 */
const applyFilters = () => {
  let result = [...allRows.value]

  // 按关键词筛选（行号或内容）
  if (searchKeyword.value && searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.trim().toLowerCase()
    result = result.filter(row => {
      // 搜索行号
      if (row.row_number.toString().includes(keyword)) {
        return true
      }
      // 搜索行内容
      const content = formatRowContent(row.row_content).toLowerCase()
      return content.includes(keyword)
    })
  }

  // 按概率等级筛选
  if (filterLevel.value) {
    result = result.filter(row => {
      if (row.is_manually_adjusted) {
        // 手动调整的行不参与概率筛选
        return false
      }
      return row.probability_level === filterLevel.value
    })
  }

  filteredRows.value = result
}

/**
 * 确认调整并进入匹配流程
 * 验证需求: 14.4
 */
const confirmAndProceed = async () => {
  try {
    // 确认对话框
    await ElMessageBox.confirm(
      '确认当前的调整结果并进入设备匹配流程？',
      '确认操作',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    // 调用API获取最终设备行
    const response = await api.get('/excel/final-device-rows', {
      params: { excel_id: props.excelId }
    })

    if (!response.data.success) {
      throw new Error(response.data.error || '获取最终设备行失败')
    }

    const finalData = response.data

    // 显示统计信息
    ElNotification({
      title: '设备行确认完成',
      message: `共识别 ${finalData.statistics.total_device_rows} 个设备行（自动: ${finalData.statistics.auto_identified}，手动: ${finalData.statistics.manually_adjusted}）`,
      type: 'success',
      duration: 3000
    })

    // 触发事件，传递数据到匹配流程
    emit('proceed-to-matching', {
      excelId: props.excelId,
      deviceRows: finalData.device_rows,
      statistics: finalData.statistics
    })

  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`操作失败: ${error.message || error}`)
      console.error('确认并进入匹配失败:', error)
    }
  }
}

/**
 * 重置组件状态（供父组件调用）
 */
const reset = () => {
  allRows.value = []
  filteredRows.value = []
  selectedRows.value = []
  searchKeyword.value = ''
  filterLevel.value = null
  statistics.value = {
    high_probability: 0,
    medium_probability: 0,
    low_probability: 0
  }
}

// 暴露方法给父组件
defineExpose({
  reset
})
</script>

<style scoped>
.device-row-adjustment {
  width: 100%;
  margin-top: 20px;
}

.adjustment-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

/* 工具栏样式 */
.toolbar {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.button-group {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 加载状态样式 */
.loading-container {
  text-align: center;
  padding: 60px 0;
}

.loading-text {
  margin-top: 20px;
  font-size: 16px;
  color: #606266;
}

/* 统计信息栏样式 */
.statistics-bar {
  margin-bottom: 20px;
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
}

.stat-item {
  text-align: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 6px;
}

.stat-item.high {
  border-left: 4px solid #409eff;
}

.stat-item.medium {
  border-left: 4px solid #e6a23c;
}

.stat-item.low {
  border-left: 4px solid #909399;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-right: 5px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

/* 表格行样式 - 自动判断 */
.device-row-adjustment :deep(.row-high-probability) {
  background-color: #e3f2fd !important;  /* 浅蓝色 */
}

.device-row-adjustment :deep(.row-medium-probability) {
  background-color: #fff9c4 !important;  /* 浅黄色 */
}

.device-row-adjustment :deep(.row-low-probability) {
  background-color: #f5f5f5 !important;  /* 浅灰色 */
}

/* 表格行样式 - 手动调整 */
.device-row-adjustment :deep(.row-manual-device) {
  background-color: #c8e6c9 !important;  /* 深绿色 */
  font-weight: 500;
}

.device-row-adjustment :deep(.row-manual-non-device) {
  background-color: #ffcdd2 !important;  /* 深红色 */
}

/* 行内容样式 */
.row-content {
  line-height: 1.6;
  word-break: break-word;
}

/* 表格样式优化 */
.device-row-adjustment :deep(.el-table) {
  font-size: 14px;
}

.device-row-adjustment :deep(.el-table th) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 600;
}

.device-row-adjustment :deep(.el-table td) {
  padding: 12px 0;
}
</style>
