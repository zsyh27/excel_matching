<template>
  <div class="whitelist-editor">
    <div class="editor-header">
      <h2>特征白名单</h2>
      <p class="description">
        白名单中的特征即使质量评分低于阈值也不会被过滤。适用于一些重要但简短的特征（如"水"、"气"、"阀"等）。
      </p>
      
      <ConfigInfoCard
        stage="preprocessing"
        stage-icon="🔍"
        stage-name="预处理配置 - 特征质量"
        stage-description="此配置在特征质量评分后生效，白名单中的特征即使质量评分低也不会被过滤。"
      >
        <template #usage>
          <p>配置重要的短特征白名单，这些特征会跳过质量评分检查。</p>
          <ul>
            <li>白名单中的特征会跳过质量评分检查，即使评分低于阈值也不会被过滤</li>
            <li>适用于重要但简短的特征，例如：
              <ul>
                <li>介质类型：水、气、油、蒸汽等</li>
                <li>设备类型：阀、泵、表等</li>
                <li>技术缩写：co、co2、pm2.5、ntc等</li>
                <li>其他重要的单字或短词特征</li>
              </ul>
            </li>
            <li>建议只添加确实需要保留的特征，避免过度使用白名单</li>
          </ul>
        </template>
        <template #examples>
          <ul>
            <li>介质类型：水、气、油、蒸汽</li>
            <li>设备类型：阀、泵、表、箱</li>
            <li>技术缩写：co、co2、pm2.5、ntc</li>
          </ul>
        </template>
        <template #notes>
          <ul>
            <li>白名单特征会跳过质量评分</li>
            <li>适用于重要但简短的特征</li>
            <li>避免过度使用白名单</li>
          </ul>
        </template>
      </ConfigInfoCard>
    </div>

    <div class="editor-body">
      <div class="section">
        <div class="keyword-input">
          <input 
            v-model="newFeature" 
            type="text" 
            placeholder="输入特征后按回车添加到白名单"
            @keyup.enter="addFeature"
            class="input-field"
          />
          <button @click="addFeature" class="btn-add">添加</button>
        </div>

        <div class="keyword-list">
          <span 
            v-for="(feature, index) in localValue" 
            :key="'whitelist-' + index"
            class="keyword-tag whitelist-tag"
          >
            {{ feature }}
            <button @click="removeFeature(index)" class="btn-remove">×</button>
          </span>
        </div>

        <div class="stats">
          共 {{ localValue.length }} 个白名单特征
        </div>
      </div>

      <div class="info-box">
        <h4>💡 使用说明</h4>
        <ul>
          <li>白名单中的特征会跳过质量评分检查，即使评分低于阈值也不会被过滤</li>
          <li>适用于重要但简短的特征，例如：
            <ul>
              <li>介质类型：水、气、油、蒸汽等</li>
              <li>设备类型：阀、泵、表等</li>
              <li>技术缩写：co、co2、pm2.5、ntc等</li>
              <li>其他重要的单字或短词特征</li>
            </ul>
          </li>
          <li>建议只添加确实需要保留的特征，避免过度使用白名单</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'WhitelistEditor',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const localValue = ref([...(props.modelValue || [])])
    const newFeature = ref('')

    const addFeature = () => {
      const feature = newFeature.value.trim()
      if (feature && !localValue.value.includes(feature)) {
        localValue.value.push(feature)
        newFeature.value = ''
        emitChange()
      }
    }

    const removeFeature = (index) => {
      localValue.value.splice(index, 1)
      emitChange()
    }

    const emitChange = () => {
      emit('update:modelValue', [...localValue.value])
      emit('change')
    }

    watch(() => props.modelValue, (newVal) => {
      localValue.value = [...(newVal || [])]
    }, { deep: true })

    return {
      localValue,
      newFeature,
      addFeature,
      removeFeature
    }
  }
}
</script>

<style scoped>
.whitelist-editor {
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
  border-radius: 16px;
  font-size: 13px;
  height: fit-content;
}

.whitelist-tag {
  background: #e8f5e9;
  color: #2e7d32;
}

.btn-remove {
  background: none;
  border: none;
  color: #2e7d32;
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
  background: rgba(46, 125, 50, 0.1);
}

.stats {
  color: #666;
  font-size: 13px;
}

.info-box {
  background: #e3f2fd;
  padding: 20px;
  border-radius: 4px;
  border-left: 4px solid #2196f3;
}

.info-box h4 {
  margin: 0 0 12px 0;
  font-size: 15px;
  color: #1565c0;
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
