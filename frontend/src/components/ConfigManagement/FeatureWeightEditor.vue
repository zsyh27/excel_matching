<template>
  <div class="feature-weight-editor">
    <div class="editor-header">
      <h2>特征权重配置</h2>
      <p class="description">
        控制规则生成时不同类型特征的权重，影响匹配准确性。权重越高，该类型特征在匹配时的重要性越大。
      </p>
      
      <ConfigInfoCard
        stage="pre-entry"
        stage-icon="📝"
        stage-name="设备信息录入前配置"
        stage-description="此配置在设备信息录入前生效，定义不同特征类型在匹配时的权重，影响匹配得分计算。"
      >
        <template #usage>
          <p>为不同类型的特征设置权重值，权重越高的特征在匹配时影响越大。</p>
          <ul>
            <li><strong>设备类型权重</strong>：设备类型特征的权重（如传感器、控制器、阀门）</li>
            <li><strong>品牌权重</strong>：品牌特征的权重</li>
            <li><strong>规格型号权重</strong>：规格型号特征的权重</li>
            <li><strong>参数权重</strong>：技术参数特征的权重</li>
            <li><strong>其他特征权重</strong>：其他类型特征的权重</li>
          </ul>
        </template>
        <template #examples>
          <ul>
            <li>设备类型：权重5（最重要）</li>
            <li>品牌：权重4</li>
            <li>规格型号：权重3</li>
            <li>参数：权重2</li>
            <li>其他特征：权重1</li>
          </ul>
        </template>
        <template #notes>
          <ul>
            <li>权重范围：0.5-10，数值越大权重越高</li>
            <li>权重会直接影响匹配得分</li>
            <li>建议根据实际业务重要性调整权重</li>
          </ul>
        </template>
      </ConfigInfoCard>
    </div>

    <div class="editor-body">
      <div class="config-item highlight-item">
        <label class="config-label">
          <span class="label-text">设备类型权重</span>
          <span class="label-desc">设备类型特征的权重值（如：传感器、控制器、阀门）- 最核心的匹配参数</span>
        </label>
        <div class="config-control">
          <input 
            v-model.number="localValue.device_type_weight" 
            type="number" 
            step="0.5"
            min="0"
            max="30"
            class="number-input"
            @input="emitChange"
          />
          <input 
            v-model.number="localValue.device_type_weight" 
            type="range" 
            min="0" 
            max="30" 
            step="0.5"
            class="range-input"
            @input="emitChange"
          />
        </div>
      </div>

      <div class="config-item highlight-item">
        <label class="config-label">
          <span class="label-text">关键参数权重（key_params）</span>
          <span class="label-desc">设备关键参数的权重值（如：量程、输出信号）- 次核心的匹配参数</span>
        </label>
        <div class="config-control">
          <input 
            v-model.number="localValue.key_params_weight" 
            type="number" 
            step="0.5"
            min="0"
            max="20"
            class="number-input"
            @input="emitChange"
          />
          <input 
            v-model.number="localValue.key_params_weight" 
            type="range" 
            min="0" 
            max="20" 
            step="0.5"
            class="range-input"
            @input="emitChange"
          />
        </div>
      </div>

      <div class="config-item">
        <label class="config-label">
          <span class="label-text">品牌权重</span>
          <span class="label-desc">品牌特征的权重值（如：霍尼韦尔、西门子）</span>
        </label>
        <div class="config-control">
          <input 
            v-model.number="localValue.brand_weight" 
            type="number" 
            step="0.5"
            min="0"
            max="20"
            class="number-input"
            @input="emitChange"
          />
          <input 
            v-model.number="localValue.brand_weight" 
            type="range" 
            min="0" 
            max="20" 
            step="0.5"
            class="range-input"
            @input="emitChange"
          />
        </div>
      </div>

      <div class="config-item">
        <label class="config-label">
          <span class="label-text">型号权重</span>
          <span class="label-desc">型号特征的权重值（如：QAA2061、V5011N1040）</span>
        </label>
        <div class="config-control">
          <input 
            v-model.number="localValue.model_weight" 
            type="number" 
            step="0.5"
            min="0"
            max="10"
            class="number-input"
            @input="emitChange"
          />
          <input 
            v-model.number="localValue.model_weight" 
            type="range" 
            min="0" 
            max="10" 
            step="0.5"
            class="range-input"
            @input="emitChange"
          />
        </div>
      </div>

      <div class="config-item">
        <label class="config-label">
          <span class="label-text">通用参数权重</span>
          <span class="label-desc">通用参数特征的权重值（如：4-20mA、0-10V）- 区分度较低</span>
        </label>
        <div class="config-control">
          <input 
            v-model.number="localValue.parameter_weight" 
            type="number" 
            step="0.1"
            min="0"
            max="5"
            class="number-input"
            @input="emitChange"
          />
          <input 
            v-model.number="localValue.parameter_weight" 
            type="range" 
            min="0" 
            max="5" 
            step="0.1"
            class="range-input"
            @input="emitChange"
          />
        </div>
      </div>

      <div class="weight-summary">
        <h3>权重说明</h3>
        <div class="summary-section">
          <h4>推荐配置（已优化）</h4>
          <ul>
            <li><strong>设备类型权重</strong>：推荐值 <span class="highlight">20.0</span>，设备类型是最核心的匹配参数，权重最高</li>
            <li><strong>关键参数权重（key_params）</strong>：推荐值 <span class="highlight">15.0</span>，关键参数是次核心的匹配参数</li>
            <li><strong>品牌权重</strong>：推荐值 <span class="highlight">10.0</span>，品牌是重要的识别特征</li>
            <li><strong>型号权重</strong>：推荐值 <span class="highlight">5.0</span>，型号通常是唯一标识</li>
            <li><strong>通用参数权重</strong>：推荐值 <span class="highlight">1.0</span>，通用参数区分度较低</li>
          </ul>
        </div>
        <div class="summary-section">
          <h4>权重作用</h4>
          <p>这些权重控制添加设备到设备库时生成匹配规则的特征权重。权重越高，该类型特征在匹配时的重要性越大。</p>
          <p><strong>注意</strong>：修改权重后，需要重新生成现有设备的规则才能生效。新添加的设备会自动使用新权重。</p>
        </div>
        <div class="summary-section">
          <h4>核心参数优先</h4>
          <p><strong>设备类型</strong>和<strong>关键参数（key_params）</strong>是匹配的核心，建议保持高权重以确保匹配准确性。</p>
          <p>添加设备时，请务必填写设备类型字段，并将最重要的参数（如量程、输出信号）填写在关键参数（key_params）中。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import ConfigInfoCard from './ConfigInfoCard.vue'

export default {
  name: 'FeatureWeightEditor',
  components: {
    ConfigInfoCard
  },
  props: {
    modelValue: {
      type: Object,
      default: () => ({
        device_type_weight: 20.0,
        key_params_weight: 15.0,
        brand_weight: 10.0,
        model_weight: 5.0,
        parameter_weight: 1.0
      })
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const localValue = ref({ ...props.modelValue })

    // 确保所有字段有默认值（使用新的推荐值）
    if (localValue.value.device_type_weight === undefined) {
      localValue.value.device_type_weight = 20.0
    }
    if (localValue.value.key_params_weight === undefined) {
      localValue.value.key_params_weight = 15.0
    }
    if (localValue.value.brand_weight === undefined) {
      localValue.value.brand_weight = 10.0
    }
    if (localValue.value.model_weight === undefined) {
      localValue.value.model_weight = 5.0
    }
    if (localValue.value.parameter_weight === undefined) {
      localValue.value.parameter_weight = 1.0
    }

    const emitChange = () => {
      emit('update:modelValue', { ...localValue.value })
      emit('change')
    }

    watch(() => props.modelValue, (newVal) => {
      localValue.value = { ...newVal }
    }, { deep: true })

    return {
      localValue,
      emitChange
    }
  }
}
</script>

<style scoped>
.feature-weight-editor {
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

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  margin-bottom: 15px;
}

.config-item.highlight-item {
  background: #fffbf0;
  border: 2px solid #ffa726;
  box-shadow: 0 2px 8px rgba(255, 167, 38, 0.1);
}

.config-item.highlight-item .label-text {
  color: #f57c00;
  font-weight: 600;
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
  gap: 15px;
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
  width: 200px;
}

.weight-summary {
  margin-top: 30px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
  border-left: 4px solid #2196f3;
}

.weight-summary h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #333;
}

.weight-summary h4 {
  margin: 15px 0 10px 0;
  font-size: 14px;
  color: #555;
  font-weight: 600;
}

.summary-section {
  margin-bottom: 20px;
}

.summary-section:last-child {
  margin-bottom: 0;
}

.summary-section p {
  margin: 5px 0;
  color: #666;
  font-size: 13px;
  line-height: 1.6;
}

.weight-summary ul {
  margin: 0;
  padding-left: 20px;
}

.weight-summary li {
  margin-bottom: 8px;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.weight-summary strong {
  color: #333;
}

.highlight {
  color: #2196f3;
  font-weight: 600;
  font-size: 15px;
}
</style>
