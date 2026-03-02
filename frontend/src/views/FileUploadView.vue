<template>
  <div class="file-upload-view">
    <!-- 功能导航区域 -->
    <div class="navigation-section">
      <h2 class="section-title">系统功能</h2>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="nav-card active" shadow="hover" @click="navigateTo('/')">
            <div class="nav-card-content">
              <el-icon :size="40" color="#409EFF">
                <upload-filled />
              </el-icon>
              <h3>上传设备清单</h3>
              <p>上传Excel文件进行设备识别和匹配</p>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="nav-card" shadow="hover" @click="navigateTo('/database/devices')">
            <div class="nav-card-content">
              <el-icon :size="40" color="#67C23A">
                <collection />
              </el-icon>
              <h3>设备库管理</h3>
              <p>管理设备库中的所有设备信息</p>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="nav-card" shadow="hover" @click="navigateTo('/database/statistics')">
            <div class="nav-card-content">
              <el-icon :size="40" color="#E6A23C">
                <data-analysis />
              </el-icon>
              <h3>统计仪表板</h3>
              <p>查看设备库的统计数据和分析</p>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="nav-card" shadow="hover" @click="navigateTo('/rule-management')">
            <div class="nav-card-content">
              <el-icon :size="40" color="#F56C6C">
                <setting />
              </el-icon>
              <h3>匹配规则管理</h3>
              <p>管理和优化设备匹配规则</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="6">
          <el-card class="nav-card" shadow="hover" @click="navigateTo('/config-management')">
            <div class="nav-card-content">
              <el-icon :size="40" color="#9C27B0">
                <tools />
              </el-icon>
              <h3>配置管理</h3>
              <p>管理系统配置参数和预处理规则</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 上传卡片 -->
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
            <div class="upload-success-content">
              <div class="file-id-info">文件ID: {{ uploadedFile.excel_id }}</div>
              <div class="action-prompt">请选择下一步操作：</div>
              <div class="action-buttons">
                <el-button 
                  type="primary" 
                  @click="goToRangeSelection"
                  :loading="navigating"
                >
                  选择数据范围
                </el-button>
                <el-button 
                  @click="skipRangeSelection"
                  :loading="skipping"
                >
                  跳过范围选择（使用默认范围）
                </el-button>
              </div>
            </div>
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
import { UploadFilled, Collection, DataAnalysis, Setting, Tools } from '@element-plus/icons-vue'
import { parseExcelRange } from '@/api/excel'

const router = useRouter()

// 导航功能
const navigateTo = (path) => {
  if (path !== '/') {
    router.push(path)
  }
}

// 上传相关状态
const uploadRef = ref(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const progressText = ref('')
const uploadedFile = ref(null)
const navigating = ref(false)
const skipping = ref(false)

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

    // 清除之前的范围选择（如果有旧的excel_id）
    // 遍历sessionStorage，清除所有以excel_range_开头的键
    const keysToRemove = []
    for (let i = 0; i < sessionStorage.length; i++) {
      const key = sessionStorage.key(i)
      if (key && key.startsWith('excel_range_')) {
        keysToRemove.push(key)
      }
    }
    keysToRemove.forEach(key => sessionStorage.removeItem(key))

    // 显示上传成功通知
    ElNotification({
      title: '上传成功',
      message: `文件 "${response.filename}" 上传成功，请选择下一步操作`,
      type: 'success',
      duration: 3000
    })

    // 保存上传文件信息
    uploadedFile.value = {
      excel_id: response.excel_id,
      filename: response.filename
    }

    // 更新进度状态
    uploading.value = false
    uploadProgress.value = 100
    uploadStatus.value = 'success'
    progressText.value = '上传完成，请选择下一步操作'

  } catch (error) {
    handleError('上传处理失败', error)
  }
}

/**
 * 跳转到数据范围选择页面
 */
const goToRangeSelection = () => {
  if (!uploadedFile.value) return
  
  navigating.value = true
  router.push({
    name: 'DataRangeSelection',
    params: { excelId: uploadedFile.value.excel_id },
    query: { filename: uploadedFile.value.filename }
  })
}

/**
 * 跳过范围选择，使用默认范围直接跳转到设备行识别
 */
const skipRangeSelection = async () => {
  if (!uploadedFile.value) return
  
  try {
    skipping.value = true
    
    // 调用parseExcelRange API使用默认范围
    const response = await parseExcelRange(uploadedFile.value.excel_id, {
      sheet_index: 0,
      start_row: 1,
      end_row: null,
      start_col: 1,
      end_col: null
    })
    
    if (response.data.success) {
      // 保存默认范围到sessionStorage
      const defaultRange = {
        sheetIndex: 0,
        startRow: 1,
        endRow: null,
        startCol: 'A',
        endCol: null
      }
      sessionStorage.setItem(`excel_range_${uploadedFile.value.excel_id}`, JSON.stringify(defaultRange))
      
      // 保存分析结果到sessionStorage
      const analysisData = {
        filename: response.data.filename,
        analysis_results: response.data.analysis_results,
        statistics: response.data.statistics
      }
      sessionStorage.setItem(`analysis_${uploadedFile.value.excel_id}`, JSON.stringify(analysisData))
      
      ElMessage.success('使用默认范围解析成功')
      
      // 直接跳转到设备行识别页面
      router.push({
        name: 'DeviceRowAdjustment',
        params: { excelId: uploadedFile.value.excel_id }
      })
    } else {
      throw new Error(response.data.error || '解析失败')
    }
  } catch (error) {
    ElMessage.error('解析失败: ' + (error.response?.data?.error_message || error.message))
  } finally {
    skipping.value = false
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
  max-width: 1200px;
  margin: 20px auto;
}

/* 导航区域样式 */
.navigation-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 20px;
  padding-left: 10px;
  border-left: 4px solid #409EFF;
}

.nav-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 180px;
  overflow: hidden;
}

.nav-card :deep(.el-card__body) {
  height: 100%;
  overflow: hidden;
  padding: 20px;
}

.nav-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.nav-card.active {
  border: 2px solid #409EFF;
  background-color: #f0f9ff;
}

.nav-card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 0;
  overflow: hidden;
}

.nav-card-content .el-icon {
  margin-bottom: 12px;
}

.nav-card-content h3 {
  margin: 8px 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.nav-card-content p {
  margin: 0;
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}

/* 上传卡片样式 */
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

.upload-success-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.file-id-info {
  font-size: 13px;
  color: #606266;
}

.action-prompt {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-top: 4px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.action-buttons .el-button {
  flex: 1;
}
</style>
