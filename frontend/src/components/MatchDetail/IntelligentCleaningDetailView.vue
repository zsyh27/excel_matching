<template>
  <div class="intelligent-cleaning-detail">
    <h4>智能清理详情</h4>
    
    <!-- 应用的规则 -->
    <div class="applied-rules">
      <el-tag
        v-for="rule in cleaningDetail.applied_rules"
        :key="rule"
        type="success"
        class="rule-tag"
      >
        {{ getRuleLabel(rule) }}
      </el-tag>
      <el-tag v-if="cleaningDetail.applied_rules.length === 0" type="info">
        未应用任何清理规则
      </el-tag>
    </div>
    
    <!-- 统计信息 -->
    <div class="statistics">
      <el-descriptions :column="3" border size="small">
        <el-descriptions-item label="原始长度">
          {{ cleaningDetail.original_length }}
        </el-descriptions-item>
        <el-descriptions-item label="清理后长度">
          {{ cleaningDetail.cleaned_length }}
        </el-descriptions-item>
        <el-descriptions-item label="删除长度">
          <el-tag type="warning">{{ cleaningDetail.deleted_length }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </div>
    
    <!-- 截断分隔符匹配 -->
    <div v-if="cleaningDetail.truncation_matches.length > 0" class="matches-section">
      <h5>截断分隔符匹配</h5>
      <el-table :data="cleaningDetail.truncation_matches" size="small">
        <el-table-column prop="delimiter" label="分隔符" width="120" />
        <el-table-column prop="position" label="位置" width="80" />
        <el-table-column prop="deleted_text" label="删除的文本" show-overflow-tooltip />
      </el-table>
    </div>
    
    <!-- 噪音模式匹配 -->
    <div v-if="cleaningDetail.noise_pattern_matches.length > 0" class="matches-section">
      <h5>噪音段落匹配</h5>
      <el-table :data="cleaningDetail.noise_pattern_matches" size="small">
        <el-table-column prop="pattern" label="模式" width="200" show-overflow-tooltip />
        <el-table-column prop="position" label="位置" width="80" />
        <el-table-column prop="matched_text" label="匹配的文本" show-overflow-tooltip />
      </el-table>
    </div>
    
    <!-- 元数据标签匹配 -->
    <div v-if="cleaningDetail.metadata_tag_matches.length > 0" class="matches-section">
      <h5>元数据标签匹配</h5>
      <el-table :data="cleaningDetail.metadata_tag_matches" size="small">
        <el-table-column prop="tag" label="标签" width="120" />
        <el-table-column prop="position" label="位置" width="80" />
        <el-table-column prop="matched_text" label="匹配的内容" show-overflow-tooltip />
      </el-table>
    </div>
    
    <!-- 删除无关关键词匹配 -->
    <div v-if="cleaningDetail.ignore_keyword_matches && cleaningDetail.ignore_keyword_matches.length > 0" class="matches-section">
      <h5>删除无关关键词匹配</h5>
      <el-table :data="cleaningDetail.ignore_keyword_matches" size="small">
        <el-table-column prop="keyword" label="关键词" width="150" />
        <el-table-column prop="count" label="出现次数" width="100" />
        <el-table-column label="匹配位置">
          <template #default="scope">
            <el-tag 
              v-for="(pos, index) in scope.row.positions" 
              :key="index"
              size="small"
              type="info"
              style="margin-right: 5px;"
            >
              {{ pos }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 文本对比 -->
    <div class="text-comparison">
      <h5>文本对比</h5>
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="comparison-box">
            <div class="comparison-label">清理前</div>
            <el-input
              v-model="cleaningDetail.before_text"
              type="textarea"
              :rows="4"
              readonly
            />
          </div>
        </el-col>
        <el-col :span="12">
          <div class="comparison-box">
            <div class="comparison-label">清理后</div>
            <el-input
              v-model="cleaningDetail.after_text"
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
  cleaningDetail: {
    type: Object,
    required: true
  }
})

function getRuleLabel(rule) {
  const labels = {
    truncation: '截断分隔符',
    noise_pattern: '噪音段落',
    metadata_tag: '元数据标签',
    ignore_keywords: '删除无关关键词',
    separator_unification: '分隔符统一'
  }
  return labels[rule] || rule
}
</script>

<style scoped>
.intelligent-cleaning-detail {
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

.applied-rules {
  margin-bottom: 16px;
}

.rule-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.statistics {
  margin-bottom: 16px;
}

.matches-section {
  margin-bottom: 16px;
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
