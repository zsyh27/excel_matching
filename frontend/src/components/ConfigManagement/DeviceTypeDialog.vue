<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑设备类型' : '添加设备类型'"
    width="500px"
    @close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="类型名称" prop="name">
        <el-input
          v-model="form.name"
          placeholder="例如: 温度传感器"
          :disabled="isEdit"
        />
        <div class="form-tip">设备类型名称，创建后不可修改</div>
      </el-form-item>
      
      <el-form-item label="描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="可选：设备类型的详细描述"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleConfirm" :loading="loading">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  deviceType: {
    type: Object,
    default: null
  },
  existingTypes: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'confirm'])

const visible = ref(false)
const loading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)

const form = ref({
  name: '',
  description: ''
})

const rules = {
  name: [
    { required: true, message: '请输入设备类型名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!isEdit.value && props.existingTypes.includes(value)) {
          callback(new Error('该设备类型已存在'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.deviceType) {
    // 编辑模式
    isEdit.value = true
    form.value = {
      name: props.deviceType.name || props.deviceType,
      description: props.deviceType.description || ''
    }
  } else if (val) {
    // 新增模式
    isEdit.value = false
    form.value = {
      name: '',
      description: ''
    }
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const handleClose = () => {
  visible.value = false
  formRef.value?.resetFields()
}

const handleConfirm = async () => {
  try {
    await formRef.value.validate()
    loading.value = true
    
    emit('confirm', {
      name: form.value.name,
      description: form.value.description
    })
    
    handleClose()
  } catch (error) {
    console.error('表单验证失败:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
