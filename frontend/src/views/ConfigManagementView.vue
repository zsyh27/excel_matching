<template>
  <div class="config-management">
    <!-- 消息提示 -->
    <transition name="message-fade">
      <div v-if="message.show" :class="['message-toast', message.type]">
        <span class="message-icon">
          {{ message.type === 'success' ? '✓' : message.type === 'error' ? '✗' : 'ℹ' }}
        </span>
        <span class="message-text">{{ message.text }}</span>
      </div>
    </transition>

    <!-- 加载遮罩 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载中...</div>
    </div>

    <div class="header">
      <h1>配置管理</h1>
      <div class="actions">
        <button @click="handleReset" class="btn btn-secondary" :disabled="!hasChanges">重置</button>
        <button @click="handleExport" class="btn btn-secondary">导出</button>
        <button @click="handleImport" class="btn btn-secondary">导入</button>
        <button @click="handleRegenerateRules" class="btn btn-warning" :disabled="regenerating">
          <span v-if="regenerating" class="btn-spinner"></span>
          {{ regenerating ? '生成中...' : '重新生成规则' }}
        </button>
        <button @click="handleSave" class="btn btn-primary" :disabled="!hasChanges || saving">
          <span v-if="saving" class="btn-spinner"></span>
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>

    <div class="content">
      <!-- 左侧导航 -->
      <div class="sidebar">
        <nav class="nav-menu">
          <div 
            v-for="item in menuItems" 
            :key="item.key"
            :class="['nav-item', { active: activeTab === item.key }]"
            @click="activeTab = item.key"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span class="nav-label">{{ item.label }}</span>
          </div>
        </nav>

        <div class="sidebar-footer">
          <button @click="showHistory = true" class="btn btn-link">
            📜 版本历史
          </button>
        </div>
      </div>

      <!-- 右侧编辑区域 -->
      <div class="main-content">
        <div class="editor-container">
          <!-- 根据activeTab显示不同的编辑器 -->
          <component 
            :is="currentEditor" 
            v-model="config[activeTab]"
            :full-config="config"
            @change="handleConfigChange"
            @update-ignore-keywords="handleUpdateIgnoreKeywords"
          />
        </div>

        <!-- 实时预览区域 -->
        <div class="preview-container">
          <h3>
            实时预览
            <span v-if="testing" class="testing-indicator">测试中...</span>
          </h3>
          <div class="preview-input">
            <input 
              v-model="testText" 
              type="text" 
              placeholder="输入测试文本..."
              @input="handleTestTextChange"
              :disabled="testing"
            />
          </div>
          <div v-if="previewResult" class="preview-result">
            <div class="preview-section">
              <h4>预处理结果</h4>
              <div class="preview-item">
                <span class="label">原始文本:</span>
                <span class="value">{{ previewResult.preprocessing.original }}</span>
              </div>
              <div class="preview-item">
                <span class="label">清理后:</span>
                <span class="value">{{ previewResult.preprocessing.cleaned }}</span>
              </div>
              <div class="preview-item">
                <span class="label">归一化:</span>
                <span class="value">{{ previewResult.preprocessing.normalized }}</span>
              </div>
              <div class="preview-item">
                <span class="label">提取特征:</span>
                <span class="value">
                  <span 
                    v-for="(feature, index) in previewResult.preprocessing.features" 
                    :key="index"
                    class="feature-tag"
                  >
                    {{ feature }}
                  </span>
                </span>
              </div>
            </div>
            <div v-if="previewResult.match_result" class="preview-section">
              <h4>匹配结果</h4>
              <div class="preview-item">
                <span class="label">状态:</span>
                <span :class="['value', previewResult.match_result.match_status]">
                  {{ previewResult.match_result.match_status === 'success' ? '成功' : '失败' }}
                </span>
              </div>
              <div v-if="previewResult.match_result.match_status === 'success'" class="preview-item">
                <span class="label">匹配设备:</span>
                <span class="value">{{ previewResult.match_result.device_text }}</span>
              </div>
              <div class="preview-item">
                <span class="label">得分:</span>
                <span class="value">{{ previewResult.match_result.score }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 版本历史弹窗 -->
    <div v-if="showHistory" class="modal" @click.self="showHistory = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>配置历史</h2>
          <button @click="showHistory = false" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <div v-if="history.length === 0" class="empty-state">
            暂无历史记录
          </div>
          <div v-else class="history-list">
            <div 
              v-for="item in history" 
              :key="item.version"
              class="history-item"
            >
              <div class="history-info">
                <span class="version">版本 {{ item.version }}</span>
                <span class="time">{{ formatTime(item.created_at) }}</span>
              </div>
              <div class="history-remark">{{ item.remark || '无备注' }}</div>
              <button @click="handleRollback(item.version)" class="btn btn-sm">回滚</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 导入文件输入 -->
    <input 
      ref="fileInput" 
      type="file" 
      accept=".json" 
      style="display: none" 
      @change="handleFileSelect"
    />
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import configApi from '../api/config'
import IgnoreKeywordsEditor from '../components/ConfigManagement/IgnoreKeywordsEditor.vue'
import SplitCharsEditor from '../components/ConfigManagement/SplitCharsEditor.vue'
import SynonymMapEditor from '../components/ConfigManagement/SynonymMapEditor.vue'
import NormalizationEditor from '../components/ConfigManagement/NormalizationEditor.vue'
import GlobalConfigEditor from '../components/ConfigManagement/GlobalConfigEditor.vue'
import BrandKeywordsEditor from '../components/ConfigManagement/BrandKeywordsEditor.vue'
import DeviceTypeEditor from '../components/ConfigManagement/DeviceTypeEditor.vue'
import FeatureWeightEditor from '../components/ConfigManagement/FeatureWeightEditor.vue'
import AdvancedConfigEditor from '../components/ConfigManagement/AdvancedConfigEditor.vue'
import DeviceRowRecognitionEditor from '../components/ConfigManagement/DeviceRowRecognitionEditor.vue'
import IntelligentCleaningEditor from '../components/ConfigManagement/IntelligentCleaningEditor.vue'

export default {
  name: 'ConfigManagementView',
  components: {
    IgnoreKeywordsEditor,
    SplitCharsEditor,
    SynonymMapEditor,
    NormalizationEditor,
    GlobalConfigEditor,
    BrandKeywordsEditor,
    DeviceTypeEditor,
    FeatureWeightEditor,
    AdvancedConfigEditor,
    DeviceRowRecognitionEditor,
    IntelligentCleaningEditor
  },
  setup() {
    const activeTab = ref('device_row_recognition')
    const config = ref({})
    const originalConfig = ref({})
    const hasChanges = ref(false)
    const testText = ref('')
    const previewResult = ref(null)
    const showHistory = ref(false)
    const history = ref([])
    const fileInput = ref(null)
    const loading = ref(false)
    const testing = ref(false)
    const regenerating = ref(false)
    const message = ref({ show: false, text: '', type: 'info' })

    // 显示消息提示
    const showMessage = (text, type = 'info') => {
      message.value = { show: true, text, type }
      setTimeout(() => {
        message.value.show = false
      }, 3000)
    }

    // 菜单项（按照业务流程排序）
    const menuItems = [
      // 1. 数据导入阶段
      { key: 'device_row_recognition', label: '设备行识别', icon: '🎯' },
      
      // 2. 特征提取配置阶段
      { key: 'intelligent_extraction', label: '智能清理', icon: '🧹' },
      { key: 'feature_split_chars', label: '处理分隔符', icon: '✂️' },
      { key: 'normalization_map', label: '归一化映射', icon: '📝' },
      { key: 'metadata_keywords', label: '高级配置', icon: '🔧' },
      
      // 3. 匹配配置阶段
      { key: 'synonym_map', label: '同义词映射', icon: '🔄' },
      { key: 'brand_keywords', label: '品牌关键词', icon: '🏷️' },
      { key: 'device_type_keywords', label: '设备类型', icon: '📦' },
      { key: 'feature_weight_config', label: '特征权重', icon: '⚖️' },
      
      // 4. 全局配置
      { key: 'global_config', label: '全局配置', icon: '⚙️' }
    ]

    // 当前编辑器组件
    const currentEditor = computed(() => {
      const editorMap = {
        'feature_split_chars': 'SplitCharsEditor',
        'synonym_map': 'SynonymMapEditor',
        'normalization_map': 'NormalizationEditor',
        'global_config': 'GlobalConfigEditor',
        'brand_keywords': 'BrandKeywordsEditor',
        'device_type_keywords': 'DeviceTypeEditor',
        'feature_weight_config': 'FeatureWeightEditor',
        'metadata_keywords': 'AdvancedConfigEditor',
        'device_row_recognition': 'DeviceRowRecognitionEditor',
        'intelligent_extraction': 'IntelligentCleaningEditor'
      }
      return editorMap[activeTab.value]
    })

    // 加载配置
    const loadConfig = async () => {
      loading.value = true
      try {
        const response = await configApi.getConfig()
        if (response.data.success) {
          config.value = response.data.config
          originalConfig.value = JSON.parse(JSON.stringify(response.data.config))
          hasChanges.value = false
        } else {
          showMessage('加载配置失败: ' + (response.data.error_message || '未知错误'), 'error')
        }
      } catch (error) {
        console.error('加载配置失败:', error)
        const errorMsg = error.response?.data?.error_message || error.message || '网络错误'
        showMessage('加载配置失败: ' + errorMsg, 'error')
      } finally {
        loading.value = false
      }
    }

    // 加载历史记录
    const loadHistory = async () => {
      try {
        const response = await configApi.getHistory()
        if (response.data.success) {
          history.value = response.data.history
        }
      } catch (error) {
        console.error('加载历史失败:', error)
      }
    }

    // 配置变更处理
    const handleConfigChange = () => {
      hasChanges.value = JSON.stringify(config.value) !== JSON.stringify(originalConfig.value)
    }
    
    // 处理 ignore_keywords 更新
    const handleUpdateIgnoreKeywords = (keywords) => {
      config.value.ignore_keywords = keywords
      handleConfigChange()
    }

    // 测试文本变更处理（防抖）
    let testTimeout = null
    const handleTestTextChange = () => {
      clearTimeout(testTimeout)
      testTimeout = setTimeout(async () => {
        if (testText.value.trim()) {
          testing.value = true
          try {
            const response = await configApi.testConfig(testText.value, config.value)
            if (response.data.success) {
              previewResult.value = response.data
            } else {
              showMessage('测试失败: ' + (response.data.error_message || '未知错误'), 'error')
            }
          } catch (error) {
            console.error('测试失败:', error)
            const errorMsg = error.response?.data?.error_message || error.message || '网络错误'
            showMessage('测试失败: ' + errorMsg, 'error')
          } finally {
            testing.value = false
          }
        } else {
          previewResult.value = null
        }
      }, 500)
    }

    // 保存配置
    const saving = ref(false)
    const handleSave = async () => {
      const remark = prompt('请输入备注信息（可选）:')
      if (remark === null) return // 用户取消

      saving.value = true
      try {
        const response = await configApi.saveConfig(config.value, remark)
        if (response.data.success) {
          showMessage('配置保存成功', 'success')
          originalConfig.value = JSON.parse(JSON.stringify(config.value))
          hasChanges.value = false
          loadHistory()
        } else {
          showMessage('配置保存失败: ' + (response.data.error_message || '未知错误'), 'error')
        }
      } catch (error) {
        console.error('保存配置失败:', error)
        const errorMsg = error.response?.data?.error_message || error.message || '网络错误，请检查连接'
        showMessage('保存配置失败: ' + errorMsg, 'error')
      } finally {
        saving.value = false
      }
    }

    // 重置配置
    const handleReset = () => {
      if (confirm('确定要重置配置吗？所有未保存的修改将丢失。')) {
        config.value = JSON.parse(JSON.stringify(originalConfig.value))
        hasChanges.value = false
      }
    }

    // 导出配置
    const handleExport = async () => {
      try {
        const response = await configApi.exportConfig()
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `config_export_${Date.now()}.json`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        showMessage('配置导出成功', 'success')
      } catch (error) {
        console.error('导出配置失败:', error)
        const errorMsg = error.response?.data?.error_message || error.message || '网络错误'
        showMessage('导出配置失败: ' + errorMsg, 'error')
      }
    }

    // 导入配置
    const handleImport = () => {
      fileInput.value.click()
    }

    const handleFileSelect = async (event) => {
      const file = event.target.files[0]
      if (!file) return

      const remark = prompt('请输入备注信息（可选）:', '导入配置')
      if (remark === null) return

      try {
        const response = await configApi.importConfig(file, remark)
        if (response.data.success) {
          showMessage('配置导入成功', 'success')
          loadConfig()
          loadHistory()
        } else {
          showMessage('配置导入失败: ' + (response.data.error_message || '未知错误'), 'error')
        }
      } catch (error) {
        console.error('导入配置失败:', error)
        const errorMsg = error.response?.data?.error_message || error.message || '网络错误'
        showMessage('导入配置失败: ' + errorMsg, 'error')
      }

      // 清空文件输入
      event.target.value = ''
    }

    // 回滚配置
    const handleRollback = async (version) => {
      if (!confirm(`确定要回滚到版本 ${version} 吗？`)) return

      try {
        const response = await configApi.rollback(version)
        if (response.data.success) {
          showMessage('配置回滚成功', 'success')
          showHistory.value = false
          loadConfig()
          loadHistory()
        } else {
          showMessage('配置回滚失败: ' + (response.data.error_message || '未知错误'), 'error')
        }
      } catch (error) {
        console.error('回滚配置失败:', error)
        const errorMsg = error.response?.data?.error_message || error.message || '网络错误'
        showMessage('回滚配置失败: ' + errorMsg, 'error')
      }
    }

    // 重新生成规则
    const handleRegenerateRules = async () => {
      if (!confirm('确定要重新生成所有设备的匹配规则吗？\n\n这将使用当前配置重新生成规则，可能需要几分钟时间。')) {
        return
      }

      regenerating.value = true
      try {
        const response = await configApi.regenerateRules(config.value)
        if (response.data.success) {
          const { total, generated, failed } = response.data.data
          showMessage(
            `规则生成完成！\n总计: ${total} 个设备\n成功: ${generated} 个\n失败: ${failed} 个`,
            'success'
          )
        } else {
          showMessage('规则生成失败: ' + (response.data.error_message || '未知错误'), 'error')
        }
      } catch (error) {
        console.error('重新生成规则失败:', error)
        const errorMsg = error.response?.data?.error_message || error.message || '网络错误'
        showMessage('重新生成规则失败: ' + errorMsg, 'error')
      } finally {
        regenerating.value = false
      }
    }

    // 格式化时间
    const formatTime = (timeStr) => {
      if (!timeStr) return ''
      const date = new Date(timeStr)
      return date.toLocaleString('zh-CN')
    }

    // 监听配置变化
    watch(config, handleConfigChange, { deep: true })

    // 键盘快捷键
    const handleKeyDown = (event) => {
      // Ctrl+S 或 Cmd+S 保存
      if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault()
        if (hasChanges.value && !saving.value) {
          handleSave()
        }
      }
      // Ctrl+Z 或 Cmd+Z 重置
      if ((event.ctrlKey || event.metaKey) && event.key === 'z' && !event.shiftKey) {
        if (hasChanges.value) {
          event.preventDefault()
          handleReset()
        }
      }
    }

    // 组件挂载时加载配置
    onMounted(() => {
      loadConfig()
      loadHistory()
      window.addEventListener('keydown', handleKeyDown)
    })

    // 组件卸载时移除事件监听
    onUnmounted(() => {
      window.removeEventListener('keydown', handleKeyDown)
    })

    return {
      activeTab,
      config,
      hasChanges,
      testText,
      previewResult,
      showHistory,
      history,
      fileInput,
      menuItems,
      currentEditor,
      loading,
      saving,
      testing,
      regenerating,
      message,
      handleConfigChange,
      handleUpdateIgnoreKeywords,
      handleTestTextChange,
      handleSave,
      handleReset,
      handleExport,
      handleImport,
      handleFileSelect,
      handleRollback,
      handleRegenerateRules,
      formatTime
    }
  }
}
</script>

<style scoped>
.config-management {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.header {
  background: white;
  padding: 20px 30px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.actions {
  display: flex;
  gap: 10px;
}

.content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  width: 250px;
  background: white;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.nav-menu {
  flex: 1;
  padding: 20px 0;
}

.nav-item {
  padding: 12px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.2s;
}

.nav-item:hover {
  background: #f5f5f5;
}

.nav-item.active {
  background: #e3f2fd;
  border-left: 3px solid #2196f3;
  color: #2196f3;
}

.nav-icon {
  font-size: 18px;
}

.nav-label {
  font-size: 14px;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: white;
}

.preview-container {
  height: 300px;
  border-top: 1px solid #e0e0e0;
  padding: 20px;
  background: #fafafa;
  overflow-y: auto;
}

.preview-container h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #333;
}

.preview-input input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.preview-result {
  margin-top: 15px;
}

.preview-section {
  margin-bottom: 15px;
}

.preview-section h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}

.preview-item {
  display: flex;
  margin-bottom: 8px;
  font-size: 13px;
}

.preview-item .label {
  width: 100px;
  color: #666;
  flex-shrink: 0;
}

.preview-item .value {
  flex: 1;
  color: #333;
}

.preview-item .value.success {
  color: #4caf50;
  font-weight: bold;
}

.preview-item .value.failed {
  color: #f44336;
  font-weight: bold;
}

.feature-tag {
  display: inline-block;
  padding: 2px 8px;
  margin-right: 5px;
  background: #e3f2fd;
  border-radius: 3px;
  font-size: 12px;
  color: #2196f3;
}

/* 按钮样式 */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
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

.btn-secondary {
  background: white;
  color: #666;
  border: 1px solid #ddd;
}

.btn-secondary:hover {
  background: #f5f5f5;
}

.btn-warning {
  background: #ff9800;
  color: white;
  border: 1px solid #f57c00;
}

.btn-warning:hover:not(:disabled) {
  background: #f57c00;
}

.btn-warning:disabled {
  background: #ffcc80;
  border-color: #ffcc80;
  cursor: not-allowed;
}

.btn-link {
  background: none;
  color: #2196f3;
  border: none;
  padding: 8px;
  width: 100%;
  text-align: left;
}

.btn-link:hover {
  background: #f5f5f5;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 12px;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 30px;
  height: 30px;
  line-height: 1;
}

.btn-close:hover {
  color: #333;
}

/* 弹窗样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.history-info .version {
  font-weight: bold;
  color: #333;
}

.history-info .time {
  font-size: 12px;
  color: #999;
}

.history-remark {
  flex: 1;
  margin: 0 15px;
  color: #666;
  font-size: 13px;
}

/* 消息提示 */
.message-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 2000;
  min-width: 300px;
}

.message-toast.success {
  background: #4caf50;
  color: white;
}

.message-toast.error {
  background: #f44336;
  color: white;
}

.message-toast.info {
  background: #2196f3;
  color: white;
}

.message-icon {
  font-size: 18px;
  font-weight: bold;
}

.message-text {
  flex: 1;
}

.message-fade-enter-active,
.message-fade-leave-active {
  transition: all 0.3s ease;
}

.message-fade-enter-from {
  opacity: 0;
  transform: translateX(100px);
}

.message-fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* 加载遮罩 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1500;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e0e0e0;
  border-top-color: #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 15px;
  color: #666;
  font-size: 14px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 按钮加载动画 */
.btn-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 5px;
  vertical-align: middle;
}

/* 测试指示器 */
.testing-indicator {
  margin-left: 10px;
  font-size: 12px;
  color: #2196f3;
  font-weight: normal;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .content {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #e0e0e0;
  }

  .nav-menu {
    display: flex;
    overflow-x: auto;
    padding: 10px;
  }

  .nav-item {
    flex-shrink: 0;
    padding: 8px 15px;
  }

  .preview-container {
    height: auto;
    min-height: 200px;
  }

  .message-toast {
    right: 10px;
    left: 10px;
    min-width: auto;
  }
}
</style>
