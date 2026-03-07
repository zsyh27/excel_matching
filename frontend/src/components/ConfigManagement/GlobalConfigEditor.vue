<template>
  <div class="global-config-editor">
    <div class="editor-header">
      <h2>全局配置</h2>
      <p class="description">
        全局处理选项，控制文本预处理和特征提取的基本行为。
      </p>
      <ConfigInfoCard config-id="global-settings" />
    </div>

    <div class="editor-body">
      <div class="config-item">
        <label class="config-label">
          <span class="label-text">默认匹配阈值</span>
          <span class="label-desc">规则匹配的最低得分要求</span>
        </label>
        <div class="config-control">
          <input 
            v-model.number="localValue.default_match_threshold" 
            type="number" 
            step="0.1"
            min="0"
            class="number-input"
            @input="emitChange"
          />
          <input 
            v-model.number="localValue.default_match_threshold" 
            type="range" 
            min="0" 
            max="10" 
            step="0.1"
            class="range-input"
            @input="emitChange"
          />
        </div>
      </div>

      <div class="config-item">
        <label class="config-label">
          <span class="label-text">统一转小写</span>
          <span class="label-desc">将所有文本转换为小写</span>
        </label>
        <div class="config-control">
          <label class="switch">
            <input 
              v-model="localValue.unify_lowercase" 
              type="checkbox"
              @change="emitChange"
            />
            <span class="slider"></span>
          </label>
        </div>
      </div>

      <div class="config-item">
        <label class="config-label">
          <span class="label-text">删除空格</span>
          <span class="label-desc">删除文本中的所有空格</span>
        </label>
        <div class="config-control">
          <label class="switch">
            <input 
              v-model="localValue.remove_whitespace" 
              type="checkbox"
              @change="emitChange"
            />
            <span class="slider"></span>
          </label>
        </div>
      </div>

      <div class="config-item">
        <label class="config-label">
          <span class="label-text">全角转半角</span>
          <span class="label-desc">将全角字符转换为半角字符</span>
        </label>
        <div class="config-control">
          <label class="switch">
            <input 
              v-model="localValue.fullwidth_to_halfwidth" 
              type="checkbox"
              @change="emitChange"
            />
            <span class="slider"></span>
          </label>
        </div>
      </div>

      <div class="config-item">
        <label class="config-label">
          <span class="label-text">最小特征长度</span>
          <span class="label-desc">提取特征的最小字符数（英文/数字）</span>
        </label>
        <div class="config-control">
          <input 
            v-model.number="localValue.min_feature_length" 
            type="number" 
            min="1"
            max="10"
            class="number-input"
            @input="emitChange"
          />
        </div>
      </div>

      <div class="config-item">
        <label class="config-label">
          <span class="label-text">最小特征长度（中文）</span>
          <span class="label-desc">提取中文特征的最小字符数</span>
        </label>
        <div class="config-control">
          <input 
            v-model.number="localValue.min_feature_length_chinese" 
            type="number" 
            min="1"
            max="10"
            class="number-input"
            @input="emitChange"
          />
        </div>
      </div>

      <!-- 智能拆分选项 -->
      <div class="section-divider">
        <h3>智能拆分选项</h3>
        <p class="section-desc">在匹配阶段自动拆分复合词和技术规格，提高匹配灵活性</p>
      </div>

      <div class="config-item">
        <label class="config-label">
          <span class="label-text">启用智能拆分</span>
          <span class="label-desc">在匹配阶段自动拆分复合词（如"室内墙装"→"室内"+"墙装"）</span>
        </label>
        <div class="config-control">
          <label class="switch">
            <input 
              v-model="localValue.intelligent_splitting_enabled" 
              type="checkbox"
              @change="emitChange"
            />
            <span class="slider"></span>
          </label>
        </div>
      </div>

      <div v-if="localValue.intelligent_splitting_enabled" class="sub-options">
        <div class="config-item">
          <label class="config-label">
            <span class="label-text">拆分复合词</span>
            <span class="label-desc">自动拆分复合词（如"室内墙装"→"室内"+"墙装"）</span>
          </label>
          <div class="config-control">
            <label class="switch">
              <input 
                v-model="localValue.split_compound_words" 
                type="checkbox"
                @change="emitChange"
              />
              <span class="slider"></span>
            </label>
          </div>
        </div>

        <div class="config-item">
          <label class="config-label">
            <span class="label-text">拆分技术规格</span>
            <span class="label-desc">自动拆分技术规格（如"DN15"→"dn"+"15"）</span>
          </label>
          <div class="config-control">
            <label class="switch">
              <input 
                v-model="localValue.split_technical_specs" 
                type="checkbox"
                @change="emitChange"
              />
              <span class="slider"></span>
            </label>
          </div>
        </div>

        <div class="config-item">
          <label class="config-label">
            <span class="label-text">按空格拆分</span>
            <span class="label-desc">按空格拆分特征（如"ntc 10k"→"ntc"+"10k"）</span>
          </label>
          <div class="config-control">
            <label class="switch">
              <input 
                v-model="localValue.split_by_space" 
                type="checkbox"
                @change="emitChange"
              />
              <span class="slider"></span>
            </label>
          </div>
        </div>
      </div>

      <!-- 元数据标签 -->
      <div class="section-divider">
        <h3>元数据标签</h3>
        <p class="section-desc">配置元数据标签模式，在文本清理阶段删除这些标签，只保留值</p>
      </div>

      <div class="config-item metadata-tags">
        <label class="config-label">
          <span class="label-text">元数据标签列表</span>
          <span class="label-desc">系统会自动识别并删除这些标签（如"型号："、"品牌："）</span>
        </label>
        <div class="tags-control">
          <div class="tags-input-wrapper">
            <input 
              v-model="newMetadataTag" 
              type="text" 
              placeholder="输入标签（如：型号、品牌）"
              class="tag-input"
              @keyup.enter="addMetadataTag"
            />
            <button @click="addMetadataTag" class="btn-add-tag" :disabled="!newMetadataTag.trim()">
              添加
            </button>
          </div>
          <div class="tags-list">
            <span 
              v-for="(tag, index) in localValue.metadata_tags" 
              :key="index"
              class="tag-item"
            >
              {{ tag }}
              <button @click="removeMetadataTag(index)" class="btn-remove-tag">×</button>
            </span>
          </div>
          <div class="quick-tags">
            <span class="quick-tags-label">常用标签：</span>
            <button 
              v-for="tag in commonMetadataTags" 
              :key="tag"
              @click="addMetadataTag(tag)"
              class="btn-quick-tag"
              :disabled="hasMetadataTag(tag)"
            >
              {{ tag }}
            </button>
          </div>
        </div>
      </div>

      <!-- 匹配阈值 -->
      <div class="section-divider">
        <h3>匹配阈值</h3>
        <p class="section-desc">设置规则匹配的最低得分要求</p>
      </div>

      <div class="config-item">
        <label class="config-label">
          <span class="label-text">默认匹配阈值</span>
          <span class="label-desc">规则匹配的最低得分要求（推荐值：5.0）</span>
        </label>
        <div class="config-control">
          <input 
            v-model.number="localValue.match_threshold" 
            type="number" 
            step="0.1"
            min="0"
            class="number-input"
            @input="emitChange"
          />
          <input 
            v-model.number="localValue.match_threshold" 
            type="range" 
            min="0" 
            max="10" 
            step="0.1"
            class="range-input"
            @input="emitChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import ConfigInfoCard from './ConfigInfoCard.vue'

export default {
  name: 'GlobalConfigEditor',
  components: {
    ConfigInfoCard
  },
  props: {
    modelValue: {
      type: Object,
      default: () => ({
        default_match_threshold: 3.0,
        unify_lowercase: true,
        remove_whitespace: true,
        fullwidth_to_halfwidth: true
      })
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const localValue = ref({ ...props.modelValue })
    const newMetadataTag = ref('')

    // 常用元数据标签
    const commonMetadataTags = [
      '型号', '品牌', '规格', '参数', '名称', '类型',
      '通径', '阀体类型', '适用介质', '尺寸', '材质',
      '功率', '电压', '电流', '频率', '温度', '压力',
      '流量', '湿度', '浓度', '范围', '精度', '输出'
    ]

    // 确保新字段有默认值
    if (localValue.value.min_feature_length === undefined) {
      localValue.value.min_feature_length = 2
    }
    if (localValue.value.min_feature_length_chinese === undefined) {
      localValue.value.min_feature_length_chinese = 1
    }
    if (localValue.value.intelligent_splitting_enabled === undefined) {
      localValue.value.intelligent_splitting_enabled = false
    }
    if (localValue.value.split_compound_words === undefined) {
      localValue.value.split_compound_words = true
    }
    if (localValue.value.split_technical_specs === undefined) {
      localValue.value.split_technical_specs = true
    }
    if (localValue.value.split_by_space === undefined) {
      localValue.value.split_by_space = true
    }
    if (localValue.value.metadata_tags === undefined) {
      localValue.value.metadata_tags = ['型号', '品牌', '规格', '参数', '名称', '类型']
    }
    if (localValue.value.match_threshold === undefined) {
      localValue.value.match_threshold = 5.0
    }

    // 添加元数据标签
    const addMetadataTag = (tag) => {
      const tagValue = typeof tag === 'string' ? tag : newMetadataTag.value.trim()
      if (tagValue && !localValue.value.metadata_tags.includes(tagValue)) {
        localValue.value.metadata_tags.push(tagValue)
        newMetadataTag.value = ''
        emitChange()
      }
    }

    // 删除元数据标签
    const removeMetadataTag = (index) => {
      localValue.value.metadata_tags.splice(index, 1)
      emitChange()
    }

    // 检查标签是否已存在
    const hasMetadataTag = (tag) => {
      return localValue.value.metadata_tags.includes(tag)
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
      newMetadataTag,
      commonMetadataTags,
      addMetadataTag,
      removeMetadataTag,
      hasMetadataTag,
      emitChange
    }
  }
}
</script>

<style scoped>
.global-config-editor {
  max-width: 700px;
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

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  margin-bottom: 15px;
}

.config-label {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.label-text {
  font-size: 15px;
  font-weight: 500;
  color: #333;
}

.label-desc {
  font-size: 13px;
  color: #999;
}

.config-control {
  display: flex;
  align-items: center;
  gap: 15px;
}

.number-input {
  width: 80px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
}

.range-input {
  width: 200px;
}

/* 开关样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 26px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 26px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #2196f3;
}

input:checked + .slider:before {
  transform: translateX(24px);
}

/* Section divider */
.section-divider {
  margin: 30px 0 20px 0;
  padding-bottom: 10px;
  border-bottom: 2px solid #e0e0e0;
}

.section-divider h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.section-desc {
  margin: 0;
  font-size: 13px;
  color: #666;
}

/* Sub options */
.sub-options {
  margin-left: 30px;
  padding-left: 20px;
  border-left: 3px solid #e3f2fd;
}

/* Metadata tags */
.metadata-tags .tags-control {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.tags-input-wrapper {
  display: flex;
  gap: 10px;
}

.tag-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.btn-add-tag {
  padding: 8px 16px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-add-tag:hover:not(:disabled) {
  background: #1976d2;
}

.btn-add-tag:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-height: 40px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
  color: #333;
}

.btn-remove-tag {
  background: none;
  border: none;
  color: #999;
  font-size: 16px;
  cursor: pointer;
  padding: 0;
  width: 16px;
  height: 16px;
  line-height: 1;
  transition: color 0.2s;
}

.btn-remove-tag:hover {
  color: #f44336;
}

.quick-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.quick-tags-label {
  font-size: 12px;
  color: #666;
  margin-right: 5px;
}

.btn-quick-tag {
  padding: 4px 10px;
  background: white;
  color: #2196f3;
  border: 1px solid #2196f3;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.btn-quick-tag:hover:not(:disabled) {
  background: #2196f3;
  color: white;
}

.btn-quick-tag:disabled {
  background: #f5f5f5;
  color: #ccc;
  border-color: #e0e0e0;
  cursor: not-allowed;
}
</style>
