<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑设备' : '添加设备'"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="设备ID" prop="device_id">
        <el-input
          v-model="formData.device_id"
          placeholder="请输入设备ID"
          :disabled="isEdit"
        />
      </el-form-item>
      
      <el-form-item label="品牌" prop="brand">
        <el-input v-model="formData.brand" placeholder="请输入品牌" />
      </el-form-item>
      
      <el-form-item label="设备名称" prop="device_name">
        <el-input v-model="formData.device_name" placeholder="请输入设备名称" />
      </el-form-item>
      
      <el-form-item label="规格型号" prop="spec_model">
        <el-input v-model="formData.spec_model" placeholder="请输入规格型号" />
      </el-form-item>
      
      <el-form-item label="详细参数" prop="detailed_params">
        <el-input
          v-model="formData.detailed_params"
          type="textarea"
          :rows="4"
          placeholder="请输入详细参数"
        />
      </el-form-item>
      
      <el-form-item label="单价" prop="unit_price">
        <el-input-number
          v-model="formData.unit_price"
          :min="0"
          :precision="2"
          :step="10"
          style="width: 100%"
        />
      </el-form-item>
      
      <el-form-item v-if="!isEdit" label="自动生成规则">
        <el-checkbox v-model="formData.auto_generate_rule">
          为该设备自动生成匹配规则
        </el-checkbox>
      </el-form-item>
      
      <el-form-item v-if="isEdit" label="重新生成规则">
        <el-checkbox v-model="formData.regenerate_rule">
          更新后重新生成匹配规则
        </el-checkbox>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSubmit">
        {{ isEdit ? '保存' : '创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createDevice, updateDevice } from '../../api/database'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  deviceData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const visible = ref(props.modelValue)
const formRef = ref(null)
const saving = ref(false)
const isEdit = ref(false)

const formData = reactive({
  device_id: '',
  brand: '',
  device_name: '',
  spec_model: '',
  detailed_params: '',
  unit_price: 0,
  auto_generate_rule: true,
  regenerate_rule: false
})

const rules = {
  device_id: [
    { required: true, message: '请输入设备ID', trigger: 'blur' }
  ],
  brand: [
    { required: true, message: '请输入品牌', trigger: 'blur' }
  ],
  device_name: [
    { required: true, message: '请输入设备名称', trigger: 'blur' }
  ],
  spec_model: [
    { required: true, message: '请输入规格型号', trigger: 'blur' }
  ],
  detailed_params: [
    { required: true, message: '请输入详细参数', trigger: 'blur' }
  ],
  unit_price: [
    { required: true, message: '请输入单价', trigger: 'blur' },
    { type: 'number', min: 0, message: '单价必须大于等于0', trigger: 'blur' }
  ]
}

// 监听 modelValue 变化
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    initForm()
  }
})

// 监听 visible 变化
watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 初始化表单
const initForm = () => {
  if (props.deviceData) {
    isEdit.value = true
    Object.assign(formData, {
      device_id: props.deviceData.device_id,
      brand: props.deviceData.brand,
      device_name: props.deviceData.device_name,
      spec_model: props.deviceData.spec_model,
      detailed_params: props.deviceData.detailed_params,
      unit_price: props.deviceData.unit_price,
      regenerate_rule: false
    })
  } else {
    isEdit.value = false
    Object.assign(formData, {
      device_id: '',
      brand: '',
      device_name: '',
      spec_model: '',
      detailed_params: '',
      unit_price: 0,
      auto_generate_rule: true
    })
  }
  
  // 清除验证
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    saving.value = true
    try {
      const requestData = {
        brand: formData.brand,
        device_name: formData.device_name,
        spec_model: formData.spec_model,
        detailed_params: formData.detailed_params,
        unit_price: formData.unit_price
      }
      
      let response
      if (isEdit.value) {
        requestData.regenerate_rule = formData.regenerate_rule
        response = await updateDevice(formData.device_id, requestData)
      } else {
        requestData.device_id = formData.device_id
        requestData.auto_generate_rule = formData.auto_generate_rule
        response = await createDevice(requestData)
      }
      
      if (response.data.success) {
        ElMessage.success(response.data.message || `设备${isEdit.value ? '更新' : '创建'}成功`)
        emit('success')
        handleClose()
      } else {
        ElMessage.error(response.data.message || `设备${isEdit.value ? '更新' : '创建'}失败`)
      }
    } catch (error) {
      console.error(`设备${isEdit.value ? '更新' : '创建'}失败:`, error)
      ElMessage.error(`设备${isEdit.value ? '更新' : '创建'}失败，请稍后重试`)
    } finally {
      saving.value = false
    }
  })
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
:deep(.el-input-number) {
  width: 100%;
}
</style>
