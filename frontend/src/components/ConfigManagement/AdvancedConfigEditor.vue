<template>
  <div class="advanced-config-editor">
    <div class="editor-header">
      <h2>高级配置</h2>
      <p class="description">
        高级预处理配置，包括元数据关键词（字段名）等。这些关键词会被识别为字段名而不是匹配特征。
      </p>
    </div>

    <div class="editor-body">
      <!-- 单位删除配置 -->
      <div class="section">
        <h3>单位删除（匹配阶段）</h3>
        <p class="section-desc">
          在匹配阶段自动删除特征末尾的单位符号，提高匹配灵活性。例如："0-2000ppm" → "0-2000"
        </p>
        
        <div class="form-group">
          <label class="switch-label">
            <input 
              type="checkbox" 
              v-model="unitRemoval.enabled"
              @change="emitUnitRemovalChange"
            />
            <span class="switch-text">启用单位删除</span>
          </label>
          <p class="help-text">
            启用后，系统会在匹配阶段自动删除配置的单位符号
          </p>
        </div>

        <div v-if="unitRemoval.enabled" style="margin-top: 20px;">
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
              v-for="(unit, index) in unitRemoval.units" 
              :key="'unit-' + index"
              class="keyword-tag unit-tag"
            >
              {{ unit }}
              <button @click="removeUnit(index)" class="btn-remove">×</button>
            </span>
          </div>

          <div class="stats">
            共 {{ unitRemoval.units.length }} 个单位
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

      <div class="section">
        <h3>特征白名单</h3>
        <p class="section-desc">
          白名单中的特征即使质量评分低于阈值也不会被过滤。适用于一些重要但简短的特征（如"水"、"气"、"阀"等）。
        </p>
        
        <div class="keyword-input">
          <input 
            v-model="newWhitelistFeature" 
            type="text" 
            placeholder="输入特征后按回车添加到白名单"
            @keyup.enter="addWhitelistFeature"
            class="input-field"
          />
          <button @click="addWhitelistFeature" class="btn-add">添加</button>
        </div>

        <div class="keyword-list">
          <span 
            v-for="(feature, index) in whitelistFeatures" 
            :key="'whitelist-' + index"
            class="keyword-tag whitelist-tag"
          >
            {{ feature }}
            <button @click="removeWhitelistFeature(index)" class="btn-remove">×</button>
          </span>
        </div>

        <div class="stats">
          共 {{ whitelistFeatures.length }} 个白名单特征
        </div>
      </div>

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
        
        <h5>特征白名单</h5>
        <ul>
          <li>白名单中的特征会跳过质量评分检查，即使评分低于阈值也不会被过滤</li>
          <li>适用于重要但简短的特征，例如：
            <ul>
              <li>介质类型：水、气、油、蒸汽等</li>
              <li>设备类型：阀、泵、表等</li>
              <li>其他重要的单字或短词特征</li>
            </ul>
          </li>
          <li>建议只添加确实需要保留的特征，避免过度使用白名单</li>
        </ul>
        
        <h5>元数据关键词</h5>
        <ul>
          <li>元数据关键词用于识别字段名称，避免将其作为匹配特征</li>
          <li>系统会自动处理两种格式：
            <ul>
              <li>简单格式："型号:QAA2061" → 提取 "QAA2061"</li>
              <li>带序号格式："2.型号:QAA2061" → 提取 "QAA2061"</li>
            </ul>
          </li>
          <li>只需添加关键词本身（如"型号"、"规格参数"），系统会自动匹配所有格式</li>
          <li>支持中文冒号（：）和英文冒号（:）</li>
          <li>常见的元数据关键词包括：型号、品牌、规格、参数、名称、规格参数、工作原理等</li>
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
    },
    fullConfig: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const localValue = ref([...(props.modelValue || [])])
    const newKeyword = ref('')
    
    // 从fullConfig中获取白名单
    const getWhitelistFromConfig = () => {
      return props.fullConfig?.intelligent_extraction?.feature_quality_scoring?.whitelist_features || ['水', '气', '阀']
    }
    
    const whitelistFeatures = ref([...getWhitelistFromConfig()])
    const newWhitelistFeature = ref('')
    
    // 单位删除配置
    const unitRemoval = ref({
      enabled: false,
      units: []
    })
    const newUnit = ref('')
    
    // 初始化单位删除配置
    const initUnitRemoval = () => {
      if (props.fullConfig && props.fullConfig.unit_removal) {
        unitRemoval.value = {
          enabled: props.fullConfig.unit_removal.enabled || false,
          units: [...(props.fullConfig.unit_removal.units || [])]
        }
      } else {
        unitRemoval.value = {
          enabled: false,
          units: []
        }
      }
    }
    
    initUnitRemoval()

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
    
    const addWhitelistFeature = () => {
      const feature = newWhitelistFeature.value.trim()
      if (feature && !whitelistFeatures.value.includes(feature)) {
        whitelistFeatures.value.push(feature)
        newWhitelistFeature.value = ''
        emitWhitelistChange()
      }
    }
    
    const removeWhitelistFeature = (index) => {
      whitelistFeatures.value.splice(index, 1)
      emitWhitelistChange()
    }
    
    const addUnit = () => {
      const unit = newUnit.value.trim()
      if (unit && !unitRemoval.value.units.includes(unit)) {
        unitRemoval.value.units.push(unit)
        newUnit.value = ''
        emitUnitRemovalChange()
      }
    }
    
    const removeUnit = (index) => {
      unitRemoval.value.units.splice(index, 1)
      emitUnitRemovalChange()
    }

    const emitChange = () => {
      emit('update:modelValue', [...localValue.value])
      emit('change')
    }
    
    const emitWhitelistChange = () => {
      // 直接修改fullConfig中的白名单（Vue允许修改对象属性）
      if (props.fullConfig) {
        if (!props.fullConfig.intelligent_extraction) {
          props.fullConfig.intelligent_extraction = {}
        }
        if (!props.fullConfig.intelligent_extraction.feature_quality_scoring) {
          props.fullConfig.intelligent_extraction.feature_quality_scoring = {}
        }
        props.fullConfig.intelligent_extraction.feature_quality_scoring.whitelist_features = [...whitelistFeatures.value]
      }
      
      // 触发change事件通知父组件
      emit('change')
    }
    
    const emitUnitRemovalChange = () => {
      // 直接修改fullConfig中的unit_removal
      if (props.fullConfig) {
        props.fullConfig.unit_removal = { ...unitRemoval.value }
      }
      
      // 触发change事件通知父组件
      emit('change')
    }

    watch(() => props.modelValue, (newVal) => {
      localValue.value = [...(newVal || [])]
    }, { deep: true })
    
    watch(() => props.fullConfig, (newVal) => {
      if (newVal) {
        whitelistFeatures.value = [...getWhitelistFromConfig()]
        initUnitRemoval()
      }
    }, { deep: true })

    return {
      localValue,
      newKeyword,
      addKeyword,
      removeKeyword,
      whitelistFeatures,
      newWhitelistFeature,
      addWhitelistFeature,
      removeWhitelistFeature,
      unitRemoval,
      newUnit,
      addUnit,
      removeUnit
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

.whitelist-tag {
  background: #e8f5e9;
  color: #2e7d32;
}

.whitelist-tag .btn-remove {
  color: #2e7d32;
}

.whitelist-tag .btn-remove:hover {
  background: rgba(46, 125, 50, 0.1);
}

.unit-tag {
  background: #fff3e0;
  color: #e65100;
}

.unit-tag .btn-remove {
  color: #e65100;
}

.unit-tag .btn-remove:hover {
  background: rgba(230, 81, 0, 0.1);
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

.info-box h5 {
  margin: 15px 0 8px 0;
  font-size: 14px;
  color: #f57c00;
  font-weight: 600;
}

.info-box h5:first-of-type {
  margin-top: 0;
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
