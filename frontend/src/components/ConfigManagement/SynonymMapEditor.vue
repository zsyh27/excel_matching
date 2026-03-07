<template>
  <div class="synonym-map-editor">
    <div class="editor-header">
      <h2>同义词映射与单位归一化</h2>
      <p class="description">
        配置同义词映射、技术术语扩展和单位归一化规则，用于匹配阶段的词汇扩展和格式统一。系统在匹配时会自动识别同义词、技术术语和单位变体，提高召回率。
      </p>
      <ConfigInfoCard config-id="synonym-map" />
    </div>

    <div class="editor-body">
      <!-- Filter toolbar -->
      <div class="filter-toolbar">
        <div class="filter-buttons">
          <button 
            :class="['filter-btn', { active: filterType === 'all' }]"
            @click="filterType = 'all'"
          >
            全部 ({{ mappings.length }})
          </button>
          <button 
            :class="['filter-btn', { active: filterType === 'synonym' }]"
            @click="filterType = 'synonym'"
          >
            同义词 ({{ synonymCount }})
          </button>
          <button 
            :class="['filter-btn', { active: filterType === 'technical' }]"
            @click="filterType = 'technical'"
          >
            技术术语 ({{ technicalCount }})
          </button>
          <button 
            :class="['filter-btn', { active: filterType === 'unit' }]"
            @click="filterType = 'unit'"
          >
            单位归一化 ({{ unitCount }})
          </button>
        </div>
      </div>

      <!-- Add new mapping toolbar -->
      <div class="toolbar">
        <select v-model="newType" class="type-select">
          <option value="synonym">同义词</option>
          <option value="technical">技术术语</option>
          <option value="unit">单位归一化</option>
        </select>
        <input 
          v-model="newSource" 
          type="text" 
          :placeholder="getSourcePlaceholder()"
          class="input-field"
        />
        <span class="arrow">→</span>
        <input 
          v-model="newTarget" 
          type="text" 
          :placeholder="getTargetPlaceholder()"
          class="input-field"
        />
        <button @click="addMapping" class="btn btn-primary">添加</button>
      </div>

      <!-- Mappings table -->
      <div class="mappings-table">
        <div class="table-header">
          <div class="col-type">类型</div>
          <div class="col-source">原词/缩写</div>
          <div class="col-arrow"></div>
          <div class="col-target">目标词/完整术语</div>
          <div class="col-enabled">启用</div>
          <div class="col-action">操作</div>
        </div>
        <div 
          v-for="mapping in filteredMappings" 
          :key="mapping.id"
          class="table-row"
        >
          <div class="col-type">
            <span :class="['type-badge', mapping.type]">
              {{ getTypeName(mapping.type) }}
            </span>
          </div>
          <div class="col-source">{{ mapping.source }}</div>
          <div class="col-arrow">→</div>
          <div class="col-target">{{ mapping.target }}</div>
          <div class="col-enabled">
            <input 
              type="checkbox" 
              :checked="mapping.enabled"
              @change="toggleEnabled(mapping.id)"
            />
          </div>
          <div class="col-action">
            <button @click="editMapping(mapping)" class="btn-edit">编辑</button>
            <button @click="removeMapping(mapping.id)" class="btn-remove">删除</button>
          </div>
        </div>
        <div v-if="filteredMappings.length === 0" class="empty-state">
          <p>暂无{{ getFilterTypeName() }}映射</p>
        </div>
      </div>

      <div class="stats">
        <span>显示 {{ filteredMappings.length }} / {{ mappings.length }} 个映射</span>
      </div>

      <!-- Action buttons -->
      <div class="action-buttons">
        <button @click="saveConfig" :disabled="saving" class="btn btn-primary">
          {{ saving ? '保存中...' : '保存配置' }}
        </button>
        <button @click="loadConfig" class="btn btn-secondary">重置</button>
      </div>
    </div>

    <!-- Edit dialog -->
    <div v-if="editingMapping" class="modal" @click.self="cancelEdit">
      <div class="modal-content">
        <div class="modal-header">
          <h3>编辑映射</h3>
          <button @click="cancelEdit" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>类型</label>
            <select v-model="editForm.type" class="form-control">
              <option value="synonym">同义词</option>
              <option value="technical">技术术语</option>
              <option value="unit">单位归一化</option>
            </select>
          </div>
          <div class="form-group">
            <label>{{ getSourceLabel(editForm.type) }}</label>
            <input v-model="editForm.source" type="text" class="form-control" />
          </div>
          <div class="form-group">
            <label>{{ getTargetLabel(editForm.type) }}</label>
            <input v-model="editForm.target" type="text" class="form-control" />
          </div>
          <div class="form-group">
            <label>
              <input type="checkbox" v-model="editForm.enabled" />
              启用
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="cancelEdit" class="btn btn-secondary">取消</button>
          <button @click="saveEdit" class="btn btn-primary">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import ConfigInfoCard from './ConfigInfoCard.vue'

export default {
  name: 'SynonymMapEditor',
  components: {
    ConfigInfoCard
  },
  props: {
    modelValue: {
      type: [Object, Array],
      default: () => ([])
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    // Convert legacy object format to array format
    const convertToArray = (value) => {
      if (Array.isArray(value)) {
        return value.map((item, index) => ({
          id: item.id || `mapping_${index}`,
          source: item.source || '',
          target: item.target || '',
          type: item.type || 'synonym',
          enabled: item.enabled !== undefined ? item.enabled : true
        }))
      } else if (typeof value === 'object' && value !== null) {
        // Legacy format: { source: target }
        return Object.entries(value).map(([source, target], index) => ({
          id: `mapping_${index}`,
          source,
          target,
          type: 'synonym',
          enabled: true
        }))
      }
      return []
    }

    const mappings = ref(convertToArray(props.modelValue))
    const filterType = ref('all')
    const newSource = ref('')
    const newTarget = ref('')
    const newType = ref('synonym')
    const editingMapping = ref(null)
    const editForm = ref({
      id: '',
      source: '',
      target: '',
      type: 'synonym',
      enabled: true
    })
    const saving = ref(false)

    // Load config from API
    const loadConfig = async () => {
      try {
        const response = await fetch('/api/config')
        const data = await response.json()
        
        if (data.success && data.config) {
          const synonymMap = data.config.synonym_map || {}
          mappings.value = convertToArray(synonymMap)
        }
      } catch (error) {
        ElMessage.error('加载配置失败: ' + error.message)
      }
    }

    // Save config to API
    const saveConfig = async () => {
      saving.value = true
      try {
        // 获取当前完整配置
        const response = await fetch('/api/config')
        const data = await response.json()
        
        if (!data.success) {
          throw new Error('获取当前配置失败')
        }
        
        // 更新同义词映射配置
        const fullConfig = data.config
        fullConfig.synonym_map = mappings.value
        
        // 保存配置
        const saveResponse = await fetch('/api/config/save', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            config: fullConfig,
            remark: '更新同义词映射配置'
          })
        })
        
        const saveData = await saveResponse.json()
        
        if (saveData.success) {
          ElMessage.success('配置保存成功')
        } else {
          throw new Error(saveData.error_message || '保存失败')
        }
      } catch (error) {
        ElMessage.error('保存配置失败: ' + error.message)
      } finally {
        saving.value = false
      }
    }

    // Computed properties
    const filteredMappings = computed(() => {
      if (filterType.value === 'all') {
        return mappings.value
      }
      return mappings.value.filter(m => m.type === filterType.value)
    })

    const synonymCount = computed(() => {
      return mappings.value.filter(m => m.type === 'synonym').length
    })

    const technicalCount = computed(() => {
      return mappings.value.filter(m => m.type === 'technical').length
    })

    const unitCount = computed(() => {
      return mappings.value.filter(m => m.type === 'unit').length
    })

    // Helper methods
    const getTypeName = (type) => {
      const typeNames = {
        'synonym': '同义词',
        'technical': '技术术语',
        'unit': '单位归一化'
      }
      return typeNames[type] || type
    }

    const getFilterTypeName = () => {
      if (filterType.value === 'all') return ''
      return getTypeName(filterType.value)
    }

    const getSourcePlaceholder = () => {
      const placeholders = {
        'synonym': '原词...',
        'technical': '缩写...',
        'unit': '原单位（如：℃、°C）...'
      }
      return placeholders[newType.value] || '原词...'
    }

    const getTargetPlaceholder = () => {
      const placeholders = {
        'synonym': '目标词...',
        'technical': '完整术语...',
        'unit': '标准单位（可为空表示删除）...'
      }
      return placeholders[newType.value] || '目标词...'
    }

    const getSourceLabel = (type) => {
      const labels = {
        'synonym': '原词',
        'technical': '缩写',
        'unit': '原单位'
      }
      return labels[type] || '原词'
    }

    const getTargetLabel = (type) => {
      const labels = {
        'synonym': '目标词',
        'technical': '完整术语',
        'unit': '标准单位'
      }
      return labels[type] || '目标词'
    }

    // Methods
    const addMapping = () => {
      const source = newSource.value.trim()
      const target = newTarget.value.trim()
      
      if (source && target) {
        const newMapping = {
          id: `mapping_${Date.now()}`,
          source,
          target,
          type: newType.value,
          enabled: true
        }
        mappings.value.push(newMapping)
        newSource.value = ''
        newTarget.value = ''
        emitChange()
      }
    }

    const removeMapping = (id) => {
      const index = mappings.value.findIndex(m => m.id === id)
      if (index !== -1) {
        mappings.value.splice(index, 1)
        emitChange()
      }
    }

    const toggleEnabled = (id) => {
      const mapping = mappings.value.find(m => m.id === id)
      if (mapping) {
        mapping.enabled = !mapping.enabled
        emitChange()
      }
    }

    const editMapping = (mapping) => {
      editingMapping.value = mapping
      editForm.value = { ...mapping }
    }

    const saveEdit = () => {
      const index = mappings.value.findIndex(m => m.id === editForm.value.id)
      if (index !== -1) {
        mappings.value[index] = { ...editForm.value }
        emitChange()
      }
      cancelEdit()
    }

    const cancelEdit = () => {
      editingMapping.value = null
      editForm.value = {
        id: '',
        source: '',
        target: '',
        type: 'synonym',
        enabled: true
      }
    }

    const emitChange = () => {
      emit('update:modelValue', [...mappings.value])
      emit('change')
    }

    // Watch for external changes
    watch(() => props.modelValue, (newVal) => {
      mappings.value = convertToArray(newVal)
    }, { deep: true })

    // Load config on mount
    onMounted(() => {
      loadConfig()
    })

    return {
      mappings,
      filterType,
      newSource,
      newTarget,
      newType,
      editingMapping,
      editForm,
      saving,
      filteredMappings,
      synonymCount,
      technicalCount,
      unitCount,
      getTypeName,
      getFilterTypeName,
      getSourcePlaceholder,
      getTargetPlaceholder,
      getSourceLabel,
      getTargetLabel,
      addMapping,
      removeMapping,
      toggleEnabled,
      editMapping,
      saveEdit,
      cancelEdit,
      saveConfig,
      loadConfig
    }
  }
}
</script>


<style scoped>
.synonym-map-editor {
  max-width: 1000px;
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

/* Filter toolbar */
.filter-toolbar {
  margin-bottom: 15px;
}

.filter-buttons {
  display: flex;
  gap: 10px;
}

.filter-btn {
  padding: 8px 16px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  background: #f5f5f5;
}

.filter-btn.active {
  background: #2196f3;
  border-color: #2196f3;
  color: white;
}

/* Toolbar */
.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}

.type-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.input-field {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.arrow {
  font-size: 18px;
  color: #999;
}

/* Mappings table */
.mappings-table {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.table-header,
.table-row {
  display: grid;
  grid-template-columns: 100px 2fr 50px 2fr 80px 140px;
  gap: 10px;
  padding: 12px 15px;
  align-items: center;
}

.table-header {
  background: #f5f5f5;
  font-weight: bold;
  font-size: 13px;
  color: #666;
}

.table-row {
  background: white;
  border-top: 1px solid #e0e0e0;
}

.table-row:hover {
  background: #fafafa;
}

.col-arrow {
  text-align: center;
  color: #999;
}

.col-enabled {
  text-align: center;
}

.col-action {
  display: flex;
  gap: 5px;
  justify-content: flex-end;
}

/* Type badge */
.type-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
}

.type-badge.synonym {
  background: #e3f2fd;
  color: #1976d2;
}

.type-badge.technical {
  background: #fff3e0;
  color: #f57c00;
}

.type-badge.unit {
  background: #e8f5e9;
  color: #388e3c;
}

/* Buttons */
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
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: white;
  border: 1px solid #ddd;
  color: #666;
}

.btn-secondary:hover {
  background: #f5f5f5;
}

.btn-edit,
.btn-remove {
  padding: 4px 12px;
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  color: #666;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit:hover {
  background: #2196f3;
  border-color: #2196f3;
  color: white;
}

.btn-remove:hover {
  background: #f44336;
  border-color: #f44336;
  color: white;
}

/* Empty state */
.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #999;
  font-size: 14px;
}

/* Stats */
.stats {
  margin-top: 15px;
  font-size: 13px;
  color: #666;
}

/* Action buttons */
.action-buttons {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* Modal */
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
  width: 500px;
  max-width: 90%;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  line-height: 1;
}

.btn-close:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 13px;
  font-weight: 600;
  color: #555;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
