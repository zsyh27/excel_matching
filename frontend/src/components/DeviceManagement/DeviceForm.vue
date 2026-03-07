<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑设备' : '添加设备'"
    width="700px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="120px"
    >
      <el-form-item label="设备ID" prop="device_id">
        <el-input
          v-model="formData.device_id"
          placeholder="自动生成"
          :disabled="true"
          readonly
        >
          <template #prefix>
            <el-icon><Key /></el-icon>
          </template>
        </el-input>
        <div class="param-hint">
          <el-icon><InfoFilled /></el-icon>
          设备ID将根据规格型号自动生成30位唯一编码
        </div>
      </el-form-item>
      
      <el-form-item label="品牌" prop="brand">
        <el-select
          v-model="formData.brand"
          filterable
          allow-create
          default-first-option
          placeholder="请选择或输入品牌"
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
      
      <!-- 设备类型选择 - 触发动态表单 -->
      <el-form-item label="设备类型" prop="device_type" required>
        <el-select
          v-model="formData.device_type"
          @change="onDeviceTypeChange"
          filterable
          clearable
          placeholder="请选择设备类型"
          style="width: 100%"
        >
          <el-option
            v-for="type in deviceTypes"
            :key="type"
            :label="type"
            :value="type"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="设备名称" prop="device_name">
        <el-input v-model="formData.device_name" placeholder="请输入设备名称" />
      </el-form-item>
      
      <el-form-item label="规格型号" prop="spec_model">
        <el-input 
          v-model="formData.spec_model" 
          placeholder="请输入规格型号"
          @input="onSpecModelChange"
        />
      </el-form-item>
      
      <!-- 动态参数表单 - 根据device_type显示 -->
      <div v-if="formData.device_type && currentDeviceParams.length > 0" class="dynamic-params">
        <el-divider content-position="left">
          <span class="divider-text">设备参数</span>
        </el-divider>
        <el-form-item
          v-for="param in currentDeviceParams"
          :key="param.name"
          :label="param.name"
          :prop="`key_params.${param.name}.value`"
          :required="param.required"
          :rules="param.required ? [{ required: true, message: `请输入${param.name}`, trigger: 'blur' }] : []"
        >
          <el-input
            :model-value="getParamValue(param.name)"
            :placeholder="`请输入${param.name}${param.unit ? '，单位：' + param.unit : ''}`"
            @update:model-value="(val) => setParamValue(param.name, val, param)"
          >
            <template v-if="param.unit" #append>{{ param.unit }}</template>
          </el-input>
          <div v-if="param.hint" class="param-hint">
            <el-icon><InfoFilled /></el-icon>
            {{ param.hint }}
          </div>
        </el-form-item>
      </div>
      
      <!-- 详细参数(可选) -->
      <el-form-item label="详细参数(可选)" prop="detailed_params">
        <el-input
          v-model="formData.detailed_params"
          type="textarea"
          :rows="3"
          placeholder="例如：立式安装 不锈钢材质 防护等级IP65 工作温度-20~60℃"
        />
        <div class="param-hint">
          <el-icon><InfoFilled /></el-icon>
          <span>
            可使用自然语言描述特殊参数，系统会自动提取关键信息用于匹配。
            <br/>
            <strong>示例：</strong>"立式安装，不锈钢材质，防护等级IP65，工作温度-20~60℃"
          </span>
        </div>
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
import { ref, reactive, watch, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled, Key } from '@element-plus/icons-vue'
import { createDevice, updateDevice } from '../../api/database'
import { getDeviceTypes } from '../../api/device'
import { getConfig } from '../../api/config'

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

// 设备类型配置
const deviceTypesConfig = ref({})
const deviceTypes = computed(() => Object.keys(deviceTypesConfig.value))

// 品牌选项
const brandOptions = ref([])

// 当前设备类型的参数配置
const currentDeviceParams = computed(() => {
  if (!formData.device_type) return []
  return deviceTypesConfig.value[formData.device_type]?.params || []
})

// 获取参数值的辅助函数
const getParamValue = (paramName) => {
  if (!formData.key_params[paramName]) {
    return ''
  }
  
  // 处理两种数据格式：
  // 1. 简单格式: {参数名: "参数值"}
  // 2. 嵌套格式: {参数名: {value: "参数值", raw_value: ..., ...}}
  const param = formData.key_params[paramName]
  
  if (typeof param === 'string') {
    // 简单格式：直接返回字符串值
    return param
  } else if (typeof param === 'object' && param !== null) {
    // 嵌套格式：返回 value 字段
    return param.value || ''
  }
  
  return ''
}

// 设置参数值的辅助函数
const setParamValue = (paramName, value, param) => {
  if (!formData.key_params[paramName]) {
    // 如果参数不存在，使用简单格式初始化
    formData.key_params[paramName] = value
  } else {
    // 如果参数已存在，检查其格式
    const existingParam = formData.key_params[paramName]
    
    if (typeof existingParam === 'string') {
      // 简单格式：直接更新值
      formData.key_params[paramName] = value
    } else if (typeof existingParam === 'object' && existingParam !== null) {
      // 嵌套格式：更新 value 和 raw_value
      formData.key_params[paramName].value = value
      formData.key_params[paramName].raw_value = value
    } else {
      // 其他情况：使用简单格式
      formData.key_params[paramName] = value
    }
  }
}

const formData = reactive({
  device_id: '',
  brand: '',
  device_type: '',
  device_name: '',
  spec_model: '',
  key_params: {},
  detailed_params: '',
  unit_price: 0,
  input_method: 'manual',
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
  device_type: [
    { required: true, message: '请选择设备类型', trigger: 'change' }
  ],
  device_name: [
    { required: true, message: '请输入设备名称', trigger: 'blur' }
  ],
  spec_model: [
    { required: true, message: '请输入规格型号', trigger: 'blur' }
  ],
  unit_price: [
    { required: true, message: '请输入单价', trigger: 'blur' },
    { type: 'number', min: 0, message: '单价必须大于等于0', trigger: 'blur' }
  ]
}

// 加载设备类型配置
const loadDeviceTypes = async () => {
  try {
    const response = await getDeviceTypes()
    if (response.data.success) {
      deviceTypesConfig.value = response.data.data.params_config || {}
    } else {
      console.error('加载设备类型配置失败:', response.data.message)
    }
  } catch (error) {
    console.error('加载设备类型配置失败:', error)
  }
}

// 加载品牌列表
const loadBrands = async () => {
  try {
    const response = await getConfig()
    if (response.data.success) {
      const config = response.data.config
      // 从brand_keywords配置中提取品牌
      if (config.brand_keywords) {
        // 兼容数组和对象两种格式
        brandOptions.value = Array.isArray(config.brand_keywords) 
          ? [...config.brand_keywords].sort() 
          : Object.keys(config.brand_keywords).sort()
      }
    }
  } catch (error) {
    console.error('加载品牌列表失败:', error)
  }
}

// 生成设备ID
const generateDeviceId = () => {
  const specModel = formData.spec_model || ''
  const brand = formData.brand || ''
  const timestamp = Date.now().toString()
  const random = Math.random().toString(36).substring(2, 8).toUpperCase()
  
  // 基于品牌+规格型号+时间戳+随机数生成30位ID
  let base = `${brand}_${specModel}_${timestamp}_${random}`
  // 移除特殊字符，只保留字母数字和下划线
  base = base.replace(/[^a-zA-Z0-9]/g, '_')
  
  // 确保长度为30位
  if (base.length > 30) {
    base = base.substring(0, 30)
  } else if (base.length < 30) {
    base = base.padEnd(30, '0')
  }
  
  return base
}

// 规格型号变化时自动生成设备ID
const onSpecModelChange = () => {
  if (!isEdit.value && formData.spec_model) {
    formData.device_id = generateDeviceId()
  }
}

// 设备类型变更时
const onDeviceTypeChange = (newType) => {
  // 清空之前的参数
  formData.key_params = {}
  
  if (!newType) return
  
  // 初始化新类型的参数结构（使用简单格式）
  const params = deviceTypesConfig.value[newType]?.params || []
  params.forEach(param => {
    formData.key_params[param.name] = ''
  })
}

// 监听品牌变化，也触发ID生成
watch(() => formData.brand, () => {
  if (!isEdit.value && formData.spec_model) {
    formData.device_id = generateDeviceId()
  }
})

// 监听 modelValue 变化
watch(() => props.modelValue, async (val) => {
  visible.value = val
  if (val) {
    // 确保设备类型配置已加载
    if (Object.keys(deviceTypesConfig.value).length === 0) {
      await loadDeviceTypes()
    }
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
    // 判断是编辑还是复制（复制时device_id为空）
    isEdit.value = !!props.deviceData.device_id
    
    Object.assign(formData, {
      device_id: props.deviceData.device_id || '',
      brand: props.deviceData.brand,
      device_type: props.deviceData.device_type || '',
      device_name: props.deviceData.device_name,
      spec_model: props.deviceData.spec_model,
      key_params: props.deviceData.key_params || {},
      detailed_params: props.deviceData.detailed_params || '',
      unit_price: props.deviceData.unit_price,
      regenerate_rule: false,
      auto_generate_rule: !isEdit.value // 复制时默认生成规则
    })
    
    // 如果是复制（device_id为空），生成新的device_id
    if (!isEdit.value && formData.spec_model) {
      formData.device_id = generateDeviceId()
    }
    
    // 确保所有当前设备类型的参数都被初始化（使用简单格式）
    if (formData.device_type) {
      const params = deviceTypesConfig.value[formData.device_type]?.params || []
      params.forEach(param => {
        if (formData.key_params[param.name] === undefined) {
          // 如果参数不存在，初始化为空字符串
          formData.key_params[param.name] = ''
        }
      })
    }
  } else {
    isEdit.value = false
    Object.assign(formData, {
      device_id: '',
      brand: '',
      device_type: '',
      device_name: '',
      spec_model: '',
      key_params: {},
      detailed_params: '',
      unit_price: 0,
      input_method: 'manual',
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
        device_type: formData.device_type || null,
        device_name: formData.device_name,
        spec_model: formData.spec_model,
        key_params: formData.key_params && Object.keys(formData.key_params).length > 0 ? formData.key_params : null,
        detailed_params: formData.detailed_params || null,
        unit_price: formData.unit_price,
        input_method: formData.input_method
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

// 组件挂载时加载设备类型配置和品牌列表
onMounted(() => {
  loadDeviceTypes()
  loadBrands()
})
</script>

<style scoped>
:deep(.el-input-number) {
  width: 100%;
}

.dynamic-params {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  margin: 16px 0;
}

.divider-text {
  font-weight: 600;
  color: #409eff;
  font-size: 14px;
}

.param-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.dynamic-params .el-form-item) {
  margin-bottom: 18px;
}

:deep(.dynamic-params .el-form-item__label) {
  color: #303133;
}
</style>
