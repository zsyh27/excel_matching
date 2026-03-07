<template>
  <div class="intelligent-cleaning-editor">
    <div class="editor-header">
      <h2>智能清理配置</h2>
      <p class="description">
        智能清理是预处理流程的第一步，用于在早期删除大量无关文本，提高后续处理效率。
      </p>
      <ConfigInfoCard config-id="noise-filter" />
    </div>

    <!-- 启用/禁用开关 -->
    <div class="config-section">
      <div class="section-header">
        <h3>总开关</h3>
      </div>
      <div class="form-group">
        <label class="switch-label">
          <input 
            type="checkbox" 
            v-model="localConfig.enabled"
            @change="emitChange"
          />
          <span class="switch-text">启用智能清理</span>
        </label>
        <p class="help-text">
          关闭后，将跳过所有智能清理步骤，直接进入删除无关关键词阶段
        </p>
      </div>
    </div>

    <!-- 文本清理配置 -->
    <div class="config-section" v-if="localConfig.enabled">
      <div class="section-header">
        <h3>文本清理规则</h3>
        <p class="section-description">
          配置噪音截断和删除规则，在早期过滤掉无关文本
        </p>
      </div>

      <!-- 启用文本清理 -->
      <div class="form-group">
        <label class="switch-label">
          <input 
            type="checkbox" 
            v-model="localConfig.text_cleaning.enabled"
            @change="emitChange"
          />
          <span class="switch-text">启用文本清理</span>
        </label>
      </div>

      <!-- 行号过滤配置 -->
      <div class="subsection" v-if="localConfig.text_cleaning.enabled">
        <h4>行号/序号过滤</h4>
        <p class="help-text">
          自动检测并删除前几列的纯数字（通常是行号、序号等），保留后面的有用内容
        </p>
        
        <div class="form-group">
          <label class="switch-label">
            <input 
              type="checkbox" 
              v-model="localConfig.text_cleaning.filter_row_numbers"
              @change="emitChange"
            />
            <span class="switch-text">启用行号过滤</span>
          </label>
        </div>

        <div class="form-group" v-if="localConfig.text_cleaning.filter_row_numbers">
          <label>检测前几列（1-5）</label>
          <input 
            type="number" 
            v-model.number="localConfig.text_cleaning.row_number_columns"
            min="1"
            max="5"
            class="number-input"
            @input="emitChange"
          />
          <p class="help-text">
            如果行内容的前N列都是纯数字，则删除这些列，保留后面的内容。例如："1 2 3 霍尼韦尔传感器" → "霍尼韦尔传感器"。推荐值：3
          </p>
        </div>
      </div>

      <!-- 噪音截断规则 -->
      <div class="subsection" v-if="localConfig.text_cleaning.enabled">
        <h4>噪音截断规则</h4>
        <p class="help-text">
          当遇到这些模式时，截断文本，丢弃后面的所有内容
        </p>
        
        <div class="rule-list">
          <div 
            v-for="(rule, index) in localConfig.text_cleaning.truncate_delimiters" 
            :key="'truncate-' + index"
            class="rule-item"
          >
            <div class="rule-content">
              <input 
                v-model="rule.description" 
                placeholder="规则描述"
                class="rule-input"
                @input="emitChange"
              />
              <input 
                v-model="rule.pattern" 
                placeholder="正则表达式模式"
                class="rule-input pattern-input"
                @input="emitChange"
              />
            </div>
            <button 
              @click="removeTruncateRule(index)" 
              class="btn-remove"
              title="删除规则"
            >
              ×
            </button>
          </div>
        </div>
        
        <button @click="addTruncateRule" class="btn-add">
          + 添加截断规则
        </button>
      </div>

      <!-- 噪音段落删除规则 -->
      <div class="subsection" v-if="localConfig.text_cleaning.enabled">
        <h4>噪音段落删除规则</h4>
        <p class="help-text">
          删除匹配这些模式的文本段落，但保留其他内容
        </p>
        
        <div class="rule-list">
          <div 
            v-for="(rule, index) in localConfig.text_cleaning.noise_section_patterns" 
            :key="'noise-' + index"
            class="rule-item"
          >
            <div class="rule-content">
              <input 
                v-model="rule.description" 
                placeholder="规则描述"
                class="rule-input"
                @input="emitChange"
              />
              <input 
                v-model="rule.pattern" 
                placeholder="正则表达式模式"
                class="rule-input pattern-input"
                @input="emitChange"
              />
            </div>
            <button 
              @click="removeNoiseRule(index)" 
              class="btn-remove"
              title="删除规则"
            >
              ×
            </button>
          </div>
        </div>
        
        <button @click="addNoiseRule" class="btn-add">
          + 添加噪音删除规则
        </button>
      </div>
    </div>

    <!-- 删除无关关键词配置 -->
    <div class="config-section" v-if="localConfig.enabled">
      <div class="section-header">
        <h3>删除无关关键词</h3>
        <p class="section-description">
          在智能清理之后，删除这些与设备匹配无关的关键词，提高匹配准确性
        </p>
      </div>

      <div class="keyword-input-box">
        <input 
          v-model="newKeyword" 
          type="text" 
          placeholder="输入关键词后按回车添加"
          @keyup.enter="addKeyword"
          class="keyword-input-field"
        />
        <button @click="addKeyword" class="btn-add-keyword">添加</button>
      </div>

      <div class="keyword-tags-container">
        <span 
          v-for="(keyword, index) in ignoreKeywords" 
          :key="'keyword-' + index"
          class="keyword-tag"
        >
          {{ keyword }}
          <button 
            @click="removeKeyword(index)" 
            class="btn-remove-tag"
            title="删除关键词"
          >
            ×
          </button>
        </span>
      </div>

      <div class="keyword-stats">
        共 {{ ignoreKeywords.length }} 个无关关键词
      </div>

      <div class="info-note" style="margin-top: 15px;">
        <strong>💡 提示</strong>：这些关键词会在智能清理之后被删除，例如："施工要求"、"验收标准"、"配件"等非设备信息
      </div>
    </div>

    <!-- 复杂参数分解配置 -->
    <div class="config-section" v-if="localConfig.enabled">
      <div class="section-header">
        <h3>复杂参数分解（技术规格拆分）</h3>
        <p class="section-description">
          将复杂的技术参数拆分为简单的数值特征，提高匹配灵活性。例如："ntc 10k" → ["ntc", "10k"]
        </p>
      </div>

      <!-- 启用复杂参数分解 -->
      <div class="form-group">
        <label class="switch-label">
          <input 
            type="checkbox" 
            v-model="localConfig.complex_parameter_decomposition.enabled"
            @change="emitChange"
          />
          <span class="switch-text">启用复杂参数分解</span>
        </label>
      </div>

      <!-- 分解模式配置 -->
      <div class="subsection" v-if="localConfig.complex_parameter_decomposition.enabled">
        <h4>分解模式</h4>
        <p class="help-text">
          配置需要分解的参数模式（使用正则表达式）。系统会自动提取匹配模式中的数值和文本部分。
        </p>
        
        <div class="rule-list">
          <div 
            v-for="(pattern, index) in localConfig.complex_parameter_decomposition.patterns" 
            :key="'decompose-pattern-' + index"
            class="rule-item"
          >
            <div class="rule-content">
              <input 
                v-model="pattern.description" 
                placeholder="模式描述（如：温度范围、电阻值）"
                class="rule-input"
                @input="emitChange"
              />
              <input 
                v-model="pattern.pattern" 
                placeholder="正则表达式（如：-?\d+~-?\d+℃）"
                class="rule-input pattern-input"
                @input="emitChange"
              />
            </div>
            <button 
              @click="removeDecomposePattern(index)" 
              class="btn-remove"
              title="删除模式"
            >
              ×
            </button>
          </div>
        </div>
        
        <button @click="addDecomposePattern" class="btn-add">
          + 添加分解模式
        </button>
      </div>

      <div class="info-note" style="margin-top: 15px;">
        <strong>💡 示例</strong>：
        <ul>
          <li><strong>"ntc 10k"</strong> → 拆分为 ["ntc", "10k"]</li>
          <li><strong>"-20~60℃"</strong> → 拆分为 ["-20", "60"]（数值部分）</li>
          <li><strong>"0-10V"</strong> → 拆分为 ["0", "10", "v"]</li>
          <li><strong>"DN15"</strong> → 拆分为 ["dn", "15"]</li>
        </ul>
        <p style="margin-top: 8px; color: #666;">
          <strong>注意</strong>：此功能在匹配阶段生效，设备录入阶段保持数据完整性。
        </p>
      </div>
    </div>

    <!-- 技术术语扩展配置 -->
    <div class="config-section" v-if="localConfig.enabled">
      <div class="section-header">
        <h3>技术术语扩展</h3>
        <p class="section-description">
          为技术术语配置同义词和缩写，提高匹配召回率。例如："485通讯" → ["RS485", "485"]
        </p>
      </div>

      <!-- 术语映射配置 -->
      <div class="subsection">
        <h4>术语映射</h4>
        <p class="help-text">
          为技术术语配置扩展词汇（一个术语可以映射到多个词汇）
        </p>
        
        <div class="term-list">
          <div 
            v-for="(expansions, term) in technicalTerms" 
            :key="'term-' + term"
            class="term-item"
          >
            <div class="term-content">
              <div class="term-label">{{ term }}</div>
              <input 
                :value="Array.isArray(expansions) ? expansions.join(', ') : ''" 
                placeholder="扩展词汇（用逗号分隔，如：RS485, 485）"
                class="term-input"
                @input="updateTermExpansions(term, $event.target.value)"
              />
            </div>
            <button 
              @click="removeTerm(term)" 
              class="btn-remove"
              title="删除术语"
            >
              ×
            </button>
          </div>
        </div>
        
        <div class="add-term-box">
          <input 
            v-model="newTerm" 
            placeholder="新术语（如：485通讯）"
            class="term-input-new"
            @keyup.enter="addTerm"
          />
          <input 
            v-model="newTermExpansions" 
            placeholder="扩展词汇（用逗号分隔，如：RS485, 485）"
            class="term-input-new"
            @keyup.enter="addTerm"
          />
          <button @click="addTerm" class="btn-add-term">添加</button>
        </div>
      </div>

      <div class="info-note" style="margin-top: 15px;">
        <strong>💡 示例</strong>：
        <ul>
          <li><strong>"485通讯"</strong> → ["RS485", "485"]</li>
          <li><strong>"4-20mA"</strong> → ["4-20mA", "电流输出"]</li>
          <li><strong>"NTC"</strong> → ["NTC", "负温度系数", "热敏电阻"]</li>
          <li><strong>"DDC"</strong> → ["DDC", "直接数字控制器"]</li>
        </ul>
        <p style="margin-top: 8px; color: #666;">
          <strong>注意</strong>：术语扩展在匹配阶段生效，可以提高对不同写法的识别能力。
        </p>
      </div>
    </div>

    <!-- 特征质量评分配置 -->
    <div class="config-section" v-if="localConfig.enabled">
      <div class="section-header">
        <h3>特征质量评分</h3>
        <p class="section-description">
          配置特征质量评分规则，过滤低质量特征
        </p>
      </div>

      <!-- 启用特征质量评分 -->
      <div class="form-group">
        <label class="switch-label">
          <input 
            type="checkbox" 
            v-model="localConfig.feature_quality_scoring.enabled"
            @change="emitChange"
          />
          <span class="switch-text">启用特征质量评分</span>
        </label>
      </div>

      <!-- 最小质量分数 -->
      <div class="form-group" v-if="localConfig.feature_quality_scoring.enabled">
        <label>最小质量分数（0-100）</label>
        <input 
          type="number" 
          v-model.number="localConfig.feature_quality_scoring.min_quality_score"
          min="0"
          max="100"
          class="number-input"
          @input="emitChange"
        />
        <p class="help-text">
          低于此分数的特征将被过滤。推荐值：50
        </p>
      </div>

      <!-- 评分规则 -->
      <div class="subsection" v-if="localConfig.feature_quality_scoring.enabled">
        <h4>评分规则</h4>
        <p class="help-text">
          配置各项评分规则的权重（正数为加分，负数为扣分）
        </p>
        
        <div class="scoring-rules">
          <div 
            v-for="(value, key) in localConfig.feature_quality_scoring.scoring_rules" 
            :key="key"
            class="scoring-rule-item"
          >
            <label>{{ getScoringRuleLabel(key) }}</label>
            <input 
              type="number" 
              v-model.number="localConfig.feature_quality_scoring.scoring_rules[key]"
              class="number-input small"
              @input="emitChange"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 使用说明 -->
    <div class="info-box">
      <h4>💡 使用说明</h4>
      <ul>
        <li><strong>执行顺序</strong>：智能清理 → 删除无关关键词 → 归一化 → 特征提取</li>
        <li><strong>行号过滤</strong>：检测前N列都是纯数字的行，自动过滤行号和序号等噪音数据</li>
        <li><strong>噪音截断</strong>：遇到"施工要求"等关键词时，截断文本，丢弃后面的所有内容</li>
        <li><strong>噪音删除</strong>：删除"按照图纸规范"等无关段落，但保留其他有用内容</li>
        <li><strong>删除关键词</strong>：删除配置的无关关键词，如"施工要求"、"验收标准"等</li>
        <li><strong>质量评分</strong>：对提取的特征进行质量评分，过滤低质量特征</li>
        <li><strong>正则表达式</strong>：使用Python正则表达式语法，注意转义特殊字符</li>
      </ul>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import ConfigInfoCard from './ConfigInfoCard.vue'

export default {
  name: 'IntelligentCleaningEditor',
  components: {
    ConfigInfoCard
  },
  props: {
    modelValue: {
      type: Object,
      required: true
    },
    fullConfig: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['update:modelValue', 'change', 'update-ignore-keywords'],
  setup(props, { emit }) {
    // 创建本地配置副本
    const localConfig = ref(JSON.parse(JSON.stringify(props.modelValue)))

    // 从父组件获取 ignore_keywords 配置
    const ignoreKeywords = ref([])
    const newKeyword = ref('')
    
    // 技术术语扩展
    const technicalTerms = ref({})
    const newTerm = ref('')
    const newTermExpansions = ref('')
    
    // 初始化 ignore_keywords
    const initIgnoreKeywords = () => {
      // 从 fullConfig 中获取 ignore_keywords
      if (props.fullConfig && Array.isArray(props.fullConfig.ignore_keywords)) {
        ignoreKeywords.value = [...props.fullConfig.ignore_keywords]
      } else {
        ignoreKeywords.value = []
      }
      console.log('初始化 ignore_keywords:', ignoreKeywords.value)
    }
    
    // 初始化技术术语
    const initTechnicalTerms = () => {
      if (localConfig.value.technical_term_expansion) {
        technicalTerms.value = { ...localConfig.value.technical_term_expansion }
      } else {
        technicalTerms.value = {}
      }
    }
    
    // 确保配置结构完整
    const ensureConfigStructure = () => {
      // 确保 enabled 存在
      if (localConfig.value.enabled === undefined) {
        localConfig.value.enabled = true
      }
      
      // 确保 text_cleaning 存在
      if (!localConfig.value.text_cleaning) {
        localConfig.value.text_cleaning = {
          enabled: true,
          filter_row_numbers: true,
          row_number_columns: 3,
          truncate_delimiters: [],
          noise_section_patterns: []
        }
      }
      
      // 确保 text_cleaning.enabled 存在
      if (localConfig.value.text_cleaning.enabled === undefined) {
        localConfig.value.text_cleaning.enabled = true
      }
      
      // 确保 complex_parameter_decomposition 存在
      if (!localConfig.value.complex_parameter_decomposition) {
        localConfig.value.complex_parameter_decomposition = {
          enabled: false,
          patterns: []
        }
      }
      
      // 确保 technical_term_expansion 存在
      if (!localConfig.value.technical_term_expansion) {
        localConfig.value.technical_term_expansion = {}
      }
      
      // 确保 feature_quality_scoring 存在
      if (!localConfig.value.feature_quality_scoring) {
        localConfig.value.feature_quality_scoring = {
          enabled: true,
          min_quality_score: 50,
          scoring_rules: {}
        }
      }
      
      // 确保 patterns 是数组
      if (!Array.isArray(localConfig.value.complex_parameter_decomposition.patterns)) {
        localConfig.value.complex_parameter_decomposition.patterns = []
      }
      
      // 确保 truncate_delimiters 是数组
      if (!Array.isArray(localConfig.value.text_cleaning.truncate_delimiters)) {
        localConfig.value.text_cleaning.truncate_delimiters = []
      }
      
      // 确保 noise_section_patterns 是数组
      if (!Array.isArray(localConfig.value.text_cleaning.noise_section_patterns)) {
        localConfig.value.text_cleaning.noise_section_patterns = []
      }
    }
    
    initIgnoreKeywords()
    ensureConfigStructure()
    initTechnicalTerms()

    // 监听外部变化
    watch(() => props.modelValue, (newValue) => {
      localConfig.value = JSON.parse(JSON.stringify(newValue))
      ensureConfigStructure()
      initTechnicalTerms()
    }, { deep: true })
    
    // 监听 fullConfig 变化
    watch(() => props.fullConfig, () => {
      initIgnoreKeywords()
    }, { deep: true })

    // 发出变更事件
    const emitChange = () => {
      emit('update:modelValue', localConfig.value)
      emit('change')
    }
    
    // 更新 ignore_keywords
    const updateIgnoreKeywords = () => {
      // 过滤空字符串
      const filtered = ignoreKeywords.value.filter(k => k && k.trim())
      // 发出更新事件，需要通知父组件更新顶层的 ignore_keywords
      emit('update:modelValue', localConfig.value)
      // 发出自定义事件，让父组件知道需要更新 ignore_keywords
      emit('update-ignore-keywords', filtered)
      emit('change')
    }
    
    // 添加关键词
    const addKeyword = () => {
      const keyword = newKeyword.value.trim()
      if (keyword && !ignoreKeywords.value.includes(keyword)) {
        ignoreKeywords.value.push(keyword)
        newKeyword.value = ''
        updateIgnoreKeywords()
      }
    }
    
    // 删除关键词
    const removeKeyword = (index) => {
      ignoreKeywords.value.splice(index, 1)
      updateIgnoreKeywords()
    }

    // 添加截断规则
    const addTruncateRule = () => {
      if (!localConfig.value.text_cleaning.truncate_delimiters) {
        localConfig.value.text_cleaning.truncate_delimiters = []
      }
      localConfig.value.text_cleaning.truncate_delimiters.push({
        description: '',
        pattern: ''
      })
      emitChange()
    }

    // 删除截断规则
    const removeTruncateRule = (index) => {
      localConfig.value.text_cleaning.truncate_delimiters.splice(index, 1)
      emitChange()
    }

    // 添加噪音删除规则
    const addNoiseRule = () => {
      if (!localConfig.value.text_cleaning.noise_section_patterns) {
        localConfig.value.text_cleaning.noise_section_patterns = []
      }
      localConfig.value.text_cleaning.noise_section_patterns.push({
        description: '',
        pattern: ''
      })
      emitChange()
    }

    // 删除噪音删除规则
    const removeNoiseRule = (index) => {
      localConfig.value.text_cleaning.noise_section_patterns.splice(index, 1)
      emitChange()
    }
    
    // 添加复杂参数分解模式
    const addDecomposePattern = () => {
      if (!localConfig.value.complex_parameter_decomposition.patterns) {
        localConfig.value.complex_parameter_decomposition.patterns = []
      }
      localConfig.value.complex_parameter_decomposition.patterns.push({
        description: '',
        pattern: ''
      })
      emitChange()
    }
    
    // 删除复杂参数分解模式
    const removeDecomposePattern = (index) => {
      localConfig.value.complex_parameter_decomposition.patterns.splice(index, 1)
      emitChange()
    }
    
    // 添加技术术语
    const addTerm = () => {
      const term = newTerm.value.trim()
      const expansions = newTermExpansions.value.trim()
      
      if (term && expansions) {
        // 将逗号分隔的字符串转换为数组
        const expansionArray = expansions.split(',').map(e => e.trim()).filter(e => e)
        
        technicalTerms.value[term] = expansionArray
        localConfig.value.technical_term_expansion = { ...technicalTerms.value }
        
        newTerm.value = ''
        newTermExpansions.value = ''
        emitChange()
      }
    }
    
    // 删除技术术语
    const removeTerm = (term) => {
      delete technicalTerms.value[term]
      localConfig.value.technical_term_expansion = { ...technicalTerms.value }
      emitChange()
    }
    
    // 更新技术术语扩展
    const updateTermExpansions = (term, value) => {
      const expansionArray = value.split(',').map(e => e.trim()).filter(e => e)
      technicalTerms.value[term] = expansionArray
      localConfig.value.technical_term_expansion = { ...technicalTerms.value }
      emitChange()
    }

    // 获取评分规则标签
    const getScoringRuleLabel = (key) => {
      const labels = {
        'is_technical_term': '是技术术语',
        'has_number': '包含数字',
        'has_unit': '包含单位',
        'in_device_keywords': '在设备关键词库中',
        'appropriate_length': '长度适中(3-20)',
        'is_metadata_label': '是元数据标签',
        'is_common_word': '是常见词',
        'too_short': '太短(<2)',
        'is_pure_number': '纯数字',
        'is_pure_punctuation': '纯标点'
      }
      return labels[key] || key
    }

    return {
      localConfig,
      ignoreKeywords,
      newKeyword,
      technicalTerms,
      newTerm,
      newTermExpansions,
      emitChange,
      addTruncateRule,
      removeTruncateRule,
      addNoiseRule,
      removeNoiseRule,
      addDecomposePattern,
      removeDecomposePattern,
      addTerm,
      removeTerm,
      updateTermExpansions,
      getScoringRuleLabel,
      updateIgnoreKeywords,
      addKeyword,
      removeKeyword
    }
  }
}
</script>

<style scoped>
.intelligent-cleaning-editor {
  padding: 20px;
}

.editor-header {
  margin-bottom: 30px;
}

.editor-header h2 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #333;
}

.description {
  margin: 0;
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
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
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
  margin: 8px 0 0 0;
  font-size: 12px;
  color: #999;
  line-height: 1.5;
}

.rule-list {
  margin-bottom: 15px;
}

.rule-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 10px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
}

.rule-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rule-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.pattern-input {
  font-family: 'Courier New', monospace;
  background: #fff;
}

.btn-remove {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border: none;
  background: #f44336;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 20px;
  line-height: 1;
  transition: background 0.2s;
}

.btn-remove:hover {
  background: #d32f2f;
}

.btn-add {
  padding: 8px 16px;
  border: 1px dashed #2196f3;
  background: white;
  color: #2196f3;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.btn-add:hover {
  background: #e3f2fd;
  border-color: #1976d2;
}

.number-input {
  width: 120px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.number-input.small {
  width: 80px;
}

.scoring-rules {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.scoring-rule-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.scoring-rule-item label {
  margin: 0;
  font-size: 13px;
  color: #666;
  font-weight: normal;
}

.info-box {
  margin-top: 30px;
  padding: 20px;
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  border-radius: 4px;
}

.info-box h4 {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #1976d2;
}

.info-box ul {
  margin: 0;
  padding-left: 20px;
}

.info-box li {
  margin-bottom: 8px;
  font-size: 13px;
  color: #555;
  line-height: 1.6;
}

.info-box li strong {
  color: #333;
}

.keywords-list {
  margin-bottom: 15px;
}

.keyword-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.keyword-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.keyword-input-box {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.keyword-input-field {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.keyword-input-field:focus {
  outline: none;
  border-color: #2196f3;
}

.btn-add-keyword {
  padding: 10px 20px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.btn-add-keyword:hover {
  background: #1976d2;
}

.keyword-tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  min-height: 100px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-bottom: 15px;
}

.keyword-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 16px;
  font-size: 13px;
  height: fit-content;
}

.btn-remove-tag {
  background: none;
  border: none;
  color: #1976d2;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s;
}

.btn-remove-tag:hover {
  background: rgba(25, 118, 210, 0.1);
}

.keyword-stats {
  color: #666;
  font-size: 13px;
  margin-bottom: 15px;
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

.term-list {
  margin-bottom: 15px;
}

.term-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
}

.term-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.term-label {
  min-width: 120px;
  font-weight: 500;
  color: #333;
  font-size: 13px;
}

.term-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
  background: white;
}

.add-term-box {
  display: flex;
  gap: 10px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 4px;
  border: 1px dashed #ddd;
}

.term-input-new {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.term-input-new:focus {
  outline: none;
  border-color: #2196f3;
}

.btn-add-term {
  padding: 8px 16px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.2s;
  white-space: nowrap;
}

.btn-add-term:hover {
  background: #1976d2;
}
</style>
