<template>
  <el-dialog
    v-model="visible"
    title="批量导入设备"
    width="900px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="batch-import">
      <!-- 文件上传区域 -->
      <div v-if="!fileUploaded" class="upload-section">
        <el-alert
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 15px"
        >
          <template #title>
            请上传包含设备信息的Excel文件（支持.xlsx和.xls格式）
          </template>
        </el-alert>
        
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          :on-change="handleFileChange"
          :on-exceed="handleExceed"
          accept=".xlsx,.xls"
          drag
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            将Excel文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 .xlsx 和 .xls 格式，文件大小不超过 10MB
            </div>
          </template>
        </el-upload>
        
        <div class="upload-actions">
          <el-button type="primary" :disabled="!selectedFile" @click="handlePreview">
            预览数据
          </el-button>
        </div>
      </div>

      <!-- 数据预览区域 -->
      <div v-if="fileUploaded && !importing" class="preview-section">
        <el-alert
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 15px"
        >
          <template #title>
            共 {{ previewData.length }} 条数据，以下显示前 10 条预览
          </template>
        </el-alert>
        
        <el-table
          :data="previewData.slice(0, 10)"
          stripe
          style="width: 100%"
          max-height="400"
        >
          <el-table-column prop="brand" label="品牌" width="120" />
          <el-table-column prop="device_type" label="设备类型" width="120">
            <template #default="{ row }">
              <span v-if="row.device_type">{{ row.device_type }}</span>
              <span v-else style="color: #909399">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="device_name" label="设备名称" width="150" />
          <el-table-column prop="spec_model" label="规格型号" width="150" />
          <el-table-column prop="unit_price" label="单价" width="100">
            <template #default="{ row }">
              ¥{{ row.unit_price }}
            </template>
          </el-table-column>
          <el-table-column label="其他参数" min-width="200">
            <template #default="{ row }">
              <div v-if="row.key_params && Object.keys(row.key_params).length > 0">
                <el-tag
                  v-for="(value, key) in row.key_params"
                  :key="key"
                  size="small"
                  style="margin: 2px"
                >
                  {{ key }}: {{ value }}
                </el-tag>
              </div>
              <span v-else style="color: #909399">-</span>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="import-options">
          <el-checkbox v-model="autoGenerateRules">
            自动为导入的设备生成匹配规则
          </el-checkbox>
        </div>
        
        <div class="preview-actions">
          <el-button @click="handleReselect">重新选择</el-button>
          <el-button type="primary" @click="handleImport">
            确认导入
          </el-button>
        </div>
      </div>

      <!-- 导入进度区域 -->
      <div v-if="importing" class="progress-section">
        <el-progress
          :percentage="importProgress"
          :status="importStatus"
          :stroke-width="20"
        />
        <p class="progress-text">{{ progressText }}</p>
      </div>

      <!-- 导入结果区域 -->
      <div v-if="importResult" class="result-section">
        <el-result
          :icon="importResult.success ? 'success' : 'warning'"
          :title="importResult.title"
        >
          <template #sub-title>
            <div class="result-stats">
              <p>成功导入: {{ importResult.inserted }} 条</p>
              <p v-if="importResult.updated > 0">更新: {{ importResult.updated }} 条</p>
              <p v-if="importResult.failed > 0" style="color: #F56C6C">
                失败: {{ importResult.failed }} 条
              </p>
            </div>
          </template>
          <template #extra>
            <el-button type="primary" @click="handleClose">完成</el-button>
          </template>
        </el-result>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { batchImportDevices } from '../../api/database'
import * as XLSX from 'xlsx'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const visible = ref(props.modelValue)
const uploadRef = ref(null)
const selectedFile = ref(null)
const fileUploaded = ref(false)
const previewData = ref([])
const autoGenerateRules = ref(true)
const importing = ref(false)
const importProgress = ref(0)
const importStatus = ref('')
const progressText = ref('')
const importResult = ref(null)

// 监听 modelValue 变化
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    resetState()
  }
})

// 监听 visible 变化
watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 重置状态
const resetState = () => {
  selectedFile.value = null
  fileUploaded.value = false
  previewData.value = []
  autoGenerateRules.value = true
  importing.value = false
  importProgress.value = 0
  importStatus.value = ''
  progressText.value = ''
  importResult.value = null
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 文件选择变化
const handleFileChange = (file) => {
  selectedFile.value = file
}

// 文件超出限制
const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

// 预览数据
const handlePreview = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  ElMessage.info('正在解析文件...')
  
  try {
    // 读取Excel文件
    const file = selectedFile.value.raw
    const reader = new FileReader()
    
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        
        // 获取第一个工作表
        const firstSheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[firstSheetName]
        
        // 将工作表转换为JSON
        const jsonData = XLSX.utils.sheet_to_json(worksheet)
        
        if (jsonData.length === 0) {
          ElMessage.warning('Excel文件中没有数据')
          return
        }
        
        // 映射Excel列名到系统字段名
        previewData.value = jsonData.map(row => {
          const device = {
            brand: row['品牌'] || '',
            device_type: row['设备类型'] || '',
            device_name: row['设备名称'] || '',
            spec_model: row['规格型号'] || '',
            unit_price: row['单价'] || 0
          }
          
          // 收集其他列作为key_params
          const excludeKeys = ['品牌', '设备类型', '设备名称', '规格型号', '单价']
          const keyParams = {}
          
          for (const [key, value] of Object.entries(row)) {
            if (!excludeKeys.includes(key) && value !== undefined && value !== null && value !== '') {
              keyParams[key] = value
            }
          }
          
          if (Object.keys(keyParams).length > 0) {
            device.key_params = keyParams
          }
          
          return device
        })
        
        fileUploaded.value = true
        ElMessage.success(`文件解析成功，共 ${previewData.value.length} 条数据`)
      } catch (error) {
        console.error('解析Excel失败:', error)
        ElMessage.error('解析Excel文件失败，请检查文件格式')
      }
    }
    
    reader.onerror = () => {
      ElMessage.error('读取文件失败')
    }
    
    reader.readAsArrayBuffer(file)
  } catch (error) {
    console.error('预览失败:', error)
    ElMessage.error('预览失败，请稍后重试')
  }
}

// 重新选择文件
const handleReselect = () => {
  fileUploaded.value = false
  previewData.value = []
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 执行导入
const handleImport = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  importing.value = true
  importProgress.value = 0
  importStatus.value = ''
  progressText.value = '正在导入设备数据...'
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value.raw)
    formData.append('auto_generate_rules', autoGenerateRules.value)
    
    // 模拟进度更新
    const progressInterval = setInterval(() => {
      if (importProgress.value < 90) {
        importProgress.value += 10
      }
    }, 200)
    
    const response = await batchImportDevices(formData)
    
    clearInterval(progressInterval)
    importProgress.value = 100
    
    if (response.data.success) {
      importStatus.value = 'success'
      progressText.value = '导入完成'
      
      const data = response.data.data
      importResult.value = {
        success: true,
        title: '导入成功',
        inserted: data.inserted || 0,
        updated: data.updated || 0,
        failed: data.failed || 0
      }
      
      emit('success')
    } else {
      importStatus.value = 'exception'
      progressText.value = '导入失败'
      
      importResult.value = {
        success: false,
        title: '导入失败',
        inserted: 0,
        updated: 0,
        failed: previewData.value.length
      }
      
      ElMessage.error(response.data.message || '导入失败')
    }
  } catch (error) {
    console.error('导入失败:', error)
    importStatus.value = 'exception'
    progressText.value = '导入失败'
    
    importResult.value = {
      success: false,
      title: '导入失败',
      inserted: 0,
      updated: 0,
      failed: previewData.value.length
    }
    
    ElMessage.error('导入失败，请稍后重试')
  } finally {
    importing.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
.batch-import {
  min-height: 300px;
}

.upload-section {
  padding: 20px 0;
}

.upload-actions {
  margin-top: 20px;
  text-align: center;
}

.preview-section {
  padding: 10px 0;
}

.import-options {
  margin: 20px 0;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.preview-actions {
  margin-top: 20px;
  text-align: right;
}

.progress-section {
  padding: 40px 20px;
  text-align: center;
}

.progress-text {
  margin-top: 20px;
  font-size: 16px;
  color: #606266;
}

.result-section {
  padding: 20px 0;
}

.result-stats p {
  margin: 5px 0;
  font-size: 16px;
}

:deep(.el-upload-dragger) {
  padding: 40px;
}
</style>
