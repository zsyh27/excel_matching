<template>
  <div class="parameter-patterns-editor">
    <div class="editor-header">
      <h2>参数提取模式配置</h2>
      <p class="description">配置用于从文本中提取参数的正则表达式模式。系统将使用这些模式自动识别和提取各种格式的参数。</p>
    </div>

    <div class="patterns-container">
      <div class="patterns-header">
        <span class="patterns-count">共 {{ localPatterns.length }} 个模式</span>
        <button class="add-btn" @click="addPattern">
          <span>+</span> 添加模式
        </button>
      </div>

      <div class="patterns-list">
        <div v-for="(pattern, index) in localPatterns" :key="index" class="pattern-item">
          <div class="pattern-header">
            <div class="pattern-info">
              <span class="pattern-id">{{ pattern.id }}</span>
              <span class="pattern-name">{{ pattern.name }}</span>
            </div>
            <div class="pattern-actions">
              <label class="toggle-switch">
                <input type="checkbox" v-model="pattern.enabled" @change="handlePatternChange" />
                <span class="toggle-slider"></span>
              </label>
              <button class="delete-btn" @click="deletePattern(index)">删除</button>
            </div>
          </div>
          
          <div class="pattern-content">
            <div class="pattern-row">
              <label>正则表达式:</label>
              <input type="text" v-model="pattern.pattern" @input="handlePatternChange" class="pattern-input" />
            </div>
            <div class="pattern-row">
              <label>描述:</label>
              <input type="text" v-model="pattern.description" @input="handlePatternChange" class="pattern-input" />
            </div>
            <div class="pattern-row examples">
              <label>示例:</label>
              <div class="examples-list">
                <span v-for="(example, exIndex) in pattern.examples" :key="exIndex" class="example-tag">
                  {{ example }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="pattern-tips">
      <h4>💡 使用说明</h4>
      <ul>
        <li><strong>正则表达式</strong>：用于匹配文本中的参数格式，支持标准正则语法</li>
        <li><strong>启用/禁用</strong>：禁用的模式不会参与参数提取</li>
        <li><strong>测试功能</strong>：可以在测试页面验证正则表达式的提取效果</li>
        <li><strong>常见格式</strong>：
          <ul>
            <li>量程：<code>\d+[-~]\d+[a-zA-Z/]+</code> 匹配 "0~1000ug/m3"</li>
            <li>输出信号：<code>\d+[-~]\d+(mA|V|VDC)</code> 匹配 "4~20mA"</li>
            <li>精度：<code>±\d+%</code> 匹配 "±5%"</li>
          </ul>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  fullConfig: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const localPatterns = ref([])

watch(() => props.modelValue, (newVal) => {
  if (newVal && Array.isArray(newVal)) {
    localPatterns.value = JSON.parse(JSON.stringify(newVal))
  }
}, { immediate: true, deep: true })

const addPattern = () => {
  localPatterns.value.push({
    id: `pattern_${Date.now()}`,
    name: '新模式',
    pattern: '',
    description: '',
    examples: [],
    enabled: true
  })
  handlePatternChange()
}

const deletePattern = (index) => {
  localPatterns.value.splice(index, 1)
  handlePatternChange()
}

const handlePatternChange = () => {
  emit('update:modelValue', JSON.parse(JSON.stringify(localPatterns.value)))
  emit('change')
}
</script>

<style scoped>
.parameter-patterns-editor {
  padding: 20px;
}

.editor-header {
  margin-bottom: 24px;
}

.editor-header h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #303133;
}

.description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.patterns-container {
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  overflow: hidden;
}

.patterns-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
}

.patterns-count {
  font-size: 14px;
  color: #606266;
}

.add-btn {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.add-btn:hover {
  background: #66b1ff;
}

.patterns-list {
  max-height: 500px;
  overflow-y: auto;
}

.pattern-item {
  border-bottom: 1px solid #ebeef5;
  padding: 16px 20px;
}

.pattern-item:last-child {
  border-bottom: none;
}

.pattern-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.pattern-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pattern-id {
  font-family: monospace;
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 2px 8px;
  border-radius: 4px;
}

.pattern-name {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.pattern-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 22px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.3s;
  border-radius: 22px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: #67c23a;
}

input:checked + .toggle-slider:before {
  transform: translateX(22px);
}

.delete-btn {
  padding: 4px 12px;
  background: #fff;
  color: #f56c6c;
  border: 1px solid #f56c6c;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.delete-btn:hover {
  background: #f56c6c;
  color: white;
}

.pattern-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.pattern-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pattern-row label {
  min-width: 100px;
  font-size: 13px;
  color: #606266;
}

.pattern-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 13px;
}

.pattern-input:focus {
  outline: none;
  border-color: #409eff;
}

.pattern-row.examples {
  align-items: flex-start;
}

.examples-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.example-tag {
  padding: 4px 8px;
  background: #ecf5ff;
  color: #409eff;
  border-radius: 4px;
  font-size: 12px;
}

.pattern-tips {
  margin-top: 20px;
  padding: 16px 20px;
  background: #fdf6ec;
  border-radius: 8px;
  border: 1px solid #faecd8;
}

.pattern-tips h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #e6a23c;
}

.pattern-tips ul {
  margin: 0;
  padding-left: 20px;
}

.pattern-tips li {
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.pattern-tips li:last-child {
  margin-bottom: 0;
}

.pattern-tips code {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
}
</style>
