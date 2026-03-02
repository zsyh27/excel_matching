<template>
  <div class="brand-keywords-editor">
    <div class="editor-header">
      <h2>品牌关键词</h2>
      <p class="description">
        定义品牌关键词，用于智能识别和拆分设备描述中的品牌信息，提高特征质量评分。
      </p>
      <div class="info-box">
        <div class="info-title">🏷️ 作用说明</div>
        <ul class="info-list">
          <li><strong>特征识别</strong>：自动识别文本中的品牌词，作为独立特征提取</li>
          <li><strong>质量评分</strong>：包含品牌关键词的特征获得更高的质量评分（+15分）</li>
          <li><strong>智能拆分</strong>：从复合描述中拆分出品牌信息（如"霍尼韦尔温度传感器"）</li>
        </ul>
        <div class="info-note">
          <strong>匹配权重</strong>：品牌特征在匹配时具有较高权重，有助于提高匹配准确性
        </div>
      </div>
    </div>

    <div class="editor-body">
      <div class="toolbar">
        <input 
          v-model="newKeyword" 
          type="text" 
          placeholder="输入新品牌..."
          @keyup.enter="addKeyword"
          class="keyword-input"
        />
        <button @click="addKeyword" class="btn btn-primary">添加</button>
      </div>

      <div class="keywords-container">
        <div 
          v-for="(keyword, index) in localValue" 
          :key="index"
          class="keyword-tag"
        >
          <span>{{ keyword }}</span>
          <button @click="removeKeyword(index)" class="btn-remove">×</button>
        </div>
      </div>

      <div class="stats">
        <span>共 {{ localValue.length }} 个品牌</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'BrandKeywordsEditor',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const localValue = ref([...props.modelValue])
    const newKeyword = ref('')

    const addKeyword = () => {
      const keyword = newKeyword.value.trim()
      if (keyword && !localValue.value.includes(keyword)) {
        localValue.value.push(keyword)
        newKeyword.value = ''
        emitChange()
      }
    }

    const removeKeyword = (index) => {
      localValue.value.splice(index, 1)
      emitChange()
    }

    const emitChange = () => {
      emit('update:modelValue', localValue.value)
      emit('change')
    }

    watch(() => props.modelValue, (newVal) => {
      localValue.value = [...newVal]
    })

    return {
      localValue,
      newKeyword,
      addKeyword,
      removeKeyword
    }
  }
}
</script>

<style scoped>
.brand-keywords-editor {
  max-width: 800px;
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
  background: #e3f2fd;
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
  background: #bbdefb;
  border-radius: 4px;
  font-size: 13px;
  color: #0d47a1;
}

.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.keyword-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.keywords-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  min-height: 100px;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background: #fafafa;
}

.keyword-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: #e3f2fd;
  border: 1px solid #2196f3;
  border-radius: 20px;
  font-size: 14px;
  color: #1976d2;
  font-weight: 500;
}

.btn-remove {
  background: none;
  border: none;
  color: #1976d2;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
}

.btn-remove:hover {
  opacity: 1;
}

.stats {
  margin-top: 10px;
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
