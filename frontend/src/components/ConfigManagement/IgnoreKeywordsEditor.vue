<template>
  <div class="ignore-keywords-editor">
    <div class="editor-header">
      <h2>删除无关关键词</h2>
      <p class="description">
        在预处理的第一步，删除这些与设备匹配无关的关键词，提高匹配准确性。
      </p>
      <div class="info-box">
        <div class="info-title">📋 使用场景</div>
        <ul class="info-list">
          <li><strong>施工要求</strong>：如"施工要求"、"验收"、"调试"等</li>
          <li><strong>商务信息</strong>：如"含税"、"不含税"、"质保"等</li>
          <li><strong>通用描述</strong>：如"品牌"、"厂家"、"国标"等</li>
        </ul>
        <div class="info-note">
          <strong>处理时机</strong>：在智能清理之后、归一化之前执行，确保这些关键词不会影响特征提取
        </div>
      </div>
    </div>

    <div class="editor-body">
      <div class="toolbar">
        <input 
          v-model="newKeyword" 
          type="text" 
          placeholder="输入新关键词..."
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
        <span>共 {{ localValue.length }} 个关键词</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'IgnoreKeywordsEditor',
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

    // 添加关键词
    const addKeyword = () => {
      const keyword = newKeyword.value.trim()
      if (keyword && !localValue.value.includes(keyword)) {
        localValue.value.push(keyword)
        newKeyword.value = ''
        emitChange()
      }
    }

    // 删除关键词
    const removeKeyword = (index) => {
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
.ignore-keywords-editor {
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
  background: #fff8e1;
  border-left: 4px solid #ffc107;
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
  background: #fff3e0;
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
  padding: 6px 12px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
}

.btn-remove {
  background: none;
  border: none;
  color: #999;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-remove:hover {
  color: #f44336;
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
