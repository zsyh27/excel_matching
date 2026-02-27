<template>
  <div class="global-config-editor">
    <div class="editor-header">
      <h2>全局配置</h2>
      <p class="description">
        全局处理选项，包括大小写转换、空格删除、全角转半角等。
      </p>
    </div>

    <div class="editor-body">
      <div class="config-item">
        <label class="config-label">
          <span class="label-text">默认匹配阈值</span>
          <span class="label-desc">规则匹配的最低得分要求</span>
        </label>
        <div class="config-control">
          <input 
            v-model.number="localValue.default_match_threshold" 
            type="number" 
            step="0.1"
            min="0"
            class="number-input"
            @input="emitChange"
          />
          <input 
            v-model.number="localValue.default_match_threshold" 
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
          <span class="label-text">统一转小写</span>
          <span class="label-desc">将所有文本转换为小写</span>
        </label>
        <div class="config-control">
          <label class="switch">
            <input 
              v-model="localValue.unify_lowercase" 
              type="checkbox"
              @change="emitChange"
            />
            <span class="slider"></span>
          </label>
        </div>
      </div>

      <div class="config-item">
        <label class="config-label">
          <span class="label-text">删除空格</span>
          <span class="label-desc">删除文本中的所有空格</span>
        </label>
        <div class="config-control">
          <label class="switch">
            <input 
              v-model="localValue.remove_whitespace" 
              type="checkbox"
              @change="emitChange"
            />
            <span class="slider"></span>
          </label>
        </div>
      </div>

      <div class="config-item">
        <label class="config-label">
          <span class="label-text">全角转半角</span>
          <span class="label-desc">将全角字符转换为半角字符</span>
        </label>
        <div class="config-control">
          <label class="switch">
            <input 
              v-model="localValue.fullwidth_to_halfwidth" 
              type="checkbox"
              @change="emitChange"
            />
            <span class="slider"></span>
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'GlobalConfigEditor',
  props: {
    modelValue: {
      type: Object,
      default: () => ({
        default_match_threshold: 3.0,
        unify_lowercase: true,
        remove_whitespace: true,
        fullwidth_to_halfwidth: true
      })
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const localValue = ref({ ...props.modelValue })

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
.global-config-editor {
  max-width: 700px;
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

/* 开关样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 26px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 26px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #2196f3;
}

input:checked + .slider:before {
  transform: translateX(24px);
}
</style>
