<template>
  <div class="match-threshold-editor">
    <div class="editor-header">
      <h2>匹配阈值</h2>
      <p class="description">
        配置默认匹配阈值，用于判断设备匹配是否成功。阈值越高，匹配要求越严格。
      </p>
    </div>

    <div class="editor-body">
      <div class="section">
        <div class="threshold-config">
          <label class="threshold-label">默认匹配阈值</label>
          <input 
            v-model.number="localValue.value" 
            type="number" 
            min="0"
            max="100"
            step="1"
            class="threshold-input"
            @change="emitChange"
          />
          <span class="threshold-unit">分</span>
        </div>

        <div class="threshold-slider">
          <input 
            v-model.number="localValue.value" 
            type="range" 
            min="0"
            max="100"
            step="1"
            class="slider"
            @input="emitChange"
          />
          <div class="slider-labels">
            <span>0</span>
            <span>25</span>
            <span>50</span>
            <span>75</span>
            <span>100</span>
          </div>
        </div>

        <div class="threshold-desc">
          <p><strong>当前阈值：{{ localValue.value }} 分</strong></p>
          <p class="desc-text">{{ getThresholdDescription() }}</p>
        </div>
      </div>

      <div class="info-box">
        <h4>💡 阈值说明</h4>
        <ul>
          <li><strong>0-3分</strong>：极宽松模式，几乎所有设备都能匹配（不推荐）</li>
          <li><strong>4-6分</strong>：宽松模式，适合特征较少或描述简单的设备</li>
          <li><strong>7-10分</strong>：平衡模式，推荐使用，适合大多数场景</li>
          <li><strong>11-15分</strong>：严格模式，要求较高的匹配度</li>
          <li><strong>16分以上</strong>：极严格模式，只匹配高度相似的设备</li>
        </ul>
        
        <h5 style="margin-top: 15px;">匹配流程</h5>
        <ol>
          <li>第一轮：使用规则自己的 match_threshold</li>
          <li>第二轮：使用此默认阈值兜底</li>
          <li>选择得分最高的匹配结果</li>
        </ol>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'MatchThresholdEditor',
  props: {
    modelValue: {
      type: Object,
      default: () => ({
        value: 5
      })
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const localValue = ref({
      value: props.modelValue?.value || 5
    })

    const getThresholdDescription = () => {
      const value = localValue.value.value
      if (value <= 3) return '极宽松：几乎所有设备都能匹配，可能产生大量误匹配'
      if (value <= 6) return '宽松：适合特征较少的设备，召回率高但准确率一般'
      if (value <= 10) return '平衡：推荐设置，在召回率和准确率之间取得平衡'
      if (value <= 15) return '严格：要求较高的匹配度，准确率高但可能漏匹配'
      return '极严格：只匹配高度相似的设备，可能导致大量匹配失败'
    }

    const emitChange = () => {
      emit('update:modelValue', { ...localValue.value })
      emit('change')
    }

    watch(() => props.modelValue, (newVal) => {
      if (newVal) {
        localValue.value = {
          value: newVal.value || 5
        }
      }
    }, { deep: true })

    return {
      localValue,
      getThresholdDescription,
      emitChange
    }
  }
}
</script>

<style scoped>
.match-threshold-editor {
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
}

.threshold-config {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 30px;
}

.threshold-label {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.threshold-input {
  width: 100px;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 600;
  text-align: center;
}

.threshold-input:focus {
  outline: none;
  border-color: #2196f3;
}

.threshold-unit {
  font-size: 14px;
  color: #666;
}

.threshold-slider {
  margin-bottom: 30px;
}

.slider {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: #e0e0e0;
  outline: none;
  -webkit-appearance: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2196f3;
  cursor: pointer;
}

.slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2196f3;
  cursor: pointer;
  border: none;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}

.threshold-desc {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 20px;
}

.threshold-desc p {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #333;
}

.threshold-desc p:last-child {
  margin-bottom: 0;
}

.desc-text {
  color: #666 !important;
  font-size: 13px !important;
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

.info-box h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #1976d2;
  font-weight: 600;
}

.info-box ul,
.info-box ol {
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
