<template>
  <div class="feature-weight-editor">
    <div class="editor-header">
      <h2>特征权重配置</h2>
      <p class="description">
        控制规则生成时不同类型特征的权重，影响匹配准确性。权重越高，该类型特征在匹配时的重要性越大。
      </p>
    </div>

    <div class="editor-body">
      <div class="config-item">
        <label class="config-label">
          <span class="label-text">品牌权重</span>
          <span class="label-desc">品牌特征的权重值（如：霍尼韦尔、西门子）</span>
        </label>
        <div class="config-control">
          <input 
            v-model.number="localValue.brand_weight" 
            type="number" 
            step="0.1"
            min="0"
            max="10"
            class="number-input"
            @input="emitChange"
          />
          <input 
            v-model.number="localValue.brand_weight" 
            type="range" 
            min="0" 
            max="10" 
            step="0.1"
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
            step="0.1"
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
            step="0.1"
            class="range-input"
            @input="emitChange"
          />
        </div>
      </div>

      <div class="config-item">
        <label class="config-label">
          <span class="label-text">设备类型权重</span>
          <span class="label-desc">设备类型特征的权重值（如：传感器、控制器、阀门）</span>
        </label>
        <div class="config-control">
          <input 
            v-model.number="localValue.device_type_weight" 
            type="number" 
            step="0.1"
            min="0"
            max="10"
            class="number-input"
            @input="emitChange"
          />
          <input 
            v-model.number="localValue.device_type_weight" 
            type="range" 
            min="0" 
            max="10" 
            step="0.1"
            class="range-input"
            @input="emitChange"
          />
        </div>
      </div>

      <div class="config-item">
        <label class="config-label">
          <span class="label-text">参数权重</span>
          <span class="label-desc">通用参数特征的权重值（如：4-20mA、0-10V）</span>
        </label>
        <div class="config-control">
          <input 
            v-model.number="localValue.parameter_weight" 
            type="number" 
            step="0.1"
            min="0"
            max="10"
            class="number-input"
            @input="emitChange"
          />
          <input 
            v-model.number="localValue.parameter_weight" 
            type="range" 
            min="0" 
            max="10" 
            step="0.1"
            class="range-input"
            @input="emitChange"
          />
        </div>
      </div>

      <div class="weight-summary">
        <h3>权重说明</h3>
        <ul>
          <li><strong>品牌权重</strong>：推荐值 3.0，品牌是重要的识别特征</li>
          <li><strong>型号权重</strong>：推荐值 3.0，型号通常是唯一标识</li>
          <li><strong>设备类型权重</strong>：推荐值 5.0，设备类型是最重要的区分特征</li>
          <li><strong>参数权重</strong>：推荐值 1.0，通用参数区分度较低</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'FeatureWeightEditor',
  props: {
    modelValue: {
      type: Object,
      default: () => ({
        brand_weight: 3.0,
        model_weight: 3.0,
        device_type_weight: 5.0,
        parameter_weight: 1.0
      })
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const localValue = ref({ ...props.modelValue })

    // 确保所有字段有默认值
    if (localValue.value.brand_weight === undefined) {
      localValue.value.brand_weight = 3.0
    }
    if (localValue.value.model_weight === undefined) {
      localValue.value.model_weight = 3.0
    }
    if (localValue.value.device_type_weight === undefined) {
      localValue.value.device_type_weight = 5.0
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
</style>
