<template>
  <div class="file-upload-view">
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
            <div>文件ID: {{ uploadedFile.excel_id }}</div>
            <div>正在跳转到设备行调整页面...</div>
          </template>
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

const router = useRouter()

// 上传相关状态
const uploadRef = ref(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const progressText = ref('')
const uploadedFile = ref(null)

// 上传接口地址
const uploadAction = '/api/excel/analyze'

// 允许的文件格式
const ALLOWED_FORMATS = ['xls', 'xlsx', 'xlsm']
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

/**
 * 上传前的文件验证
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
  progressText.value = '正在上传并分析文件...'
  uploadedFile.value = null

  return true
}

/**
 * 上传进度处理
 */
const handleProgress = (event) => {
  uploadProgress.value = Math.floor(event.percent)
  
  if (uploadProgress.value < 100) {
    progressText.value = `正在上传文件... ${uploadProgress.value}%`
  } else {
    progressText.value = '上传完成，正在分析设备行...'
  }
}

/**
 * 上传成功处理
 */
const handleUploadSuccess = async (response, file) => {
  try {
    if (!response.success) {
      throw new Error(response.error || '上传失败')
    }

    // 显示上传成功通知
    ElNotification({
      title: '分析完成',
      message: `文件 "${response.filename}" 分析完成，共识别 ${response.statistics.high_probability} 个高概率设备行`,
      type: 'success',
      duration: 2000
    })

    // 保存上传文件信息
    uploadedFile.value = {
      excel_id: response.excel_id,
      filename: response.filename
    }

    // 将分析结果保存到 sessionStorage，供调整页面使用
    sessionStorage.setItem(`analysis_${response.excel_id}`, JSON.stringify({
      filename: response.filename,
      analysis_results: response.analysis_results,
      statistics: response.statistics
    }))

    // 更新进度状态
    uploading.value = false
    uploadProgress.value = 100
    uploadStatus.value = 'success'
    progressText.value = '分析完成，正在跳转...'

    // 延迟跳转到设备行调整页面
    setTimeout(() => {
      router.push({
        name: 'DeviceRowAdjustment',
        params: { excelId: response.excel_id }
      })
    }, 1500)

  } catch (error) {
    handleError('上传处理失败', error)
  }
}

/**
 * 上传失败处理
 */
const handleUploadError = (error) => {
  uploading.value = false
  uploadStatus.value = 'exception'
  progressText.value = '上传失败'

  let errorMessage = '文件上传失败，请重试'
  
  try {
    if (error.message) {
      const errorData = JSON.parse(error.message)
      errorMessage = errorData.error || errorMessage
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
 * 统一错误处理
 */
const handleError = (title, error) => {
  uploading.value = false
  uploadStatus.value = 'exception'
  uploadProgress.value = 0

  const errorMessage = error.response?.data?.error || error.message || '未知错误'

  ElNotification({
    title: title,
    message: errorMessage,
    type: 'error',
    duration: 5000
  })
}
</script>

<style scoped>
.file-upload-view {
  width: 100%;
  max-width: 800px;
  margin: 40px auto;
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
