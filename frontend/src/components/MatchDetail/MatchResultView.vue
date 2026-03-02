<template>
  <div class="match-result">
    <el-result
      :icon="finalResult.match_status === 'success' ? 'success' : 'error'"
      :title="finalResult.match_status === 'success' ? '匹配成功' : '匹配失败'"
    >
      <template #sub-title>
        <div class="result-details">
          <el-descriptions :column="1" border>
            <el-descriptions-item v-if="finalResult.matched_device_text" label="匹配设备">
              <span class="device-text">{{ finalResult.matched_device_text }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="匹配得分">
              <el-tag :type="getScoreTagType()" size="large">
                {{ finalResult.match_score.toFixed(2) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item v-if="finalResult.threshold" label="匹配阈值">
              <span class="threshold-text">{{ finalResult.threshold }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="决策原因">
              <span class="reason-text">{{ decisionReason }}</span>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </template>
      
      <template #extra>
        <div v-if="suggestions && suggestions.length > 0" class="suggestions">
          <h4>
            <el-icon><InfoFilled /></el-icon>
            优化建议
          </h4>
          <el-alert
            v-for="(suggestion, index) in suggestions"
            :key="index"
            :title="suggestion"
            type="info"
            :closable="false"
            class="suggestion-item"
            show-icon
          />
        </div>
        <el-empty
          v-else
          description="暂无优化建议"
          :image-size="80"
        />
      </template>
    </el-result>
  </div>
</template>

<script setup>
import { InfoFilled } from '@element-plus/icons-vue'

/**
 * 最终匹配结果展示组件
 * 
 * 展示匹配结果、决策原因和优化建议
 * 验证需求: Requirements 5.1-5.5, 12.1-12.5
 */

const props = defineProps({
  finalResult: {
    type: Object,
    required: true,
    validator: (value) => {
      return value &&
             typeof value.match_status === 'string' &&
             typeof value.match_score === 'number'
    }
  },
  decisionReason: {
    type: String,
    required: true
  },
  suggestions: {
    type: Array,
    default: () => []
  }
})

/**
 * 获取得分标签类型
 */
function getScoreTagType() {
  if (props.finalResult.match_status === 'success') {
    return 'success'
  }
  
  // 如果有阈值，判断得分与阈值的关系
  if (props.finalResult.threshold) {
    const score = props.finalResult.match_score
    const threshold = props.finalResult.threshold
    const diff = threshold - score
    
    if (diff <= 1) {
      return 'warning' // 接近阈值
    }
  }
  
  return 'danger'
}
</script>

<style scoped>
.match-result {
  padding: 20px;
}

:deep(.el-result__title) {
  font-size: 24px;
  font-weight: bold;
  margin-top: 20px;
}

.result-details {
  margin: 20px auto;
  max-width: 600px;
}

.device-text {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.threshold-text {
  font-size: 16px;
  font-weight: 600;
  color: #606266;
}

.reason-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.suggestions {
  margin-top: 30px;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
}

.suggestions h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #303133;
  font-weight: 600;
}

.suggestion-item {
  margin-bottom: 12px;
}

.suggestion-item:last-child {
  margin-bottom: 0;
}

:deep(.el-alert__title) {
  font-size: 14px;
  line-height: 1.6;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  width: 120px;
}

:deep(.el-descriptions__content) {
  font-size: 15px;
}
</style>
