<template>
  <div class="device-type-recognition-test">
    <div class="section-header">
      <h2>🎯 设备类型识别测试</h2>
      <p class="description">输入设备描述，测试设备类型识别功能</p>
    </div>

    <div class="test-area">
      <div class="test-input">
        <input 
          v-model="testText" 
          type="text" 
          placeholder="输入设备描述进行测试，例如：CO浓度探测器、温度传感器、蝶阀"
          @input="onInputChange"
          @blur="testRecognition"
          @keyup.enter="testRecognition"
        />
        <div v-if="testing" class="testing-indicator">
          <span class="loading-spinner"></span>
          识别中...
        </div>
      </div>

      <div v-if="testResult" class="test-result">
        <div class="result-header">
          <h4>🎯 设备类型识别结果</h4>
          <div class="confidence-indicator">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: (testResult.confidence * 100) + '%' }"></div>
            </div>
            <span class="confidence-text">置信度: {{ (testResult.confidence * 100).toFixed(1) }}%</span>
          </div>
        </div>
        
        <div class="result-grid">
          <div class="result-item">
            <span class="label">设备类型:</span>
            <span class="value">{{ testResult.sub_type || testResult.main_type || '未识别' }}</span>
          </div>
          <div class="result-item">
            <span class="label">分类:</span>
            <span class="value">{{ testResult.main_type || '未知' }}</span>
          </div>
          <div class="result-item">
            <span class="label">置信度:</span>
            <div class="confidence-info">
              <span class="confidence-value" :class="getConfidenceClass(testResult.confidence)">
                {{ (testResult.confidence * 100).toFixed(1) }}%
              </span>
              <span class="confidence-tooltip" :title="getConfidenceExplanation(testResult.mode, testResult.confidence)">
                ❓
              </span>
            </div>
          </div>
          <div class="result-item">
            <span class="label">识别模式:</span>
            <div class="mode-info">
              <span class="value mode-badge" :class="testResult.mode">
                {{ getModeText(testResult.mode) }}
              </span>
              <span class="mode-description">{{ getModeDescription(testResult.mode) }}</span>
            </div>
          </div>
          <div class="result-item full-width">
            <span class="label">关键词:</span>
            <div class="keywords-info">
              <div class="keywords">
                <span v-for="keyword in testResult.keywords" :key="keyword" class="keyword-tag">
                  {{ keyword }}
                </span>
                <span v-if="!testResult.keywords || testResult.keywords.length === 0" class="no-keywords">
                  无关键词
                </span>
              </div>
              <div v-if="testResult.keywords && testResult.keywords.length > 0" class="keywords-description">
                通过关键词"{{ testResult.keywords.join('、') }}"识别出设备类型
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const testText = ref('')
const testResult = ref(null)
const testing = ref(false)

// 防抖定时器
let debounceTimer = null

const onInputChange = () => {
  // 清除之前的定时器
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
  
  // 设置新的定时器
  debounceTimer = setTimeout(() => {
    if (testText.value.trim()) {
      testRecognition()
    }
  }, 500)
}

const testRecognition = async () => {
  if (!testText.value.trim()) {
    testResult.value = null
    return
  }

  testing.value = true
  try {
    const response = await fetch('/api/intelligent-extraction/device-type/recognize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text: testText.value })
    })

    const result = await response.json()
    
    if (result.success && result.data) {
      testResult.value = result.data
    } else {
      console.error('识别失败:', result.error)
      testResult.value = null
    }
  } catch (error) {
    console.error('测试失败:', error)
    testResult.value = null
  } finally {
    testing.value = false
  }
}

const getModeText = (mode) => {
  switch (mode) {
    case 'exact': return '精确匹配'
    case 'fuzzy': return '模糊匹配'
    case 'keyword': return '关键词匹配'
    case 'inference': return '类型推断'
    default: return '未知'
  }
}

const getModeDescription = (mode) => {
  switch (mode) {
    case 'exact': return '完全匹配设备类型名称'
    case 'fuzzy': return '部分匹配设备类型'
    case 'keyword': return '通过关键词组合识别'
    case 'inference': return '根据关键词推断类型'
    default: return ''
  }
}

const getConfidenceClass = (confidence) => {
  if (confidence >= 0.9) return 'high'
  if (confidence >= 0.7) return 'medium'
  return 'low'
}

const getConfidenceExplanation = (mode, confidence) => {
  const confidencePercent = (confidence * 100).toFixed(1)
  switch (mode) {
    case 'exact':
      return `精确匹配 - 完全匹配设备类型名称，置信度 ${confidencePercent}%`
    case 'fuzzy':
      return `模糊匹配 - 部分匹配设备类型，置信度 ${confidencePercent}%`
    case 'keyword':
      return `关键词匹配 - 通过关键词组合识别，置信度 ${confidencePercent}%`
    case 'inference':
      return `类型推断 - 根据关键词推断类型，置信度 ${confidencePercent}%`
    default:
      return `置信度 ${confidencePercent}%`
  }
}
</script>

<style scoped>
.device-type-recognition-test {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.section-header {
  margin-bottom: 30px;
}

.section-header h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #303133;
}

.description {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.test-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.test-input {
  position: relative;
}

.test-input input {
  width: 100%;
  padding: 12px 16px;
  font-size: 14px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.test-input input:focus {
  outline: none;
  border-color: #409EFF;
}

.testing-indicator {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409EFF;
  font-size: 14px;
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #409EFF;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.test-result {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e4e7ed;
}

.result-header h4 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.confidence-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  width: 120px;
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #67c23a, #409EFF);
  transition: width 0.3s;
}

.confidence-text {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-item.full-width {
  grid-column: 1 / -1;
}

.result-item .label {
  font-size: 13px;
  color: #909399;
  font-weight: 500;
}

.result-item .value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.confidence-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.confidence-value {
  font-size: 16px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 4px;
}

.confidence-value.high {
  color: #67c23a;
  background: #f0f9ff;
}

.confidence-value.medium {
  color: #e6a23c;
  background: #fdf6ec;
}

.confidence-value.low {
  color: #f56c6c;
  background: #fef0f0;
}

.confidence-tooltip {
  cursor: help;
  font-size: 14px;
  opacity: 0.6;
}

.mode-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mode-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
  width: fit-content;
}

.mode-badge.exact {
  background: #f0f9ff;
  color: #409EFF;
}

.mode-badge.fuzzy {
  background: #f4f4f5;
  color: #909399;
}

.mode-badge.keyword {
  background: #fdf6ec;
  color: #e6a23c;
}

.mode-badge.inference {
  background: #fef0f0;
  color: #f56c6c;
}

.mode-description {
  font-size: 12px;
  color: #909399;
}

.keywords-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  display: inline-block;
  padding: 4px 12px;
  background: #ecf5ff;
  color: #409EFF;
  border-radius: 4px;
  font-size: 13px;
}

.no-keywords {
  color: #909399;
  font-size: 13px;
}

.keywords-description {
  font-size: 12px;
  color: #606266;
  font-style: italic;
}
</style>
