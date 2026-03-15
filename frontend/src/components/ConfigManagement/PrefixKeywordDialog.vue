<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑前缀关键词' : '添加前缀关键词'"
    width="600px"
    @close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
      <el-form-item label="前缀词" prop="prefix">
        <el-input
          v-model="form.prefix"
          placeholder="例如: 室内、室外、管道"
          :disabled="isEdit"
        />
        <div class="form-tip">前缀关键词，创建后不可修改</div>
      </el-form-item>
      
      <el-form-item label="关联设备类型" prop="types">
        <el-select
          v-model="form.types"
          multiple
          filterable
          allow-create
          default-first-option
          placeholder="选择或输入设备类型"
          style="width: 100%"
        >
          <el-option
            v-for="type in deviceTypes"
            :key="type"
            :label="type"
            :value="type"
          />
        </el-select>
        <div class="form-tip">
          支持从列表选择或手动输入新的设备类型。当设备描述中包含此前缀词时，将优先匹配这些设备类型
        </div>
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
  prefixKeyword: {
    type: Object,
    default: null
  },
  deviceTypes: {
    type: Array,
    default: () => []
  },
  existingPrefixes: {
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
  prefix: '',
  types: []
})

const rules = {
  prefix: [
    { required: true, message: '请输入前缀词', trigger: 'blur' },
    { min: 1, max: 20, message: '长度在 1 到 20 个字符', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!isEdit.value && props.existingPrefixes.includes(value)) {
          callback(new Error('该前缀词已存在'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  types: [
    { required: true, message: '请至少选择一个设备类型', trigger: 'change' },
    { type: 'array', min: 1, message: '请至少选择一个设备类型', trigger: 'change' }
  ]
}

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.prefixKeyword) {
    // 编辑模式
    isEdit.value = true
    form.value = {
      prefix: props.prefixKeyword.prefix || '',
      types: props.prefixKeyword.types || []
    }
  } else if (val) {
    // 新增模式
    isEdit.value = false
    form.value = {
      prefix: '',
      types: []
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
      prefix: form.value.prefix,
      types: form.value.types
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
