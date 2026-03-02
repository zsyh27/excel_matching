<template>
  <div class="candidate-rules">
    <el-empty
      v-if="!candidates || candidates.length === 0"
      description="未找到候选规则"
      :image-size="150"
    />
    
    <div v-else class="candidates-list">
      <el-alert
        v-if="candidates.length > 20"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      >
        <template #title>
          共找到 {{ candidates.length }} 个候选规则，当前显示前 20 个得分最高的候选
        </template>
      </el-alert>
      
      <div
        v-for="(candidate, index) in displayedCandidates"
        :key="candidate.rule_id"
        class="candidate-card"
        :class="{ 'qualified': candidate.is_qualified, 'selected': index === 0 }"
      >
        <div class="candidate-header">
          <div class="rank-badge" :class="{ 'top-rank': index === 0 }">
            #{{ index + 1 }}
          </div>
          <div class="device-info">
            <h4>{{ candidate.device_info.device_name }}</h4>
            <p>{{ candidate.device_info.brand }} - {{ candidate.device_info.spec_model }}</p>
          </div>
          <div class="score-info">
            <el-progress
              :percentage="getScorePercentage(candidate)"
              :status="candidate.is_qualified ? 'success' : 'exception'"
              :stroke-width="12"
            />
            <span class="score-text">
              {{ candidate.weight_score.toFixed(1) }} / {{ candidate.match_threshold }}
            </span>
          </div>
        </div>
        
        <el-collapse accordion>
          <el-collapse-item title="查看详情" name="detail">
            <div class="candidate-detail">
              <!-- 匹配到的特征 -->
              <div class="matched-features">
                <h5>匹配到的特征 ({{ candidate.matched_features.length }})</h5>
                <el-table :data="candidate.matched_features" size="small" border>
                  <el-table-column prop="feature" label="特征" min-width="150" />
                  <el-table-column prop="feature_type" label="类型" width="100" align="center">
                    <template #default="{ row }">
                      <el-tag :type="getFeatureTypeColor(row.feature_type)" size="small">
                        {{ getFeatureTypeLabel(row.feature_type) }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="weight" label="权重" width="80" align="center" />
                  <el-table-column label="贡献" width="150" align="center">
                    <template #default="{ row }">
                      <div class="contribution-cell">
                        <el-progress
                          :percentage="row.contribution_percentage"
                          :show-text="false"
                          :stroke-width="8"
                          :color="getContributionColor(row.contribution_percentage)"
                        />
                        <span class="contribution-text">
                          {{ row.contribution_percentage.toFixed(1) }}%
                        </span>
                      </div>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
              
              <!-- 未匹配的特征 -->
              <div v-if="candidate.unmatched_features && candidate.unmatched_features.length > 0" class="unmatched-features">
                <h5>未匹配的特征 ({{ candidate.unmatched_features.length }})</h5>
                <div class="unmatched-tags">
                  <el-tag
                    v-for="(feature, idx) in candidate.unmatched_features"
                    :key="idx"
                    type="info"
                    class="feature-tag"
                  >
                    {{ feature }}
                  </el-tag>
                </div>
              </div>
              
              <!-- 得分计算 -->
              <div class="score-calculation">
                <h5>得分计算</h5>
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="总得分">
                    <span class="score-value">{{ candidate.weight_score.toFixed(2) }}</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="匹配阈值">
                    <span class="threshold-value">
                      {{ candidate.match_threshold }}
                      <el-tag size="small" :type="candidate.threshold_type === 'rule' ? 'primary' : 'info'">
                        {{ candidate.threshold_type === 'rule' ? '规则阈值' : '默认阈值' }}
                      </el-tag>
                    </span>
                  </el-descriptions-item>
                  <el-descriptions-item label="最大可能得分">
                    {{ candidate.total_possible_score.toFixed(2) }}
                  </el-descriptions-item>
                  <el-descriptions-item label="得分率">
                    <el-progress
                      :percentage="getScoreRate(candidate)"
                      :stroke-width="10"
                      :color="getScoreRateColor(getScoreRate(candidate))"
                    />
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

/**
 * 候选规则列表展示组件
 * 
 * 展示所有候选规则及其详细匹配信息
 * 验证需求: Requirements 3.1-3.5, 4.1-4.5, 7.1-7.5, 8.4
 */

const props = defineProps({
  candidates: {
    type: Array,
    required: true,
    default: () => []
  }
})

/**
 * 限制显示的候选规则数量（最多20条）
 */
const displayedCandidates = computed(() => {
  if (!props.candidates || props.candidates.length === 0) {
    return []
  }
  return props.candidates.slice(0, 20)
})

/**
 * 计算得分百分比（相对于阈值）
 */
function getScorePercentage(candidate) {
  return Math.min((candidate.weight_score / candidate.match_threshold) * 100, 100)
}

/**
 * 计算得分率（相对于最大可能得分）
 */
function getScoreRate(candidate) {
  if (candidate.total_possible_score === 0) return 0
  return Math.round((candidate.weight_score / candidate.total_possible_score) * 100)
}

/**
 * 获取特征类型的颜色
 */
function getFeatureTypeColor(type) {
  const colors = {
    brand: 'success',
    device_type: 'primary',
    model: 'warning',
    parameter: 'info'
  }
  return colors[type] || 'info'
}

/**
 * 获取特征类型的标签
 */
function getFeatureTypeLabel(type) {
  const labels = {
    brand: '品牌',
    device_type: '类型',
    model: '型号',
    parameter: '参数'
  }
  return labels[type] || type
}

/**
 * 获取贡献度的颜色
 */
function getContributionColor(percentage) {
  if (percentage >= 30) return '#67c23a'
  if (percentage >= 15) return '#e6a23c'
  return '#909399'
}

/**
 * 获取得分率的颜色
 */
function getScoreRateColor(rate) {
  if (rate >= 80) return '#67c23a'
  if (rate >= 60) return '#e6a23c'
  return '#f56c6c'
}
</script>

<style scoped>
.candidate-rules {
  padding: 20px;
}

.candidates-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.candidate-card {
  border: 2px solid #dcdfe6;
  border-radius: 8px;
  padding: 20px;
  background-color: #fff;
  transition: all 0.3s;
}

.candidate-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.candidate-card.qualified {
  border-color: #67c23a;
  background-color: #f0f9ff;
}

.candidate-card.selected {
  border-color: #409eff;
  border-width: 3px;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.3);
}

.candidate-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 15px;
}

.rank-badge {
  flex-shrink: 0;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
}

.rank-badge.top-rank {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.device-info {
  flex: 1;
}

.device-info h4 {
  margin: 0 0 5px 0;
  font-size: 18px;
  color: #303133;
  font-weight: 600;
}

.device-info p {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.score-info {
  flex-shrink: 0;
  width: 200px;
  text-align: center;
}

.score-text {
  display: block;
  margin-top: 8px;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.candidate-detail {
  padding: 15px 0;
}

.matched-features,
.unmatched-features,
.score-calculation {
  margin-bottom: 25px;
}

.matched-features h5,
.unmatched-features h5,
.score-calculation h5 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
  padding-bottom: 10px;
  border-bottom: 2px solid #e4e7ed;
}

.contribution-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.contribution-text {
  font-weight: 600;
  color: #303133;
  min-width: 50px;
}

.unmatched-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.feature-tag {
  font-size: 13px;
  padding: 6px 12px;
}

.score-value {
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
}

.threshold-value {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
}

:deep(.el-collapse-item__header) {
  font-size: 15px;
  font-weight: 600;
  color: #409eff;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}
</style>
