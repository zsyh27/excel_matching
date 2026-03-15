<template>
  <div class="preview-section ui-preview-step">
    <h4>🖥️ 步骤5：用户界面展示</h4>
    
    <div class="preview-item">
      <span class="label">显示格式:</span>
      <span class="value">{{ data?.display_format === 'dropdown' ? '下拉选择框' : data?.display_format || '未知' }}</span>
    </div>

    <div v-if="matching?.candidates?.length" class="device-selector">
      <div class="section-title">🎯 设备选择</div>
      <p class="selector-hint">系统已为您匹配到 {{ matching.candidates.length }} 个候选设备，您可以选择最合适的设备：</p>
      
      <div class="dropdown-container">
        <el-select 
          v-model="selectedDeviceId" 
          class="device-dropdown" 
          @change="handleDeviceChange" 
          placeholder="请选择设备"
          popper-class="device-select-popper"
        >
          <el-option v-for="candidate in matching.candidates" :key="candidate.device_id" :value="candidate.device_id">
            <div class="device-option">
              <div class="device-option-main">
                {{ candidate.device_name }} - {{ candidate.spec_model }}
                <span class="score-text">({{ candidate.total_score?.toFixed(1) }}分)</span>
              </div>
              <div class="device-option-params" v-if="candidate.all_params && Object.keys(candidate.all_params).length > 0">
                <template v-for="(value, name) in candidate.all_params" :key="name">
                  <span 
                    class="param-tag" 
                    :class="{ 'param-matched': candidate.matched_params?.includes(name) }"
                  >
                    {{ name }}: {{ value }}
                  </span>
                </template>
              </div>
            </div>
          </el-option>
        </el-select>
      </div>

      <div v-if="selectedDevice" class="selected-device-info">
        <div class="info-header">
          <span class="info-title">📋 已选设备详情</span>
          <span :class="['score-indicator', getScoreLevel(selectedDevice.total_score)]">
            {{ selectedDevice.total_score?.toFixed(1) }}分
          </span>
        </div>
        
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">设备名称</span>
            <span class="info-value">{{ selectedDevice.device_name }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">品牌</span>
            <span class="info-value">{{ selectedDevice.brand || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">型号</span>
            <span class="info-value">{{ selectedDevice.spec_model || '未知' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">设备类型</span>
            <span class="info-value">{{ selectedDevice.device_type || '未知' }}</span>
          </div>
        </div>

        <div class="match-summary">
          <div class="summary-item">
            <span class="summary-label">匹配参数</span>
            <div class="summary-tags">
              <span v-for="param in (selectedDevice.matched_params || [])" :key="param" class="tag matched">
                {{ param }}
              </span>
              <span v-if="!selectedDevice.matched_params?.length" class="no-data">无</span>
            </div>
          </div>
          <div class="summary-item">
            <span class="summary-label">未匹配参数</span>
            <div class="summary-tags">
              <span v-for="param in (selectedDevice.unmatched_params || [])" :key="param" class="tag unmatched">
                {{ param }}
              </span>
              <span v-if="!selectedDevice.unmatched_params?.length" class="no-data">全部匹配</span>
            </div>
          </div>
        </div>

        <div class="score-details-mini">
          <div class="mini-score-item">
            <span class="mini-label">类型</span>
            <div class="mini-bar">
              <div class="mini-bar-fill" :style="{ width: (selectedDevice.score_details?.device_type_score || 0) / 50 * 100 + '%' }"></div>
            </div>
            <span class="mini-value">{{ selectedDevice.score_details?.device_type_score?.toFixed(1) || 0 }}</span>
          </div>
          <div class="mini-score-item">
            <span class="mini-label">参数</span>
            <div class="mini-bar">
              <div class="mini-bar-fill green" :style="{ width: (selectedDevice.score_details?.parameter_score || 0) / 30 * 100 + '%' }"></div>
            </div>
            <span class="mini-value">{{ selectedDevice.score_details?.parameter_score?.toFixed(1) || 0 }}</span>
          </div>
          <div class="mini-score-item">
            <span class="mini-label">品牌</span>
            <div class="mini-bar">
              <div class="mini-bar-fill orange" :style="{ width: (selectedDevice.score_details?.brand_score || 0) / 10 * 100 + '%' }"></div>
            </div>
            <span class="mini-value">{{ selectedDevice.score_details?.brand_score?.toFixed(1) || 0 }}</span>
          </div>
        </div>
      </div>

      <div class="filter-section">
        <div class="section-subtitle">🔍 按设备类型筛选</div>
        <div class="filter-options">
          <button 
            v-for="option in (data?.filter_options || [])" 
            :key="option"
            :class="['filter-btn', { active: activeFilter === option }]"
            @click="toggleFilter(option)"
          >
            {{ option }}
          </button>
          <button 
            :class="['filter-btn', { active: activeFilter === '' }]"
            @click="clearFilter"
          >
            全部
          </button>
        </div>
      </div>
    </div>

    <div v-else class="no-candidates">
      <span class="no-data">暂无候选设备</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  data: Object,
  matching: Object
})

const selectedDeviceId = ref('')
const activeFilter = ref('')

const selectedDevice = computed(() => {
  if (!selectedDeviceId.value || !props.matching?.candidates) return null
  return props.matching.candidates.find(c => c.device_id === selectedDeviceId.value)
})

watch(() => props.matching?.candidates, (candidates) => {
  if (candidates?.length && !selectedDeviceId.value) {
    selectedDeviceId.value = props.data?.default_selected || candidates[0]?.device_id
  }
}, { immediate: true })

const handleDeviceChange = () => {
  console.log('Selected device:', selectedDeviceId.value)
}

const getScoreLevel = (score) => {
  if (score >= 80) return 'high'
  if (score >= 60) return 'medium'
  return 'low'
}

const isParamValueMatched = (matchedParams, paramName) => {
  if (!matchedParams || !paramName) return false
  return matchedParams.includes(paramName)
}

const toggleFilter = (option) => {
  activeFilter.value = activeFilter.value === option ? '' : option
}

const clearFilter = () => {
  activeFilter.value = ''
}
</script>

<style scoped>
.ui-preview-step {
  background: #fff;
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

.device-selector {
  margin-top: 16px;
  border-top: 1px solid #ebeef5;
  padding-top: 16px;
}

.selector-hint {
  font-size: 13px;
  color: #606266;
  margin-bottom: 12px;
}

.dropdown-container {
  position: relative;
  margin-bottom: 16px;
}

.device-dropdown {
  width: 100%;
}

.device-option {
  padding: 8px 0;
  max-width: 100%;
}

.device-option-main {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
}

.score-text {
  color: #909399;
  font-size: 12px;
  margin-left: 4px;
}

.device-option-params {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
  max-height: 120px;
  overflow-y: auto;
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

.selected-device-info {
  background: linear-gradient(135deg, #f0f7ff 0%, #e6f4ff 100%);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid #d9ecff;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.info-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.score-indicator {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}

.score-indicator.high {
  background: #f0f9eb;
  color: #67c23a;
}

.score-indicator.medium {
  background: #fdf6ec;
  color: #e6a23c;
}

.score-indicator.low {
  background: #fef0f0;
  color: #f56c6c;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: white;
  border-radius: 6px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
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

.match-summary {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.summary-item {
  flex: 1;
}

.summary-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
  display: block;
}

.summary-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
}

.tag.matched {
  background: #f0f9eb;
  color: #67c23a;
}

.tag.unmatched {
  background: #fef0f0;
  color: #f56c6c;
}

.score-details-mini {
  display: flex;
  gap: 12px;
  padding: 10px;
  background: white;
  border-radius: 6px;
}

.mini-score-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
}

.mini-label {
  font-size: 11px;
  color: #909399;
  width: 28px;
}

.mini-bar {
  flex: 1;
  height: 6px;
  background: #ebeef5;
  border-radius: 3px;
  overflow: hidden;
}

.mini-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #409EFF, #66b1ff);
  border-radius: 3px;
}

.mini-bar-fill.green {
  background: linear-gradient(90deg, #67c23a, #85ce61);
}

.mini-bar-fill.orange {
  background: linear-gradient(90deg, #e6a23c, #f0c78a);
}

.mini-value {
  font-size: 11px;
  color: #606266;
  font-weight: 500;
  width: 28px;
  text-align: right;
}

.filter-section {
  margin-top: 16px;
}

.filter-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-btn {
  padding: 6px 14px;
  border: 1px solid #dcdfe6;
  border-radius: 16px;
  background: white;
  color: #606266;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #409EFF;
  color: #409EFF;
}

.filter-btn.active {
  background: #409EFF;
  border-color: #409EFF;
  color: white;
}

.no-candidates {
  text-align: center;
  padding: 20px;
}

.no-data {
  color: #909399;
  font-size: 13px;
}
</style>

<style>
/* 全局样式：设备选择下拉弹出层 */
.device-select-popper {
  max-width: 600px !important;
  z-index: 9999 !important;
}

.device-select-popper .el-select-dropdown__item {
  height: auto !important;
  min-height: 34px;
  padding: 8px 12px;
  line-height: 1.4;
}

.device-select-popper .el-select-dropdown__item.hover {
  background-color: #f5f7fa;
}

/* 高亮匹配参数 */
.device-select-popper .param-tag.param-matched {
  background-color: #e1f3d8 !important;
  color: #67c23a !important;
  font-weight: 500 !important;
}
</style>
