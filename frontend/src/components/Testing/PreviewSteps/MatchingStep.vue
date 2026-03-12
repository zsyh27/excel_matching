<template>
  <div class="preview-section">
    <h4>🏆 步骤4：智能匹配评分</h4>
    <div class="preview-item">
      <span class="label">匹配状态:</span>
      <span :class="['value', data?.status === 'success' ? 'success' : 'failed']">
        {{ data?.status === 'success' ? '成功' : '失败' }}
      </span>
    </div>
    <div class="preview-item">
      <span class="label">候选设备:</span>
      <span class="value">{{ data?.candidates?.length || 0 }} 个</span>
    </div>
    <div v-if="data?.candidates?.length" class="preview-item">
      <span class="label">最佳匹配:</span>
      <span class="value">
        {{ data.candidates[0]?.device_name || '无' }}
        ({{ data.candidates[0]?.total_score?.toFixed(1) || 0 }}分)
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
