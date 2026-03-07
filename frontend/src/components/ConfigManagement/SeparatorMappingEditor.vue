<template>
  <div class="separator-mapping-editor">
    <div class="editor-header">
      <h2>分隔符统一</h2>
      <p class="description">
        配置分隔符映射规则，将各种不同格式的分隔符统一转换为标准格式，用于文本清理阶段。
      </p>
    </div>

    <el-alert
      type="info"
      :closable="false"
      show-icon
      class="config-explanation"
    >
      <template #title>
        <strong>功能说明</strong>
      </template>
      <div class="explanation-content">
        <p><strong>分隔符统一在文本清理阶段执行</strong>，目的是标准化文本格式</p>
        <ul>
          <li><strong>执行时机</strong>：预处理的第一步（智能清理阶段）</li>
          <li><strong>主要功能</strong>：将中文分隔符转换为英文分隔符，统一全角半角</li>
          <li><strong>典型场景</strong>：
            <ul>
              <li>中文分号 <code>；</code> → 英文分号 <code>;</code></li>
              <li>中文逗号 <code>，</code> → 英文逗号 <code>,</code></li>
              <li>全角空格 <code>　</code> → 半角空格 <code> </code></li>
            </ul>
          </li>
        </ul>
        <p class="tip">💡 <strong>与"处理分隔符"的区别</strong>：分隔符统一是<strong>转换</strong>格式，处理分隔符是<strong>拆分</strong>文本</p>
      </div>
    </el-alert>

    <!-- 添加映射 -->
    <div class="config-section">
      <div class="section-header">
        <h3>添加映射规则</h3>
      </div>

      <div class="add-mapping-form">
        <div class="form-row">
          <div class="form-field">
            <label>源分隔符</label>
            <input 
              v-model="newMapping.from" 
              type="text" 
              placeholder="输入要转换的分隔符..."
              class="mapping-input"
              maxlength="5"
            />
            <p class="field-hint">例如：；（中文分号）</p>
          </div>
          
          <div class="arrow">→</div>
          
          <div class="form-field">
            <label>目标分隔符</label>
            <input 
              v-model="newMapping.to" 
              type="text" 
              placeholder="输入转换后的分隔符..."
              class="mapping-input"
              maxlength="5"
            />
            <p class="field-hint">例如：;（英文分号）</p>
          </div>
        </div>

        <button @click="addMapping" class="btn btn-primary" :disabled="!canAddMapping">
          <span class="btn-icon">+</span> 添加映射
        </button>
      </div>
    </div>

    <!-- 映射列表 -->
    <div class="config-section">
      <div class="section-header">
        <h3>当前映射规则</h3>
        <p class="section-description">
          共 {{ localValue.length }} 条映射规则
        </p>
      </div>

      <div v-if="localValue.length === 0" class="empty-state">
        <p>暂无映射规则</p>
        <p class="empty-hint">添加映射规则以统一不同格式的分隔符</p>
      </div>

      <div v-else class="mappings-list">
        <div 
          v-for="(mapping, index) in localValue" 
          :key="index"
          class="mapping-item"
        >
          <div class="mapping-content">
            <div class="mapping-from">
              <span class="char-display">{{ displayChar(mapping.from) }}</span>
              <span class="char-code">{{ getCharCode(mapping.from) }}</span>
            </div>
            
            <div class="mapping-arrow">→</div>
            
            <div class="mapping-to">
              <span class="char-display">{{ displayChar(mapping.to) }}</span>
              <span class="char-code">{{ getCharCode(mapping.to) }}</span>
            </div>
          </div>
          
          <button @click="removeMapping(index)" class="btn-remove" title="删除">
            ×
          </button>
        </div>
      </div>
    </div>

    <!-- 示例说明 -->
    <div class="example-section">
      <h3>💡 示例效果</h3>
      <div class="example-item">
        <div class="example-label">输入文本：</div>
        <div class="example-value">"温度传感器；湿度传感器，CO2传感器"</div>
      </div>
      <div class="example-item">
        <div class="example-label">转换后：</div>
        <div class="example-value">"温度传感器;湿度传感器,CO2传感器"</div>
      </div>
      <div class="example-note">
        中文分号和逗号被统一转换为英文格式，便于后续的文本处理
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, computed } from 'vue'

export default {
  name: 'SeparatorMappingEditor',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const localValue = ref([...(props.modelValue || [])])
    const newMapping = ref({
      from: '',
      to: ''
    })

    // 检查是否可以添加映射
    const canAddMapping = computed(() => {
      return newMapping.value.from && newMapping.value.to
    })

    // 显示字符（特殊字符显示名称）
    const displayChar = (char) => {
      const specialChars = {
        '\n': '换行符',
        '\t': '制表符',
        ' ': '空格',
        '　': '全角空格',
        '\\': '反斜杠',
        '；': '中文分号',
        '，': '中文逗号',
        '：': '中文冒号',
        '（': '中文左括号',
        '）': '中文右括号'
      }
      return specialChars[char] || char
    }

    // 获取字符编码
    const getCharCode = (char) => {
      return `U+${char.charCodeAt(0).toString(16).toUpperCase().padStart(4, '0')}`
    }

    // 添加映射
    const addMapping = () => {
      if (!canAddMapping.value) return

      const from = newMapping.value.from
      const to = newMapping.value.to

      // 检查是否已存在相同的源分隔符
      const exists = localValue.value.some(m => m.from === from)
      if (exists) {
        alert('该源分隔符已存在映射规则')
        return
      }

      localValue.value.push({ from, to })
      newMapping.value = { from: '', to: '' }
      emitChange()
    }

    // 删除映射
    const removeMapping = (index) => {
      localValue.value.splice(index, 1)
      emitChange()
    }

    // 发送变更事件
    const emitChange = () => {
      emit('update:modelValue', localValue.value)
      emit('change')
    }

    // 监听外部变化
    watch(() => props.modelValue, (newVal) => {
      localValue.value = [...(newVal || [])]
    })

    return {
      localValue,
      newMapping,
      canAddMapping,
      displayChar,
      getCharCode,
      addMapping,
      removeMapping
    }
  }
}
</script>

<style scoped>
.separator-mapping-editor {
  max-width: 900px;
}

.editor-header h2 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #333;
}

.description {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.config-explanation {
  margin-bottom: 25px;
}

.explanation-content {
  font-size: 13px;
  line-height: 1.8;
}

.explanation-content p {
  margin: 8px 0;
}

.explanation-content ul {
  margin: 5px 0;
  padding-left: 20px;
}

.explanation-content li {
  margin: 4px 0;
}

.explanation-content code {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  color: #e6a23c;
  font-family: 'Courier New', monospace;
  font-weight: 600;
}

.explanation-content .tip {
  margin-top: 12px;
  padding: 8px 12px;
  background-color: #f0f9ff;
  border-left: 3px solid #409eff;
  border-radius: 4px;
}

.config-section {
  margin-bottom: 25px;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.section-header {
  margin-bottom: 15px;
}

.section-header h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #333;
}

.section-description {
  margin: 0;
  color: #666;
  font-size: 13px;
}

.add-mapping-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-row {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.form-field {
  flex: 1;
}

.form-field label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.mapping-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.mapping-input:focus {
  outline: none;
  border-color: #2196f3;
}

.field-hint {
  margin: 5px 0 0 0;
  font-size: 12px;
  color: #999;
}

.arrow {
  font-size: 24px;
  color: #999;
  margin-top: 32px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1976d2;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 16px;
  margin-right: 5px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.empty-state p {
  margin: 5px 0;
}

.empty-hint {
  font-size: 13px;
}

.mappings-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mapping-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  transition: all 0.2s;
}

.mapping-item:hover {
  border-color: #2196f3;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.1);
}

.mapping-content {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
}

.mapping-from,
.mapping-to {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 150px;
}

.char-display {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.char-code {
  font-size: 12px;
  color: #999;
  font-family: monospace;
}

.mapping-arrow {
  font-size: 20px;
  color: #2196f3;
  font-weight: bold;
}

.btn-remove {
  background: none;
  border: none;
  color: #999;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  line-height: 1;
  border-radius: 4px;
  transition: all 0.2s;
}

.btn-remove:hover {
  background: #ffebee;
  color: #f44336;
}

.example-section {
  margin-top: 25px;
  padding: 20px;
  background: #fff3cd;
  border-left: 4px solid #ffc107;
  border-radius: 4px;
}

.example-section h3 {
  margin: 0 0 15px 0;
  font-size: 15px;
  color: #856404;
}

.example-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  font-size: 13px;
}

.example-label {
  font-weight: 500;
  color: #856404;
  min-width: 80px;
}

.example-value {
  font-family: 'Courier New', monospace;
  color: #333;
  background: white;
  padding: 4px 8px;
  border-radius: 3px;
}

.example-note {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #ffe69c;
  font-size: 12px;
  color: #856404;
  line-height: 1.6;
}
</style>
