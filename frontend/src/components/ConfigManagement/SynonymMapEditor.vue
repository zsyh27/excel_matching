<template>
  <div class="synonym-map-editor">
    <div class="editor-header">
      <h2>同义词映射</h2>
      <p class="description">
        配置同义词映射，用于匹配阶段的同义词扩展。系统在匹配时会自动识别同义词，提高召回率。
      </p>
      <div class="info-box">
        <div class="info-title">💡 工作原理</div>
        <ul class="info-list">
          <li><strong>预处理阶段</strong>：保留原始词汇，不进行同义词替换</li>
          <li><strong>匹配阶段</strong>：使用同义词扩展进行模糊匹配，支持双向匹配</li>
          <li><strong>示例</strong>：Excel输入"阀"可以匹配规则中的"阀门"，反之亦然</li>
        </ul>
        <div class="info-note">
          <strong>优势</strong>：保留原始信息，灵活的匹配策略，提高召回率而不丢失信息
        </div>
      </div>
    </div>

    <div class="editor-body">
      <div class="toolbar">
        <input 
          v-model="newSource" 
          type="text" 
          placeholder="原词..."
          class="input-field"
        />
        <span class="arrow">→</span>
        <input 
          v-model="newTarget" 
          type="text" 
          placeholder="目标词..."
          class="input-field"
        />
        <button @click="addMapping" class="btn btn-primary">添加</button>
      </div>

      <div class="mappings-table">
        <div class="table-header">
          <div class="col-source">原词</div>
          <div class="col-arrow"></div>
          <div class="col-target">目标词</div>
          <div class="col-action">操作</div>
        </div>
        <div 
          v-for="(target, source) in localValue" 
          :key="source"
          class="table-row"
        >
          <div class="col-source">{{ source }}</div>
          <div class="col-arrow">→</div>
          <div class="col-target">{{ target }}</div>
          <div class="col-action">
            <button @click="removeMapping(source)" class="btn-remove">删除</button>
          </div>
        </div>
      </div>

      <div class="stats">
        <span>共 {{ Object.keys(localValue).length }} 个映射</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'SynonymMapEditor',
  props: {
    modelValue: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const localValue = ref({ ...props.modelValue })
    const newSource = ref('')
    const newTarget = ref('')

    // 添加映射
    const addMapping = () => {
      const source = newSource.value.trim()
      const target = newTarget.value.trim()
      
      if (source && target) {
        localValue.value[source] = target
        newSource.value = ''
        newTarget.value = ''
        emitChange()
      }
    }

    // 删除映射
    const removeMapping = (source) => {
      delete localValue.value[source]
      emitChange()
    }

    // 发送变更事件
    const emitChange = () => {
      emit('update:modelValue', { ...localValue.value })
      emit('change')
    }

    // 监听外部变化
    watch(() => props.modelValue, (newVal) => {
      localValue.value = { ...newVal }
    }, { deep: true })

    return {
      localValue,
      newSource,
      newTarget,
      addMapping,
      removeMapping
    }
  }
}
</script>

<style scoped>
.synonym-map-editor {
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

.info-box {
  margin-bottom: 20px;
  padding: 15px;
  background: #f0f9ff;
  border-left: 4px solid #2196f3;
  border-radius: 4px;
}

.info-title {
  font-size: 14px;
  font-weight: 600;
  color: #1976d2;
  margin-bottom: 10px;
}

.info-list {
  margin: 10px 0;
  padding-left: 20px;
  font-size: 13px;
  line-height: 1.8;
  color: #555;
}

.info-list li {
  margin: 5px 0;
}

.info-note {
  margin-top: 10px;
  padding: 8px 12px;
  background: #e3f2fd;
  border-radius: 4px;
  font-size: 13px;
  color: #1565c0;
}

.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
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

.mappings-table {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.table-header,
.table-row {
  display: grid;
  grid-template-columns: 2fr 50px 2fr 100px;
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

.col-action {
  text-align: right;
}

.btn-remove {
  padding: 4px 12px;
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  color: #666;
  font-size: 12px;
  cursor: pointer;
}

.btn-remove:hover {
  background: #f44336;
  border-color: #f44336;
  color: white;
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
