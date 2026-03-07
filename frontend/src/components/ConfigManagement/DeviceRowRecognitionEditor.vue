<template>
  <div class="device-row-recognition-editor">
    <div class="editor-header">
      <h2>设备行识别配置</h2>
      <p class="description">
        控制Excel文件中设备行的智能识别，包括概率阈值和评分权重。
      </p>
      
      <ConfigInfoCard
        stage="import"
        stage-icon="📥"
        stage-name="数据导入阶段"
        stage-description="此配置在Excel数据导入时生效，用于智能识别哪些行是设备数据行，过滤掉标题、合计等非设备行。"
      >
        <template #usage>
          <p>配置设备行的识别规则，系统会根据规则自动过滤非设备数据行。</p>
          <ul>
            <li><strong>概率阈值</strong>：设置高、中、低概率阈值，判断一行是否为设备行</li>
            <li><strong>评分权重</strong>：设置不同特征的评分权重（设备类型、品牌、参数等）</li>
            <li><strong>智能识别</strong>：基于机器学习模型自动识别设备行</li>
          </ul>
        </template>
        <template #examples>
          <ul>
            <li>包含关键词：传感器、探测器、控制器、阀门等</li>
            <li>排除关键词：合计、小计、总计、备注等</li>
            <li>行号范围：跳过前N行标题</li>
          </ul>
        </template>
        <template #notes>
          <ul>
            <li>识别规则会影响导入的设备数量</li>
            <li>建议先测试识别效果再批量导入</li>
            <li>可以通过预览功能查看识别结果</li>
          </ul>
        </template>
      </ConfigInfoCard>
    </div>

    <div class="editor-body">
      <!-- 概率阈值配置 -->
      <div class="section">
        <h3>概率阈值</h3>
        <p class="section-desc">
          设置设备行识别的概率阈值，用于判断一行是否为设备行。
        </p>

        <div class="config-item">
          <label class="config-label">
            <span class="label-text">高概率阈值</span>
            <span class="label-desc">得分超过此值判定为高概率设备行</span>
          </label>
          <div class="config-control">
            <input 
              v-model.number="localValue.probability_thresholds.high" 
              type="number" 
              min="0"
              max="100"
              class="number-input"
              @input="emitChange"
            />
            <span class="unit">分</span>
          </div>
        </div>

        <div class="config-item">
          <label class="config-label">
            <span class="label-text">中概率阈值</span>
            <span class="label-desc">得分超过此值判定为中概率设备行</span>
          </label>
          <div class="config-control">
            <input 
              v-model.number="localValue.probability_thresholds.medium" 
              type="number" 
              min="0"
              max="100"
              class="number-input"
              @input="emitChange"
            />
            <span class="unit">分</span>
          </div>
        </div>
      </div>

      <!-- 评分权重配置 -->
      <div class="section">
        <h3>评分权重</h3>
        <p class="section-desc">
          三个维度的评分权重，总和应为1.0。
        </p>

        <div class="config-item">
          <label class="config-label">
            <span class="label-text">数据类型权重</span>
            <span class="label-desc">数据类型维度的权重（推荐0.3）</span>
          </label>
          <div class="config-control">
            <input 
              v-model.number="localValue.scoring_weights.data_type" 
              type="number" 
              step="0.05"
              min="0"
              max="1"
              class="number-input"
              @input="emitChange"
            />
            <input 
              v-model.number="localValue.scoring_weights.data_type" 
              type="range" 
              min="0" 
              max="1" 
              step="0.05"
              class="range-input"
              @input="emitChange"
            />
          </div>
        </div>

        <div class="config-item">
          <label class="config-label">
            <span class="label-text">行业特征权重</span>
            <span class="label-desc">行业特征维度的权重（推荐0.35）</span>
          </label>
          <div class="config-control">
            <input 
              v-model.number="localValue.scoring_weights.industry" 
              type="number" 
              step="0.05"
              min="0"
              max="1"
              class="number-input"
              @input="emitChange"
            />
            <input 
              v-model.number="localValue.scoring_weights.industry" 
              type="range" 
              min="0" 
              max="1" 
              step="0.05"
              class="range-input"
              @input="emitChange"
            />
          </div>
        </div>

        <div class="config-item">
          <label class="config-label">
            <span class="label-text">结构特征权重</span>
            <span class="label-desc">结构特征维度的权重（推荐0.35）</span>
          </label>
          <div class="config-control">
            <input 
              v-model.number="localValue.scoring_weights.structure" 
              type="number" 
              step="0.05"
              min="0"
              max="1"
              class="number-input"
              @input="emitChange"
            />
            <input 
              v-model.number="localValue.scoring_weights.structure" 
              type="range" 
              min="0" 
              max="1" 
              step="0.05"
              class="range-input"
              @input="emitChange"
            />
          </div>
        </div>

        <div class="weight-sum" :class="{ 'weight-sum-error': weightSum !== 1.0 }">
          权重总和: {{ weightSum.toFixed(2) }} 
          <span v-if="weightSum !== 1.0" class="error-text">（应为 1.0）</span>
        </div>
      </div>

      <div class="info-box">
        <h4>💡 配置说明</h4>
        <ul>
          <li><strong>高概率阈值</strong>：推荐值 50，得分超过50分的行会被自动识别为设备行</li>
          <li><strong>中概率阈值</strong>：推荐值 30，得分在30-50之间的行需要用户确认</li>
          <li><strong>评分权重</strong>：三个维度的权重总和必须为1.0，建议保持默认值</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import ConfigInfoCard from './ConfigInfoCard.vue'

export default {
  name: 'DeviceRowRecognitionEditor',
  components: {
    ConfigInfoCard
  },
  props: {
    modelValue: {
      type: Object,
      default: () => ({
        probability_thresholds: {
          high: 50,
          medium: 30
        },
        scoring_weights: {
          data_type: 0.3,
          industry: 0.35,
          structure: 0.35
        }
      })
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const localValue = ref(JSON.parse(JSON.stringify(props.modelValue)))

    // 确保结构完整
    if (!localValue.value.probability_thresholds) {
      localValue.value.probability_thresholds = { high: 50, medium: 30 }
    }
    if (!localValue.value.scoring_weights) {
      localValue.value.scoring_weights = { data_type: 0.3, industry: 0.35, structure: 0.35 }
    }

    const weightSum = computed(() => {
      const weights = localValue.value.scoring_weights
      return weights.data_type + weights.industry + weights.structure
    })

    const emitChange = () => {
      emit('update:modelValue', JSON.parse(JSON.stringify(localValue.value)))
      emit('change')
    }

    watch(() => props.modelValue, (newVal) => {
      localValue.value = JSON.parse(JSON.stringify(newVal))
    }, { deep: true })

    return {
      localValue,
      weightSum,
      emitChange
    }
  }
}
</script>

<style scoped>
.device-row-recognition-editor {
  max-width: 800px;
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

.section h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #333;
}

.section-desc {
  margin: 0 0 20px 0;
  color: #666;
  font-size: 13px;
  line-height: 1.6;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.config-item:last-child {
  border-bottom: none;
}

.config-label {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.label-text {
  font-size: 15px;
  font-weight: 500;
  color: #333;
}

.label-desc {
  font-size: 13px;
  color: #999;
}

.config-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

.number-input {
  width: 80px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
}

.range-input {
  width: 150px;
}

.unit {
  color: #666;
  font-size: 13px;
}

.weight-sum {
  margin-top: 15px;
  padding: 12px;
  background: #e8f5e9;
  border-radius: 4px;
  color: #2e7d32;
  font-size: 14px;
  font-weight: 500;
  text-align: center;
}

.weight-sum-error {
  background: #ffebee;
  color: #c62828;
}

.error-text {
  font-weight: normal;
  font-size: 13px;
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

.info-box strong {
  color: #333;
}
</style>
