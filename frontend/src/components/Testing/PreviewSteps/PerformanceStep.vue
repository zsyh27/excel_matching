<template>
  <div class="preview-section">
    <h4>⏱️ 性能统计</h4>
    <div class="preview-item">
      <span class="label">总处理时间:</span>
      <span class="value">{{ data?.total_time_ms?.toFixed(2) || 0 }}ms</span>
    </div>
    <div class="preview-item">
      <span class="label">各步骤耗时:</span>
      <span class="value">
        步骤1: {{ data?.step1_time_ms?.toFixed(2) || 0 }}ms, 
        步骤2: {{ data?.step2_time_ms?.toFixed(2) || 0 }}ms, 
        步骤3: {{ data?.step3_time_ms?.toFixed(2) || 0 }}ms, 
        步骤4: {{ data?.step4_time_ms?.toFixed(2) || 0 }}ms
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
