<template>
  <div class="device-input-form">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>设备录入</span>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        label-position="left"
      >
        <!-- 设备描述输入区域 -->
        <el-form-item label="设备描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="6"
            placeholder="请输入设备的参数说明文本，例如：西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA"
            :disabled="loading"
            @input="handleDescriptionChange"
          />
          <div class="input-hint">
            支持自由文本输入，系统将自动识别品牌、设备类型、型号和关键参数
          </div>
        </el-form-item>

        <!-- 价格输入框 -->
        <el-form-item label="价格" prop="price">
          <el-input
            v-model.number="formData.price"
            type="number"
            placeholder="请输入设备价格"
            :disabled="loading"
            :min="0"
            step="0.01"
          >
            <template #append>元</template>
          </el-input>
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <div class="button-group">
            <el-button
              type="primary"
              :loading="loading"
              :disabled="!canParse"
              @click="handleSmartParse"
            >
              <el-icon v-if="!loading"><MagicStick /></el-icon>
              智能解析
            </el-button>
            <el-button
              type="default"
              :disabled="loading"
              @click="handleManualFill"
            >
              <el-icon><Edit /></el-icon>
              手动填写
            </el-button>
            <el-button
              :disabled="loading"
              @click="handleReset"
            >
              <el-icon><RefreshLeft /></el-icon>
              重置
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick, Edit, RefreshLeft } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  // 初始数据（用于编辑场景）
  initialData: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['parse', 'manual-fill', 'reset'])

// Refs
const formRef = ref(null)
const loading = ref(false)

// Form data
const formData = ref({
  description: props.initialData.description || '',
  price: props.initialData.price || null
})

// Validation rules
const rules = {
  description: [
    {
      required: true,
      message: '请输入设备描述',
      trigger: 'blur'
    },
    {
      min: 5,
      message: '设备描述至少需要5个字符',
      trigger: 'blur'
    },
    {
      validator: (rule, value, callback) => {
        if (value && value.trim().length === 0) {
          callback(new Error('设备描述不能只包含空白字符'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  price: [
    {
      type: 'number',
      message: '价格必须是数字',
      trigger: 'blur'
    },
    {
      validator: (rule, value, callback) => {
        if (value !== null && value !== undefined && value < 0) {
          callback(new Error('价格不能为负数'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// Computed
const canParse = computed(() => {
  return formData.value.description && 
         formData.value.description.trim().length >= 5 &&
         !loading.value
})

// Watch for initial data changes
watch(() => props.initialData, (newData) => {
  if (newData) {
    formData.value.description = newData.description || ''
    formData.value.price = newData.price || null
  }
}, { deep: true })

// Methods
const handleDescriptionChange = () => {
  // 清除描述字段的验证错误
  if (formRef.value) {
    formRef.value.clearValidate('description')
  }
}

const handleSmartParse = async () => {
  // 验证表单
  try {
    await formRef.value.validate()
  } catch (error) {
    ElMessage.warning('请检查表单输入')
    return
  }

  // 触发解析事件
  emit('parse', {
    description: formData.value.description.trim(),
    price: formData.value.price
  })
}

const handleManualFill = () => {
  // 验证描述字段（手动填写时描述是可选的）
  emit('manual-fill', {
    description: formData.value.description?.trim() || '',
    price: formData.value.price
  })
}

const handleReset = () => {
  // 重置表单
  formRef.value.resetFields()
  formData.value = {
    description: '',
    price: null
  }
  emit('reset')
}

// 暴露方法给父组件
const setLoading = (value) => {
  loading.value = value
}

const resetForm = () => {
  handleReset()
}

const getFormData = () => {
  return {
    description: formData.value.description?.trim() || '',
    price: formData.value.price
  }
}

defineExpose({
  setLoading,
  resetForm,
  getFormData
})
</script>

<style scoped>
.device-input-form {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.input-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}

.button-group {
  display: flex;
  gap: 12px;
}

.button-group .el-button {
  display: flex;
  align-items: center;
  gap: 4px;
}

:deep(.el-textarea__inner) {
  font-family: 'Microsoft YaHei', Arial, sans-serif;
  line-height: 1.6;
}

:deep(.el-input-number) {
  width: 100%;
}
</style>
