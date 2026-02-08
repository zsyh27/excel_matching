<template>
  <el-button 
    v-if="hasData" 
    type="primary" 
    size="default"
    @click="handleExport"
    :loading="exporting"
    :disabled="!fileId"
  >
    <el-icon v-if="!exporting"><Download /></el-icon>
    <span>{{ exporting ? '导出中...' : '导出报价清单' }}</span>
  </el-button>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElNotification, ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import api from '../api/index.js'

/**
 * ExportButton 组件
 * 负责导出报价清单功能
 * 验证需求: 9.4, 9.5
 */

// 定义 props
const props = defineProps({
  fileId: {
    type: String,
    default: null,
    required: true
  },
  matchedRows: {
    type: Array,
    default: () => [],
    required: true
  },
  originalFilename: {
    type: String,
    default: ''
  }
})

// 定义 emits
const emit = defineEmits(['export-success', 'export-error'])

// 状态管理
const exporting = ref(false)

// 计算属性
const hasData = computed(() => props.matchedRows && props.matchedRows.length > 0)

/**
 * 处理导出操作
 * 验证需求: 9.4, 9.5
 */
const handleExport = async () => {
  // 验证必需参数
  if (!props.fileId) {
    ElMessage.error('缺少文件 ID，无法导出')
    emit('export-error', { message: '缺少文件 ID' })
    return
  }

  if (!props.matchedRows || props.matchedRows.length === 0) {
    ElMessage.error('没有可导出的数据')
    emit('export-error', { message: '没有可导出的数据' })
    return
  }

  try {
    exporting.value = true

    // 调用后端导出接口
    // 验证需求: 9.4
    const response = await api.post('/export', {
      file_id: props.fileId,
      matched_rows: props.matchedRows
    }, {
      responseType: 'blob', // 重要：指定响应类型为 blob
      timeout: 60000 // 导出可能需要更长时间
    })

    // 触发文件下载
    // 验证需求: 9.4
    downloadFile(response.data)

    // 显示成功通知
    // 验证需求: 9.5
    ElNotification({
      title: '导出成功',
      message: '报价清单已成功导出，请查看下载文件',
      type: 'success',
      duration: 3000
    })

    // 触发成功事件
    emit('export-success', {
      filename: generateFilename(),
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('导出失败:', error)

    // 处理错误响应
    let errorMessage = '导出报价清单失败'
    
    if (error.response) {
      // 如果响应是 blob 类型，需要转换为文本读取错误信息
      if (error.response.data instanceof Blob) {
        try {
          const text = await error.response.data.text()
          const errorData = JSON.parse(text)
          errorMessage = errorData.error_message || errorMessage
        } catch (e) {
          // 无法解析错误信息，使用默认消息
        }
      } else if (error.response.data && error.response.data.error_message) {
        errorMessage = error.response.data.error_message
      }
    } else if (error.message) {
      errorMessage = error.message
    }

    // 显示失败通知
    // 验证需求: 9.5
    ElNotification({
      title: '导出失败',
      message: errorMessage,
      type: 'error',
      duration: 4000
    })

    // 触发错误事件
    emit('export-error', {
      message: errorMessage,
      error: error
    })

  } finally {
    exporting.value = false
  }
}

/**
 * 下载文件
 * 创建临时链接并触发下载
 */
const downloadFile = (blob) => {
  // 创建 Blob 对象
  const fileBlob = new Blob([blob], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  })

  // 创建下载链接
  const url = window.URL.createObjectURL(fileBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = generateFilename()
  
  // 触发下载
  document.body.appendChild(link)
  link.click()
  
  // 清理
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

/**
 * 生成导出文件名
 */
const generateFilename = () => {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
  const baseName = props.originalFilename 
    ? props.originalFilename.replace(/\.[^/.]+$/, '') 
    : '报价清单'
  return `${baseName}_导出_${timestamp}.xlsx`
}

// 暴露方法给父组件
defineExpose({
  handleExport
})
</script>

<style scoped>
.el-button {
  font-weight: 500;
}

.el-button .el-icon {
  margin-right: 5px;
}
</style>
