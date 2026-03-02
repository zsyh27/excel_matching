<template>
  <el-dialog
    v-model="visible"
    title="匹配详情"
    width="90%"
    :close-on-click-modal="false"
    draggable
    destroy-on-close
  >
    <div v-loading="loading" class="dialog-content">
      <!-- 错误提示区域 -->
      <div v-if="error" class="error-container">
        <el-alert
          :title="error"
          type="error"
          :closable="false"
          show-icon
          class="error-alert"
        >
          <template #default>
            <div class="error-details">
              <p>{{ error }}</p>
              <div v-if="errorRetryable" class="error-actions">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="retryLoad"
                  :loading="retrying"
                >
                  <el-icon><Refresh /></el-icon>
                  重试
                </el-button>
                <el-button 
                  size="small" 
                  @click="visible = false"
                >
                  关闭
                </el-button>
              </div>
            </div>
          </template>
        </el-alert>
      </div>
      
      <!-- 详情内容 -->
      <el-tabs v-else-if="detail" v-model="activeTab" class="detail-tabs">
        <!-- Tab 1: 特征提取 -->
        <el-tab-pane label="特征提取" name="extraction">
          <FeatureExtractionView :preprocessing="detail.preprocessing" />
        </el-tab-pane>
        
        <!-- Tab 2: 候选规则 -->
        <el-tab-pane name="candidates">
          <template #label>
            <span>
              候选规则
              <el-badge
                v-if="detail.candidates && detail.candidates.length > 0"
                :value="detail.candidates.length"
                class="tab-badge"
              />
            </span>
          </template>
          <CandidateRulesView :candidates="detail.candidates" />
        </el-tab-pane>
        
        <!-- Tab 3: 匹配结果 -->
        <el-tab-pane label="匹配结果" name="result">
          <MatchResultView
            :final-result="detail.final_result"
            :decision-reason="detail.decision_reason"
            :suggestions="detail.optimization_suggestions"
          />
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <div class="footer-info">
          <span v-if="detail" class="timestamp">
            匹配时间: {{ formatTimestamp(detail.timestamp) }}
          </span>
          <span v-if="detail" class="duration">
            耗时: {{ detail.match_duration_ms.toFixed(2) }}ms
          </span>
        </div>
        <div class="footer-actions">
          <el-button @click="exportDetail" :loading="exporting" :disabled="!detail || error">
            <el-icon><Download /></el-icon>
            导出详情
          </el-button>
          <el-button type="primary" @click="visible = false">关闭</el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Refresh } from '@element-plus/icons-vue'
import matchApi from '@/api/match'
import FeatureExtractionView from './FeatureExtractionView.vue'
import CandidateRulesView from './CandidateRulesView.vue'
import MatchResultView from './MatchResultView.vue'

/**
 * 匹配详情对话框主组件
 * 
 * 使用el-tabs组织三个子视图，提供详情查看和导出功能
 * 包含完善的错误处理和重试机制
 * 验证需求: Requirements 1.2, 1.3, 1.4, 9.1, 9.4, 9.5
 */

const props = defineProps({
  cacheKey: {
    type: String,
    default: null
  },
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

// 状态管理
const visible = ref(false)
const activeTab = ref('extraction')
const detail = ref(null)
const loading = ref(false)
const error = ref(null)
const errorRetryable = ref(false)
const exporting = ref(false)
const retrying = ref(false)

/**
 * 监听 modelValue 变化
 */
watch(() => props.modelValue, async (newVal) => {
  visible.value = newVal
  if (newVal && props.cacheKey) {
    await loadDetail()
  }
})

/**
 * 监听 visible 变化，同步到父组件
 */
watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
  
  // 关闭时重置状态
  if (!newVal) {
    activeTab.value = 'extraction'
    error.value = null
    errorRetryable.value = false
    retrying.value = false
  }
})

/**
 * 加载匹配详情
 * @param {boolean} isRetry - 是否为重试操作
 */
async function loadDetail(isRetry = false) {
  if (!props.cacheKey) {
    error.value = '缓存键不能为空'
    errorRetryable.value = false
    return
  }

  if (isRetry) {
    retrying.value = true
  } else {
    loading.value = true
  }
  
  error.value = null
  errorRetryable.value = false
  detail.value = null

  try {
    const response = await matchApi.getMatchDetail(props.cacheKey, {
      enableRetry: true,
      maxRetries: 2,
      timeout: 30000
    })
    
    if (response.data.success) {
      detail.value = response.data.detail
      
      // 如果是重试成功，显示成功提示
      if (isRetry) {
        ElMessage.success('加载成功')
      }
    } else {
      error.value = response.data.error_message || '加载匹配详情失败'
      errorRetryable.value = false
    }
  } catch (err) {
    console.error('加载匹配详情失败:', err)
    error.value = err.message || '加载匹配详情失败，请稍后重试'
    errorRetryable.value = err.isRetryable !== false
    
    // 如果是网络错误或超时，提供更详细的提示
    if (err.originalError) {
      const originalError = err.originalError
      if (originalError.code === 'ECONNABORTED') {
        error.value = '请求超时，服务器响应时间过长。请检查网络连接或稍后重试。'
      } else if (!originalError.response) {
        error.value = '无法连接到服务器，请检查网络连接或确认服务器是否正常运行。'
      }
    }
  } finally {
    loading.value = false
    retrying.value = false
  }
}

/**
 * 重试加载
 */
async function retryLoad() {
  await loadDetail(true)
}

/**
 * 导出匹配详情
 */
async function exportDetail() {
  if (!props.cacheKey) {
    ElMessage.error('缓存键不能为空')
    return
  }

  exporting.value = true

  try {
    const blob = await matchApi.exportMatchDetail(props.cacheKey, 'json', {
      enableRetry: true,
      maxRetries: 2,
      timeout: 60000
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `match_detail_${props.cacheKey}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (err) {
    console.error('导出匹配详情失败:', err)
    
    // 提供友好的错误提示
    let errorMessage = err.message || '导出失败，请稍后重试'
    
    // 如果错误可重试，提示用户可以重试
    if (err.isRetryable) {
      errorMessage += '。您可以稍后再次尝试导出。'
    }
    
    ElMessage.error({
      message: errorMessage,
      duration: 5000,
      showClose: true
    })
  } finally {
    exporting.value = false
  }
}

/**
 * 格式化时间戳
 */
function formatTimestamp(timestamp) {
  if (!timestamp) return '-'
  
  try {
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (e) {
    return timestamp
  }
}
</script>

<style scoped>
.dialog-content {
  min-height: 400px;
}

.error-container {
  margin-bottom: 20px;
}

.error-alert {
  margin-bottom: 20px;
}

.error-details {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.error-details p {
  margin: 0;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.detail-tabs {
  margin-top: 10px;
}

:deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 500;
}

.tab-badge {
  margin-left: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-info {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #909399;
}

.footer-actions {
  display: flex;
  gap: 10px;
}

.timestamp,
.duration {
  display: flex;
  align-items: center;
}

:deep(.el-dialog__header) {
  border-bottom: 1px solid #e4e7ed;
  padding: 20px 20px 15px;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-dialog__footer) {
  border-top: 1px solid #e4e7ed;
  padding: 15px 20px;
}
</style>
