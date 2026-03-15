<template>
  <div class="preview-section">
    <h4>🔧 步骤2：参数候选提取</h4>
    
    <!-- 参数候选列表 -->
    <div v-if="parameterCandidates?.length" class="candidates-section">
      <div class="section-subtitle">提取到的参数候选（共{{ parameterCandidates.length }}个）</div>
      <div class="candidates-list">
        <div v-for="(candidate, index) in parameterCandidates" :key="index" class="candidate-item">
          <span class="candidate-type">{{ getTypeLabel(candidate.param_type) }}</span>
          <span class="candidate-value">{{ candidate.value }}</span>
          <span class="candidate-confidence">{{ (candidate.confidence * 100).toFixed(0) }}%</span>
        </div>
      </div>
    </div>
    
    <!-- 兼容旧版显示 -->
    <div v-if="!parameterCandidates?.length">
      <div class="preview-item">
        <span class="label">量程参数:</span>
        <span class="value">
          {{ data?.range?.value || '未提取' }}
          <span v-if="data?.range?.confidence" class="confidence">
            ({{ (data.range.confidence * 100).toFixed(1) }}%)
          </span>
        </span>
      </div>
      <div class="preview-item">
        <span class="label">输出信号:</span>
        <span class="value">
          {{ data?.output?.value || '未提取' }}
          <span v-if="data?.output?.confidence" class="confidence">
            ({{ (data.output.confidence * 100).toFixed(1) }}%)
          </span>
        </span>
      </div>
      <div class="preview-item">
        <span class="label">精度参数:</span>
        <span class="value">
          {{ data?.accuracy?.value || '未提取' }}
          <span v-if="data?.accuracy?.confidence" class="confidence">
            ({{ (data.accuracy.confidence * 100).toFixed(1) }}%)
          </span>
        </span>
      </div>
      <div v-if="data?.specs?.length" class="preview-item">
        <span class="label">规格参数:</span>
        <span class="value">
          <span 
            v-for="(spec, index) in data.specs" 
            :key="index"
            class="feature-tag"
          >
            {{ spec }}
          </span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: Object,
  fullData: Object
})

const parameterCandidates = computed(() => {
  return props.fullData?.parameter_candidates || []
})

const getTypeLabel = (type) => {
  const labels = {
    'range': '量程',
    'output': '输出信号',
    'accuracy': '精度',
    'temperature': '温度',
    'resolution': '分辨率',
    'communication': '通讯方式',
    'medium': '介质',
    'brand': '品牌'
  }
  return labels[type] || type
}
</script>

<style scoped src="./step-styles.css"></style>

<style scoped>
.candidates-section {
  margin-top: 12px;
}

.section-subtitle {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.candidates-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.candidate-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.candidate-type {
  font-size: 12px;
  color: #409eff;
  background: #ecf5ff;
  padding: 2px 8px;
  border-radius: 4px;
  min-width: 60px;
  text-align: center;
}

.candidate-value {
  flex: 1;
  font-size: 13px;
  color: #303133;
}

.candidate-confidence {
  font-size: 12px;
  color: #67c23a;
  font-weight: 600;
}
</style>
