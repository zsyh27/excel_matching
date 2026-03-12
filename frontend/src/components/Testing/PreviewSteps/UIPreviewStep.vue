<template>
  <div class="preview-section">
    <h4>🖥️ 步骤5：用户界面展示</h4>
    <div class="preview-item">
      <span class="label">默认选中:</span>
      <span class="value">
        {{ getDefaultSelectedDevice()?.device_name || '无' }}
      </span>
    </div>
    <div class="preview-item">
      <span class="label">筛选选项:</span>
      <span class="value">
        <span 
          v-for="(option, index) in (data?.filter_options || [])" 
          :key="index"
          class="feature-tag"
        >
          {{ option }}
        </span>
        <span v-if="!(data?.filter_options?.length)" class="no-data">无筛选选项</span>
      </span>
    </div>
    <div class="preview-item">
      <span class="label">显示格式:</span>
      <span class="value">{{ data?.display_format || '未知' }}</span>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  data: Object,
  matching: Object
})

const getDefaultSelectedDevice = () => {
  if (!props.matching?.candidates?.length) return null
  return props.matching.candidates[0]
}
</script>

<style scoped src="./step-styles.css"></style>
