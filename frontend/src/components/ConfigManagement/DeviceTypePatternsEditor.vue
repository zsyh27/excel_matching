<template>
  <div class="device-type-patterns-editor">
    <div class="editor-header">
      <h2>设备类型模式</h2>
      <p class="description">
        配置设备类型识别模式，包括基础设备类型和前缀关键词映射，用于智能识别设备类型。
      </p>
      
      <ConfigInfoCard
        stage="intelligent-extraction"
        stage-icon="🧠"
        stage-name="智能特征提取"
        stage-description="此配置用于智能特征提取阶段的设备类型识别，是五步流程的第一步。"
        usage-text="设备类型模式用于从用户输入的设备描述中智能识别设备类型，支持精确匹配、模糊匹配、关键词匹配和类型推断四种模式。"
        :examples="[
          '基础设备类型：传感器、探测器、变送器、执行器等',
          '前缀关键词：温度→温度传感器、CO→CO浓度探测器',
          '智能识别：CO浓度探测器 → 探测器类型，置信度90%'
        ]"
        :notes="[
          '设备类型识别是五步流程的第一步，准确率直接影响后续步骤',
          '支持四种识别模式：精确匹配、模糊匹配、关键词匹配、类型推断',
          '前缀关键词可以提高识别准确率和覆盖范围'
        ]"
      >
        <template #usage>
          <ul>
            <li><strong>精确匹配</strong>：完全匹配设备类型名称（置信度100%）</li>
            <li><strong>模糊匹配</strong>：部分匹配设备类型（置信度90%）</li>
            <li><strong>关键词匹配</strong>：通过关键词组合匹配（置信度80%）</li>
            <li><strong>类型推断</strong>：根据前缀关键词推断类型（置信度70%）</li>
          </ul>
        </template>
      </ConfigInfoCard>
    </div>

    <div class="editor-body">
      <div class="config-section">
        <div class="section-header">
          <h3>基础设备类型</h3>
          <div class="header-actions">
            <button @click="refreshDeviceTypes" :disabled="refreshing" class="btn btn-secondary btn-sm">
              {{ refreshing ? '刷新中...' : '🔄 刷新' }}
            </button>
            <span class="type-count">共 {{ deviceTypesFromDB.length }} 种类型</span>
          </div>
        </div>

        <div class="device-types-categories">
          <div v-for="(category, categoryName) in categorizedDeviceTypes" :key="categoryName" class="category-section">
            <div class="category-header" @click="toggleCategory(categoryName)">
              <span class="toggle-icon">{{ expandedCategories[categoryName] ? '▼' : '▶' }}</span>
              <span class="category-name">{{ categoryName }}</span>
              <span class="category-count">({{ category.length }} 种)</span>
            </div>
            <div v-if="expandedCategories[categoryName]" class="category-content">
              <div class="device-type-tags">
                <span v-for="item in category" :key="item.type" class="device-type-tag">
                  {{ item.type }}
                  <span class="device-count">{{ item.count }}</span>
                </span>
              </div>
            </div>
          </div>
          <div v-if="!deviceTypesFromDB || deviceTypesFromDB.length === 0" class="empty-state">
            暂无设备类型数据，点击刷新按钮从数据库加载
          </div>
        </div>
      </div>

      <div class="config-section">
        <div class="section-header">
          <h3>前缀关键词</h3>
          <button @click="addPrefixKeyword" class="btn btn-primary">
            + 添加前缀词
          </button>
        </div>

        <div class="prefix-keywords-list">
          <div v-for="(types, prefix) in config.prefix_keywords" :key="prefix" class="prefix-item">
            <div class="prefix-info">
              <span class="prefix-name">{{ prefix }}</span>
              <div class="prefix-types">
                <span v-for="type in types" :key="type" class="type-tag">{{ type }}</span>
              </div>
            </div>
            <div class="item-actions">
              <button @click="editPrefixKeyword(prefix)" class="btn btn-sm">编辑</button>
              <button @click="deletePrefixKeyword(prefix)" class="btn btn-sm btn-danger">删除</button>
            </div>
          </div>
          <div v-if="!config.prefix_keywords || Object.keys(config.prefix_keywords).length === 0" class="empty-state">
            暂无前缀关键词，点击上方按钮添加
          </div>
        </div>
      </div>

      <div class="config-section">
        <div class="section-header">
          <h3>设备类型识别测试</h3>
        </div>

        <div class="test-area">
          <div class="test-input">
            <input 
              v-model="testText" 
              type="text" 
              placeholder="输入设备描述进行测试，例如：CO浓度探测器、温度传感器、蝶阀"
              @input="onInputChange"
              @blur="testRecognition"
            />
            <div v-if="testing" class="testing-indicator">
              <span class="loading-spinner"></span>
              识别中...
            </div>
          </div>

          <div v-if="testResult" class="test-result">
            <div class="result-header">
              <h4>🎯 设备类型识别结果</h4>
              <div class="confidence-indicator">
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: (testResult.confidence * 100) + '%' }"></div>
                </div>
                <span class="confidence-text">置信度: {{ (testResult.confidence * 100).toFixed(1) }}%</span>
              </div>
            </div>
            
            <div class="result-grid">
              <div class="result-item">
                <span class="label">设备类型:</span>
                <span class="value">{{ testResult.sub_type || testResult.main_type || '未识别' }}</span>
              </div>
              <div class="result-item">
                <span class="label">分类:</span>
                <span class="value">{{ testResult.main_type || '未知' }}</span>
              </div>
              <div class="result-item">
                <span class="label">置信度:</span>
                <div class="confidence-info">
                  <span class="confidence-value" :class="getConfidenceClass(testResult.confidence)">
                    {{ (testResult.confidence * 100).toFixed(1) }}%
                  </span>
                  <span class="confidence-tooltip" :title="getConfidenceExplanation(testResult.mode, testResult.confidence)">
                    ❓
                  </span>
                </div>
              </div>
              <div class="result-item">
                <span class="label">识别模式:</span>
                <div class="mode-info">
                  <span class="value mode-badge" :class="testResult.mode">
                    {{ getModeText(testResult.mode) }}
                  </span>
                  <span class="mode-description">{{ getModeDescription(testResult.mode) }}</span>
                </div>
              </div>
              <div class="result-item">
                <span class="label">关键词:</span>
                <div class="keywords-info">
                  <div class="keywords">
                    <span v-for="keyword in testResult.keywords" :key="keyword" class="keyword-tag">
                      {{ keyword }}
                    </span>
                    <span v-if="!testResult.keywords || testResult.keywords.length === 0" class="no-keywords">
                      无关键词
                    </span>
                  </div>
                  <div v-if="testResult.keywords && testResult.keywords.length > 0" class="keywords-description">
                    通过关键词"{{ testResult.keywords.join('、') }}"识别出设备类型
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="action-buttons">
        <button @click="saveConfig" :disabled="saving" class="btn btn-primary">
          {{ saving ? '保存中...' : '保存配置' }}
        </button>
        <button @click="resetConfig" class="btn btn-secondary">重置</button>
      </div>
    </div>

    <!-- 前缀关键词对话框 -->
    <PrefixKeywordDialog
      v-model="showPrefixDialog"
      :prefix-keyword="editingPrefix"
      :device-types="availableDeviceTypes"
      :existing-prefixes="Object.keys(config.prefix_keywords)"
      @confirm="handlePrefixConfirm"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import ConfigInfoCard from './ConfigInfoCard.vue'
import PrefixKeywordDialog from './PrefixKeywordDialog.vue'

const config = ref({
  device_types: [],
  prefix_keywords: {},
  main_types: {}
})

const deviceTypesFromDB = ref([])
const categorizedDeviceTypes = ref({})
const expandedCategories = ref({})
const refreshing = ref(false)

const testText = ref('')
const testResult = ref(null)
const testing = ref(false)
const saving = ref(false)

// 前缀关键词对话框相关
const showPrefixDialog = ref(false)
const editingPrefix = ref(null)

// 防抖定时器
let debounceTimer = null

// 计算可用的设备类型列表（从基础设备类型中获取）
const availableDeviceTypes = computed(() => {
  const types = []
  
  // 从分类的设备类型中提取所有设备类型
  Object.values(categorizedDeviceTypes.value).forEach(category => {
    if (Array.isArray(category)) {
      category.forEach(item => {
        if (item.type && !types.includes(item.type)) {
          types.push(item.type)
        }
      })
    }
  })
  
  // 按字母顺序排序
  return types.sort()
})

const onInputChange = () => {
  // 清除之前的定时器
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
  
  // 如果输入为空，清除结果
  if (!testText.value.trim()) {
    testResult.value = null
    return
  }
  
  // 设置新的定时器，500ms后自动执行识别
  debounceTimer = setTimeout(() => {
    testRecognition()
  }, 500)
}

const loadConfig = async () => {
  try {
    const response = await fetch('/api/config')
    const data = await response.json()
    
    if (data.success && data.config) {
      const ieConfig = data.config.intelligent_extraction || {}
      const deviceTypeConfig = ieConfig.device_type_recognition || {}
      
      config.value = {
        device_types: deviceTypeConfig.device_types || [],
        prefix_keywords: deviceTypeConfig.prefix_keywords || {},
        main_types: deviceTypeConfig.main_types || {}
      }
    }
  } catch (error) {
    console.error('加载配置失败:', error)
    alert('加载配置失败: ' + error.message)
  }
}

const refreshDeviceTypes = async () => {
  refreshing.value = true
  try {
    const response = await fetch('/api/devices/types-from-database')
    const data = await response.json()
    
    if (data.success && data.data) {
      deviceTypesFromDB.value = data.data.device_types || []
      categorizedDeviceTypes.value = data.data.categorized || {}
      
      // 默认展开所有分类
      Object.keys(categorizedDeviceTypes.value).forEach(category => {
        expandedCategories.value[category] = true
      })
    } else {
      alert('获取设备类型失败: ' + (data.error_message || '未知错误'))
    }
  } catch (error) {
    console.error('获取设备类型失败:', error)
    alert('获取设备类型失败: ' + error.message)
  } finally {
    refreshing.value = false
  }
}

const toggleCategory = (categoryName) => {
  expandedCategories.value[categoryName] = !expandedCategories.value[categoryName]
}

const saveConfig = async () => {
  saving.value = true
  try {
    // 获取当前完整配置
    const response = await fetch('/api/config')
    const data = await response.json()
    
    if (!data.success) {
      throw new Error('获取当前配置失败')
    }
    
    // 更新智能提取配置
    const fullConfig = data.config
    if (!fullConfig.intelligent_extraction) {
      fullConfig.intelligent_extraction = {}
    }
    if (!fullConfig.intelligent_extraction.device_type_recognition) {
      fullConfig.intelligent_extraction.device_type_recognition = {}
    }
    
    fullConfig.intelligent_extraction.device_type_recognition = {
      ...fullConfig.intelligent_extraction.device_type_recognition,
      device_types: config.value.device_types,
      prefix_keywords: config.value.prefix_keywords,
      main_types: config.value.main_types
    }
    
    // 保存配置
    const saveResponse = await fetch('/api/config/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        config: fullConfig,
        remark: '更新设备类型模式配置'
      })
    })
    
    const saveData = await saveResponse.json()
    
    if (saveData.success) {
      alert('配置保存成功')
    } else {
      throw new Error(saveData.error_message || '保存失败')
    }
  } catch (error) {
    console.error('保存配置失败:', error)
    alert('保存配置失败: ' + error.message)
  } finally {
    saving.value = false
  }
}

const testRecognition = async () => {
  if (!testText.value || !testText.value.trim()) {
    testResult.value = null
    return
  }

  testing.value = true
  try {
    const response = await fetch('/api/intelligent-extraction/extract', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text: testText.value.trim() })
    })
    
    const result = await response.json()
    
    if (result.success && result.data) {
      testResult.value = result.data.device_type || {}
    } else {
      console.error('识别失败:', result.error?.message || '未知错误')
      testResult.value = null
    }
  } catch (error) {
    console.error('识别失败:', error)
    testResult.value = null
  } finally {
    testing.value = false
  }
}

const getModeText = (mode) => {
  switch (mode) {
    case 'exact': return '精确匹配'
    case 'fuzzy': return '模糊匹配'
    case 'keyword': return '关键词匹配'
    case 'inference': return '类型推断'
    default: return '未知'
  }
}

const getModeDescription = (mode) => {
  return '精确匹配100% > 模糊匹配90% > 关键词匹配80% > 类型推断70%'
}

const getConfidenceClass = (confidence) => {
  if (confidence >= 0.9) return 'high'
  if (confidence >= 0.7) return 'medium'
  return 'low'
}

const getConfidenceExplanation = (mode, confidence) => {
  const baseExplanation = {
    'exact': '精确匹配：完全匹配设备类型名称',
    'fuzzy': '模糊匹配：部分匹配设备类型名称', 
    'keyword': '关键词匹配：通过关键词组合匹配',
    'inference': '类型推断：根据前缀关键词推断类型'
  }
  
  const confidenceLevel = confidence >= 0.9 ? '高' : confidence >= 0.7 ? '中' : '低'
  const confidenceDesc = confidence >= 0.9 ? '识别准确度很高' : 
                         confidence >= 0.7 ? '识别准确度中等' : '识别准确度较低'
  
  return `${baseExplanation[mode] || '未知模式'}，置信度${(confidence * 100).toFixed(1)}%（${confidenceLevel}），${confidenceDesc}`
}

const addDeviceType = () => {
  alert('基础设备类型从数据库读取，不可手动添加。如需添加新设备类型，请在设备管理中录入相应设备。')
}

const editDeviceType = (index) => {
  alert('基础设备类型从数据库读取，不可手动编辑。')
}

const deleteDeviceType = (index) => {
  alert('基础设备类型从数据库读取，不可手动删除。')
}

const addPrefixKeyword = () => {
  editingPrefix.value = null
  showPrefixDialog.value = true
}

const editPrefixKeyword = (prefix) => {
  editingPrefix.value = {
    prefix: prefix,
    types: config.value.prefix_keywords[prefix] || []
  }
  showPrefixDialog.value = true
}

const deletePrefixKeyword = (prefix) => {
  if (confirm('确定要删除这个前缀关键词吗？')) {
    delete config.value.prefix_keywords[prefix]
  }
}

const handlePrefixConfirm = (data) => {
  if (editingPrefix.value) {
    // 编辑模式：删除旧的，添加新的
    const oldPrefix = editingPrefix.value.prefix
    if (oldPrefix !== data.prefix) {
      delete config.value.prefix_keywords[oldPrefix]
    }
  }
  
  // 添加或更新前缀关键词
  config.value.prefix_keywords[data.prefix] = data.types
  
  // 关闭对话框
  showPrefixDialog.value = false
  editingPrefix.value = null
}

const resetConfig = () => {
  if (confirm('确定要重置配置吗？所有未保存的修改将丢失。')) {
    loadConfig()
  }
}

onMounted(() => {
  loadConfig()
  refreshDeviceTypes()
})
</script>

<style scoped>
.device-type-patterns-editor {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.editor-header {
  margin-bottom: 30px;
}

.editor-header h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: #333;
}

.description {
  margin: 0 0 20px 0;
  color: #666;
  line-height: 1.6;
}

.editor-body {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.config-section {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.type-count {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.info-text {
  margin-bottom: 20px;
  padding: 12px 16px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.device-types-categories {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.category-section {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #f5f5f5;
  cursor: pointer;
  transition: background-color 0.2s;
  user-select: none;
}

.category-header:hover {
  background: #eeeeee;
}

.toggle-icon {
  font-size: 12px;
  color: #666;
  width: 12px;
  text-align: center;
}

.category-name {
  font-weight: 500;
  color: #333;
  flex: 1;
}

.category-count {
  font-size: 13px;
  color: #666;
}

.category-content {
  padding: 16px;
  background: white;
}

.device-type-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.device-type-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 16px;
  font-size: 13px;
  border: 1px solid #bbdefb;
  font-weight: 500;
}

.device-count {
  background: #1976d2;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: bold;
  min-width: 20px;
  text-align: center;
}



.prefix-keywords-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.prefix-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
}

.prefix-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.prefix-name {
  font-weight: 500;
  color: #333;
}

.prefix-types {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.type-tag {
  display: inline-block;
  padding: 2px 8px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 3px;
  font-size: 12px;
  border: 1px solid #bbdefb;
}

.item-actions {
  display: flex;
  gap: 8px;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 40px 20px;
  font-style: italic;
}

.test-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.test-input {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
}

.test-input input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.test-input input:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.1);
}

.testing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 13px;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #e0e0e0;
  border-top: 2px solid #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 设备类型识别测试样式 */
.test-result {
  margin-top: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  background: white;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #e0e0e0;
}

.result-header h4 {
  margin: 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.confidence-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  width: 120px;
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50 0%, #8bc34a 100%);
  transition: width 0.3s ease;
}

.confidence-text {
  font-size: 13px;
  font-weight: 500;
  color: #666;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  padding: 20px;
}

.result-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.result-item .label {
  width: 80px;
  font-weight: 500;
  color: #666;
  flex-shrink: 0;
  font-size: 14px;
}

.result-item .value {
  color: #333;
  font-size: 14px;
}

.mode-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.mode-badge.exact {
  background: #e8f5e8;
  color: #2e7d32;
}

.mode-badge.fuzzy {
  background: #e3f2fd;
  color: #1565c0;
}

.mode-badge.keyword {
  background: #fff3e0;
  color: #ef6c00;
}

.mode-badge.inference {
  background: #fce4ec;
  color: #c2185b;
}

.keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.keyword-tag {
  padding: 3px 8px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 12px;
  font-size: 12px;
  border: 1px solid #bbdefb;
}

.mode-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mode-description {
  font-size: 12px;
  color: #666;
  font-style: italic;
}

.keywords-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.keywords-description {
  font-size: 12px;
  color: #666;
  font-style: italic;
}

.no-keywords {
  color: #999;
  font-style: italic;
  font-size: 12px;
}

/* 置信度显示样式 */
.confidence-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.confidence-value {
  font-weight: 600;
  font-size: 14px;
}

.confidence-value.high {
  color: #4caf50;
}

.confidence-value.medium {
  color: #ff9800;
}

.confidence-value.low {
  color: #f44336;
}

.confidence-tooltip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  background: #e0e0e0;
  color: #666;
  border-radius: 50%;
  font-size: 10px;
  cursor: help;
  transition: all 0.2s;
}

.confidence-tooltip:hover {
  background: #2196f3;
  color: white;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

/* 按钮样式 */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1976d2;
}

.btn-secondary {
  background: white;
  color: #666;
  border: 1px solid #ddd;
}

.btn-secondary:hover:not(:disabled) {
  background: #f5f5f5;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 12px;
}

.btn-danger {
  background: #f44336;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #d32f2f;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .device-type-patterns-editor {
    padding: 15px;
  }

  .section-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .device-type-item,
  .prefix-item {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .item-actions {
    justify-content: flex-end;
  }

  .test-input {
    flex-direction: column;
  }

  .action-buttons {
    flex-direction: column;
  }
}
</style>
