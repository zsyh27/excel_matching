<template>
  <el-dialog
    v-model="visible"
    title="批量查看匹配详情"
    width="95%"
    :close-on-click-modal="false"
    class="batch-detail-dialog"
  >
    <div class="batch-detail-container">
      <!-- 左侧设备列表 -->
      <div class="device-list-panel">
        <div class="panel-header">
          <span>设备列表 ({{ deviceItems.length }})</span>
        </div>
        <div class="device-list">
          <div
            v-for="(item, index) in deviceItems"
            :key="item.cacheKey"
            class="device-item"
            :class="{ active: currentIndex === index }"
            @click="selectDevice(index)"
          >
            <div class="device-item-header">
              <span class="device-number">{{ item.rowNumber }}</span>
              <el-tag
                :type="getStatusType(item.matchResult)"
                size="small"
              >
                {{ getStatusText(item.matchResult) }}
              </el-tag>
            </div>
            <div class="device-item-description">
              {{ item.deviceDescription }}
            </div>
            <div v-if="item.matchResult && item.matchResult.matched_device_text" class="device-item-match">
              <el-icon><Check /></el-icon>
              {{ item.matchResult.matched_device_text }}
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧详情面板 -->
      <div class="detail-panel">
        <div class="panel-header">
          <span>详情 - 设备 {{ currentDevice?.rowNumber }}</span>
          <div class="navigation-buttons">
            <el-button
              size="small"
              :disabled="currentIndex === 0"
              @click="previousDevice"
            >
              <el-icon><ArrowLeft /></el-icon>
              上一个
            </el-button>
            <span class="nav-info">{{ currentIndex + 1 }} / {{ deviceItems.length }}</span>
            <el-button
              size="small"
              :disabled="currentIndex === deviceItems.length - 1"
              @click="nextDevice"
            >
              下一个
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-container">
          <el-result
            icon="error"
            title="加载失败"
            :sub-title="error"
          >
            <template #extra>
              <el-button type="primary" @click="loadCurrentDetail">重试</el-button>
            </template>
          </el-result>
        </div>

        <!-- 详情内容 -->
        <div v-else-if="currentDetail" class="detail-content">
          <el-tabs v-model="activeTab">
            <!-- Tab 1: 特征提取 -->
            <el-tab-pane label="特征提取" name="extraction">
              <FeatureExtractionView :preprocessing="currentDetail.preprocessing" />
            </el-tab-pane>

            <!-- Tab 2: 候选规则 -->
            <el-tab-pane label="候选规则" name="candidates">
              <CandidateRulesView :candidates="currentDetail.candidates" />
            </el-tab-pane>

            <!-- Tab 3: 匹配结果 -->
            <el-tab-pane label="匹配结果" name="result">
              <MatchResultView
                :final-result="currentDetail.final_result"
                :decision-reason="currentDetail.decision_reason"
                :suggestions="currentDetail.optimization_suggestions"
              />
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- 空状态 -->
        <el-empty
          v-else
          description="请选择一个设备查看详情"
          :image-size="150"
        />
      </div>
    </div>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowRight, Check, Loading } from '@element-plus/icons-vue'
import { getMatchDetail } from '@/api/match'
import FeatureExtractionView from './FeatureExtractionView.vue'
import CandidateRulesView from './CandidateRulesView.vue'
import MatchResultView from './MatchResultView.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  deviceItems: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

// 状态管理
const visible = ref(false)
const currentIndex = ref(0)
const currentDetail = ref(null)
const loading = ref(false)
const error = ref(null)
const activeTab = ref('extraction')

// 详情缓存
const detailCache = ref(new Map())

// 计算属性
const currentDevice = computed(() => {
  return props.deviceItems[currentIndex.value] || null
})

// 监听 modelValue 变化
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
  if (newVal && props.deviceItems.length > 0) {
    currentIndex.value = 0
    loadCurrentDetail()
  }
})

// 监听 visible 变化
watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
  if (!newVal) {
    // 关闭时清理状态
    currentDetail.value = null
    currentIndex.value = 0
    detailCache.value.clear()
    error.value = null
  }
})

/**
 * 选择设备
 * 验证需求: Requirements 10.2, 10.4
 */
const selectDevice = (index) => {
  if (index >= 0 && index < props.deviceItems.length) {
    currentIndex.value = index
    loadCurrentDetail()
  }
}

/**
 * 上一个设备
 * 验证需求: Requirements 10.5
 */
const previousDevice = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
    loadCurrentDetail()
  }
}

/**
 * 下一个设备
 * 验证需求: Requirements 10.5
 */
const nextDevice = () => {
  if (currentIndex.value < props.deviceItems.length - 1) {
    currentIndex.value++
    loadCurrentDetail()
  }
}

/**
 * 加载当前设备的详情
 * 验证需求: Requirements 10.3
 */
const loadCurrentDetail = async () => {
  if (!currentDevice.value) {
    return
  }

  const cacheKey = currentDevice.value.cacheKey

  // 检查缓存
  if (detailCache.value.has(cacheKey)) {
    currentDetail.value = detailCache.value.get(cacheKey)
    error.value = null
    return
  }

  // 加载详情
  loading.value = true
  error.value = null

  try {
    const response = await getMatchDetail(cacheKey)
    if (response.data.success) {
      const detail = response.data.detail
      detailCache.value.set(cacheKey, detail)
      currentDetail.value = detail
    } else {
      throw new Error(response.data.error_message || '加载详情失败')
    }
  } catch (err) {
    console.error('加载匹配详情失败:', err)
    error.value = err.message || '加载详情失败，请稍后重试'
    currentDetail.value = null
  } finally {
    loading.value = false
  }
}

/**
 * 获取匹配状态类型
 * 验证需求: Requirements 10.3
 */
const getStatusType = (matchResult) => {
  if (!matchResult) return 'info'
  return matchResult.match_status === 'success' ? 'success' : 'warning'
}

/**
 * 获取匹配状态文本
 * 验证需求: Requirements 10.3
 */
const getStatusText = (matchResult) => {
  if (!matchResult) return '未匹配'
  return matchResult.match_status === 'success' ? '成功' : '失败'
}
</script>

<style scoped>
.batch-detail-dialog :deep(.el-dialog__body) {
  padding: 0;
  height: 70vh;
}

.batch-detail-container {
  display: flex;
  height: 100%;
}

/* 左侧设备列表 */
.device-list-panel {
  width: 350px;
  border-right: 1px solid #dcdfe6;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid #dcdfe6;
  font-weight: 600;
  font-size: 15px;
  color: #303133;
  background: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.device-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.device-item {
  padding: 12px;
  margin-bottom: 8px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.device-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.device-item.active {
  border-color: #409eff;
  background: #ecf5ff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.device-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.device-number {
  font-weight: 600;
  color: #409eff;
  font-size: 14px;
}

.device-item-description {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.device-item-match {
  font-size: 12px;
  color: #67c23a;
  display: flex;
  align-items: center;
  gap: 4px;
}

.device-item-match .el-icon {
  font-size: 14px;
}

/* 右侧详情面板 */
.detail-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.navigation-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-info {
  font-size: 13px;
  color: #909399;
  font-weight: normal;
}

.detail-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.loading-container,
.error-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 12px;
  color: #909399;
}

.loading-container .el-icon {
  font-size: 32px;
}

/* 滚动条样式 */
.device-list::-webkit-scrollbar,
.detail-content::-webkit-scrollbar {
  width: 6px;
}

.device-list::-webkit-scrollbar-thumb,
.detail-content::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}

.device-list::-webkit-scrollbar-thumb:hover,
.detail-content::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc;
}
</style>
