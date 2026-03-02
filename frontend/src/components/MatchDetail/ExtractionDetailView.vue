<template>
  <div class="extraction-detail">
    <h4>特征提取配置</h4>
    
    <!-- 使用的分隔符 -->
    <div class="config-section">
      <h5>使用的分隔符</h5>
      <el-tag
        v-for="char in extractionDetail.split_chars"
        :key="char"
        class="split-char-tag"
      >
        {{ char }}
      </el-tag>
    </div>
    
    <!-- 识别的品牌 -->
    <div v-if="extractionDetail.identified_brands.length > 0" class="config-section">
      <h5>识别的品牌关键词</h5>
      <el-tag
        v-for="brand in extractionDetail.identified_brands"
        :key="brand"
        type="success"
        class="keyword-tag"
      >
        {{ brand }}
      </el-tag>
    </div>
    
    <!-- 识别的设备类型 -->
    <div v-if="extractionDetail.identified_device_types.length > 0" class="config-section">
      <h5>识别的设备类型关键词</h5>
      <el-tag
        v-for="type in extractionDetail.identified_device_types"
        :key="type"
        type="primary"
        class="keyword-tag"
      >
        {{ type }}
      </el-tag>
    </div>
    
    <!-- 提取的特征详情 -->
    <div class="features-section">
      <h5>提取的特征详情 ({{ extractionDetail.extracted_features.length }})</h5>
      <el-table :data="extractionDetail.extracted_features" size="small">
        <el-table-column prop="feature" label="特征" />
        <el-table-column prop="feature_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getFeatureTypeColor(row.feature_type)" size="small">
              {{ getFeatureTypeLabel(row.feature_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="150">
          <template #default="{ row }">
            {{ getSourceLabel(row.source) }}
          </template>
        </el-table-column>
        <el-table-column prop="quality_score" label="质量评分" width="100">
          <template #default="{ row }">
            <el-tag :type="getQualityScoreColor(row.quality_score)" size="small">
              {{ row.quality_score.toFixed(2) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="position" label="位置" width="80" />
      </el-table>
    </div>
    
    <!-- 被过滤的特征 -->
    <div v-if="extractionDetail.filtered_features.length > 0" class="filtered-section">
      <h5>被过滤的特征 ({{ extractionDetail.filtered_features.length }})</h5>
      <el-table :data="extractionDetail.filtered_features" size="small">
        <el-table-column prop="feature" label="特征" />
        <el-table-column prop="filter_reason" label="过滤原因" width="150">
          <template #default="{ row }">
            {{ getFilterReasonLabel(row.filter_reason) }}
          </template>
        </el-table-column>
        <el-table-column prop="quality_score" label="质量评分" width="100">
          <template #default="{ row }">
            <el-tag type="danger" size="small">
              {{ row.quality_score.toFixed(2) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  extractionDetail: {
    type: Object,
    required: true
  }
})

function getFeatureTypeColor(type) {
  const colors = {
    brand: 'success',
    device_type: 'primary',
    model: 'warning',
    parameter: 'info'
  }
  return colors[type] || 'info'
}

function getFeatureTypeLabel(type) {
  const labels = {
    brand: '品牌',
    device_type: '设备类型',
    model: '型号',
    parameter: '参数'
  }
  return labels[type] || type
}

function getSourceLabel(source) {
  const labels = {
    brand_keywords: '品牌关键词库',
    device_type_keywords: '设备类型关键词库',
    parameter_recognition: '参数识别'
  }
  return labels[source] || source
}

function getQualityScoreColor(score) {
  if (score >= 0.8) return 'success'
  if (score >= 0.5) return 'warning'
  return 'danger'
}

function getFilterReasonLabel(reason) {
  const labels = {
    low_quality: '质量评分低',
    duplicate: '重复特征',
    invalid: '无效特征'
  }
  return labels[reason] || reason
}
</script>

<style scoped>
.extraction-detail {
  padding: 16px;
}

h4 {
  margin-top: 0;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
}

h5 {
  margin-top: 16px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
}

.config-section {
  margin-bottom: 16px;
}

.split-char-tag,
.keyword-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.features-section,
.filtered-section {
  margin-bottom: 16px;
}
</style>
