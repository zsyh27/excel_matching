<template>
  <div class="advanced-config-editor">
    <div class="editor-header">
      <h2>高级配置</h2>
      <p class="description">
        高级预处理配置，包括元数据关键词（字段名）等。这些关键词会被识别为字段名而不是匹配特征。
      </p>
    </div>

    <div class="editor-body">
      <div class="section">
        <h3>元数据关键词</h3>
        <p class="section-desc">
          这些关键词通常是字段名称（如"型号"、"品牌"），在特征提取时会被忽略，只提取其对应的值。
        </p>
        
        <div class="keyword-input">
          <input 
            v-model="newKeyword" 
            type="text" 
            placeholder="输入关键词后按回车添加"
            @keyup.enter="addKeyword"
            class="input-field"
          />
          <button @click="addKeyword" class="btn-add">添加</button>
        </div>

        <div class="keyword-list">
          <span 
            v-for="(keyword, index) in localValue" 
            :key="index"
            class="keyword-tag"
          >
            {{ keyword }}
            <button @click="removeKeyword(index)" class="btn-remove">×</button>
          </span>
        </div>

        <div class="stats">
          共 {{ localValue.length }} 个元数据关键词
        </div>
      </div>

      <div class="info-box">
        <h4>💡 使用说明</h4>
        <ul>
          <li>元数据关键词用于识别字段名称，避免将其作为匹配特征</li>
          <li>例如："型号：QAA2061" 中，"型号"是字段名，"QAA2061"才是特征</li>
          <li>常见的元数据关键词包括：型号、品牌、规格、参数、名称等</li>
          <li>添加元数据关键词可以提高特征提取的准确性</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'AdvancedConfigEditor',
  props: {
    modelValue: {
      type: Array,
      default: () => [
        '型号', '通径', '阀体类型', '适用介质', '品牌',
        '规格', '参数', '名称', '类型', '尺寸', '材质',
        '功率', '电压', '电流', '频率', '温度', '压力',
        '流量', '湿度', '浓度', '范围', '精度', '输出',
        '输入', '信号', '接口', '安装', '防护', '等级'
      ]
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
      emit('update:modelValue', [...localValue.value])
      emit('change')
    }

    watch(() => props.modelValue, (newVal) => {
      localValue.value = [...newVal]
    }, { deep: true })

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
.advanced-config-editor {
  max-width: 900px;
}

.editor-header h2 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #333;
}

.description {
  margin: 0 0 30px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.section {
  background: white;
  padding: 25px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  margin-bottom: 20px;
}

.section h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #333;
}

.section-desc {
  margin: 0 0 20px 0;
  color: #666;
  font-size: 13px;
  line-height: 1.6;
}

.keyword-input {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.input-field {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.input-field:focus {
  outline: none;
  border-color: #2196f3;
}

.btn-add {
  padding: 10px 20px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.btn-add:hover {
  background: #1976d2;
}

.keyword-list {
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

.btn-remove {
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

.btn-remove:hover {
  background: rgba(25, 118, 210, 0.1);
}

.stats {
  color: #666;
  font-size: 13px;
}

.info-box {
  background: #fff3e0;
  padding: 20px;
  border-radius: 4px;
  border-left: 4px solid #ff9800;
}

.info-box h4 {
  margin: 0 0 12px 0;
  font-size: 15px;
  color: #e65100;
}

.info-box ul {
  margin: 0;
  padding-left: 20px;
}

.info-box li {
  margin-bottom: 8px;
  color: #666;
  font-size: 13px;
  line-height: 1.6;
}
</style>
