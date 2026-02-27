<template>
  <div class="split-chars-editor">
    <div class="editor-header">
      <h2>处理分隔符</h2>
      <p class="description">
        定义用于拆分特征的分隔符。这些字符将被用来分割设备描述文本。
      </p>
    </div>

    <div class="editor-body">
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
import { ref, watch } from 'vue'

export default {
  name: 'SplitCharsEditor',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const localValue = ref([...props.modelValue])
    const newChar = ref('')

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

    // 监听外部变化
    watch(() => props.modelValue, (newVal) => {
      localValue.value = [...newVal]
    })

    return {
      localValue,
      newChar,
      displayChar,
      getCharCode,
      addChar,
      removeChar
    }
  }
}
</script>

<style scoped>
.split-chars-editor {
  max-width: 800px;
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
