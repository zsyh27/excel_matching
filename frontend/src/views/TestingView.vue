<template>
  <div class="testing-view">
    <div class="header">
      <h1>测试功能</h1>
      <p class="subtitle">测试智能提取和设备类型识别功能</p>
    </div>

    <div class="content">
      <!-- 设备类型识别测试 -->
      <div class="test-section">
        <DeviceTypeRecognitionTest />
      </div>
      
      <!-- 六步流程实时预览 -->
      <div class="test-section">
        <SixStepPreview />
      </div>
    </div>
  </div>
</template>

<script setup>
import DeviceTypeRecognitionTest from '../components/Testing/DeviceTypeRecognitionTest.vue'
import SixStepPreview from '../components/Testing/SixStepPreview.vue'
</script>

<style scoped>
.testing-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.header {
  padding: 20px 30px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.subtitle {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  overflow-y: auto;
}

.test-section {
  background: white;
  border-radius: 4px;
  padding: 30px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>
