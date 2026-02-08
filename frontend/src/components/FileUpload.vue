<template>
  <div class="file-upload-container">
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <span>上传设备清单</span>
        </div>
      </template>

      <!-- 文件上传区域 -->
      <el-upload
        ref="uploadRef"
        class="upload-area"
        drag
        :action="uploadAction"
        :before-upload="beforeUpload"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :on-progress="handleProgress"
        :show-file-list="false"
        :auto-upload="true"
        accept=".xls,.xlsx,.xlsm"
        name="file"
      >
        <el-icon class="el-icon--upload" :size="67">
          <upload-filled />
        </el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            仅支持 xls、xlsx、xlsm 格式的 Excel 文件，文件大小不超过 10MB
          </div>
        </template>
      </el-upload>

      <!-- 上传进度 -->
      <div v-if="uploading" class="progress-container">
        <el-progress
          :percentage="uploadProgress"
          :status="uploadStatus"
          :stroke-width="20"
        />
        <div class="progress-text">{{ progressText }}</div>
      </div>

      <!-- 已上传文件信息 -->
      <div v-if="uploadedFile" class="file-info">
        <el-alert
          :title="`已上传: ${uploadedFile.filename}`"
          type="success"
          :closable="false"
          show-icon
        >
          <template #default>
            <div>文件格式: {{ uploadedFile.format.toUpperCase() }}</div>
            <div v-if="parseResult">
              总行数: {{ parseResult.total_rows }} | 
              有效行数: {{ parseResult.valid_rows }} | 
              设备行数: {{ parseResult.device_rows }}
            </div>
          </template>
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import api from '../api/index.js'

// 定义 emits
const emit = defineEmits(['upload-success', 'parse-complete'])

// 上传相关状态
const uploadRef = ref(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const progressText = ref('')
const uploadedFile = ref(null)
const parseResult = ref(null)

// 上传接口地址
const uploadAction = '/api/upload'

// 允许的文件格式
const ALLOWED_FORMATS = ['xls', 'xlsx', 'xlsm']
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

/**
 * 上传前的文件验证
 * 验证需求: 1.1, 1.2, 1.3, 1.4
 */
const beforeUpload = (file) => {
  // 验证文件格式
  const fileName = file.name
  const fileExt = fileName.substring(fileName.lastIndexOf('.') + 1).toLowerCase()
  
  if (!ALLOWED_FORMATS.includes(fileExt)) {
    ElMessage.error({
      message: `不支持的文件格式！仅支持 ${ALLOWED_FORMATS.join('、')} 格式`,
      duration: 3000
    })
    return false
  }

  // 验证文件大小
  if (file.size > MAX_FILE_SIZE) {
    ElMessage.error({
      message: `文件大小超过限制！最大支持 ${MAX_FILE_SIZE / 1024 / 1024}MB`,
      duration: 3000
    })
    return false
  }

  // 重置状态
  uploading.value = true
  uploadProgress.value = 0
  uploadStatus.value = ''
  progressText.value = '正在上传文件...'
  uploadedFile.value = null
  parseResult.value = null

  return true
}

/**
 * 上传进度处理
 * 验证需求: 9.1
 */
const handleProgress = (event) => {
  uploadProgress.value = Math.floor(event.percent)
  
  if (uploadProgress.value < 100) {
    progressText.value = `正在上传文件... ${uploadProgress.value}%`
  } else {
    progressText.value = '上传完成，正在解析文件...'
  }
}

/**
 * 上传成功处理
 * 验证需求: 9.1, 9.2
 */
const handleUploadSuccess = async (response, file) => {
  try {
    if (!response.success) {
      throw new Error(response.error_message || '上传失败')
    }

    // 显示上传成功通知
    ElNotification({
      title: '上传成功',
      message: `文件 "${response.filename}" 上传成功，正在解析...`,
      type: 'success',
      duration: 2000
    })

    // 保存上传文件信息
    uploadedFile.value = {
      file_id: response.file_id,
      filename: response.filename,
      format: response.format
    }

    // 触发上传成功事件
    emit('upload-success', uploadedFile.value)

    // 自动调用解析接口
    await parseFile(response.file_id)

  } catch (error) {
    handleError('上传处理失败', error)
  }
}

/**
 * 上传失败处理
 * 验证需求: 9.2
 */
const handleUploadError = (error) => {
  uploading.value = false
  uploadStatus.value = 'exception'
  progressText.value = '上传失败'

  let errorMessage = '文件上传失败，请重试'
  
  try {
    if (error.message) {
      const errorData = JSON.parse(error.message)
      errorMessage = errorData.error_message || errorMessage
    }
  } catch (e) {
    // 解析失败，使用默认错误消息
  }

  ElNotification({
    title: '上传失败',
    message: errorMessage,
    type: 'error',
    duration: 4000
  })
}

/**
 * 调用解析接口
 * 验证需求: 9.2
 */
const parseFile = async (fileId) => {
  try {
    progressText.value = '正在解析文件...'
    
    const response = await api.post('/parse', { file_id: fileId })
    
    if (!response.data.success) {
      throw new Error(response.data.error_message || '解析失败')
    }

    const result = response.data.parse_result
    parseResult.value = result

    // 更新进度状态
    uploading.value = false
    uploadProgress.value = 100
    uploadStatus.value = 'success'
    progressText.value = '解析完成'

    // 显示解析成功通知
    ElNotification({
      title: '解析成功',
      message: `成功解析 ${result.device_rows} 个设备行`,
      type: 'success',
      duration: 3000
    })

    // 触发解析完成事件
    emit('parse-complete', {
      file_id: fileId,
      parse_result: result
    })

  } catch (error) {
    handleError('文件解析失败', error)
  }
}

/**
 * 统一错误处理
 */
const handleError = (title, error) => {
  uploading.value = false
  uploadStatus.value = 'exception'
  uploadProgress.value = 0

  const errorMessage = error.response?.data?.error_message || error.message || '未知错误'
  const errorDetail = error.response?.data?.details?.error_detail || ''

  ElNotification({
    title: title,
    message: errorDetail ? `${errorMessage}: ${errorDetail}` : errorMessage,
    type: 'error',
    duration: 5000
  })
}

/**
 * 重置上传状态（供父组件调用）
 */
const reset = () => {
  uploading.value = false
  uploadProgress.value = 0
  uploadStatus.value = ''
  progressText.value = ''
  uploadedFile.value = null
  parseResult.value = null
}

// 暴露方法给父组件
defineExpose({
  reset
})
</script>

<style scoped>
.file-upload-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.upload-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload) {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.el-icon--upload {
  color: #409EFF;
  margin-bottom: 16px;
}

.el-upload__text {
  font-size: 14px;
  color: #606266;
}

.el-upload__text em {
  color: #409EFF;
  font-style: normal;
}

.el-upload__tip {
  margin-top: 12px;
  font-size: 12px;
  color: #909399;
  text-align: center;
}

.progress-container {
  margin-top: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.progress-text {
  margin-top: 10px;
  text-align: center;
  font-size: 14px;
  color: #606266;
}

.file-info {
  margin-top: 20px;
}

.file-info :deep(.el-alert__content) {
  width: 100%;
}

.file-info :deep(.el-alert__description) {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.6;
}
</style>
