<template>
  <div class="device-input-view">
    <el-row :gutter="20">
      <el-col :span="24">
        <h2 class="page-title">智能设备录入</h2>
        <p class="page-description">
          通过智能解析功能，系统可以自动从设备描述文本中提取品牌、设备类型、型号和关键参数，大幅减少手动录入工作量。
        </p>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 左侧：设备录入表单 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="10">
        <DeviceInputForm
          ref="inputFormRef"
          :initial-data="initialFormData"
          @parse="handleParse"
          @manual-fill="handleManualFill"
          @reset="handleReset"
        />
      </el-col>

      <!-- 右侧：解析结果确认界面 -->
      <el-col :xs="24" :sm="24" :md="12" :lg="14">
        <ParseResultDisplay
          v-if="parseResult"
          :parse-result="parseResult"
          :loading="saving"
          @confirm="handleConfirmSave"
          @edit="handleEditResult"
          @update="handleUpdateResult"
          @reparse="handleReparse"
        />

        <div v-else class="empty-placeholder">
          <el-empty description="请输入设备描述并点击智能解析按钮">
            <template #image>
              <el-icon :size="100" color="#909399">
                <Document />
              </el-icon>
            </template>
          </el-empty>
        </div>
      </el-col>
    </el-row>

    <!-- 成功提示对话框 -->
    <el-dialog
      v-model="successDialogVisible"
      title="设备创建成功"
      width="400px"
      :close-on-click-modal="false"
    >
      <div class="success-content">
        <el-icon :size="60" color="#67C23A">
          <SuccessFilled />
        </el-icon>
        <p>设备已成功保存到数据库</p>
        <p class="device-id">设备ID: {{ createdDeviceId }}</p>
      </div>
      <template #footer>
        <el-button type="primary" @click="handleContinueInput">
          继续录入
        </el-button>
        <el-button @click="handleViewDevice">
          查看设备
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, SuccessFilled } from '@element-plus/icons-vue'
import DeviceInputForm from '../components/DeviceInput/DeviceInputForm.vue'
import ParseResultDisplay from '../components/DeviceInput/ParseResultDisplay.vue'
import { parseDeviceDescription, createIntelligentDevice } from '../api/device'

const router = useRouter()

// Refs
const inputFormRef = ref(null)
const parseResult = ref(null)
const initialFormData = ref({})
const successDialogVisible = ref(false)
const createdDeviceId = ref('')
const saving = ref(false)

// Methods
const handleParse = async (formData) => {
  try {
    // 设置加载状态
    inputFormRef.value?.setLoading(true)

    // 调用解析API
    const response = await parseDeviceDescription(formData)

    if (response.data.success) {
      parseResult.value = {
        ...response.data.data,
        _rawDescription: formData.description  // 保存原始描述用于后续保存
      }
      ElMessage.success('解析完成')
    } else {
      ElMessage.error(response.data.message || '解析失败')
    }
  } catch (error) {
    console.error('解析错误:', error)
    
    // 处理不同类型的错误
    if (error.response) {
      const errorData = error.response.data
      if (errorData.error_code === 'EMPTY_DESCRIPTION') {
        ElMessage.warning('设备描述不能为空')
      } else if (errorData.error_code === 'INVALID_PRICE') {
        ElMessage.warning('价格格式无效')
      } else {
        ElMessage.error(errorData.message || '解析失败，请稍后重试')
      }
    } else {
      ElMessage.error('网络错误，请检查连接')
    }
  } finally {
    inputFormRef.value?.setLoading(false)
  }
}

const handleManualFill = (formData) => {
  // 跳转到手动填写页面（待实现）
  ElMessage.info('手动填写功能即将推出')
  console.log('手动填写:', formData)
}

const handleReset = () => {
  parseResult.value = null
  ElMessage.info('表单已重置')
}

const handleReparse = () => {
  const formData = inputFormRef.value?.getFormData()
  if (formData) {
    handleParse(formData)
  }
}

const handleConfirmSave = async () => {
  if (!parseResult.value) {
    ElMessage.warning('没有可保存的解析结果')
    return
  }

  try {
    saving.value = true

    // 获取原始表单数据（如果可用）
    const formData = inputFormRef.value?.getFormData()
    
    // 使用保存的原始描述或从表单获取
    const rawDescription = parseResult.value._rawDescription || formData?.description || ''

    // 构建设备数据
    const deviceData = {
      raw_description: rawDescription,
      brand: parseResult.value.brand,
      device_type: parseResult.value.device_type,
      model: parseResult.value.model,
      key_params: parseResult.value.key_params || {},
      price: parseResult.value.price || formData?.price,
      confidence_score: parseResult.value.confidence_score
    }

    // 调用创建设备API
    const response = await createIntelligentDevice(deviceData)

    if (response.data.success) {
      createdDeviceId.value = response.data.data.id
      successDialogVisible.value = true
    } else {
      ElMessage.error(response.data.message || '保存失败')
    }
  } catch (error) {
    console.error('保存错误:', error)
    
    if (error.response) {
      const errorData = error.response.data
      ElMessage.error(errorData.message || '保存失败，请稍后重试')
    } else {
      ElMessage.error('网络错误，请检查连接')
    }
  } finally {
    saving.value = false
  }
}

const handleEditResult = () => {
  // 编辑功能已在 ParseResultDisplay 组件内部实现
  console.log('进入编辑模式:', parseResult.value)
}

const handleUpdateResult = (updatedResult) => {
  // 更新解析结果
  parseResult.value = updatedResult
  console.log('解析结果已更新:', updatedResult)
}

const handleContinueInput = () => {
  successDialogVisible.value = false
  createdDeviceId.value = ''
  parseResult.value = null
  inputFormRef.value?.resetForm()
}

const handleViewDevice = () => {
  successDialogVisible.value = false
  // 跳转到设备管理页面
  router.push('/database/devices')
}
</script>

<style scoped>
.device-input-view {
  padding: 20px;
}

.page-title {
  margin: 0 0 10px 0;
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.page-description {
  margin: 0 0 20px 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.empty-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.success-content {
  text-align: center;
  padding: 20px;
}

.success-content p {
  margin: 15px 0;
  font-size: 16px;
  color: #303133;
}

.success-content .device-id {
  font-size: 14px;
  color: #909399;
  font-family: monospace;
}

@media (max-width: 768px) {
  .device-input-view {
    padding: 10px;
  }

  .page-title {
    font-size: 20px;
  }

  .empty-placeholder {
    min-height: 300px;
  }
}
</style>
