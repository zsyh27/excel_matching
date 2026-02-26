<template>
  <div class="rule-editor">
    <el-card v-loading="loading">
      <!-- 设备基本信息 -->
      <div class="device-info-section">
        <h3>设备信息</h3>
        <el-descriptions v-if="ruleData" :column="2" border>
          <el-descriptions-item label="设备ID">{{ ruleData.device_info.device_id }}</el-descriptions-item>
          <el-descriptions-item label="规则ID">{{ ruleData.rule_id }}</el-descriptions-item>
          <el-descriptions-item label="品牌">{{ ruleData.device_info.brand }}</el-descriptions-item>
          <el-descriptions-item label="设备名称">{{ ruleData.device_info.device_name }}</el-descriptions-item>
          <el-descriptions-item label="规格型号" :span="2">{{ ruleData.device_info.spec_model }}</el-descriptions-item>
          <el-descriptions-item label="详细参数" :span="2">{{ ruleData.device_info.detailed_params }}</el-descriptions-item>
          <el-descriptions-item label="单价">¥{{ ruleData.device_info.unit_price }}</el-descriptions-item>
          <el-descriptions-item label="特征数量">{{ features.length }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 匹配阈值编辑 -->
      <div class="threshold-section">
        <h3>匹配阈值</h3>
        <el-row :gutter="20" align="middle">
          <el-col :span="8">
            <el-input-number
              v-model="matchThreshold"
              :min="0"
              :max="100"
              :step="0.5"
              :precision="1"
              @change="handleThresholdChange"
            />
            <span style="margin-left: 10px; color: #909399">
              当前阈值: {{ matchThreshold }}
            </span>
          </el-col>
          <el-col :span="16">
            <el-alert
              :type="getThresholdAlertType(matchThreshold)"
              :closable="false"
              show-icon
            >
              <template #title>
                {{ getThresholdTip(matchThreshold) }}
              </template>
            </el-alert>
          </el-col>
        </el-row>
      </div>

      <!-- 特征列表和权重编辑 -->
      <div class="features-section">
        <div class="section-header">
          <h3>特征与权重配置</h3>
          <div class="action-buttons">
            <el-button size="small" @click="handleAddFeature">
              <el-icon><Plus /></el-icon>
              添加特征
            </el-button>
            <el-button size="small" @click="showBatchAdjustDialog">
              <el-icon><Operation /></el-icon>
              批量调整
            </el-button>
            <el-button size="small" type="warning" @click="handleReset">
              <el-icon><RefreshLeft /></el-icon>
              重置为默认
            </el-button>
          </div>
        </div>

        <el-table :data="features" stripe style="width: 100%; margin-top: 15px">
          <el-table-column prop="feature" label="特征" min-width="200" />
          <el-table-column label="权重" width="180">
            <template #default="{ row }">
              <el-input-number
                v-model="row.weight"
                :min="0"
                :max="10"
                :step="0.5"
                :precision="1"
                size="small"
                @change="handleWeightChange"
              />
            </template>
          </el-table-column>
          <el-table-column prop="type" label="类型" width="120">
            <template #default="{ row }">
              <el-tag>{{ getFeatureTypeLabel(row.type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row, $index }">
              <el-button
                size="small"
                type="danger"
                link
                @click="handleDeleteFeature($index)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 权重分布图表 -->
      <div class="chart-section">
        <h3>权重分布</h3>
        <div ref="chartContainer" class="chart-container"></div>
      </div>

      <!-- 保存按钮 -->
      <div class="footer-actions">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          保存修改
        </el-button>
      </div>
    </el-card>

    <!-- 添加特征对话框 -->
    <el-dialog
      v-model="addFeatureDialogVisible"
      title="添加新特征"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="newFeature" label-width="80px">
        <el-form-item label="特征名称">
          <el-input v-model="newFeature.feature" placeholder="请输入特征名称" />
        </el-form-item>
        <el-form-item label="权重">
          <el-input-number
            v-model="newFeature.weight"
            :min="0"
            :max="10"
            :step="0.5"
            :precision="1"
          />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="newFeature.type" placeholder="请选择类型">
            <el-option label="品牌" value="brand" />
            <el-option label="设备类型" value="device_type" />
            <el-option label="型号" value="model" />
            <el-option label="参数" value="parameter" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addFeatureDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAddFeature">确定</el-button>
      </template>
    </el-dialog>

    <!-- 批量调整权重对话框 -->
    <el-dialog
      v-model="batchAdjustDialogVisible"
      title="批量调整权重"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="batchAdjust" label-width="100px">
        <el-form-item label="特征类型">
          <el-select v-model="batchAdjust.type" placeholder="请选择特征类型">
            <el-option label="全部" value="all" />
            <el-option label="品牌" value="brand" />
            <el-option label="设备类型" value="device_type" />
            <el-option label="型号" value="model" />
            <el-option label="参数" value="parameter" />
          </el-select>
        </el-form-item>
        <el-form-item label="新权重值">
          <el-input-number
            v-model="batchAdjust.weight"
            :min="0"
            :max="10"
            :step="0.5"
            :precision="1"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchAdjustDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmBatchAdjust">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Operation, RefreshLeft } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '../../api'

const props = defineProps({
  ruleId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['save', 'cancel'])

// 数据状态
const loading = ref(false)
const saving = ref(false)
const ruleData = ref(null)
const matchThreshold = ref(0)
const features = ref([])
const originalData = ref(null) // 保存原始数据用于重置

// 图表
const chartContainer = ref(null)
let chartInstance = null

// 对话框状态
const addFeatureDialogVisible = ref(false)
const batchAdjustDialogVisible = ref(false)

// 新特征表单
const newFeature = reactive({
  feature: '',
  weight: 1.0,
  type: 'parameter'
})

// 批量调整表单
const batchAdjust = reactive({
  type: 'all',
  weight: 1.0
})

// 获取规则详情
const fetchRuleDetail = async () => {
  loading.value = true
  try {
    const response = await api.get(`/rules/management/${props.ruleId}`)
    
    if (response.data.success) {
      ruleData.value = response.data.rule
      matchThreshold.value = response.data.rule.match_threshold
      features.value = [...response.data.rule.features].sort((a, b) => b.weight - a.weight)
      
      // 保存原始数据
      originalData.value = JSON.parse(JSON.stringify({
        match_threshold: matchThreshold.value,
        features: features.value
      }))
      
      // 渲染图表
      await nextTick()
      renderChart()
    } else {
      ElMessage.error(response.data.message || '获取规则详情失败')
    }
  } catch (error) {
    console.error('获取规则详情失败:', error)
    ElMessage.error('获取规则详情失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 阈值变化处理
const handleThresholdChange = () => {
  // 实时更新，无需额外操作
}

// 权重变化处理
const handleWeightChange = () => {
  // 重新排序特征列表
  features.value.sort((a, b) => b.weight - a.weight)
  // 更新图表
  renderChart()
}

// 添加特征
const handleAddFeature = () => {
  newFeature.feature = ''
  newFeature.weight = 1.0
  newFeature.type = 'parameter'
  addFeatureDialogVisible.value = true
}

// 确认添加特征
const confirmAddFeature = () => {
  if (!newFeature.feature.trim()) {
    ElMessage.warning('请输入特征名称')
    return
  }
  
  // 检查是否已存在
  if (features.value.some(f => f.feature === newFeature.feature)) {
    ElMessage.warning('该特征已存在')
    return
  }
  
  features.value.push({
    feature: newFeature.feature,
    weight: newFeature.weight,
    type: newFeature.type
  })
  
  features.value.sort((a, b) => b.weight - a.weight)
  renderChart()
  
  addFeatureDialogVisible.value = false
  ElMessage.success('特征添加成功')
}

// 删除特征
const handleDeleteFeature = (index) => {
  ElMessageBox.confirm('确定要删除该特征吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    features.value.splice(index, 1)
    renderChart()
    ElMessage.success('特征删除成功')
  }).catch(() => {
    // 取消删除
  })
}

// 显示批量调整对话框
const showBatchAdjustDialog = () => {
  batchAdjust.type = 'all'
  batchAdjust.weight = 1.0
  batchAdjustDialogVisible.value = true
}

// 确认批量调整
const confirmBatchAdjust = () => {
  const targetType = batchAdjust.type
  const newWeight = batchAdjust.weight
  
  let count = 0
  features.value.forEach(feature => {
    if (targetType === 'all' || feature.type === targetType) {
      feature.weight = newWeight
      count++
    }
  })
  
  features.value.sort((a, b) => b.weight - a.weight)
  renderChart()
  
  batchAdjustDialogVisible.value = false
  ElMessage.success(`已调整 ${count} 个特征的权重`)
}

// 重置为默认
const handleReset = () => {
  ElMessageBox.confirm('确定要重置为默认配置吗？此操作将丢失所有修改。', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    if (originalData.value) {
      matchThreshold.value = originalData.value.match_threshold
      features.value = JSON.parse(JSON.stringify(originalData.value.features))
      renderChart()
      ElMessage.success('已重置为默认配置')
    }
  }).catch(() => {
    // 取消重置
  })
}

// 保存修改
const handleSave = async () => {
  saving.value = true
  try {
    const requestData = {
      match_threshold: matchThreshold.value,
      features: features.value.map(f => ({
        feature: f.feature,
        weight: f.weight
      }))
    }
    
    const response = await api.put(`/rules/management/${props.ruleId}`, requestData)
    
    if (response.data.success) {
      ElMessage.success('规则保存成功')
      // 更新原始数据
      originalData.value = JSON.parse(JSON.stringify({
        match_threshold: matchThreshold.value,
        features: features.value
      }))
      emit('save')
    } else {
      ElMessage.error(response.data.message || '规则保存失败')
    }
  } catch (error) {
    console.error('规则保存失败:', error)
    ElMessage.error('规则保存失败，请稍后重试')
  } finally {
    saving.value = false
  }
}

// 取消编辑
const handleCancel = () => {
  emit('cancel')
}

// 获取阈值提示类型
const getThresholdAlertType = (threshold) => {
  if (threshold < 3) return 'error'
  if (threshold < 5) return 'warning'
  return 'success'
}

// 获取阈值提示信息
const getThresholdTip = (threshold) => {
  if (threshold < 3) return '阈值过低，可能导致误匹配'
  if (threshold < 5) return '阈值适中，建议根据实际情况调整'
  return '阈值合理，能有效避免误匹配'
}

// 获取特征类型标签
const getFeatureTypeLabel = (type) => {
  const typeMap = {
    brand: '品牌',
    device_type: '设备类型',
    model: '型号',
    parameter: '参数'
  }
  return typeMap[type] || type
}

// 渲染权重分布图表
const renderChart = () => {
  if (!chartContainer.value || features.value.length === 0) return
  
  if (!chartInstance) {
    chartInstance = echarts.init(chartContainer.value)
  }
  
  // 按类型分组统计
  const typeStats = {}
  features.value.forEach(feature => {
    const type = getFeatureTypeLabel(feature.type)
    if (!typeStats[type]) {
      typeStats[type] = { count: 0, totalWeight: 0 }
    }
    typeStats[type].count++
    typeStats[type].totalWeight += feature.weight
  })
  
  const option = {
    title: {
      text: '特征权重分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: features.value.map(f => f.feature),
      axisLabel: {
        interval: 0,
        rotate: 45,
        formatter: (value) => {
          return value.length > 10 ? value.substring(0, 10) + '...' : value
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '权重'
    },
    series: [
      {
        name: '权重',
        type: 'bar',
        data: features.value.map(f => ({
          value: f.weight,
          itemStyle: {
            color: f.weight >= 5 ? '#F56C6C' : f.weight >= 3 ? '#E6A23C' : '#409EFF'
          }
        })),
        label: {
          show: true,
          position: 'top'
        }
      }
    ]
  }
  
  chartInstance.setOption(option)
}

// 监听特征变化，更新图表
watch(features, () => {
  nextTick(() => {
    renderChart()
  })
}, { deep: true })

// 组件挂载时获取数据
onMounted(() => {
  fetchRuleDetail()
  
  // 监听窗口大小变化，调整图表
  window.addEventListener('resize', () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  })
})
</script>

<style scoped>
.rule-editor {
  margin-top: 20px;
}

.device-info-section,
.threshold-section,
.features-section,
.chart-section {
  margin-bottom: 30px;
}

.device-info-section h3,
.threshold-section h3,
.features-section h3,
.chart-section h3 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.chart-container {
  width: 100%;
  height: 400px;
}

.footer-actions {
  margin-top: 30px;
  text-align: right;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}

:deep(.el-input-number) {
  width: 120px;
}

:deep(.el-table) {
  font-size: 14px;
}
</style>
