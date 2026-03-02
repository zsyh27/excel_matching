<template>
  <div class="matching-view">
    <el-card class="matching-card">
      <template #header>
        <div class="card-header">
          <el-button 
            type="default" 
            size="small"
            @click="goBack"
          >
            <el-icon><ArrowLeft /></el-icon>
            返回调整
          </el-button>
          <span>设备匹配与报价</span>
          <ExportButton
            :file-id="excelId"
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

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-icon class="is-loading" :size="40">
          <Loading />
        </el-icon>
        <div class="loading-text">正在匹配设备...</div>
      </div>

      <!-- 结果表格 -->
      <el-table
        v-else-if="hasResults"
        :data="displayRows"
        stripe
        border
        style="width: 100%"
        :row-class-name="getRowClassName"
        max-height="600"
      >
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
          min-width="350"
        >
          <template #default="scope">
            <!-- 使用下拉框展示候选设备 -->
            <el-select
              v-model="scope.row.selected_device_id"
              placeholder="请选择设备"
              filterable
              clearable
              @change="handleDeviceSelect(scope.row)"
              style="width: 100%"
            >
              <!-- 如果有候选设备，显示候选列表 -->
              <el-option
                v-for="candidate in scope.row.candidates || []"
                :key="candidate.device_id"
                :label="candidate.matched_device_text"
                :value="candidate.device_id"
              >
                <div class="device-option">
                  <div class="device-option-main">
                    {{ candidate.brand }} {{ candidate.device_name }}
                    <el-tag v-if="candidate.match_score === scope.row.match_result?.match_score" size="small" type="success" style="margin-left: 8px">最佳</el-tag>
                  </div>
                  <div class="device-option-sub">
                    {{ candidate.spec_model }} | ¥{{ candidate.unit_price.toFixed(2) }} | 得分: {{ candidate.match_score.toFixed(1) }}
                  </div>
                </div>
              </el-option>
              
              <!-- 如果没有候选设备，显示所有设备库 -->
              <template v-if="!scope.row.candidates || scope.row.candidates.length === 0">
                <el-option
                  v-for="device in allDevices"
                  :key="device.device_id"
                  :label="device.display_text"
                  :value="device.device_id"
                >
                  <div class="device-option">
                    <div class="device-option-main">{{ device.brand }} {{ device.device_name }}</div>
                    <div class="device-option-sub">{{ device.spec_model }} | ¥{{ device.unit_price.toFixed(2) }}</div>
                  </div>
                </el-option>
              </template>
            </el-select>
            
            <!-- 匹配状态标签 -->
            <div class="match-info">
              <el-tag v-if="scope.row.match_result?.match_status === 'success'" size="small" type="success">
                匹配成功
              </el-tag>
              <el-tag v-else-if="scope.row.selected_device_id" size="small" type="info">
                手动选择
              </el-tag>
              <el-tag v-else size="small" type="warning">
                待选择
              </el-tag>
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
            <span class="price-text">
              {{ formatPrice(scope.row.unit_price) }}
            </span>
          </template>
        </el-table-column>

        <!-- 操作列 - 新增查看详情按钮 -->
        <el-table-column
          label="操作"
          width="120"
          align="center"
          fixed="right"
        >
          <template #default="scope">
            <el-button
              v-if="scope.row.detail_cache_key"
              type="primary"
              size="small"
              link
              @click="showMatchDetail(scope.row.detail_cache_key)"
            >
              查看详情
            </el-button>
            <span v-else class="no-detail-text">-</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty
        v-else
        description="暂无数据"
        :image-size="150"
      />
    </el-card>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import { ArrowLeft, Loading } from '@element-plus/icons-vue'
import api from '../api/index.js'
import ExportButton from '../components/ExportButton.vue'

const props = defineProps({
  excelId: {
    type: String,
    required: true
  }
})

const router = useRouter()
const route = useRoute()

// 状态管理
const loading = ref(false)
const displayRows = ref([])
const allDevices = ref([])
const originalFilename = ref('')
const statistics = ref({
  total_devices: 0,
  matched: 0,
  unmatched: 0,
  accuracy_rate: 0
})

// 不再需要对话框状态，改用新标签页打开

// 计算属性
const hasResults = computed(() => displayRows.value.length > 0)

/**
 * 组件挂载时加载数据
 */
onMounted(async () => {
  await loadDevices()
  
  // 从路由状态获取设备行数据
  const deviceRows = history.state?.deviceRows
  
  if (deviceRows && deviceRows.length > 0) {
    // 使用传递的最终设备行数据进行匹配
    await matchDevices(deviceRows)
  } else {
    ElMessage.warning('未找到设备行数据，请重新上传文件')
    router.push({ name: 'FileUpload' })
  }
})

/**
 * 返回调整页面
 */
const goBack = () => {
  router.push({
    name: 'DeviceRowAdjustment',
    params: { excelId: props.excelId }
  })
}

/**
 * 加载所有设备列表
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
 */
const matchDevices = async (deviceRows) => {
  try {
    loading.value = true

    // 将设备行数据转换为匹配接口需要的格式
    const rows = deviceRows.map(deviceRow => ({
      row_number: deviceRow.row_number,
      raw_data: deviceRow.row_content,
      row_type: 'device'
    }))

    const response = await api.post('/match', { rows })
    
    if (!response.data.success) {
      throw new Error(response.data.error_message || '匹配失败')
    }

    // 更新显示数据
    displayRows.value = response.data.matched_rows.map(row => ({
      ...row,
      // 初始化 selected_device_id：如果匹配成功，使用匹配的设备ID；否则为 null
      selected_device_id: row.match_result?.match_status === 'success' 
        ? row.match_result.device_id 
        : null,
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
  } finally {
    loading.value = false
  }
}

/**
 * 处理设备选择（包括候选设备和手动选择）
 */
const handleDeviceSelect = (row) => {
  if (!row.selected_device_id) {
    // 清除选择
    row.unit_price = 0.00
    if (row.match_result) {
      row.match_result.device_id = null
      row.match_result.matched_device_text = null
      row.match_result.unit_price = 0.00
      row.match_result.match_status = 'failed'
    }
    updateStatistics()
    return
  }

  // 查找选中的设备（先从候选列表查找，再从所有设备查找）
  let selectedDevice = null
  
  // 1. 从候选列表查找
  if (row.candidates && row.candidates.length > 0) {
    selectedDevice = row.candidates.find(c => c.device_id === row.selected_device_id)
    if (selectedDevice) {
      // 使用候选设备的信息
      row.unit_price = selectedDevice.unit_price

      if (!row.match_result) {
        row.match_result = {}
      }
      
      row.match_result.device_id = selectedDevice.device_id
      row.match_result.matched_device_text = selectedDevice.matched_device_text
      row.match_result.unit_price = selectedDevice.unit_price
      row.match_result.match_status = 'success'
      row.match_result.match_score = selectedDevice.match_score
      row.match_result.match_reason = selectedDevice.match_score === row.candidates[0]?.match_score 
        ? '自动匹配（最佳）' 
        : `用户选择（得分: ${selectedDevice.match_score.toFixed(1)}）`

      updateStatistics()
      
      ElMessage.success(`已选择: ${selectedDevice.brand} ${selectedDevice.device_name}`)
      return
    }
  }
  
  // 2. 从所有设备库查找（手动选择）
  selectedDevice = allDevices.value.find(d => d.device_id === row.selected_device_id)
  
  if (selectedDevice) {
    row.unit_price = selectedDevice.unit_price

    if (!row.match_result) {
      row.match_result = {}
    }
    
    row.match_result.device_id = selectedDevice.device_id
    row.match_result.matched_device_text = selectedDevice.display_text
    row.match_result.unit_price = selectedDevice.unit_price
    row.match_result.match_status = 'success'
    row.match_result.match_score = 0
    row.match_result.match_reason = '手动选择'

    updateStatistics()

    ElMessage.success(`已选择设备: ${selectedDevice.brand} ${selectedDevice.device_name}`)
  }
}

/**
 * 更新统计信息
 */
const updateStatistics = () => {
  const matched = displayRows.value.filter(row => 
    row.match_result && row.match_result.match_status === 'success'
  ).length
  
  statistics.value = {
    total_devices: displayRows.value.length,
    matched: matched,
    unmatched: displayRows.value.length - matched,
    accuracy_rate: displayRows.value.length > 0 
      ? Math.round((matched / displayRows.value.length) * 100 * 100) / 100 
      : 0
  }
}

/**
 * 格式化价格
 */
const formatPrice = (price) => {
  if (price === null || price === undefined) {
    return '0.00'
  }
  return Number(price).toFixed(2)
}

/**
 * 获取行的 CSS 类名
 */
const getRowClassName = ({ row }) => {
  if (!row.match_result || row.match_result.match_status === 'failed') {
    return 'unmatched-row'
  }
  return ''
}

/**
 * 显示匹配详情 - 在新标签页打开
 */
const showMatchDetail = (cacheKey) => {
  if (!cacheKey) {
    ElMessage.warning('该设备没有详情信息')
    return
  }
  
  // 在新标签页打开匹配详情页面
  const routeData = router.resolve({
    name: 'MatchDetail',
    params: { cacheKey: cacheKey }
  })
  window.open(routeData.href, '_blank')
}

/**
 * 导出成功处理
 */
const handleExportSuccess = (data) => {
  console.log('导出成功:', data)
}

/**
 * 导出错误处理
 */
const handleExportError = (error) => {
  console.error('导出错误:', error)
}
</script>

<style scoped>
.matching-view {
  width: 100%;
  padding: 20px;
}

.matching-card {
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

/* 统计面板样式 */
.statistics-panel {
  margin-bottom: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  border-radius: 6px;
  transition: transform 0.2s;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-item.success {
  background: linear-gradient(135deg, #f0f9ff 0%, #c6f6d5 100%);
  border: 2px solid #67c23a;
}

.stat-item.warning {
  background: linear-gradient(135deg, #fff9c4 0%, #ffe082 100%);
  border: 2px solid #e6a23c;
}

.stat-item.info {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border: 2px solid #409eff;
}

.stat-item:not(.success):not(.warning):not(.info) {
  background: rgba(255, 255, 255, 0.95);
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
.matching-view :deep(.el-table) {
  font-size: 14px;
}

.matching-view :deep(.unmatched-row) {
  background-color: #fdf6ec;
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
  display: flex;
  align-items: center;
}

.device-option-sub {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

/* 匹配信息样式 */
.match-info {
  margin-top: 5px;
}

/* 操作列样式 */
.no-detail-text {
  color: #c0c4cc;
  font-size: 14px;
}
</style>
