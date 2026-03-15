<template>
  <div class="match-weights-editor">
    <div class="editor-header">
      <h2>匹配权重配置</h2>
      <p class="description">配置设备匹配评分的权重值。权重值越高，该维度对最终评分的影响越大。</p>
    </div>

    <div class="weights-container">
      <div class="weight-item">
        <div class="weight-info">
          <span class="weight-name">设备类型匹配</span>
          <span class="weight-desc">设备类型完全匹配的权重（如：传感器、控制器、阀门）</span>
        </div>
        <div class="weight-control">
          <input 
            type="number" 
            v-model.number="localWeights.device_type"
            min="0"
            max="100"
            step="5"
            @input="handleWeightChange"
          />
          <span class="weight-percent">%</span>
        </div>
      </div>

      <div class="weight-item">
        <div class="weight-info">
          <span class="weight-name">设备类型关键词匹配</span>
          <span class="weight-desc">设备类型关键词匹配到设备参数的权重（如：PM匹配到PM2.5）</span>
        </div>
        <div class="weight-control">
          <input 
            type="number" 
            v-model.number="localWeights.keyword"
            min="0"
            max="100"
            step="5"
            @input="handleWeightChange"
          />
          <span class="weight-percent">%</span>
        </div>
      </div>

      <div class="weight-item">
        <div class="weight-info">
          <span class="weight-name">参数匹配</span>
          <span class="weight-desc">参数匹配的权重（量程、输出信号、精度等）</span>
        </div>
        <div class="weight-control">
          <input 
            type="number" 
            v-model.number="localWeights.parameters"
            min="0"
            max="100"
            step="5"
            @input="handleWeightChange"
          />
          <span class="weight-percent">%</span>
        </div>
      </div>

      <div class="weight-item">
        <div class="weight-info">
          <span class="weight-name">品牌匹配</span>
          <span class="weight-desc">品牌完全匹配的权重（如：霍尼韦尔、西门子）</span>
        </div>
        <div class="weight-control">
          <input 
            type="number" 
            v-model.number="localWeights.brand"
            min="0"
            max="100"
            step="5"
            @input="handleWeightChange"
          />
          <span class="weight-percent">%</span>
        </div>
      </div>

      <div class="weight-item">
        <div class="weight-info">
          <span class="weight-name">其他匹配</span>
          <span class="weight-desc">其他特征匹配的权重（介质、其他特征）</span>
        </div>
        <div class="weight-control">
          <input 
            type="number" 
            v-model.number="localWeights.others"
            min="0"
            max="100"
            step="5"
            @input="handleWeightChange"
          />
          <span class="weight-percent">%</span>
        </div>
      </div>
    </div>

    <div class="weight-summary">
      <div class="summary-row">
        <span class="summary-label">权重总计:</span>
        <span :class="['summary-value', { 'error': totalWeight !== 100 }]">
          {{ totalWeight }}%
        </span>
        <span v-if="totalWeight !== 100" class="summary-hint">
          ⚠️ 权重总计应为100%
        </span>
        <span v-else class="summary-hint success">
          ✓ 权重配置正确
        </span>
      </div>
    </div>

    <div class="weight-tips">
      <h4>💡 配置说明</h4>
      <ul>
        <li><strong>型号精确匹配优先</strong>：如果文本中提取到型号，系统会优先进行型号精确匹配，找到则直接返回该设备（100分）</li>
        <li><strong>权重评分匹配</strong>：如果没有型号，则使用权重评分进行匹配</li>
        <li><strong>权重总和必须为100%</strong>：确保各维度权重之和为100%</li>
        <li><strong>设备类型关键词匹配</strong>：与设备类型匹配同等重要，是设备类型识别的核心结果</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  },
  fullConfig: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const localWeights = ref({
  device_type: 30,
  keyword: 30,
  parameters: 20,
  brand: 15,
  others: 5
})

const totalWeight = computed(() => {
  return Object.values(localWeights.value).reduce((sum, val) => sum + (val || 0), 0)
})

watch(() => props.modelValue, (newVal) => {
  if (newVal && Object.keys(newVal).length > 0) {
    localWeights.value = { ...newVal }
  }
}, { immediate: true, deep: true })

const handleWeightChange = () => {
  emit('update:modelValue', { ...localWeights.value })
  emit('change')
}
</script>

<style scoped>
.match-weights-editor {
  padding: 20px;
}

.editor-header {
  margin-bottom: 24px;
}

.editor-header h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #303133;
}

.description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.weights-container {
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  overflow: hidden;
}

.weight-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
}

.weight-item:last-child {
  border-bottom: none;
}

.weight-info {
  flex: 1;
}

.weight-name {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.weight-desc {
  display: block;
  font-size: 13px;
  color: #909399;
}

.weight-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.weight-control input {
  width: 80px;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
}

.weight-control input:focus {
  outline: none;
  border-color: #409eff;
}

.weight-percent {
  font-size: 14px;
  color: #606266;
}

.weight-summary {
  margin-top: 20px;
  padding: 16px 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.summary-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.summary-label {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
}

.summary-value {
  font-size: 20px;
  font-weight: 700;
  color: #67c23a;
}

.summary-value.error {
  color: #f56c6c;
}

.summary-hint {
  font-size: 13px;
  color: #f56c6c;
}

.summary-hint.success {
  color: #67c23a;
}

.weight-tips {
  margin-top: 20px;
  padding: 16px 20px;
  background: #fdf6ec;
  border-radius: 8px;
  border: 1px solid #faecd8;
}

.weight-tips h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #e6a23c;
}

.weight-tips ul {
  margin: 0;
  padding-left: 20px;
}

.weight-tips li {
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.weight-tips li:last-child {
  margin-bottom: 0;
}
</style>
