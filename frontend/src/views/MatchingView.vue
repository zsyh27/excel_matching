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
          min-width="300"
        >
          <template #default="scope">
            <!-- 匹配成功 -->
            <div v-if="scope.row.match_result && scope.row.match_result.match_status === 'success'">
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
            <span class="price-text">
              {{ formatPrice(scope.row.unit_price) }}
            </span>
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
  } finally {
    loading.value = false
  }
}

/**
 * 手动选择设备后的处理
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
}

.device-option-sub {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}
</style>
