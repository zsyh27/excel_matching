<template>
  <div class="config-info-card">
    <!-- 简洁视图 -->
    <div class="compact-view">
      <div class="compact-header">
        <div class="workflow-badge" :class="`stage-${finalStage}`">
          <span class="stage-icon">{{ finalStageIcon }}</span>
          <span class="stage-name">{{ finalStageName }}</span>
        </div>
        <button class="detail-button" @click="showDialog = true">
          <span class="icon">ℹ️</span>
          查看详情
        </button>
      </div>
      <p class="compact-description">{{ finalUsageText }}</p>
    </div>

    <!-- 详细信息对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="`配置说明 - ${finalStageName}`"
      width="700px"
      class="config-detail-dialog"
    >
      <div class="dialog-content">
        <!-- 流程位置 -->
        <div class="info-section workflow-position">
          <div class="section-header">
            <span class="icon">🔄</span>
            <h4>流程位置</h4>
          </div>
          <div class="workflow-badge" :class="`stage-${finalStage}`">
            <span class="stage-icon">{{ finalStageIcon }}</span>
            <span class="stage-name">{{ finalStageName }}</span>
          </div>
          <p class="stage-description">{{ finalStageDescription }}</p>
        </div>

        <!-- 使用说明 -->
        <div class="info-section usage-guide">
          <div class="section-header">
            <span class="icon">💡</span>
            <h4>使用说明</h4>
          </div>
          <div class="usage-content">
            <slot name="usage">
              <p v-if="finalUsageText">{{ finalUsageText }}</p>
            </slot>
          </div>
        </div>

        <!-- 示例（可选） -->
        <div v-if="$slots.examples || finalExamples" class="info-section examples">
          <div class="section-header">
            <span class="icon">📋</span>
            <h4>配置示例</h4>
          </div>
          <div class="examples-content">
            <slot name="examples">
              <ul v-if="finalExamples">
                <li v-for="(example, index) in finalExamples" :key="index">
                  {{ example }}
                </li>
              </ul>
            </slot>
          </div>
        </div>

        <!-- 注意事项（可选） -->
        <div v-if="$slots.notes || finalNotes" class="info-section notes">
          <div class="section-header">
            <span class="icon">⚠️</span>
            <h4>注意事项</h4>
          </div>
          <div class="notes-content">
            <slot name="notes">
              <ul v-if="finalNotes">
                <li v-for="(note, index) in finalNotes" :key="index">
                  {{ note }}
                </li>
              </ul>
            </slot>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { getConfigInfo } from '../../config/configInfoMap'

export default {
  name: 'ConfigInfoCard',
  props: {
    // 配置项ID（用于从configInfoMap获取信息）
    configId: {
      type: String,
      default: null
    },
    // 流程阶段：pre-entry, import, preprocessing, matching, global
    stage: {
      type: String,
      required: false,
      validator: (value) => ['pre-entry', 'import', 'preprocessing', 'matching', 'global'].includes(value)
    },
    // 阶段图标
    stageIcon: {
      type: String,
      default: ''
    },
    // 阶段名称
    stageName: {
      type: String,
      required: false
    },
    // 阶段描述
    stageDescription: {
      type: String,
      required: false
    },
    // 使用说明文本
    usageText: {
      type: String,
      default: ''
    },
    // 示例列表
    examples: {
      type: Array,
      default: null
    },
    // 注意事项列表
    notes: {
      type: Array,
      default: null
    }
  },
  setup(props) {
    const showDialog = ref(false)

    // 如果提供了configId，从configInfoMap获取配置信息
    const configInfo = computed(() => {
      if (props.configId) {
        return getConfigInfo(props.configId)
      }
      return null
    })

    // 计算最终使用的属性值（优先使用props，其次使用configInfo）
    const finalStage = computed(() => props.stage || configInfo.value?.stage || '')
    const finalStageIcon = computed(() => props.stageIcon || configInfo.value?.stageIcon || '')
    const finalStageName = computed(() => props.stageName || configInfo.value?.stageName || '')
    const finalStageDescription = computed(() => props.stageDescription || configInfo.value?.stageDescription || '')
    const finalUsageText = computed(() => props.usageText || configInfo.value?.usageText || '')
    const finalExamples = computed(() => props.examples || configInfo.value?.examples || null)
    const finalNotes = computed(() => props.notes || configInfo.value?.notes || null)

    return {
      showDialog,
      finalStage,
      finalStageIcon,
      finalStageName,
      finalStageDescription,
      finalUsageText,
      finalExamples,
      finalNotes
    }
  }
}
</script>

<style scoped>
/* 简洁视图 */
.config-info-card {
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.compact-view {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.compact-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
}

.compact-description {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: #666;
}

.detail-button {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 12px;
  background: white;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  font-size: 13px;
  color: #555;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  flex-shrink: 0;
}

.detail-button:hover {
  background: #f5f5f5;
  border-color: #409eff;
  color: #409eff;
}

.detail-button .icon {
  font-size: 14px;
}

/* 工作流徽章 */
.workflow-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.workflow-badge.stage-pre-entry {
  background: #e3f2fd;
  color: #1976d2;
  border: 1px solid #90caf9;
}

.workflow-badge.stage-import {
  background: #f3e5f5;
  color: #7b1fa2;
  border: 1px solid #ce93d8;
}

.workflow-badge.stage-preprocessing {
  background: #fff3e0;
  color: #e65100;
  border: 1px solid #ffb74d;
}

.workflow-badge.stage-matching {
  background: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #81c784;
}

.workflow-badge.stage-global {
  background: #fce4ec;
  color: #c2185b;
  border: 1px solid #f48fb1;
}

.stage-icon {
  font-size: 14px;
}

.stage-name {
  font-size: 13px;
}

/* 对话框内容样式 */
.dialog-content {
  max-height: 70vh;
  overflow-y: auto;
}

.info-section {
  margin-bottom: 20px;
}

.info-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.section-header .icon {
  font-size: 18px;
}

.section-header h4 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

/* 流程位置 */
.workflow-position {
  padding-bottom: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.workflow-position .workflow-badge {
  margin-bottom: 10px;
}

.stage-description {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: #666;
}

/* 使用说明 */
.usage-content {
  font-size: 13px;
  line-height: 1.7;
  color: #555;
}

.usage-content p {
  margin: 0 0 10px 0;
}

.usage-content p:last-child {
  margin-bottom: 0;
}

.usage-content ul {
  margin: 0;
  padding-left: 20px;
}

.usage-content li {
  margin-bottom: 6px;
}

/* 示例 */
.examples-content {
  background: white;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}

.examples-content ul {
  margin: 0;
  padding-left: 20px;
}

.examples-content li {
  margin-bottom: 8px;
  font-size: 13px;
  line-height: 1.6;
  color: #555;
  font-family: 'Consolas', 'Monaco', monospace;
}

/* 注意事项 */
.notes {
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 6px;
  padding: 15px;
}

.notes .section-header h4 {
  color: #856404;
}

.notes-content ul {
  margin: 0;
  padding-left: 20px;
}

.notes-content li {
  margin-bottom: 6px;
  font-size: 13px;
  line-height: 1.6;
  color: #856404;
}

/* 对话框样式覆盖 */
:deep(.el-dialog__header) {
  padding: 20px 20px 15px;
  border-bottom: 1px solid #e0e0e0;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-dialog__title) {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}
</style>
