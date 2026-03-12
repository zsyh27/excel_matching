<template>
  <div v-if="data" class="preview-section">
    <h4>🔧 步骤0：文本预处理</h4>
    <div class="preview-item">
      <span class="label">原始文本:</span>
      <span class="value">{{ data.original || '无' }}</span>
    </div>
    <div class="preview-item">
      <span class="label">归一化文本:</span>
      <span class="value">{{ data.normalized || '无' }}</span>
    </div>
    <div class="preview-item">
      <span class="label">提取特征:</span>
      <span class="value">
        <span 
          v-for="(feature, index) in (data.features || [])" 
          :key="index"
          class="feature-tag"
        >
          {{ feature }}
        </span>
        <span v-if="!(data.features?.length)" class="no-data">无特征</span>
      </span>
    </div>
    <div v-if="data.normalization_detail" class="preview-item">
      <span class="label">归一化映射:</span>
      <span class="value">
        {{ data.normalization_detail.normalization_mappings?.length || 0 }} 个映射
        <br>
        全局配置: {{ data.normalization_detail.global_configs?.join(', ') || '无' }}
      </span>
    </div>
    <div v-if="data.extraction_detail" class="preview-item">
      <span class="label">特征提取:</span>
      <span class="value">
        提取: {{ data.extraction_detail.extracted_features?.length || 0 }} 个
        <br>
        过滤: {{ data.extraction_detail.filtered_features?.length || 0 }} 个
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
