/**
 * ⚠️ DEPRECATED - 此组件已废弃
 * 
 * 此配置已合并到 GlobalConfigEditor.vue
 * 智能拆分功能现在在全局配置中管理
 * 
 * 废弃日期：2026-03-07
 * 原因：配置简化和合并（阶段2）
 */

<template>
  <div class="split-chars-editor">
    <div class="editor-header">
      <h2>处理分隔符</h2>
      <p class="description">
        配置文本拆分规则，定义用于拆分设备描述的分隔符，将文本拆分为独立特征。
      </p>
      
      <ConfigInfoCard
        stage="preprocessing"
        stage-icon="🔍"
        stage-name="预处理配置 - 特征提取"
        stage-description="此配置在特征提取时生效，定义用于拆分设备描述的分隔符，将文本拆分为独立特征。"
      >
        <template #usage>
          <p>配置分隔符列表，系统会使用这些分隔符将设备描述拆分为多个特征。</p>
          <ul>
            <li><strong>常用分隔符</strong>：空格、逗号、分号、斜杠</li>
            <li><strong>中文分隔符</strong>：、，；</li>
            <li><strong>特殊分隔符</strong>：+、-、_、|</li>
            <li><strong>智能拆分</strong>：在匹配阶段自动拆分复合词（如"室内墙装" → ["室内", "墙装"]）</li>
          </ul>
        </template>
        <template #examples>
          <ul>
            <li>常用分隔符：空格、逗号、分号、斜杠</li>
            <li>中文分隔符：、，；</li>
            <li>特殊分隔符：+、-、_、|</li>
          </ul>
        </template>
        <template #notes>
          <ul>
            <li>分隔符会影响特征的粒度</li>
            <li>过多的分隔符可能导致特征过于细碎</li>
            <li>建议根据实际数据格式调整</li>
          </ul>
        </template>
      </ConfigInfoCard>
    </div>

    <!-- 智能拆分配置 -->
    <div class="config-section">
      <div class="section-header">
        <h3>智能拆分（匹配阶段）</h3>
        <p class="section-description">
          在匹配阶段自动拆分复合词和技术规格，提高匹配灵活性。例如："室内墙装" → ["室内", "墙装"]
        </p>
      </div>

      <el-alert
        type="warning"
        :closable="false"
        show-icon
        class="config-explanation"
      >
        <template #title>
          <strong>重要说明</strong>
        </template>
        <div class="explanation-content">
          <p><strong>智能拆分仅在匹配阶段生效</strong></p>
          <ul>
            <li><strong>设备录入阶段</strong>：保持数据完整性，不拆分（如"室内墙装"保持完整）</li>
            <li><strong>匹配阶段</strong>：智能拆分，提高灵活性（如"室内墙装" → ["室内", "墙装"]）</li>
          </ul>
          <p class="tip">💡 这种设计既保证了数据完整性，又提高了匹配召回率</p>
        </div>
      </el-alert>

      <!-- 启用智能拆分 -->
      <div class="form-group">
        <label class="switch-label">
          <input 
            type="checkbox" 
            v-model="intelligentSplitting.enabled"
            @change="emitIntelligentSplittingChange"
          />
          <span class="switch-text">启用智能拆分</span>
        </label>
        <p class="help-text">
          启用后，系统会在匹配阶段自动拆分复合词、技术规格等，提高匹配灵活性
        </p>
      </div>

      <!-- 拆分选项 -->
      <div class="subsection" v-if="intelligentSplitting.enabled">
        <h4>拆分选项</h4>
        
        <div class="form-group">
          <label class="switch-label">
            <input 
              type="checkbox" 
              v-model="intelligentSplitting.split_compound_words"
              @change="emitIntelligentSplittingChange"
            />
            <span class="switch-text">拆分复合词</span>
          </label>
          <p class="help-text">
            自动拆分复合词，例如："室内墙装" → ["室内", "墙装"]
          </p>
        </div>

        <div class="form-group">
          <label class="switch-label">
            <input 
              type="checkbox" 
              v-model="intelligentSplitting.split_technical_specs"
              @change="emitIntelligentSplittingChange"
            />
            <span class="switch-text">拆分技术规格</span>
          </label>
          <p class="help-text">
            自动拆分技术规格，例如："ntc 10k" → ["ntc", "10k"]，"DN15" → ["dn", "15"]
          </p>
        </div>

        <div class="form-group">
          <label class="switch-label">
            <input 
              type="checkbox" 
              v-model="intelligentSplitting.split_by_space"
              @change="emitIntelligentSplittingChange"
            />
            <span class="switch-text">按空格拆分</span>
          </label>
          <p class="help-text">
            按空格拆分特征，例如："ntc 10k" → ["ntc", "10k"]
          </p>
        </div>
      </div>

      <div class="info-note" style="margin-top: 15px;">
        <strong>💡 示例效果</strong>：
        <ul>
          <li><strong>"室内墙装"</strong> → 拆分为 ["室内", "墙装"]，可以匹配"室内吊装"</li>
          <li><strong>"ntc 10k"</strong> → 拆分为 ["ntc", "10k"]，可以匹配"NTC10K"</li>
          <li><strong>"DN15"</strong> → 拆分为 ["dn", "15"]，可以匹配"通径15"</li>
        </ul>
      </div>
    </div>

    <!-- 分隔符配置 -->
    <div class="config-section">
      <div class="section-header">
        <h3>分隔符配置</h3>
        <p class="section-description">
          定义用于拆分特征的分隔符。这些字符将被用来分割设备描述文本。
        </p>
      </div>

      <el-alert
        type="info"
        :closable="false"
        show-icon
        class="config-explanation"
      >
        <template #title>
          <strong>配置说明</strong>
        </template>
        <div class="explanation-content">
          <p><strong>第一个分隔符</strong>是"标准分隔符"（当前：<code>{{ standardSeparator }}</code>）</p>
          <ul>
            <li>在智能清理阶段，常见分隔符（逗号、空格、制表符等）会自动转换为标准分隔符</li>
            <li>您<strong>不需要</strong>手动添加这些常见分隔符到列表中</li>
          </ul>
          <p><strong>其他分隔符</strong>用于特征提取时的文本拆分</p>
          <ul>
            <li>如果您的设备描述使用了特殊分隔符（如 <code>|</code>、<code>/</code>），可以添加到列表中</li>
            <li>系统会按照这些分隔符拆分文本，提取独立的特征</li>
          </ul>
          <p class="tip">💡 <strong>建议：</strong>大多数情况下，只需保留默认的 <code>+</code> 作为标准分隔符即可</p>
        </div>
      </el-alert>

      <div class="toolbar">
        <input 
          v-model="newChar" 
          type="text" 
          placeholder="输入新分隔符..."
          @keyup.enter="addChar"
          class="char-input"
          maxlength="5"
        />
        <button @click="addChar" class="btn btn-primary">添加</button>
      </div>

      <div class="chars-list">
        <div 
          v-for="(char, index) in localValue" 
          :key="index"
          class="char-item"
        >
          <span class="char-display">{{ displayChar(char) }}</span>
          <span class="char-code">{{ getCharCode(char) }}</span>
          <button @click="removeChar(index)" class="btn-remove">×</button>
        </div>
      </div>

      <div class="stats">
        <span>共 {{ localValue.length }} 个分隔符</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, computed } from 'vue'
import ConfigInfoCard from './ConfigInfoCard.vue'

export default {
  name: 'SplitCharsEditor',
  components: {
    ConfigInfoCard
  },
  props: {
    modelValue: {
      type: Array,
      default: () => []
    },
    fullConfig: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const localValue = ref([...(props.modelValue || [])])
    const newChar = ref('')
    
    // 智能拆分配置
    const intelligentSplitting = ref({
      enabled: false,
      split_compound_words: true,
      split_technical_specs: true,
      split_by_space: true
    })
    
    // 初始化智能拆分配置
    const initIntelligentSplitting = () => {
      if (props.fullConfig && props.fullConfig.intelligent_splitting) {
        intelligentSplitting.value = { ...props.fullConfig.intelligent_splitting }
      }
    }
    
    initIntelligentSplitting()

    // 计算标准分隔符（第一个分隔符）
    const standardSeparator = computed(() => {
      return localValue.value.length > 0 ? localValue.value[0] : '未设置'
    })

    // 显示字符（特殊字符显示名称）
    const displayChar = (char) => {
      const specialChars = {
        '\n': '换行符',
        '\t': '制表符',
        ' ': '空格',
        '\\': '反斜杠'
      }
      return specialChars[char] || char
    }

    // 获取字符编码
    const getCharCode = (char) => {
      return `U+${char.charCodeAt(0).toString(16).toUpperCase().padStart(4, '0')}`
    }

    // 添加分隔符
    const addChar = () => {
      const char = newChar.value
      if (char && !localValue.value.includes(char)) {
        localValue.value.push(char)
        newChar.value = ''
        emitChange()
      }
    }

    // 删除分隔符
    const removeChar = (index) => {
      localValue.value.splice(index, 1)
      emitChange()
    }

    // 发送变更事件
    const emitChange = () => {
      emit('update:modelValue', localValue.value)
      emit('change')
    }
    
    // 发送智能拆分配置变更
    const emitIntelligentSplittingChange = () => {
      // 直接修改fullConfig中的intelligent_splitting
      if (props.fullConfig) {
        props.fullConfig.intelligent_splitting = { ...intelligentSplitting.value }
      }
      emit('change')
    }

    // 监听外部变化
    watch(() => props.modelValue, (newVal) => {
      localValue.value = [...(newVal || [])]
    })
    
    watch(() => props.fullConfig, () => {
      initIntelligentSplitting()
    }, { deep: true })

    return {
      localValue,
      newChar,
      intelligentSplitting,
      standardSeparator,
      displayChar,
      getCharCode,
      addChar,
      removeChar,
      emitIntelligentSplittingChange
    }
  }
}
</script>

<style scoped>
.split-chars-editor {
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

.config-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.section-header {
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
}

.section-description {
  margin: 0;
  color: #666;
  font-size: 13px;
}

.subsection {
  margin-top: 20px;
  padding: 15px;
  background: white;
  border-radius: 6px;
}

.subsection h4 {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

.switch-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: normal;
}

.switch-label input[type="checkbox"] {
  margin-right: 10px;
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.switch-text {
  font-size: 14px;
  color: #333;
}

.help-text {
  margin: 8px 0 0 28px;
  font-size: 12px;
  color: #999;
  line-height: 1.5;
}

.config-explanation {
  margin-bottom: 20px;
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

.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.char-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.chars-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 15px;
}

.char-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 15px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.char-display {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  min-width: 100px;
}

.char-code {
  flex: 1;
  font-size: 13px;
  color: #999;
  font-family: monospace;
}

.btn-remove {
  background: none;
  border: none;
  color: #999;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  line-height: 1;
}

.btn-remove:hover {
  color: #f44336;
}

.stats {
  margin-top: 15px;
  font-size: 13px;
  color: #666;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover {
  background: #1976d2;
}
</style>
