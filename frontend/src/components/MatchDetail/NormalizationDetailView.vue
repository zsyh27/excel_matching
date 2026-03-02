<template>
  <div class="normalization-detail">
    <h4>归一化详情</h4>
    
    <!-- 同义词映射 -->
    <div v-if="normalizationDetail.synonym_mappings.length > 0" class="mappings-section">
      <h5>同义词映射 ({{ normalizationDetail.synonym_mappings.length }})</h5>
      <el-table :data="normalizationDetail.synonym_mappings" size="small">
        <el-table-column prop="rule_name" label="规则" width="150" />
        <el-table-column prop="from_text" label="转换前" width="150" />
        <el-table-column label="→" width="50" align="center">
          <template>→</template>
        </el-table-column>
        <el-table-column prop="to_text" label="转换后" width="150" />
        <el-table-column prop="position" label="位置" width="80" />
      </el-table>
    </div>
    
    <!-- 归一化映射 -->
    <div v-if="normalizationDetail.normalization_mappings.length > 0" class="mappings-section">
      <h5>归一化映射 ({{ normalizationDetail.normalization_mappings.length }})</h5>
      <el-table :data="normalizationDetail.normalization_mappings" size="small">
        <el-table-column prop="rule_name" label="规则" width="150" />
        <el-table-column prop="from_text" label="转换前" width="150" />
        <el-table-column label="→" width="50" align="center">
          <template>→</template>
        </el-table-column>
        <el-table-column prop="to_text" label="转换后" width="150" />
        <el-table-column prop="position" label="位置" width="80" />
      </el-table>
    </div>
    
    <!-- 全局配置 -->
    <div v-if="normalizationDetail.global_configs.length > 0" class="global-configs">
      <h5>应用的全局配置</h5>
      <el-tag
        v-for="config in normalizationDetail.global_configs"
        :key="config"
        type="primary"
        class="config-tag"
      >
        {{ config }}
      </el-tag>
    </div>
    
    <!-- 文本对比 -->
    <div class="text-comparison">
      <h5>文本对比</h5>
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="comparison-box">
            <div class="comparison-label">归一化前</div>
            <el-input
              v-model="normalizationDetail.before_text"
              type="textarea"
              :rows="4"
              readonly
            />
          </div>
        </el-col>
        <el-col :span="12">
          <div class="comparison-box">
            <div class="comparison-label">归一化后</div>
            <el-input
              v-model="normalizationDetail.after_text"
              type="textarea"
              :rows="4"
              readonly
            />
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  normalizationDetail: {
    type: Object,
    required: true
  }
})
</script>

<style scoped>
.normalization-detail {
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

.mappings-section {
  margin-bottom: 16px;
}

.global-configs {
  margin-bottom: 16px;
}

.config-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.text-comparison {
  margin-top: 16px;
}

.comparison-box {
  margin-bottom: 8px;
}

.comparison-label {
  font-weight: 600;
  margin-bottom: 8px;
  color: #606266;
}
</style>
