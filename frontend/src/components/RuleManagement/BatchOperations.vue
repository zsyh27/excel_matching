<template>
  <div class="batch-operations">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>批量操作</span>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 按特征类型批量调整权重 -->
        <el-tab-pane label="调整权重" name="weight">
          <el-form :model="weightForm" label-width="120px" class="operation-form">
            <el-form-item label="特征类型">
              <el-select v-model="weightForm.feature_type" placeholder="请选择特征类型">
                <el-option label="品牌" value="brand" />
                <el-option label="设备类型" value="device_type" />
                <el-option label="型号" value="model" />
                <el-option label="参数" value="parameter" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="新权重值">
              <el-input-number
                v-model="weightForm.new_weight"
                :min="0"
                :max="10"
                :step="0.5"
                :precision="1"
              />
            </el-form-item>
            
            <el-form-item label="应用范围">
              <el-radio-group v-model="weightForm.scope">
                <el-radio label="all">所有规则</el-radio>
                <el-radio label="selected">选中的规则</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item v-if="weightForm.scope === 'selected'" label="规则ID列表">
              <el-input
                v-model="weightForm.rule_ids_text"
                type="textarea"
                :rows="3"
                placeholder="输入规则ID，用逗号分隔，例如：R_SENSOR001,R_SENSOR002"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="applyWeightAdjustment" :loading="loading">
                <el-icon><Check /></el-icon>
                应用调整
              </el-button>
              <el-button @click="resetWeightForm">
                <el-icon><Refresh /></el-icon>
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 按设备类型批量调整阈值 -->
        <el-tab-pane label="调整阈值" name="threshold">
          <el-form :model="thresholdForm" label-width="120px" class="operation-form">
            <el-form-item label="设备类型">
              <el-input
                v-model="thresholdForm.device_type"
                placeholder="输入设备类型关键词，例如：传感器、控制器"
              />
            </el-form-item>
            
            <el-form-item label="新阈值">
              <el-input-number
                v-model="thresholdForm.new_threshold"
                :min="0"
                :max="20"
                :step="0.5"
                :precision="1"
              />
            </el-form-item>
            
            <el-form-item label="应用范围">
              <el-radio-group v-model="thresholdForm.scope">
                <el-radio label="all">所有规则</el-radio>
                <el-radio label="selected">选中的规则</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item v-if="thresholdForm.scope === 'selected'" label="规则ID列表">
              <el-input
                v-model="thresholdForm.rule_ids_text"
                type="textarea"
                :rows="3"
                placeholder="输入规则ID，用逗号分隔"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="applyThresholdAdjustment" :loading="loading">
                <el-icon><Check /></el-icon>
                应用调整
              </el-button>
              <el-button @click="resetThresholdForm">
                <el-icon><Refresh /></el-icon>
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 批量重置规则 -->
        <el-tab-pane label="重置规则" name="reset">
          <el-form :model="resetForm" label-width="120px" class="operation-form">
            <el-alert
              title="警告"
              type="warning"
              description="重置操作将恢复规则到自动生成的初始状态，此操作不可撤销！"
              :closable="false"
              show-icon
              class="warning-alert"
            />
            
            <el-form-item label="重置范围">
              <el-radio-group v-model="resetForm.scope">
                <el-radio label="all">所有规则</el-radio>
                <el-radio label="selected">选中的规则</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item v-if="resetForm.scope === 'selected'" label="规则ID列表">
              <el-input
                v-model="resetForm.rule_ids_text"
                type="textarea"
                :rows="3"
                placeholder="输入规则ID，用逗号分隔"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="danger" @click="applyReset" :loading="loading">
                <el-icon><Delete /></el-icon>
                重置规则
              </el-button>
              <el-button @click="resetResetForm">
                <el-icon><Refresh /></el-icon>
                取消
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 操作结果 -->
    <el-card v-if="operationResult" class="result-card">
      <template #header>
        <div class="card-header">
          <span>操作结果</span>
        </div>
      </template>
      
      <el-result
        :icon="operationResult.success ? 'success' : 'error'"
        :title="operationResult.success ? '操作成功' : '操作失败'"
      >
        <template #sub-title>
          <div class="result-details">
            <p v-if="operationResult.success">
              成功更新 {{ operationResult.affected_count }} 条规则
            </p>
            <p v-else>
              {{ operationResult.message }}
            </p>
          </div>
        </template>
        <template #extra>
          <el-button type="primary" @click="operationResult = null">确定</el-button>
        </template>
      </el-result>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Refresh, Delete } from '@element-plus/icons-vue'
import api from '@/api'

const activeTab = ref('weight')
const loading = ref(false)
const operationResult = ref(null)

const weightForm = reactive({
  feature_type: 'parameter',
  new_weight: 1.0,
  scope: 'all',
  rule_ids_text: ''
})

const thresholdForm = reactive({
  device_type: '',
  new_threshold: 5.0,
  scope: 'all',
  rule_ids_text: ''
})

const resetForm = reactive({
  scope: 'selected',
  rule_ids_text: ''
})

const parseRuleIds = (text) => {
  if (!text || !text.trim()) return []
  return text.split(',').map(id => id.trim()).filter(id => id)
}

const applyWeightAdjustment = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要将所有${weightForm.feature_type === 'brand' ? '品牌' : 
        weightForm.feature_type === 'device_type' ? '设备类型' : 
        weightForm.feature_type === 'model' ? '型号' : '参数'}特征的权重调整为 ${weightForm.new_weight} 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    operationResult.value = null
    
    const rule_ids = weightForm.scope === 'selected' ? parseRuleIds(weightForm.rule_ids_text) : []
    
    const response = await api.post('/rules/management/batch-update', {
      operation: 'update_weights_by_type',
      feature_type: weightForm.feature_type,
      new_weight: weightForm.new_weight,
      rule_ids: rule_ids
    })
    
    if (response.data.success) {
      operationResult.value = {
        success: true,
        affected_count: response.data.updated_count || 0
      }
      ElMessage.success('权重调整成功')
    } else {
      operationResult.value = {
        success: false,
        message: response.data.message || '操作失败'
      }
      ElMessage.error(response.data.message || '权重调整失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('权重调整失败:', error)
      operationResult.value = {
        success: false,
        message: error.response?.data?.message || error.message
      }
      ElMessage.error('权重调整失败: ' + (error.response?.data?.message || error.message))
    }
  } finally {
    loading.value = false
  }
}

const applyThresholdAdjustment = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要将阈值调整为 ${thresholdForm.new_threshold} 吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    operationResult.value = null
    
    const rule_ids = thresholdForm.scope === 'selected' ? parseRuleIds(thresholdForm.rule_ids_text) : []
    
    const response = await api.post('/rules/management/batch-update', {
      operation: 'update_threshold',
      device_type: thresholdForm.device_type,
      new_threshold: thresholdForm.new_threshold,
      rule_ids: rule_ids
    })
    
    if (response.data.success) {
      operationResult.value = {
        success: true,
        affected_count: response.data.updated_count || 0
      }
      ElMessage.success('阈值调整成功')
    } else {
      operationResult.value = {
        success: false,
        message: response.data.message || '操作失败'
      }
      ElMessage.error(response.data.message || '阈值调整失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('阈值调整失败:', error)
      operationResult.value = {
        success: false,
        message: error.response?.data?.message || error.message
      }
      ElMessage.error('阈值调整失败: ' + (error.response?.data?.message || error.message))
    }
  } finally {
    loading.value = false
  }
}

const applyReset = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置规则吗？此操作将恢复规则到自动生成的初始状态，不可撤销！',
      '警告',
      {
        confirmButtonText: '确定重置',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    
    loading.value = true
    operationResult.value = null
    
    const rule_ids = resetForm.scope === 'selected' ? parseRuleIds(resetForm.rule_ids_text) : []
    
    if (resetForm.scope === 'selected' && rule_ids.length === 0) {
      ElMessage.warning('请输入要重置的规则ID')
      loading.value = false
      return
    }
    
    const response = await api.post('/rules/management/batch-update', {
      operation: 'reset_rules',
      rule_ids: rule_ids
    })
    
    if (response.data.success) {
      operationResult.value = {
        success: true,
        affected_count: response.data.updated_count || 0
      }
      ElMessage.success('规则重置成功')
    } else {
      operationResult.value = {
        success: false,
        message: response.data.message || '操作失败'
      }
      ElMessage.error(response.data.message || '规则重置失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('规则重置失败:', error)
      operationResult.value = {
        success: false,
        message: error.response?.data?.message || error.message
      }
      ElMessage.error('规则重置失败: ' + (error.response?.data?.message || error.message))
    }
  } finally {
    loading.value = false
  }
}

const resetWeightForm = () => {
  weightForm.feature_type = 'parameter'
  weightForm.new_weight = 1.0
  weightForm.scope = 'all'
  weightForm.rule_ids_text = ''
}

const resetThresholdForm = () => {
  thresholdForm.device_type = ''
  thresholdForm.new_threshold = 5.0
  thresholdForm.scope = 'all'
  thresholdForm.rule_ids_text = ''
}

const resetResetForm = () => {
  resetForm.scope = 'selected'
  resetForm.rule_ids_text = ''
}
</script>

<style scoped>
.batch-operations {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.operation-form {
  max-width: 600px;
  margin-top: 20px;
}

.warning-alert {
  margin-bottom: 20px;
}

.result-card {
  margin-top: 20px;
}

.result-details {
  text-align: center;
  padding: 20px;
  font-size: 16px;
}
</style>
