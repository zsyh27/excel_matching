<template>
  <div class="device-type-editor">
    <div class="editor-header">
      <h2>设备类型关键词</h2>
      <p class="description">
        定义设备类型关键词，用于智能识别和拆分设备描述中的设备类型信息，这是匹配的核心特征。
      </p>
      <div class="info-box">
        <div class="info-title">⚙️ 核心作用</div>
        <ul class="info-list">
          <li><strong>特征识别</strong>：自动识别文本中的设备类型，作为独立特征提取</li>
          <li><strong>质量评分</strong>：包含设备类型的特征获得更高的质量评分（+15分）</li>
          <li><strong>单字保护</strong>：设备类型关键词中的单字（如"阀"）不会因长度过短被过滤</li>
          <li><strong>匹配权重</strong>：设备类型特征具有最高权重（权重系数×4），是匹配的关键</li>
        </ul>
        <div class="info-note">
          <strong>重要性</strong>：设备类型是匹配算法的核心依据，建议包含所有常见设备类型及其简称
        </div>
      </div>
    </div>

    <div class="editor-body">
      <div class="toolbar">
        <input 
          v-model="newKeyword" 
          type="text" 
          placeholder="输入新设备类型..."
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
        <span>共 {{ localValue.length }} 个设备类型</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'DeviceTypeEditor',
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
.device-type-editor {
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
  background: #fff3e0;
  border-left: 4px solid #ff9800;
  border-radius: 4px;
}

.info-title {
  font-size: 14px;
  font-weight: 600;
  color: #f57c00;
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
  background: #ffe0b2;
  border-radius: 4px;
  font-size: 13px;
  color: #e65100;
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
  background: #fff3e0;
  border: 1px solid #ff9800;
  border-radius: 20px;
  font-size: 14px;
  color: #f57c00;
  font-weight: 500;
}

.btn-remove {
  background: none;
  border: none;
  color: #f57c00;
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
