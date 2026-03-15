<template>
  <div class="five-step-preview">
    <div class="section-header">
      <h2>🔄 五步流程实时预览</h2>
      <p class="description">输入设备描述，查看完整的五步处理流程</p>
    </div>

    <div class="preview-input">
      <input 
        v-model="testText" 
        type="text" 
        placeholder="输入设备描述进行测试，例如：CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%"
        @input="handleTestTextChange"
        :disabled="testing"
      />
      <div v-if="testing" class="testing-indicator">
        <span class="loading-spinner"></span>
        分析中...
      </div>
    </div>

    <div v-if="previewResult" class="preview-result">
      <!-- 步骤1：设备类型识别 -->
      <DeviceTypeStep :data="previewResult.step1_device_type" />
      
      <!-- 步骤2：参数候选提取 -->
      <ParameterStep :data="previewResult.step2_parameters" :fullData="previewResult" />
      
      <!-- 步骤3：辅助信息提取 -->
      <AuxiliaryStep :data="previewResult.step3_auxiliary" />
      
      <!-- 步骤4：智能匹配评分 -->
      <MatchingStep :data="previewResult.step4_matching" />
      
      <!-- 步骤5：用户界面展示 -->
      <UIPreviewStep :data="previewResult.step5_ui_preview" :matching="previewResult.step4_matching" />
      
      <!-- 性能统计 -->
      <PerformanceStep :data="previewResult.debug_info?.performance" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import DeviceTypeStep from './PreviewSteps/DeviceTypeStep.vue'
import ParameterStep from './PreviewSteps/ParameterStep.vue'
import AuxiliaryStep from './PreviewSteps/AuxiliaryStep.vue'
import MatchingStep from './PreviewSteps/MatchingStep.vue'
import UIPreviewStep from './PreviewSteps/UIPreviewStep.vue'
import PerformanceStep from './PreviewSteps/PerformanceStep.vue'

const testText = ref('')
const previewResult = ref(null)
const testing = ref(false)

let testTimeout = null

const handleTestTextChange = () => {
  clearTimeout(testTimeout)
  testTimeout = setTimeout(async () => {
    if (testText.value.trim()) {
      testing.value = true
      try {
        const response = await fetch('/api/intelligent-extraction/preview', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ text: testText.value })
        })
        
        const result = await response.json()
        
        if (result.success && result.data) {
          const data = result.data
          previewResult.value = {
            step1_device_type: data.step1_device_type || {},
            step2_parameters: data.step2_parameters || {},
            parameter_candidates: data.parameter_candidates || [],  // Add parameter_candidates at root level
            step3_auxiliary: data.step3_auxiliary || {},
            step4_matching: data.step4_matching || { status: 'no_match', candidates: [] },
            step5_ui_preview: data.step5_ui_preview || {},
            debug_info: data.debug_info || {}
          }
        }
      } catch (error) {
        console.error('测试失败:', error)
      } finally {
        testing.value = false
      }
    } else {
      previewResult.value = null
    }
  }, 500)
}
</script>

<style scoped>
.five-step-preview {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.section-header {
  margin-bottom: 30px;
}

.section-header h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #303133;
}

.description {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.preview-input {
  position: relative;
  margin-bottom: 20px;
}

.preview-input input {
  width: 100%;
  padding: 12px 16px;
  font-size: 14px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.preview-input input:focus {
  outline: none;
  border-color: #409EFF;
}

.testing-indicator {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  color: #409EFF;
  font-size: 14px;
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #409EFF;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.preview-result {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>
