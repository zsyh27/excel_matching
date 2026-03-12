<template>
  <div class="preview-section">
    <h4>📋 步骤1：设备类型识别</h4>
    <div class="preview-item">
      <span class="label">识别结果:</span>
      <span class="value">{{ data?.sub_type || '未识别' }}</span>
    </div>
    <div class="preview-item">
      <span class="label">主类型:</span>
      <span class="value">{{ data?.main_type || '未知' }}</span>
    </div>
    <div class="preview-item">
      <span class="label">置信度:</span>
      <span class="value">{{ ((data?.confidence || 0) * 100).toFixed(1) }}%</span>
    </div>
    <div class="preview-item">
      <span class="label">识别模式:</span>
      <span class="value">{{ getModeText(data?.mode) }}</span>
    </div>
    <div class="preview-item">
      <span class="label">关键词:</span>
      <span class="value">
        <span 
          v-for="(keyword, index) in (data?.keywords || [])" 
          :key="index"
          class="feature-tag"
        >
          {{ keyword }}
        </span>
        <span v-if="!(data?.keywords?.length)" class="no-data">无关键词</span>
      </span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: Object
})

const getModeText = (mode) => {
  switch (mode) {
    case 'exact': return '精确匹配'
    case 'fuzzy': return '模糊匹配'
    case 'keyword': return '关键词匹配'
    case 'inference': return '类型推断'
    default: return '未知'
  }
}
</script>

<style scoped src="./step-styles.css"></style>
