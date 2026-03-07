/**
 * ⚠️ DEPRECATED - 此组件已废弃
 * 
 * 此配置已合并到 GlobalConfigEditor.vue
 * 元数据标签功能现在在全局配置中管理
 * 
 * 废弃日期：2026-03-07
 * 原因：配置简化和合并（阶段2）
 */

<template>
  <div class="metadata-rules-editor">
    <div class="editor-header">
      <h2>元数据处理</h2>
      <p class="description">
        配置元数据标签模式，在文本清理阶段删除这些标签，只保留值。例如："型号：ML-5000" → "ML-5000"
      </p>
      
      <ConfigInfoCard
        stage="preprocessing"
        stage-icon="🔍"
        stage-name="预处理配置 - 文本清理"
        stage-description="此配置在特征提取前生效，用于识别和提取设备描述中的元数据信息（如品牌、型号等）。"
      >
        <template #usage>
          <p>配置元数据提取规则，系统会根据规则从设备描述中提取结构化信息。</p>
          <ul>
            <li><strong>执行时机</strong>：预处理的第一步（文本清理阶段）</li>
            <li><strong>主要功能</strong>：识别并删除元数据标签（如"型号："、"品牌："）</li>
            <li><strong>典型场景</strong>："型号：ML-5000" → "ML-5000"、"品牌：霍尼韦尔" → "霍尼韦尔"</li>
            <li><strong>与复杂参数分解的区别</strong>：元数据处理是删除标签，复杂参数分解是拆分复合参数</li>
          </ul>
        </template>
        <template #examples>
          <ul>
            <li>品牌提取：识别"西门子"、"施耐德"等品牌词</li>
            <li>型号提取：识别"型号：XXX"、"规格：XXX"等模式</li>
            <li>参数提取：识别"DN50"、"4-20mA"等技术参数</li>
          </ul>
        </template>
        <template #notes>
          <ul>
            <li>元数据会作为独立特征参与匹配</li>
            <li>提取规则支持正则表达式</li>
            <li>提取的元数据会影响特征质量评分</li>
          </ul>
        </template>
      </ConfigInfoCard>
    </div>

    <!-- 添加规则 -->
    <div class="config-section">
      <div class="section-header">
        <h3>添加元数据标签</h3>
      </div>

      <div class="add-rule-form">
        <div class="form-row">
          <div class="form-field">
            <label>标签模式</label>
            <input 
              v-model="newRule.pattern" 
              type="text" 
              placeholder="输入标签模式（如：型号、品牌、通径）"
              class="rule-input"
            />
            <p class="field-hint">系统会自动匹配 "标签："、"标签:" 和 "序号.标签：" 等格式</p>
          </div>
        </div>

        <button @click="addRule" class="btn btn-primary" :disabled="!canAddRule">
          <span class="btn-icon">+</span> 添加标签
        </button>
      </div>
    </div>

    <!-- 规则列表 -->
    <div class="config-section">
      <div class="section-header">
        <h3>当前元数据标签</h3>
        <p class="section-description">
          共 {{ localValue.length }} 个标签规则
        </p>
      </div>

      <div v-if="localValue.length === 0" class="empty-state">
        <p>暂无元数据标签</p>
        <p class="empty-hint">添加标签规则以自动删除字段名称</p>
      </div>

      <div v-else class="rules-list">
        <div 
          v-for="(rule, index) in localValue" 
          :key="index"
          class="rule-item"
        >
          <div class="rule-content">
            <div class="rule-pattern">
              <span class="pattern-label">标签：</span>
              <span class="pattern-value">{{ rule.pattern || rule }}</span>
            </div>
            
            <div class="rule-action">
              <span class="action-badge">删除标签</span>
            </div>
          </div>
          
          <button @click="removeRule(index)" class="btn-remove" title="删除">
            ×
          </button>
        </div>
      </div>
    </div>

    <!-- 示例说明 -->
    <div class="example-section">
      <h3>💡 示例效果</h3>
      
      <div class="example-group">
        <h4>简单格式</h4>
        <div class="example-item">
          <div class="example-label">输入文本：</div>
          <div class="example-value">"型号：ML-5000"</div>
        </div>
        <div class="example-item">
          <div class="example-label">处理后：</div>
          <div class="example-value">"ML-5000"</div>
        </div>
      </div>

      <div class="example-group">
        <h4>带序号格式</h4>
        <div class="example-item">
          <div class="example-label">输入文本：</div>
          <div class="example-value">"2.品牌：霍尼韦尔"</div>
        </div>
        <div class="example-item">
          <div class="example-label">处理后：</div>
          <div class="example-value">"霍尼韦尔"</div>
        </div>
      </div>

      <div class="example-note">
        系统会自动识别中文冒号（：）和英文冒号（:），以及带序号的格式（如"1."、"2."等）
      </div>
    </div>

    <!-- 常用标签 -->
    <div class="quick-add-section">
      <h3>快速添加常用标签</h3>
      <div class="quick-add-buttons">
        <button 
          v-for="tag in commonTags" 
          :key="tag"
          @click="quickAddTag(tag)"
          class="btn-quick-add"
          :disabled="hasTag(tag)"
        >
          {{ tag }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, computed } from 'vue'
import ConfigInfoCard from './ConfigInfoCard.vue'

export default {
  name: 'MetadataRulesEditor',
  components: {
    ConfigInfoCard
  },
  props: {
    modelValue: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const localValue = ref([...(props.modelValue || [])])
    const newRule = ref({
      pattern: ''
    })

    // 常用标签
    const commonTags = [
      '型号', '品牌', '规格', '参数', '名称', '类型',
      '通径', '阀体类型', '适用介质', '尺寸', '材质',
      '功率', '电压', '电流', '频率', '温度', '压力',
      '流量', '湿度', '浓度', '范围', '精度', '输出'
    ]

    // 检查是否可以添加规则
    const canAddRule = computed(() => {
      return newRule.value.pattern.trim() !== ''
    })

    // 检查标签是否已存在
    const hasTag = (tag) => {
      return localValue.value.some(rule => {
        const pattern = typeof rule === 'string' ? rule : rule.pattern
        return pattern === tag
      })
    }

    // 添加规则
    const addRule = () => {
      if (!canAddRule.value) return

      const pattern = newRule.value.pattern.trim()

      // 检查是否已存在
      if (hasTag(pattern)) {
        alert('该标签已存在')
        return
      }

      // 添加规则（简化格式，只存储pattern字符串）
      localValue.value.push(pattern)
      newRule.value = { pattern: '' }
      emitChange()
    }

    // 快速添加标签
    const quickAddTag = (tag) => {
      if (hasTag(tag)) return
      
      localValue.value.push(tag)
      emitChange()
    }

    // 删除规则
    const removeRule = (index) => {
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
      newRule,
      commonTags,
      canAddRule,
      hasTag,
      addRule,
      quickAddTag,
      removeRule
    }
  }
}
</script>

<style scoped>
.metadata-rules-editor {
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

.add-rule-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-row {
  display: flex;
  gap: 15px;
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

.rule-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.rule-input:focus {
  outline: none;
  border-color: #2196f3;
}

.field-hint {
  margin: 5px 0 0 0;
  font-size: 12px;
  color: #999;
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

.rules-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rule-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  transition: all 0.2s;
}

.rule-item:hover {
  border-color: #2196f3;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.1);
}

.rule-content {
  display: flex;
  align-items: center;
  gap: 20px;
  flex: 1;
}

.rule-pattern {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 200px;
}

.pattern-label {
  font-size: 13px;
  color: #999;
}

.pattern-value {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.rule-action {
  display: flex;
  align-items: center;
}

.action-badge {
  padding: 4px 12px;
  background: #e3f2fd;
  color: #2196f3;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
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

.example-group {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ffe69c;
}

.example-group:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.example-group h4 {
  margin: 0 0 10px 0;
  font-size: 13px;
  color: #856404;
  font-weight: 600;
}

.example-item {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
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
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ffe69c;
  font-size: 12px;
  color: #856404;
  line-height: 1.6;
}

.quick-add-section {
  margin-top: 25px;
  padding: 20px;
  background: #f0f9ff;
  border-left: 4px solid #2196f3;
  border-radius: 4px;
}

.quick-add-section h3 {
  margin: 0 0 15px 0;
  font-size: 15px;
  color: #1976d2;
}

.quick-add-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.btn-quick-add {
  padding: 6px 12px;
  background: white;
  color: #2196f3;
  border: 1px solid #2196f3;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.btn-quick-add:hover:not(:disabled) {
  background: #2196f3;
  color: white;
}

.btn-quick-add:disabled {
  background: #f5f5f5;
  color: #ccc;
  border-color: #e0e0e0;
  cursor: not-allowed;
}
</style>
