<template>
  <div class="preview-section">
    <h4>ℹ️ 步骤3：辅助信息提取</h4>
    <div class="preview-item">
      <span class="label">品牌信息:</span>
      <span class="value">{{ data?.brand || '未识别' }}</span>
    </div>
    <div class="preview-item">
      <span class="label">适用介质:</span>
      <span class="value">{{ data?.medium || '未识别' }}</span>
    </div>
    <div class="preview-item">
      <span class="label">设备型号:</span>
      <span class="value">{{ data?.model || '未识别' }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: Object
})
</script>

<style scoped src="./step-styles.css"></style>
