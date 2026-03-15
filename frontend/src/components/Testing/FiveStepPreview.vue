<template>
  <div class="five-step-preview">
    <div class="section-header">
      <div class="header-content">
        <div>
          <h2>🔄 五步流程实时预览</h2>
          <p class="description">输入设备描述，查看完整的五步处理流程</p>
        </div>
        <div class="header-controls">
          <el-switch
            v-model="recordLog"
            active-text="记录匹配日志"
            inactive-text="不记录日志"
            :active-value="true"
            :inactive-value="false"
          />
          <el-tooltip content="开启后，每次测试匹配都会记录到匹配日志中，可在统计页面查看" placement="top">
            <el-icon class="info-icon"><QuestionFilled /></el-icon>
          </el-tooltip>
        </div>
      </div>
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

    <!-- 日志记录提示 -->
    <el-alert
      v-if="lastLogId"
      type="success"
      :closable="true"
      @close="lastLogId = null"
      style="margin-bottom: 15px"
    >
      <template #title>
        匹配日志已记录
      </template>
      <div>
        日志ID: <el-link type="primary" @click="viewLog">{{ lastLogId }}</el-link>
        - 可在统计页面的"匹配日志"标签中查看详情
      </div>
    </el-alert>

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
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import DeviceTypeStep from './PreviewSteps/DeviceTypeStep.vue'
import ParameterStep from './PreviewSteps/ParameterStep.vue'
import AuxiliaryStep from './PreviewSteps/AuxiliaryStep.vue'
import MatchingStep from './PreviewSteps/MatchingStep.vue'
import UIPreviewStep from './PreviewSteps/UIPreviewStep.vue'
import PerformanceStep from './PreviewSteps/PerformanceStep.vue'

const router = useRouter()

const testText = ref('')
const previewResult = ref(null)
const testing = ref(false)
const recordLog = ref(false)  // 是否记录日志
const lastLogId = ref(null)   // 最后记录的日志ID

let testTimeout = null

const handleTestTextChange = () => {
  clearTimeout(testTimeout)
  lastLogId.value = null  // 清除之前的日志ID
  
  testTimeout = setTimeout(async () => {
    if (testText.value.trim()) {
      testing.value = true
      try {
        const response = await fetch('/api/intelligent-extraction/preview', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ 
            text: testText.value,
            record_log: recordLog.value  // 传递日志记录标志
          })
        })
        
        const result = await response.json()
        
        if (result.success && result.data) {
          const data = result.data
          previewResult.value = {
            step1_device_type: data.step1_device_type || {},
            step2_parameters: data.step2_parameters || {},
            parameter_candidates: data.parameter_candidates || [],
            step3_auxiliary: data.step3_auxiliary || {},
            step4_matching: data.step4_matching || { status: 'no_match', candidates: [] },
            step5_ui_preview: data.step5_ui_preview || {},
            debug_info: data.debug_info || {}
          }
          
          // 如果返回了日志ID，显示提示
          if (result.log_id) {
            lastLogId.value = result.log_id
            ElMessage.success({
              message: `匹配日志已记录: ${result.log_id}`,
              duration: 3000
            })
          }
        }
      } catch (error) {
        console.error('测试失败:', error)
        ElMessage.error('测试失败，请检查后端服务')
      } finally {
        testing.value = false
      }
    } else {
      previewResult.value = null
    }
  }, 500)
}

// 查看日志详情
const viewLog = () => {
  if (lastLogId.value) {
    router.push({
      name: 'Statistics',
      query: { tab: 'logs', logId: lastLogId.value }
    })
  }
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

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-icon {
  color: #909399;
  cursor: help;
  font-size: 16px;
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
