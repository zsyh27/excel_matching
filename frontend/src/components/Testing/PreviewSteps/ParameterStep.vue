<template>
  <div class="preview-section">
    <h4>🔧 步骤2：技术参数提取</h4>
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
</template>

<script setup>
defineProps({
  data: Object
})
</script>

<style scoped src="./step-styles.css"></style>
