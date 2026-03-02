<template>
  <div class="result-table-container">
    <el-card class="result-card">
      <template #header>
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

      <!-- 匹配统计信息 -->
      <div v-if="hasResults" class="statistics-panel">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stat-item">
              <div class="stat-label">总设备数</div>
              <div class="stat-value">{{ statistics.total_devices }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item success">
              <div class="stat-label">匹配成功</div>
              <div class="stat-value">{{ statistics.matched }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item warning">
              <div class="stat-label">匹配失败</div>
              <div class="stat-value">{{ statistics.unmatched }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-item info">
              <div class="stat-label">准确率</div>
              <div class="stat-value">{{ statistics.accuracy_rate }}%</div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 批量操作工具栏 -->
      <div v-if="hasResults && selectedRows.length > 0" class="batch-toolbar">
        <span class="batch-info">已选择 {{ selectedRows.length }} 个设备</span>
        <el-button
          type="primary"
          size="small"
          @click="handleBatchViewDetail"
        >
          批量查看详情
        </el-button>
        <el-button
          size="small"
          @click="clearSelection"
        >
          取消选择
        </el-button>
      </div>

      <!-- 结果表格 -->
      <el-table
        v-if="hasResults"
        ref="resultTableRef"
        :data="displayRows"
        stripe
        border
        style="width: 100%"
        :row-class-name="getRowClassName"
        max-height="600"
        @selection-change="handleSelectionChange"
      >
        <!-- 复选框列 -->
        <el-table-column
          type="selection"
          width="55"
          align="center"
          :selectable="isRowSelectable"
        />

        <!-- 原始行号 -->
        <el-table-column
          prop="row_number"
          label="行号"
          width="80"
          align="center"
        />

        <!-- 设备描述 -->
        <el-table-column
          prop="device_description"
          label="设备描述"
          min-width="200"
          show-overflow-tooltip
        />

        <!-- 匹配设备 -->
        <el-table-column
          label="匹配设备"
          min-width="300"
        >
          <template #default="scope">
            <!-- 非设备行 -->
            <span v-if="scope.row.row_type !== 'device'" class="non-device-text">
              {{ scope.row.row_type === 'header' ? '表头' : 
                 scope.row.row_type === 'summary' ? '合计' : '备注' }}
            </span>

            <!-- 匹配成功 -->
            <div v-else-if="scope.row.match_result && scope.row.match_result.match_status === 'success'">
              <div class="matched-device-text">
                {{ scope.row.match_result.matched_device_text }}
              </div>
              <div class="match-info">
                <el-tag size="small" type="success">
                  匹配成功 (得分: {{ scope.row.match_result.match_score }})
                </el-tag>
              </div>
            </div>

            <!-- 匹配失败 - 显示下拉选择器 -->
            <div v-else>
              <el-select
                v-model="scope.row.selected_device_id"
                placeholder="待人工匹配"
                filterable
                clearable
                @change="handleManualSelect(scope.row)"
                style="width: 100%"
              >
                <el-option
                  v-for="device in allDevices"
                  :key="device.device_id"
                  :label="device.display_text"
                  :value="device.device_id"
                >
                  <div class="device-option">
                    <div class="device-option-main">{{ device.brand }} {{ device.device_name }}</div>
                    <div class="device-option-sub">{{ device.spec_model }}</div>
                  </div>
                </el-option>
              </el-select>
              <div v-if="!scope.row.selected_device_id" class="match-info">
                <el-tag size="small" type="warning">
                  待人工匹配
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- 单价 -->
        <el-table-column
          label="单价"
          width="120"
          align="right"
        >
          <template #default="scope">
            <span v-if="scope.row.row_type !== 'device'" class="non-device-text">-</span>
            <span v-else class="price-text">
              {{ formatPrice(scope.row.unit_price) }}
            </span>
          </template>
        </el-table-column>

        <!-- 操作 -->
        <el-table-column
          label="操作"
          width="120"
          align="center"
          fixed="right"
        >
          <template #default="scope">
            <el-button
              v-if="scope.row.row_type === 'device' && scope.row.detail_cache_key"
              type="primary"
              size="small"
              link
              @click="handleViewDetail(scope.row)"
            >
              查看详情
            </el-button>
            <span v-else class="non-device-text">-</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty
        v-else
        description="暂无数据，请先上传并解析 Excel 文件"
        :image-size="150"
      />
    </el-card>

    <!-- 批量查看详情对话框 -->
    <BatchMatchDetailView
      v-model="showBatchDetailView"
      :device-items="batchCacheKeys"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import api from '../api/index.js'
import ExportButton from './ExportButton.vue'
import BatchMatchDetailView from './MatchDetail/BatchMatchDetailView.vue'

const router = useRouter()

// 定义 props
const props = defineProps({
  fileId: {
    type: String,
    default: null
  },
  parseResult: {
    type: Object,
    default: null
  },
  originalFilename: {
    type: String,
    default: ''
  }
})

// 定义 emits
const emit = defineEmits(['export-success'])

// 状态管理
const displayRows = ref([])
const allDevices = ref([])
const statistics = ref({
  total_devices: 0,
  matched: 0,
  unmatched: 0,
  accuracy_rate: 0
})

// 批量选择状态
const selectedRows = ref([])
const resultTableRef = ref(null)

// 批量查看详情状态
const showBatchDetailView = ref(false)
const batchCacheKeys = ref([])

// 计算属性
const hasResults = computed(() => displayRows.value.length > 0)

/**
 * 监听 parseResult 变化，自动触发匹配
 * 验证需求: 5.1, 9.3
 */
watch(() => props.parseResult, async (newVal) => {
  if (newVal && newVal.rows) {
    await loadDevices()
    await matchDevices(newVal.rows)
  }
}, { immediate: true })

/**
 * 加载所有设备列表
 * 验证需求: 5.4
 */
const loadDevices = async () => {
  try {
    const response = await api.get('/devices')
    if (response.data.success) {
      allDevices.value = response.data.devices
    }
  } catch (error) {
    ElMessage.error('加载设备列表失败')
    console.error('加载设备列表失败:', error)
  }
}

/**
 * 调用匹配接口
 * 验证需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 9.3
 */
const matchDevices = async (rows) => {
  try {
    const response = await api.post('/match', { rows })
    
    if (!response.data.success) {
      throw new Error(response.data.error_message || '匹配失败')
    }

    // 更新显示数据
    displayRows.value = response.data.matched_rows.map(row => ({
      ...row,
      selected_device_id: null,
      unit_price: row.match_result?.unit_price || 0.00
    }))

    // 更新统计信息
    statistics.value = response.data.statistics

    // 显示匹配完成通知
    ElNotification({
      title: '匹配完成',
      message: response.data.message || `成功匹配 ${statistics.value.matched} 个设备`,
      type: statistics.value.unmatched > 0 ? 'warning' : 'success',
      duration: 3000
    })

  } catch (error) {
    ElMessage.error('设备匹配失败')
    console.error('设备匹配失败:', error)
  }
}

/**
 * 手动选择设备后的处理
 * 验证需求: 5.5, 5.6
 */
const handleManualSelect = (row) => {
  if (!row.selected_device_id) {
    // 清除选择
    row.unit_price = 0.00
    if (row.match_result) {
      row.match_result.device_id = null
      row.match_result.matched_device_text = null
      row.match_result.unit_price = 0.00
      row.match_result.match_status = 'failed'
    }
    return
  }

  // 查找选中的设备
  const selectedDevice = allDevices.value.find(d => d.device_id === row.selected_device_id)
  
  if (selectedDevice) {
    // 更新单价
    row.unit_price = selectedDevice.unit_price

    // 更新匹配结果
    if (!row.match_result) {
      row.match_result = {}
    }
    
    row.match_result.device_id = selectedDevice.device_id
    row.match_result.matched_device_text = selectedDevice.display_text
    row.match_result.unit_price = selectedDevice.unit_price
    row.match_result.match_status = 'success'
    row.match_result.match_score = 0
    row.match_result.match_reason = '人工选择'

    // 更新统计信息
    updateStatistics()

    ElMessage.success(`已选择设备: ${selectedDevice.brand} ${selectedDevice.device_name}`)
  }
}

/**
 * 更新统计信息
 */
const updateStatistics = () => {
  const deviceRows = displayRows.value.filter(row => row.row_type === 'device')
  const matched = deviceRows.filter(row => 
    row.match_result && row.match_result.match_status === 'success'
  ).length
  
  statistics.value = {
    total_devices: deviceRows.length,
    matched: matched,
    unmatched: deviceRows.length - matched,
    accuracy_rate: deviceRows.length > 0 
      ? Math.round((matched / deviceRows.length) * 100 * 100) / 100 
      : 0
  }
}

/**
 * 格式化价格
 * 验证需求: 5.7, 6.7
 */
const formatPrice = (price) => {
  if (price === null || price === undefined) {
    return '0.00'
  }
  return Number(price).toFixed(2)
}

/**
 * 获取行的 CSS 类名
 * 验证需求: 5.3
 */
const getRowClassName = ({ row }) => {
  if (row.row_type !== 'device') {
    return 'non-device-row'
  }
  
  if (!row.match_result || row.match_result.match_status === 'failed') {
    return 'unmatched-row'
  }
  
  return ''
}

/**
 * 导出成功处理
 * 验证需求: 9.4, 9.5
 */
const handleExportSuccess = (data) => {
  console.log('导出成功:', data)
  emit('export-success', data)
}

/**
 * 导出错误处理
 * 验证需求: 9.5
 */
const handleExportError = (error) => {
  console.error('导出错误:', error)
}

/**
 * 重置组件状态（供父组件调用）
 */
const reset = () => {
  displayRows.value = []
  statistics.value = {
    total_devices: 0,
    matched: 0,
    unmatched: 0,
    accuracy_rate: 0
  }
}

/**
 * 查看匹配详情
 * 在新标签页打开
 * 验证需求: Requirements 1.1, 1.2
 */
const handleViewDetail = (row) => {
  if (!row.detail_cache_key) {
    ElMessage.warning('该设备没有详情信息')
    return
  }
  
  // 在新标签页打开匹配详情页面
  const routeData = router.resolve({
    name: 'MatchDetail',
    params: { cacheKey: row.detail_cache_key }
  })
  window.open(routeData.href, '_blank')
}

/**
 * 判断行是否可选择
 * 只有设备行且有详情缓存键的行才可选择
 * 验证需求: Requirements 10.1
 */
const isRowSelectable = (row) => {
  return row.row_type === 'device' && !!row.detail_cache_key
}

/**
 * 处理表格选择变化
 * 验证需求: Requirements 10.1
 */
const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

/**
 * 清除选择
 * 验证需求: Requirements 10.1
 */
const clearSelection = () => {
  if (resultTableRef.value) {
    resultTableRef.value.clearSelection()
  }
  selectedRows.value = []
}

/**
 * 批量查看详情
 * 验证需求: Requirements 10.1, 10.2
 */
const handleBatchViewDetail = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要查看的设备')
    return
  }
  
  // 收集所有选中行的缓存键
  batchCacheKeys.value = selectedRows.value
    .filter(row => row.detail_cache_key)
    .map(row => ({
      cacheKey: row.detail_cache_key,
      rowNumber: row.row_number,
      deviceDescription: row.device_description,
      matchResult: row.match_result
    }))
  
  if (batchCacheKeys.value.length === 0) {
    ElMessage.warning('选中的设备没有详情信息')
    return
  }
  
  showBatchDetailView.value = true
}

// 暴露方法给父组件
defineExpose({
  reset
})
</script>

<style scoped>
.result-table-container {
  width: 100%;
  margin-top: 20px;
}

.result-card {
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

/* 统计面板样式 */
.statistics-panel {
  margin-bottom: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
}

/* 批量操作工具栏样式 */
.batch-toolbar {
  margin-bottom: 15px;
  padding: 12px 16px;
  background: #ecf5ff;
  border: 1px solid #b3d8ff;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.batch-info {
  font-size: 14px;
  color: #409eff;
  font-weight: 500;
  flex: 1;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 6px;
  transition: transform 0.2s;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-item.success {
  border-left: 4px solid #67c23a;
}

.stat-item.warning {
  border-left: 4px solid #e6a23c;
}

.stat-item.info {
  border-left: 4px solid #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

/* 表格样式 */
.result-table-container :deep(.el-table) {
  font-size: 14px;
}

.result-table-container :deep(.non-device-row) {
  background-color: #f5f7fa;
}

.result-table-container :deep(.unmatched-row) {
  background-color: #fdf6ec;
}

.non-device-text {
  color: #909399;
  font-style: italic;
}

.matched-device-text {
  color: #303133;
  line-height: 1.6;
  margin-bottom: 5px;
}

.match-info {
  margin-top: 5px;
}

.price-text {
  font-weight: bold;
  color: #f56c6c;
  font-size: 15px;
}

/* 设备选择器样式 */
.device-option {
  padding: 5px 0;
}

.device-option-main {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.device-option-sub {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

/* 空状态样式 */
.result-table-container :deep(.el-empty) {
  padding: 60px 0;
}
</style>
