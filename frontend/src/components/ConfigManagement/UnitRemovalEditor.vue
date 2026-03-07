<template>
  <div class="unit-removal-editor">
    <div class="editor-header">
      <h2>单位删除</h2>
      <p class="description">
        在匹配阶段自动删除特征末尾的单位符号，提高匹配灵活性。例如："0-2000ppm" → "0-2000"
      </p>
      <ConfigInfoCard config-id="unit-remove" />
    </div>

    <div class="editor-body">
      <div class="section">
        <div class="form-group">
          <label class="switch-label">
            <input 
              type="checkbox" 
              v-model="localValue.enabled"
              @change="emitChange"
            />
            <span class="switch-text">启用单位删除</span>
          </label>
          <p class="help-text">
            启用后，系统会在匹配阶段自动删除配置的单位符号
          </p>
        </div>

        <div v-if="localValue.enabled" style="margin-top: 20px;">
          <h4 style="margin: 0 0 10px 0; font-size: 14px; color: #333;">单位列表</h4>
          
          <div class="keyword-input">
            <input 
              v-model="newUnit" 
              type="text" 
              placeholder="输入单位后按回车添加（如：ppm、ma、v）"
              @keyup.enter="addUnit"
              class="input-field"
            />
            <button @click="addUnit" class="btn-add">添加</button>
          </div>

          <div class="keyword-list">
            <span 
              v-for="(unit, index) in localValue.units" 
              :key="'unit-' + index"
              class="keyword-tag unit-tag"
            >
              {{ unit }}
              <button @click="removeUnit(index)" class="btn-remove">×</button>
            </span>
          </div>

          <div class="stats">
            共 {{ localValue.units.length }} 个单位
          </div>
        </div>

        <div class="info-note" style="margin-top: 15px;">
          <strong>💡 示例效果</strong>：
          <ul>
            <li><strong>"0-2000ppm"</strong> → "0-2000"</li>
            <li><strong>"4-20ma"</strong> → "4-20"</li>
            <li><strong>"2-10v"</strong> → "2-10"</li>
            <li><strong>"50%rh"</strong> → "50"</li>
          </ul>
          <p style="margin-top: 8px; color: #666;">
            <strong>注意</strong>：单位删除仅在匹配阶段生效，设备录入阶段保持数据完整性。
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import ConfigInfoCard from './ConfigInfoCard.vue'

export default {
  name: 'UnitRemovalEditor',
  components: {
    ConfigInfoCard
  },
  props: {
    modelValue: {
      type: Object,
      default: () => ({
        enabled: false,
        units: []
      })
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const localValue = ref({
      enabled: props.modelValue?.enabled || false,
      units: [...(props.modelValue?.units || [])]
    })
    const newUnit = ref('')

    const addUnit = () => {
      const unit = newUnit.value.trim().toLowerCase()
      if (unit && !localValue.value.units.includes(unit)) {
        localValue.value.units.push(unit)
        newUnit.value = ''
        emitChange()
      }
    }

    const removeUnit = (index) => {
      localValue.value.units.splice(index, 1)
      emitChange()
    }

    const emitChange = () => {
      emit('update:modelValue', { ...localValue.value })
      emit('change')
    }

    watch(() => props.modelValue, (newVal) => {
      if (newVal) {
        localValue.value = {
          enabled: newVal.enabled || false,
          units: [...(newVal.units || [])]
        }
      }
    }, { deep: true })

    return {
      localValue,
      newUnit,
      addUnit,
      removeUnit
    }
  }
}
</script>

<style scoped>
.unit-removal-editor {
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
}

.form-group {
  margin-bottom: 20px;
}

.switch-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.switch-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.switch-text {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.help-text {
  margin: 8px 0 0 28px;
  color: #666;
  font-size: 13px;
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

.unit-tag {
  background: #fff3e0;
  color: #e65100;
}

.btn-remove {
  background: none;
  border: none;
  color: #e65100;
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
  background: rgba(230, 81, 0, 0.1);
}

.stats {
  color: #666;
  font-size: 13px;
}

.info-note {
  padding: 12px;
  background: #fff3cd;
  border-left: 4px solid #ffc107;
  border-radius: 4px;
  font-size: 13px;
  color: #856404;
}

.info-note strong {
  color: #856404;
}

.info-note ul {
  margin: 8px 0 0 0;
  padding-left: 20px;
}

.info-note li {
  margin: 4px 0;
}

.info-note p {
  margin: 0;
}
</style>
