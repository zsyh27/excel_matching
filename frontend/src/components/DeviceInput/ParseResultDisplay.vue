<template>
  <div class="parse-result-display">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>{{ isEditMode ? '编辑解析结果' : '解析结果' }}</span>
          <el-tag :type="confidenceType" size="large">
            置信度: {{ confidencePercentage }}%
          </el-tag>
        </div>
      </template>

      <!-- 基本信息 - 显示模式 -->
      <div v-if="!isEditMode" class="basic-info">
        <h4 class="section-title">基本信息</h4>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="品牌" label-class-name="label-cell">
            <span v-if="parseResult.brand" class="value-text">
              {{ parseResult.brand }}
            </span>
            <el-tag v-else type="info" size="small">未识别</el-tag>
          </el-descriptions-item>
          
          <el-descriptions-item label="设备类型" label-class-name="label-cell">
            <span v-if="parseResult.device_type" class="value-text">
              {{ parseResult.device_type }}
            </span>
            <el-tag v-else type="info" size="small">未识别</el-tag>
          </el-descriptions-item>
          
          <el-descriptions-item label="型号" label-class-name="label-cell">
            <span v-if="parseResult.model" class="value-text">
              {{ parseResult.model }}
            </span>
            <el-tag v-else type="info" size="small">未识别</el-tag>
          </el-descriptions-item>
          
          <el-descriptions-item v-if="showPrice" label="价格" label-class-name="label-cell">
            <span class="value-text price-text">
              ¥{{ formattedPrice }}
            </span>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 基本信息 - 编辑模式 -->
      <div v-else class="basic-info-edit">
        <h4 class="section-title">基本信息</h4>
        <el-form :model="editForm" label-width="100px" label-position="left">
          <el-form-item label="品牌">
            <el-select
              v-model="editForm.brand"
              placeholder="请选择品牌"
              clearable
              filterable
              style="width: 100%"
            >
              <el-option
                v-for="brand in brandOptions"
                :key="brand"
                :label="brand"
                :value="brand"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="设备类型">
            <el-select
              v-model="editForm.device_type"
              placeholder="请选择设备类型"
              clearable
              filterable
              style="width: 100%"
              @change="handleDeviceTypeChange"
            >
              <el-option
                v-for="type in deviceTypeOptions"
                :key="type"
                :label="type"
                :value="type"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="型号">
            <el-input
              v-model="editForm.model"
              placeholder="请输入型号"
              clearable
            />
          </el-form-item>

          <el-form-item v-if="showPrice" label="价格">
            <span class="value-text price-text">
              ¥{{ formattedPrice }}
            </span>
          </el-form-item>
        </el-form>
      </div>

      <!-- 关键参数 - 显示模式 -->
      <div v-if="!isEditMode && hasKeyParams" class="key-params">
        <h4 class="section-title">
          <el-icon><Setting /></el-icon>
          关键参数
        </h4>
        <el-descriptions :column="1" border>
          <el-descriptions-item
            v-for="(value, key) in parseResult.key_params"
            :key="key"
            :label="key"
            label-class-name="label-cell"
          >
            <span class="value-text">{{ value }}</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 关键参数 - 编辑模式 -->
      <div v-if="isEditMode" class="key-params-edit">
        <h4 class="section-title">
          <el-icon><Setting /></el-icon>
          关键参数
        </h4>
        <el-form :model="editForm" label-width="100px" label-position="left">
          <el-form-item
            v-for="(value, key) in editForm.key_params"
            :key="key"
            :label="key"
          >
            <div class="param-edit-row">
              <el-input
                v-model="editForm.key_params[key]"
                :placeholder="`请输入${key}`"
                clearable
              />
              <el-button
                type="danger"
                :icon="Delete"
                circle
                size="small"
                @click="removeParam(key)"
              />
            </div>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              :icon="Plus"
              @click="showAddParamDialog = true"
            >
              添加参数
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 未识别内容 -->
      <div v-if="hasUnrecognizedText" class="unrecognized-text">
        <h4 class="section-title">
          <el-icon><Warning /></el-icon>
          未识别内容
        </h4>
        <div class="unrecognized-tags">
          <el-tag
            v-for="(text, index) in parseResult.unrecognized_text"
            :key="index"
            type="info"
            class="unrecognized-tag"
            effect="plain"
          >
            {{ text }}
          </el-tag>
        </div>
        <p class="unrecognized-hint">
          以上内容未能被系统识别，您可以在编辑时手动处理
        </p>
      </div>

      <!-- 置信度说明 -->
      <div class="confidence-info">
        <el-alert
          :type="confidenceAlertType"
          :closable="false"
          show-icon
        >
          <template #title>
            <span class="confidence-title">{{ confidenceMessage }}</span>
          </template>
        </el-alert>
      </div>

      <!-- 操作按钮 - 显示模式 -->
      <div v-if="!isEditMode" class="result-actions">
        <el-button
          type="primary"
          size="large"
          :disabled="loading"
          @click="handleConfirm"
        >
          <el-icon><Check /></el-icon>
          确认保存
        </el-button>
        <el-button
          size="large"
          :disabled="loading"
          @click="handleEdit"
        >
          <el-icon><Edit /></el-icon>
          编辑修正
        </el-button>
        <el-button
          size="large"
          :disabled="loading"
          @click="handleReparse"
        >
          <el-icon><RefreshRight /></el-icon>
          重新解析
        </el-button>
      </div>

      <!-- 操作按钮 - 编辑模式 -->
      <div v-else class="result-actions">
        <el-button
          type="primary"
          size="large"
          :disabled="loading"
          @click="handleSaveEdit"
        >
          <el-icon><Check /></el-icon>
          保存修改
        </el-button>
        <el-button
          size="large"
          :disabled="loading"
          @click="handleCancelEdit"
        >
          <el-icon><Close /></el-icon>
          取消
        </el-button>
        <el-button
          size="large"
          :disabled="loading"
          @click="handleReparse"
        >
          <el-icon><RefreshRight /></el-icon>
          重新解析
        </el-button>
      </div>
    </el-card>

    <!-- 添加参数对话框 -->
    <el-dialog
      v-model="showAddParamDialog"
      title="添加参数"
      width="400px"
    >
      <el-form :model="newParam" label-width="80px">
        <el-form-item label="参数名称">
          <el-input
            v-model="newParam.name"
            placeholder="请输入参数名称"
            clearable
          />
        </el-form-item>
        <el-form-item label="参数值">
          <el-input
            v-model="newParam.value"
            placeholder="请输入参数值"
            clearable
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddParamDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddParam">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { Check, Edit, RefreshRight, Setting, Warning, Close, Delete, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps({
  parseResult: {
    type: Object,
    required: true,
    validator: (value) => {
      return (
        typeof value === 'object' &&
        'confidence_score' in value
      )
    }
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['confirm', 'edit', 'reparse', 'update'])

// 编辑模式状态
const isEditMode = ref(false)
const showAddParamDialog = ref(false)

// 编辑表单数据
const editForm = ref({
  brand: null,
  device_type: null,
  model: null,
  key_params: {}
})

// 新参数数据
const newParam = ref({
  name: '',
  value: ''
})

// 品牌选项（从配置文件中获取）
const brandOptions = [
  '西门子',
  '霍尼韦尔',
  '施耐德',
  '江森自控',
  '贝尔莫',
  '丹佛斯',
  '艾默生',
  'ABB',
  '欧姆龙',
  '三菱',
  '富士',
  '台达',
  '海林',
  '和利时'
]

// 设备类型选项（从配置文件中获取）
const deviceTypeOptions = [
  'CO2传感器',
  '座阀',
  '温度传感器',
  '压力传感器',
  '执行器',
  '湿度传感器',
  '流量传感器',
  '液位传感器',
  '电动阀',
  '变频器',
  '控制器',
  '风机盘管',
  '水泵',
  '差压传感器',
  '电磁阀'
]

// 初始化编辑表单
const initEditForm = () => {
  editForm.value = {
    brand: props.parseResult.brand,
    device_type: props.parseResult.device_type,
    model: props.parseResult.model,
    key_params: { ...(props.parseResult.key_params || {}) }
  }
}

// 监听 parseResult 变化，重置编辑模式
watch(() => props.parseResult, () => {
  isEditMode.value = false
  initEditForm()
}, { deep: true })

// Computed properties
const confidencePercentage = computed(() => {
  return (props.parseResult.confidence_score * 100).toFixed(0)
})

const confidenceType = computed(() => {
  const score = props.parseResult.confidence_score
  if (score >= 0.8) return 'success'
  if (score >= 0.6) return 'warning'
  return 'danger'
})

const confidenceAlertType = computed(() => {
  const score = props.parseResult.confidence_score
  if (score >= 0.8) return 'success'
  if (score >= 0.6) return 'warning'
  return 'error'
})

const confidenceMessage = computed(() => {
  const score = props.parseResult.confidence_score
  if (score >= 0.8) {
    return '解析置信度高，建议直接保存'
  } else if (score >= 0.6) {
    return '解析置信度中等，建议检查后保存'
  } else {
    return '解析置信度较低，建议仔细检查或重新解析'
  }
})

const hasKeyParams = computed(() => {
  return (
    props.parseResult.key_params &&
    Object.keys(props.parseResult.key_params).length > 0
  )
})

const hasUnrecognizedText = computed(() => {
  return (
    props.parseResult.unrecognized_text &&
    props.parseResult.unrecognized_text.length > 0
  )
})

const showPrice = computed(() => {
  return props.parseResult.price !== null && props.parseResult.price !== undefined
})

const formattedPrice = computed(() => {
  if (!showPrice.value) return '0.00'
  return props.parseResult.price.toFixed(2)
})

// Methods
const handleConfirm = () => {
  emit('confirm', props.parseResult)
}

const handleEdit = () => {
  initEditForm()
  isEditMode.value = true
  emit('edit', props.parseResult)
}

const handleReparse = () => {
  isEditMode.value = false
  emit('reparse')
}

const handleSaveEdit = () => {
  // 验证必填字段
  if (!editForm.value.brand && !editForm.value.device_type && !editForm.value.model) {
    ElMessage.warning('请至少填写品牌、设备类型或型号中的一项')
    return
  }

  // 创建更新后的解析结果
  const updatedResult = {
    ...props.parseResult,
    brand: editForm.value.brand,
    device_type: editForm.value.device_type,
    model: editForm.value.model,
    key_params: { ...editForm.value.key_params }
  }

  isEditMode.value = false
  emit('update', updatedResult)
  ElMessage.success('修改已保存')
}

const handleCancelEdit = () => {
  isEditMode.value = false
  initEditForm()
}

const handleDeviceTypeChange = (newType) => {
  // 当设备类型改变时，可以选择清空关键参数或保留
  // 这里选择保留，让用户手动调整
  console.log('设备类型已更改为:', newType)
}

const removeParam = (paramKey) => {
  delete editForm.value.key_params[paramKey]
}

const handleAddParam = () => {
  if (!newParam.value.name || !newParam.value.value) {
    ElMessage.warning('请输入参数名称和参数值')
    return
  }

  if (editForm.value.key_params[newParam.value.name]) {
    ElMessage.warning('该参数已存在')
    return
  }

  editForm.value.key_params[newParam.value.name] = newParam.value.value
  
  // 重置新参数表单
  newParam.value = {
    name: '',
    value: ''
  }
  
  showAddParamDialog.value = false
  ElMessage.success('参数已添加')
}

// 初始化
initEditForm()
</script>

<style scoped>
.parse-result-display {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: bold;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 6px;
}

.basic-info,
.basic-info-edit {
  margin-bottom: 20px;
}

.key-params,
.key-params-edit,
.unrecognized-text {
  margin-top: 20px;
  margin-bottom: 20px;
}

.value-text {
  color: #303133;
  font-weight: 500;
}

.price-text {
  color: #F56C6C;
  font-size: 16px;
  font-weight: bold;
}

.param-edit-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.param-edit-row .el-input {
  flex: 1;
}

.unrecognized-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.unrecognized-tag {
  font-size: 13px;
}

.unrecognized-hint {
  margin: 8px 0 0 0;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

.confidence-info {
  margin: 20px 0;
}

.confidence-title {
  font-size: 14px;
  font-weight: 500;
}

.result-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.result-actions .el-button {
  display: flex;
  align-items: center;
  gap: 6px;
}

:deep(.label-cell) {
  font-weight: 600;
  background-color: #fafafa;
}

:deep(.el-descriptions__label) {
  width: 120px;
}

@media (max-width: 768px) {
  .result-actions {
    flex-direction: column;
  }

  .result-actions .el-button {
    width: 100%;
    justify-content: center;
  }

  :deep(.el-descriptions__label) {
    width: 100px;
  }
}
</style>
