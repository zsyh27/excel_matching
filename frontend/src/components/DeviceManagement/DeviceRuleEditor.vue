<template>
  <el-dialog
    v-model="visible"
    title="编辑规则"
    width="700px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-loading="loading" class="rule-editor">
      <el-alert
        title="权重配置说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <div style="font-size: 13px; line-height: 1.8">
          <p style="margin: 0 0 8px 0">调整特征权重以优化匹配效果。当前权重策略：</p>
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px">
            <div>• 设备类型: <strong>{{ weightConfig.device_type_weight }}</strong></div>
            <div>• 关键参数: <strong>{{ weightConfig.key_params_weight }}</strong></div>
            <div>• 品牌: <strong>{{ weightConfig.brand_weight }}</strong></div>
            <div>• 型号: <strong>{{ weightConfig.model_weight }}</strong></div>
            <div>• 普通参数: <strong>{{ weightConfig.parameter_weight }}</strong></div>
          </div>
          <p style="margin: 8px 0 0 0; color: #909399; font-size: 12px">
            提示：选择特征类型后，权重会自动设置为标准值，您也可以手动调整
          </p>
        </div>
      </el-alert>

      <!-- 规则摘要 -->
      <div class="rule-summary">
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="匹配阈值">
            <el-input-number
              v-model="editForm.match_threshold"
              :min="0"
              :max="50"
              :step="0.5"
              :precision="1"
              size="small"
            />
          </el-descriptions-item>
          <el-descriptions-item label="当前总权重">
            <el-tag type="primary">{{ totalWeight }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="特征数量">
            {{ editForm.features.length }}
          </el-descriptions-item>
        </el-descriptions>
        <div style="margin-top: 8px; font-size: 12px; color: #909399">
          注意：实际总权重由后端根据特征类型和配置策略计算，此处显示的是特征权重之和，仅供参考
        </div>
      </div>

      <!-- 特征列表 -->
      <div class="features-section">
        <div class="section-header">
          <h4>特征列表</h4>
          <el-button size="small" type="primary" @click="handleAddFeature">
            添加特征
          </el-button>
        </div>

        <el-table :data="editForm.features" stripe>
          <el-table-column prop="feature" label="特征" min-width="150">
            <template #default="{ row, $index }">
              <el-input
                v-model="row.feature"
                placeholder="输入特征"
                size="small"
                @input="validateFeature($index)"
              />
            </template>
          </el-table-column>
          
          <el-table-column prop="type" label="类型" width="140">
            <template #default="{ row }">
              <el-select 
                v-model="row.type" 
                placeholder="选择类型" 
                size="small"
                @change="onFeatureTypeChange(row)"
              >
                <el-option label="品牌" value="brand" />
                <el-option label="设备类型" value="device_type" />
                <el-option label="设备名称" value="device_name" />
                <el-option label="型号" value="model" />
                <el-option label="参数" value="parameter" />
              </el-select>
              <div style="font-size: 11px; color: #909399; margin-top: 2px">
                {{ getWeightHint(row.type) }}
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="weight" label="权重" width="220">
            <template #default="{ row }">
              <div class="weight-editor">
                <el-slider
                  v-model="row.weight"
                  :min="0"
                  :max="25"
                  :step="0.5"
                  :show-tooltip="false"
                  style="width: 100px"
                />
                <el-input-number
                  v-model="row.weight"
                  :min="0"
                  :max="25"
                  :step="0.5"
                  :precision="1"
                  size="small"
                  style="width: 90px"
                />
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="80" align="center">
            <template #default="{ $index }">
              <el-button
                size="small"
                type="danger"
                :icon="Delete"
                circle
                @click="handleDeleteFeature($index)"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 预估匹配效果 -->
      <div class="match-preview">
        <h4>预估匹配效果</h4>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="匹配难度">
            <el-tag :type="getMatchDifficultyType()">
              {{ getMatchDifficultyLabel() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="建议">
            {{ getMatchSuggestion() }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSave" :loading="saving">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { updateDeviceRule } from '../../api/database'
import { getConfig } from '../../api/config'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  deviceId: {
    type: String,
    required: true
  },
  rule: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'saved'])

const visible = ref(props.modelValue)
const loading = ref(false)
const saving = ref(false)

// 权重配置
const weightConfig = ref({
  device_type_weight: 20.0,
  key_params_weight: 15.0,
  brand_weight: 10.0,
  model_weight: 5.0,
  parameter_weight: 1.0
})

const editForm = ref({
  features: [],
  match_threshold: 5.0
})

// 监听 modelValue 变化
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    initForm()
    loadWeightConfig()
  }
})

// 监听 visible 变化
watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 加载权重配置
const loadWeightConfig = async () => {
  try {
    const response = await getConfig()
    if (response.data.success && response.data.config) {
      const config = response.data.config
      if (config.feature_weight_config) {
        weightConfig.value = {
          device_type_weight: config.feature_weight_config.device_type_weight || 20.0,
          key_params_weight: config.feature_weight_config.key_params_weight || 15.0,
          brand_weight: config.feature_weight_config.brand_weight || 10.0,
          model_weight: config.feature_weight_config.model_weight || 5.0,
          parameter_weight: config.feature_weight_config.parameter_weight || 1.0
        }
      }
    }
  } catch (error) {
    console.error('加载权重配置失败:', error)
  }
}

// 初始化表单
const initForm = () => {
  if (props.rule) {
    editForm.value = {
      features: JSON.parse(JSON.stringify(props.rule.features || [])),
      match_threshold: props.rule.match_threshold || 5.0
    }
  } else {
    editForm.value = {
      features: [],
      match_threshold: 5.0
    }
  }
}

// 计算总权重（简单相加，仅供参考）
const totalWeight = computed(() => {
  return editForm.value.features.reduce((sum, f) => sum + (f.weight || 0), 0).toFixed(1)
})

// 获取特征类型的标准权重
const getStandardWeight = (type) => {
  const weightMap = {
    'device_type': weightConfig.value.device_type_weight,
    'device_name': weightConfig.value.device_type_weight,
    'brand': weightConfig.value.brand_weight,
    'model': weightConfig.value.model_weight,
    'parameter': weightConfig.value.parameter_weight
  }
  return weightMap[type] || weightConfig.value.parameter_weight
}

// 获取特征类型的权重说明
const getWeightHint = (type) => {
  const hintMap = {
    'device_type': `标准权重: ${weightConfig.value.device_type_weight} (设备类型)`,
    'device_name': `标准权重: ${weightConfig.value.device_type_weight} (设备名称)`,
    'brand': `标准权重: ${weightConfig.value.brand_weight} (品牌)`,
    'model': `标准权重: ${weightConfig.value.model_weight} (型号)`,
    'parameter': `标准权重: ${weightConfig.value.parameter_weight} (参数)`
  }
  return hintMap[type] || `标准权重: ${weightConfig.value.parameter_weight}`
}

// 添加特征
const handleAddFeature = () => {
  editForm.value.features.push({
    feature: '',
    type: 'parameter',
    weight: weightConfig.value.parameter_weight
  })
}

// 删除特征
const handleDeleteFeature = (index) => {
  editForm.value.features.splice(index, 1)
}

// 验证特征
const validateFeature = (index) => {
  // 可以添加特征验证逻辑
}

// 当特征类型改变时，自动调整权重为标准权重
const onFeatureTypeChange = (feature) => {
  feature.weight = getStandardWeight(feature.type)
}

// 获取匹配难度类型
const getMatchDifficultyType = () => {
  const ratio = editForm.value.match_threshold / totalWeight.value
  if (ratio < 0.3) return 'success'
  if (ratio < 0.5) return 'warning'
  return 'danger'
}

// 获取匹配难度标签
const getMatchDifficultyLabel = () => {
  const ratio = editForm.value.match_threshold / totalWeight.value
  if (ratio < 0.3) return '容易'
  if (ratio < 0.5) return '中等'
  return '困难'
}

// 获取匹配建议
const getMatchSuggestion = () => {
  const ratio = editForm.value.match_threshold / totalWeight.value
  if (ratio < 0.3) {
    return '阈值较低，匹配较容易，但可能出现误匹配'
  } else if (ratio < 0.5) {
    return '阈值适中，匹配效果较好'
  } else {
    return '阈值较高，匹配较严格，可能导致匹配失败'
  }
}

// 保存规则
const handleSave = async () => {
  // 验证
  if (editForm.value.features.length === 0) {
    ElMessage.warning('请至少添加一个特征')
    return
  }

  for (let i = 0; i < editForm.value.features.length; i++) {
    const feature = editForm.value.features[i]
    if (!feature.feature || !feature.feature.trim()) {
      ElMessage.warning(`第 ${i + 1} 个特征不能为空`)
      return
    }
    if (!feature.type) {
      ElMessage.warning(`第 ${i + 1} 个特征必须选择类型`)
      return
    }
  }

  saving.value = true
  try {
    const response = await updateDeviceRule(props.deviceId, {
      features: editForm.value.features,
      match_threshold: editForm.value.match_threshold
    })

    if (response.data.success) {
      emit('saved', response.data.rule)
    } else {
      ElMessage.error(response.data.message || '保存失败')
    }
  } catch (error) {
    console.error('保存规则失败:', error)
    ElMessage.error('保存规则失败，请稍后重试')
  } finally {
    saving.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}

// 组件挂载时加载权重配置
onMounted(() => {
  loadWeightConfig()
})
</script>

<style scoped>
.rule-editor {
  padding: 10px 0;
}

.rule-summary {
  margin-bottom: 20px;
}

.features-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.section-header h4 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.weight-editor {
  display: flex;
  align-items: center;
  gap: 10px;
}

.match-preview h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #303133;
}
</style>
