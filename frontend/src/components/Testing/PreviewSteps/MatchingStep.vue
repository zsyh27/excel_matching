<template>
  <div class="preview-section matching-step">
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

    <div v-if="data?.candidates?.length" class="matching-details">
      <div class="section-title">📊 最佳匹配分析</div>
      
      <div class="best-candidate">
        <div class="candidate-header" @click="toggleBestMatch">
          <div class="header-left">
            <span class="rank">🥇 #1</span>
            <span class="device-name">{{ data.candidates[0]?.device_name || '无' }}</span>
            <span class="score-badge">{{ data.candidates[0]?.total_score?.toFixed(1) || 0 }}分</span>
            <span class="price-badge" v-if="data.candidates[0]?.unit_price">
              ¥{{ data.candidates[0]?.unit_price?.toLocaleString() }}
            </span>
          </div>
          <span :class="['collapse-icon', { 'collapsed': !showBestMatch }]">
            {{ showBestMatch ? '▼' : '▶' }}
          </span>
        </div>
        
        <div v-show="showBestMatch" class="candidate-content">
        
        <div class="candidate-info">
          <div class="info-row">
            <span class="info-label">品牌:</span>
            <span class="info-value">{{ data.candidates[0]?.brand || '未知' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">型号:</span>
            <span class="info-value">{{ data.candidates[0]?.spec_model || '未知' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">设备类型:</span>
            <span class="info-value">{{ data.candidates[0]?.device_type || '未知' }}</span>
          </div>
        </div>

        <div class="device-all-params">
          <div class="section-subtitle">📋 设备参数列表</div>
          <div class="params-text-line">
            <template v-for="(value, name) in (data.candidates[0]?.all_params || {})" :key="name">
              <span 
                :class="['param-chip', { 'highlight': isParamMatched(name) }]"
                :title="isParamMatched(name) ? getMatchTooltip(name) : ''"
              >
                <span class="param-chip-name">{{ name }}:</span>
                <span class="param-chip-value">{{ value }}</span>
                <span v-if="isParamMatched(name)" class="match-indicator">✓</span>
              </span>
            </template>
            <span v-if="!Object.keys(data.candidates[0]?.all_params || {}).length" class="no-params">
              暂无参数信息
            </span>
          </div>
          <div class="params-legend">
            <span class="legend-item"><span class="legend-dot matched"></span> 已匹配参数</span>
            <span class="legend-item"><span class="legend-dot unmatched"></span> 未匹配参数</span>
          </div>
        </div>

        <div class="score-breakdown">
          <div class="section-subtitle">📈 评分明细</div>
          
          <!-- 型号精确匹配提示 -->
          <div v-if="data.candidates[0]?.score_details?.model_match_score > 0" class="model-match-notice">
            <span class="notice-icon">🎯</span>
            <span class="notice-text">型号精确匹配 - 直接返回结果</span>
          </div>
          
          <div class="score-compact">
            <div class="score-compact-item">
              <span class="score-label">设备类型</span>
              <div class="score-mini-bar">
                <div class="score-mini-fill type" :style="{ width: getScorePercent('device_type_score', 0) + '%' }"></div>
              </div>
              <span class="score-mini-value">{{ data.candidates[0]?.score_details?.device_type_score?.toFixed(1) || 0 }}</span>
            </div>
            <div class="score-compact-item">
              <span class="score-label">设备类型关键词</span>
              <div class="score-mini-bar">
                <div class="score-mini-fill keyword" :style="{ width: getScorePercent('keyword_score', 0) + '%' }"></div>
              </div>
              <span class="score-mini-value">{{ data.candidates[0]?.score_details?.keyword_score?.toFixed(1) || 0 }}</span>
            </div>
            <div class="score-compact-item">
              <span class="score-label">参数匹配</span>
              <div class="score-mini-bar">
                <div class="score-mini-fill param" :style="{ width: getScorePercent('parameter_score', 0) + '%' }"></div>
              </div>
              <span class="score-mini-value">{{ data.candidates[0]?.score_details?.parameter_score?.toFixed(1) || 0 }}</span>
            </div>
            <div class="score-compact-item">
              <span class="score-label">品牌匹配</span>
              <div class="score-mini-bar">
                <div class="score-mini-fill brand" :style="{ width: getScorePercent('brand_score', 0) + '%' }"></div>
              </div>
              <span class="score-mini-value">{{ data.candidates[0]?.score_details?.brand_score?.toFixed(1) || 0 }}</span>
            </div>
            <div class="score-compact-item">
              <span class="score-label">其他匹配</span>
              <div class="score-mini-bar">
                <div class="score-mini-fill other" :style="{ width: getScorePercent('other_score', 0) + '%' }"></div>
              </div>
              <span class="score-mini-value">{{ data.candidates[0]?.score_details?.other_score?.toFixed(1) || 0 }}</span>
            </div>
          </div>
        </div>

        <div class="params-match-detail">
          <div class="section-subtitle">📊 参数匹配详情</div>
          <div class="param-details-list">
            <div 
              v-for="detail in (data.candidates[0]?.param_match_details || [])" 
              :key="detail.param_name" 
              :class="['param-detail-item', detail.matched ? 'matched' : 'unmatched']"
            >
              <div class="param-detail-header">
                <span class="param-name">{{ detail.param_name }}</span>
                <span :class="['match-status', detail.matched ? 'success' : 'fail']">
                  {{ detail.matched ? '✅ 匹配' : '❌ 不匹配' }}
                </span>
                <span :class="['match-type-badge', detail.match_type]">
                  {{ getMatchTypeLabel(detail.match_type) }}
                </span>
              </div>
              
              <div class="param-values">
                <div class="value-row">
                  <span class="value-label">输入值:</span>
                  <span class="value-content input">{{ detail.input_value || '未提供' }}</span>
                </div>
                <div class="value-arrow">→</div>
                <div class="value-row">
                  <span class="value-label">设备值:</span>
                  <span class="value-content device">{{ detail.device_value || '无' }}</span>
                </div>
              </div>
              
              <div class="match-reason">
                <span class="reason-icon">💡</span>
                <span class="reason-text">{{ detail.match_reason }}</span>
              </div>
              
              <div v-if="detail.extraction_pattern" class="extraction-pattern">
                <div class="pattern-header">
                  <span class="pattern-icon">🔧</span>
                  <span class="pattern-title">提取正则表达式</span>
                </div>
                <div class="pattern-content">
                  <code class="pattern-code">{{ detail.extraction_pattern }}</code>
                </div>
                <div class="pattern-desc">{{ detail.extraction_pattern_desc }}</div>
              </div>
              
              <div v-if="detail.matched" class="param-score">
                <span class="score-label">得分贡献:</span>
                <span class="score-value">+{{ (detail.match_score * 30).toFixed(1) }}分</span>
              </div>
            </div>
          </div>
        </div>

        <div class="params-summary">
          <div class="summary-row">
            <span class="summary-label">✅ 已匹配:</span>
            <span class="summary-value success">{{ data.candidates[0]?.matched_params?.join('、') || '无' }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">⚠️ 未匹配:</span>
            <span class="summary-value warning">{{ data.candidates[0]?.unmatched_params?.join('、') || '全部匹配' }}</span>
          </div>
        </div>
        </div>
      </div>

      <div v-if="data.candidates.length > 1" class="other-candidates">
        <div class="section-title">📋 其他候选设备</div>
        <div class="candidate-list">
          <div v-for="(candidate, index) in data.candidates.slice(1, 15)" :key="candidate.device_id" class="candidate-item">
            <div class="candidate-header">
              <span class="rank">#{{ index + 2 }}</span>
              <span class="device-name">{{ candidate.device_name }}</span>
              <span class="score-badge small">{{ candidate.total_score?.toFixed(1) }}分</span>
              <span class="price-badge small" v-if="candidate.unit_price">
                ¥{{ candidate.unit_price?.toLocaleString() }}
              </span>
            </div>
            <div class="candidate-brief">
              <span>{{ candidate.brand }} | {{ candidate.spec_model }}</span>
            </div>
            <!-- 显示全部参数，高亮匹配参数 -->
            <div class="candidate-params" v-if="candidate.all_params && Object.keys(candidate.all_params).length > 0">
              <template v-for="(value, name) in candidate.all_params" :key="name">
                <span 
                  class="param-tag" 
                  :class="{ 'param-matched': candidate.matched_params?.includes(name) }"
                  :title="candidate.matched_params?.includes(name) ? '已匹配' : ''"
                >
                  {{ name }}: {{ value }}
                </span>
              </template>
            </div>
            <div class="matched-details">
              <span class="matched-label">匹配项:</span>
              <span class="matched-items">{{ candidate.matched_params?.join('、') || '无' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="no-match">
      <span class="no-data">未找到匹配的设备</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  data: Object
})

const showBestMatch = ref(true)

const toggleBestMatch = () => {
  showBestMatch.value = !showBestMatch.value
}

const getScorePercent = (scoreKey, candidateIndex) => {
  const maxScores = {
    device_type_score: 30,
    keyword_score: 30,
    parameter_score: 20,
    brand_score: 15,
    other_score: 5,
    model_match_score: 100
  }
  const candidate = props.data?.candidates?.[candidateIndex]
  if (!candidate) return 0
  const score = candidate.score_details?.[scoreKey] || 0
  const max = maxScores[scoreKey] || 100
  return (score / max) * 100
}

const getMatchTypeLabel = (matchType) => {
  const labels = {
    'exact': '精确匹配',
    'overlap': '范围重叠',
    'equivalent': '等效匹配',
    'fuzzy': '模糊匹配',
    'none': '不匹配'
  }
  return labels[matchType] || matchType
}

const isParamMatched = (paramName) => {
  const candidate = props.data?.candidates?.[0]
  if (!candidate) return false
  
  const matchedParams = candidate.matched_params || []
  return matchedParams.includes(paramName)
}

const getMatchTooltip = (paramName) => {
  const details = props.data?.candidates?.[0]?.param_match_details || []
  const detail = details.find(d => d.param_name === paramName)
  if (detail) {
    return `${detail.match_reason}`
  }
  return ''
}
</script>

<style scoped>
.matching-step {
  background: #fff;
}

.matching-details {
  margin-top: 16px;
  border-top: 1px solid #ebeef5;
  padding-top: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 3px solid #409EFF;
}

.section-subtitle {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
}

.best-candidate {
  background: linear-gradient(135deg, #f6f9fc 0%, #eef2f7 100%);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid #e4e7ed;
}

.candidate-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
  cursor: pointer;
  user-select: none;
}

.candidate-header:hover {
  opacity: 0.8;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.collapse-icon {
  font-size: 12px;
  color: #909399;
  transition: transform 0.3s;
}

.collapse-icon.collapsed {
  transform: rotate(-90deg);
}

.candidate-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.rank {
  font-size: 14px;
  font-weight: 600;
  color: #409EFF;
}

.device-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  flex: 1;
}

.score-badge {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
}

.score-badge.small {
  font-size: 12px;
  padding: 2px 8px;
}

.price-badge {
  background: linear-gradient(135deg, #f56c6c 0%, #f89898 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
}

.price-badge.small {
  font-size: 12px;
  padding: 2px 8px;
}

.matched-details {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  margin-top: 8px;
  padding: 8px;
  background: #f0f9eb;
  border-radius: 4px;
  font-size: 12px;
}

.matched-label {
  color: #67c23a;
  font-weight: 600;
  white-space: nowrap;
}

.matched-items {
  color: #606266;
  line-height: 1.5;
}

.candidate-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 16px;
  padding: 12px;
  background: white;
  border-radius: 6px;
}

.device-all-params {
  margin-bottom: 16px;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
}

.params-text-line {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.param-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  background: #f4f4f5;
  border-radius: 4px;
  font-size: 12px;
  border: 1px solid #e4e7ed;
  transition: all 0.2s;
}

.param-chip.highlight {
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
  border-color: #67c23a;
  box-shadow: 0 2px 4px rgba(103, 194, 58, 0.2);
}

.param-chip-name {
  color: #909399;
  font-weight: 500;
}

.param-chip-value {
  color: #303133;
  font-weight: 600;
}

.param-chip.highlight .param-chip-name {
  color: #67c23a;
}

.param-chip.highlight .param-chip-value {
  color: #409EFF;
}

.match-indicator {
  color: #67c23a;
  font-weight: bold;
  margin-left: 2px;
}

.no-params {
  color: #909399;
  font-size: 13px;
  padding: 8px;
}

.params-legend {
  display: flex;
  gap: 16px;
  padding-top: 8px;
  border-top: 1px dashed #e4e7ed;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #909399;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-dot.matched {
  background: #67c23a;
}

.legend-dot.unmatched {
  background: #e4e7ed;
}

.info-row {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-label {
  font-size: 12px;
  color: #909399;
}

.info-value {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
}

.score-breakdown {
  margin-bottom: 16px;
}

.score-compact {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  padding: 10px;
  background: white;
  border-radius: 6px;
}

.score-compact-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-label {
  font-size: 12px;
  color: #606266;
  min-width: 60px;
}

.score-mini-bar {
  flex: 1;
  height: 6px;
  background: #ebeef5;
  border-radius: 3px;
  overflow: hidden;
}

.score-mini-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.score-mini-fill.type {
  background: linear-gradient(90deg, #409EFF, #66b1ff);
}

.score-mini-fill.keyword {
  background: linear-gradient(90deg, #9b59b6, #be90d4);
}

.score-mini-fill.param {
  background: linear-gradient(90deg, #67c23a, #85ce61);
}

.score-mini-fill.brand {
  background: linear-gradient(90deg, #e6a23c, #f0c78a);
}

.score-mini-fill.other {
  background: linear-gradient(90deg, #909399, #b4b4b4);
}

.model-match-notice {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #fff7e6 0%, #ffecc7 100%);
  border: 1px solid #ffd666;
  border-radius: 8px;
  margin-bottom: 16px;
}

.notice-icon {
  font-size: 20px;
}

.notice-text {
  font-size: 14px;
  font-weight: 600;
  color: #d48806;
}

.score-mini-value {
  font-size: 12px;
  font-weight: 600;
  color: #409EFF;
  min-width: 28px;
  text-align: right;
}

.params-match-detail {
  margin-bottom: 16px;
}

.param-details-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.param-detail-item {
  background: white;
  border-radius: 8px;
  padding: 14px;
  border: 1px solid #ebeef5;
  transition: all 0.2s;
}

.param-detail-item.matched {
  border-left: 3px solid #67c23a;
}

.param-detail-item.unmatched {
  border-left: 3px solid #f56c6c;
}

.param-detail-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.param-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.match-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.match-status.success {
  background: #f0f9eb;
  color: #67c23a;
}

.match-status.fail {
  background: #fef0f0;
  color: #f56c6c;
}

.match-type-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  background: #f4f4f5;
  color: #909399;
}

.match-type-badge.exact {
  background: #e1f3d8;
  color: #67c23a;
}

.match-type-badge.overlap {
  background: #fdf6ec;
  color: #e6a23c;
}

.match-type-badge.equivalent {
  background: #ecf5ff;
  color: #409EFF;
}

.match-type-badge.fuzzy {
  background: #f0f9eb;
  color: #85ce61;
}

.match-type-badge.none {
  background: #fef0f0;
  color: #f56c6c;
}

.param-values {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
  padding: 10px;
  background: #fafafa;
  border-radius: 6px;
}

.value-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.value-label {
  font-size: 11px;
  color: #909399;
}

.value-content {
  font-size: 13px;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 4px;
}

.value-content.input {
  background: #ecf5ff;
  color: #409EFF;
}

.value-content.device {
  background: #f0f9eb;
  color: #67c23a;
}

.value-arrow {
  color: #c0c4cc;
  font-size: 16px;
}

.match-reason {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 8px 10px;
  background: #fdf6ec;
  border-radius: 6px;
  margin-bottom: 8px;
}

.reason-icon {
  font-size: 14px;
}

.reason-text {
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
}

.extraction-pattern {
  margin-bottom: 8px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 6px;
  border: 1px dashed #dcdfe6;
}

.pattern-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.pattern-icon {
  font-size: 14px;
}

.pattern-title {
  font-size: 12px;
  font-weight: 600;
  color: #606266;
}

.pattern-content {
  margin-bottom: 6px;
}

.pattern-code {
  display: block;
  padding: 8px 12px;
  background: #fff;
  border-radius: 4px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  color: #e6a23c;
  word-break: break-all;
  border: 1px solid #e4e7ed;
}

.pattern-desc {
  font-size: 11px;
  color: #909399;
  font-style: italic;
}

.reason-text {
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
}

.param-score {
  display: flex;
  align-items: center;
  gap: 6px;
}

.score-label {
  font-size: 12px;
  color: #909399;
}

.score-value {
  font-size: 13px;
  font-weight: 600;
  color: #67c23a;
}

.params-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
}

.summary-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-label {
  font-size: 12px;
  color: #909399;
  min-width: 80px;
}

.summary-value {
  font-size: 13px;
  font-weight: 500;
}

.summary-value.success {
  color: #67c23a;
}

.summary-value.warning {
  color: #e6a23c;
}

.other-candidates {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.candidate-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.candidate-item {
  background: #fafafa;
  padding: 10px 12px;
  border-radius: 6px;
  border: 1px solid #ebeef5;
}

.candidate-item .candidate-header {
  margin-bottom: 6px;
}

.candidate-item .rank {
  font-size: 12px;
  color: #909399;
}

.candidate-item .device-name {
  font-size: 14px;
}

.candidate-brief {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

.candidate-params {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin: 8px 0;
}

.param-tag {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 3px;
  background-color: #f4f4f5;
  color: #606266;
  white-space: nowrap;
}

.param-tag.param-matched {
  background-color: #e1f3d8;
  color: #67c23a;
  font-weight: 500;
}

.matched-count {
  color: #67c23a;
}

.no-match {
  text-align: center;
  padding: 20px;
}

.no-data {
  color: #909399;
  font-size: 13px;
}
</style>
