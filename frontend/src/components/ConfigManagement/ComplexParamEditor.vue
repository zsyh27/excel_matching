<template>
  <div class="complex-param-editor">
    <div class="editor-header">
      <h2>复杂参数分解</h2>
      <p class="description">
        配置复杂参数的分解规则，将组合参数拆分为独立特征。例如："温度+湿度传感器" → ["温度传感器", "湿度传感器"]
      </p>
      
      <ConfigInfoCard
        stage="preprocessing"
        stage-icon="🔍"
        stage-name="预处理配置 - 特征提取"
        stage-description="此配置在特征提取时生效，用于智能分解复杂的技术参数（如'DN50 PN16'分解为'DN50'和'PN16'）。"
      >
        <template #usage>
          <p>配置复杂参数的分解规则，系统会自动识别并拆分复合参数。</p>
          <ul>
            <li><strong>执行时机</strong>：特征提取阶段</li>
            <li><strong>主要功能</strong>：识别并拆分复合参数（如"温度+湿度"、"4-20mA"）</li>
            <li><strong>典型场景</strong>："温度+湿度传感器" → ["温度传感器", "湿度传感器"]</li>
            <li><strong>与元数据处理的区别</strong>：元数据处理是删除标签，复杂参数分解是拆分复合参数</li>
          </ul>
        </template>
        <template #examples>
          <ul>
            <li>DN50 PN16 → DN50, PN16</li>
            <li>4-20mA DC24V → 4-20mA, DC24V</li>
            <li>0-10V 0-100% → 0-10V, 0-100%</li>
          </ul>
        </template>
        <template #notes>
          <ul>
            <li>参数分解有助于提高匹配准确性</li>
            <li>支持自定义分解规则</li>
            <li>分解后的参数会作为独立特征</li>
          </ul>
        </template>
      </ConfigInfoCard>
    </div>

    <!-- 启用开关 -->
    <div class="config-section">
      <div class="section-header">
        <h3>启用复杂参数分解</h3>
      </div>

      <div class="form-group">
        <label class="switch-label">
          <input 
            type="checkbox" 
            v-model="localValue.enabled"
            @change="emitChange"
          />
          <span class="switch-text">启用复杂参数分解功能</span>
        </label>
        <p class="help-text">
          启用后，系统会在特征提取阶段自动拆分复合参数
        </p>
      </div>
    </div>

    <!-- 分解模式列表 -->
    <div v-if="localValue.enabled" class="config-section">
      <div class="section-header">
        <h3>分解模式</h3>
        <p class="section-description">
          配置需要分解的复合参数模式
        </p>
      </div>

      <div class="patterns-list">
        <div class="pattern-item">
          <div class="pattern-icon">🔢</div>
          <div class="pattern-content">
            <div class="pattern-title">数值范围 + 单位</div>
            <div class="pattern-desc">如："4-20mA" → ["4-20", "mA"]</div>
            <div class="pattern-examples">
              <span class="example-tag">4-20mA</span>
              <span class="example-tag">0-10V</span>
              <span class="example-tag">2-10V</span>
            </div>
          </div>
          <div class="pattern-status">
            <span class="status-badge active">内置规则</span>
          </div>
        </div>

        <div class="pattern-item">
          <div class="pattern-icon">➕</div>
          <div class="pattern-content">
            <div class="pattern-title">加号连接的复合参数</div>
            <div class="pattern-desc">如："温度+湿度传感器" → ["温度传感器", "湿度传感器"]</div>
            <div class="pattern-examples">
              <span class="example-tag">温度+湿度</span>
              <span class="example-tag">温度+CO2</span>
            </div>
          </div>
          <div class="pattern-status">
            <span class="status-badge active">内置规则</span>
          </div>
        </div>

        <div class="pattern-item">
          <div class="pattern-icon">🔤</div>
          <div class="pattern-content">
            <div class="pattern-title">字母 + 数字组合</div>
            <div class="pattern-desc">如："DN15" → ["DN", "15"]</div>
            <div class="pattern-examples">
              <span class="example-tag">DN15</span>
              <span class="example-tag">DN20</span>
              <span class="example-tag">DN25</span>
            </div>
          </div>
          <div class="pattern-status">
            <span class="status-badge active">内置规则</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 示例说明 -->
    <div class="example-section">
      <h3>💡 分解效果示例</h3>
      
      <div class="example-group">
        <h4>数值范围 + 单位</h4>
        <div class="example-item">
          <div class="example-label">输入：</div>
          <div class="example-value">"4-20mA"</div>
        </div>
        <div class="example-item">
          <div class="example-label">分解后：</div>
          <div class="example-value">["4-20", "mA"]</div>
        </div>
      </div>

      <div class="example-group">
        <h4>复合传感器</h4>
        <div class="example-item">
          <div class="example-label">输入：</div>
          <div class="example-value">"温度+湿度传感器"</div>
        </div>
        <div class="example-item">
          <div class="example-label">分解后：</div>
          <div class="example-value">["温度传感器", "湿度传感器"]</div>
        </div>
      </div>

      <div class="example-group">
        <h4>通径规格</h4>
        <div class="example-item">
          <div class="example-label">输入：</div>
          <div class="example-value">"DN15"</div>
        </div>
        <div class="example-item">
          <div class="example-label">分解后：</div>
          <div class="example-value">["DN", "15"]</div>
        </div>
      </div>

      <div class="example-note">
        分解后的特征会作为独立特征参与匹配，提高匹配灵活性
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import ConfigInfoCard from './ConfigInfoCard.vue'

export default {
  name: 'ComplexParamEditor',
  components: {
    ConfigInfoCard
  },
  props: {
    modelValue: {
      type: Object,
      default: () => ({
        enabled: false,
        complex_parameter_decomposition: {}
      })
    }
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    const localValue = ref({
      enabled: props.modelValue?.enabled || false,
      complex_parameter_decomposition: props.modelValue?.complex_parameter_decomposition || {}
    })

    // 发送变更事件
    const emitChange = () => {
      emit('update:modelValue', { ...localValue.value })
      emit('change')
    }

    // 监听外部变化
    watch(() => props.modelValue, (newVal) => {
      if (newVal) {
        localValue.value = {
          enabled: newVal.enabled || false,
          complex_parameter_decomposition: newVal.complex_parameter_decomposition || {}
        }
      }
    }, { deep: true })

    return {
      localValue,
      emitChange
    }
  }
}
</script>

<style scoped>
.complex-param-editor {
  max-width: 900px;
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

.config-explanation {
  margin-bottom: 25px;
}

.explanation-content {
  font-size: 13px;
  line-height: 1.8;
}

.explanation-content p {
  margin: 8px 0;
}

.explanation-content ul {
  margin: 5px 0;
  padding-left: 20px;
}

.explanation-content li {
  margin: 4px 0;
}

.explanation-content .tip {
  margin-top: 12px;
  padding: 8px 12px;
  background-color: #f0f9ff;
  border-left: 3px solid #409eff;
  border-radius: 4px;
}

.config-section {
  margin-bottom: 25px;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.section-header {
  margin-bottom: 15px;
}

.section-header h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #333;
}

.section-description {
  margin: 0;
  color: #666;
  font-size: 13px;
}

.form-group {
  margin-bottom: 15px;
}

.switch-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: normal;
}

.switch-label input[type="checkbox"] {
  margin-right: 10px;
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.switch-text {
  font-size: 14px;
  color: #333;
}

.help-text {
  margin: 8px 0 0 28px;
  font-size: 12px;
  color: #999;
  line-height: 1.5;
}

.patterns-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.pattern-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 20px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  transition: all 0.2s;
}

.pattern-item:hover {
  border-color: #2196f3;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.1);
}

.pattern-icon {
  font-size: 32px;
  line-height: 1;
}

.pattern-content {
  flex: 1;
}

.pattern-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.pattern-desc {
  font-size: 13px;
  color: #666;
  margin-bottom: 12px;
}

.pattern-examples {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.example-tag {
  padding: 4px 10px;
  background: #e3f2fd;
  color: #2196f3;
  border-radius: 12px;
  font-size: 12px;
  font-family: 'Courier New', monospace;
}

.pattern-status {
  display: flex;
  align-items: center;
}

.status-badge {
  padding: 4px 12px;
  background: #e8f5e9;
  color: #4caf50;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #e8f5e9;
  color: #4caf50;
}

.example-section {
  margin-top: 25px;
  padding: 20px;
  background: #fff3cd;
  border-left: 4px solid #ffc107;
  border-radius: 4px;
}

.example-section h3 {
  margin: 0 0 15px 0;
  font-size: 15px;
  color: #856404;
}

.example-group {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ffe69c;
}

.example-group:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.example-group h4 {
  margin: 0 0 10px 0;
  font-size: 13px;
  color: #856404;
  font-weight: 600;
}

.example-item {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 13px;
}

.example-label {
  font-weight: 500;
  color: #856404;
  min-width: 80px;
}

.example-value {
  font-family: 'Courier New', monospace;
  color: #333;
  background: white;
  padding: 4px 8px;
  border-radius: 3px;
}

.example-note {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ffe69c;
  font-size: 12px;
  color: #856404;
  line-height: 1.6;
}
</style>
