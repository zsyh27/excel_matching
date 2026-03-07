<template>
  <div class="quality-score-editor">
    <div class="editor-header">
      <h2>特征质量评分</h2>
      <p class="description">
        配置特征质量评分规则，用于过滤低质量特征，提高匹配准确性。
      </p>
      
      <ConfigInfoCard
        stage="preprocessing"
        stage-icon="🔍"
        stage-name="预处理配置 - 特征质量"
        stage-description="此配置在特征提取后生效，用于评估特征的质量，过滤低质量特征。"
      >
        <template #usage>
          <p>配置特征质量评分规则和阈值，低于阈值的特征会被过滤。</p>
          <ul>
            <li><strong>长度评分</strong>：中文≥2字，英文≥3字</li>
            <li><strong>品牌加分</strong>：包含品牌词+15分</li>
            <li><strong>技术参数加分</strong>：包含数字+10分</li>
            <li><strong>质量阈值</strong>：设置最低质量分数</li>
          </ul>
        </template>
        <template #examples>
          <ul>
            <li>长度评分：中文≥2字，英文≥3字</li>
            <li>品牌加分：包含品牌词+15分</li>
            <li>技术参数加分：包含数字+10分</li>
          </ul>
        </template>
        <template #notes>
          <ul>
            <li>质量评分会影响特征的保留</li>
            <li>阈值设置过高可能过滤有用特征</li>
            <li>建议根据实际效果调整阈值</li>
          </ul>
        </template>
      </ConfigInfoCard>
    </div>

    <div class="editor-body">
      <div class="section">
        <div class="form-group">
          <label class="switch-label">
            <input 
              type="checkbox" 
              v-model="localValue.enabled"
              @change="emitChange"
            />
            <span class="switch-text">启用质量评分</span>
          </label>
          <p class="help-text">
            启用后，系统会根据配置的规则对提取的特征进行质量评分，过滤低质量特征
          </p>
        </div>

        <div v-if="localValue.enabled" style="margin-top: 20px;">
          <h4 style="margin: 0 0 15px 0; font-size: 14px; color: #333;">评分规则</h4>
          
          <div class="rule-item">
            <label class="rule-label">最小特征长度（中文）</label>
            <input 
              v-model.number="localValue.min_length_chinese" 
              type="number" 
              min="1"
              class="rule-input"
              @change="emitChange"
            />
            <span class="rule-desc">特征长度小于此值将被过滤</span>
          </div>

          <div class="rule-item">
            <label class="rule-label">最小特征长度（英文）</label>
            <input 
              v-model.number="localValue.min_length_english" 
              type="number" 
              min="1"
              class="rule-input"
              @change="emitChange"
            />
            <span class="rule-desc">特征长度小于此值将被过滤</span>
          </div>

          <div class="rule-item">
            <label class="rule-label">质量评分阈值</label>
            <input 
              v-model.number="localValue.threshold" 
              type="number" 
              min="0"
              max="1"
              step="0.1"
              class="rule-input"
              @change="emitChange"
            />
            <span class="rule-desc">评分低于此阈值的特征将被过滤（0-1之间）</span>
          </div>
        </div>

        <div class="info-note" style="margin-top: 15px;">
          <strong>💡 评分说明</strong>：
          <ul>
            <li>系统会根据特征的长度、是否包含数字、是否有意义等维度进行评分</li>
            <li>白名单中的特征会跳过质量评分检查</li>
            <li>建议阈值设置为 0.3-0.5 之间</li>
          </ul>
        </div>
      </div>

      <div class="info-box">
        <h4>💡 使用建议</h4>
        <ul>
          <li><strong>最小长度</strong>：建议中文设置为1，英文设置为2</li>
          <li><strong>质量阈值</strong>：
            <ul>
              <li>0.3：宽松模式，保留更多特征</li>
              <li>0.5：平衡模式，过滤明显无意义的特征</li>
              <li>0.7：严格模式，只保留高质量特征</li>
            </ul>
          </li>
          <li><strong>配合白名单</strong>：对于重要但可能被过滤的短特征，添加到白名单中</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import ConfigInfoCard from './ConfigInfoCard.vue'

export default {
  name: 'QualityScoreEditor',
  components: {
    ConfigInfoCard
  },
  props: {
    modelValue: {
      type: Object,
      default: () => ({
        enabled: false,
        min_length_chinese: 1,
        min_length_english: 2,
        threshold: 0.5
      })
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const localValue = ref({
      enabled: props.modelValue?.enabled || false,
      min_length_chinese: props.modelValue?.min_length_chinese || 1,
      min_length_english: props.modelValue?.min_length_english || 2,
      threshold: props.modelValue?.threshold || 0.5
    })

    const emitChange = () => {
      emit('update:modelValue', { ...localValue.value })
      emit('change')
    }

    watch(() => props.modelValue, (newVal) => {
      if (newVal) {
        localValue.value = {
          enabled: newVal.enabled || false,
          min_length_chinese: newVal.min_length_chinese || 1,
          min_length_english: newVal.min_length_english || 2,
          threshold: newVal.threshold || 0.5
        }
      }
    }, { deep: true })

    return {
      localValue,
      emitChange
    }
  }
}
</script>

<style scoped>
.quality-score-editor {
  max-width: 900px;
}

.editor-header h2 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #333;
}

.description {
  margin: 0 0 30px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.section {
  background: white;
  padding: 25px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.switch-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.switch-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.switch-text {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.help-text {
  margin: 8px 0 0 28px;
  color: #666;
  font-size: 13px;
}

.rule-item {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.rule-label {
  min-width: 180px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.rule-input {
  width: 120px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.rule-input:focus {
  outline: none;
  border-color: #2196f3;
}

.rule-desc {
  flex: 1;
  font-size: 13px;
  color: #666;
}

.info-note {
  padding: 12px;
  background: #fff3cd;
  border-left: 4px solid #ffc107;
  border-radius: 4px;
  font-size: 13px;
  color: #856404;
}

.info-note strong {
  color: #856404;
}

.info-note ul {
  margin: 8px 0 0 0;
  padding-left: 20px;
}

.info-note li {
  margin: 4px 0;
}

.info-box {
  background: #e3f2fd;
  padding: 20px;
  border-radius: 4px;
  border-left: 4px solid #2196f3;
}

.info-box h4 {
  margin: 0 0 12px 0;
  font-size: 15px;
  color: #1565c0;
}

.info-box ul {
  margin: 0;
  padding-left: 20px;
}

.info-box li {
  margin-bottom: 8px;
  color: #666;
  font-size: 13px;
  line-height: 1.6;
}
</style>
