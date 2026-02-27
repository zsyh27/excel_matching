<template>
  <div class="normalization-editor">
    <div class="editor-header">
      <h2>归一化映射</h2>
      <p class="description">
        将各种格式的字符统一转换为标准格式，例如：单位符号、特殊字符等。
      </p>
    </div>

    <div class="editor-body">
      <div class="toolbar">
        <input 
          v-model="newSource" 
          type="text" 
          placeholder="原字符..."
          class="input-field"
        />
        <span class="arrow">→</span>
        <input 
          v-model="newTarget" 
          type="text" 
          placeholder="目标字符（可为空表示删除）..."
          class="input-field"
        />
        <button @click="addMapping" class="btn btn-primary">添加</button>
      </div>

      <div class="mappings-table">
        <div class="table-header">
          <div class="col-source">原字符</div>
          <div class="col-arrow"></div>
          <div class="col-target">目标字符</div>
          <div class="col-action">操作</div>
        </div>
        <div 
          v-for="(target, source) in localValue" 
          :key="source"
          class="table-row"
        >
          <div class="col-source">{{ source }}</div>
          <div class="col-arrow">→</div>
          <div class="col-target">
            <span v-if="target === ''" class="empty-value">(删除)</span>
            <span v-else>{{ target }}</span>
          </div>
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
  name: 'NormalizationEditor',
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

    const addMapping = () => {
      const source = newSource.value.trim()
      const target = newTarget.value.trim()
      
      if (source) {
        localValue.value[source] = target
        newSource.value = ''
        newTarget.value = ''
        emitChange()
      }
    }

    const removeMapping = (source) => {
      delete localValue.value[source]
      emitChange()
    }

    const emitChange = () => {
      emit('update:modelValue', { ...localValue.value })
      emit('change')
    }

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
.normalization-editor {
  max-width: 900px;
}

.editor-header h2 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #333;
}

.description {
  margin: 0 0 20px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
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
  max-height: 500px;
  overflow-y: auto;
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
  position: sticky;
  top: 0;
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

.empty-value {
  color: #999;
  font-style: italic;
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
