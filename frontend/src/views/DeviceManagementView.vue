<template>
  <div class="device-management-view">
    <el-card class="header-card">
      <h2>设备库管理</h2>
      <p>管理设备库中的设备信息，支持添加、编辑、删除和批量导入</p>
    </el-card>

    <el-card>
      <DeviceList
        ref="deviceListRef"
        @view="handleViewDevice"
        @edit="handleEditDevice"
        @copy="handleCopyDevice"
        @add="handleAddDevice"
        @batch-import="handleBatchImport"
        @consistency-check="handleConsistencyCheck"
      />
    </el-card>

    <!-- 设备表单对话框 -->
    <DeviceForm
      v-model="formDialogVisible"
      :device-data="currentDevice"
      @success="handleFormSuccess"
    />

    <!-- 设备详情对话框 -->
    <DeviceDetail
      v-model="detailDialogVisible"
      :device-id="currentDeviceId"
      @edit="handleEditFromDetail"
      @delete="handleDeleteSuccess"
      @view-rule="handleViewRule"
    />

    <!-- 批量导入对话框 -->
    <BatchImport
      v-model="importDialogVisible"
      @success="handleImportSuccess"
    />

    <!-- 数据一致性检查对话框 -->
    <ConsistencyCheck
      v-model="checkDialogVisible"
      @fixed="handleFixSuccess"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import DeviceList from '../components/DeviceManagement/DeviceList.vue'
import DeviceForm from '../components/DeviceManagement/DeviceForm.vue'
import DeviceDetail from '../components/DeviceManagement/DeviceDetail.vue'
import BatchImport from '../components/DeviceManagement/BatchImport.vue'
import ConsistencyCheck from '../components/DeviceManagement/ConsistencyCheck.vue'

const router = useRouter()

// 组件引用
const deviceListRef = ref(null)

// 对话框状态
const formDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const importDialogVisible = ref(false)
const checkDialogVisible = ref(false)

// 当前操作的设备
const currentDevice = ref(null)
const currentDeviceId = ref('')

// 查看设备详情
const handleViewDevice = (device) => {
  currentDeviceId.value = device.device_id
  detailDialogVisible.value = true
}

// 编辑设备
const handleEditDevice = (device) => {
  currentDevice.value = device
  formDialogVisible.value = true
}

// 复制设备
const handleCopyDevice = (device) => {
  // 创建设备副本，清空device_id，修改设备名称
  const deviceCopy = {
    ...device,
    device_id: '', // 清空ID，让系统自动生成
    device_name: `${device.device_name} (副本)`,
    spec_model: device.spec_model ? `${device.spec_model}-COPY` : '',
    // 保留其他所有字段
    brand: device.brand,
    device_type: device.device_type,
    key_params: device.key_params ? JSON.parse(JSON.stringify(device.key_params)) : null,
    detailed_params: device.detailed_params,
    unit_price: device.unit_price,
    input_method: 'manual'
  }
  
  currentDevice.value = deviceCopy
  formDialogVisible.value = true
}

// 从详情对话框编辑
const handleEditFromDetail = (device) => {
  currentDevice.value = device
  formDialogVisible.value = true
}

// 添加设备
const handleAddDevice = () => {
  currentDevice.value = null
  formDialogVisible.value = true
}

// 表单提交成功
const handleFormSuccess = () => {
  if (deviceListRef.value) {
    deviceListRef.value.refresh()
  }
}

// 删除成功
const handleDeleteSuccess = () => {
  if (deviceListRef.value) {
    deviceListRef.value.refresh()
  }
}

// 批量导入
const handleBatchImport = () => {
  importDialogVisible.value = true
}

// 导入成功
const handleImportSuccess = () => {
  if (deviceListRef.value) {
    deviceListRef.value.refresh()
  }
}

// 数据一致性检查
const handleConsistencyCheck = () => {
  checkDialogVisible.value = true
}

// 修复成功
const handleFixSuccess = () => {
  if (deviceListRef.value) {
    deviceListRef.value.refresh()
  }
}

// 查看规则详情
const handleViewRule = (rule) => {
  // 在新标签页打开规则编辑页面
  const routeData = router.resolve({
    name: 'RuleEditor',
    params: { ruleId: rule.rule_id }
  })
  window.open(routeData.href, '_blank')
}
</script>

<style scoped>
.device-management-view {
  /* 移除最大宽度限制，与配置管理页面一致 */
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header-card {
  margin-bottom: 20px;
  flex-shrink: 0; /* 防止卡片被压缩 */
}

.header-card h2 {
  margin: 0 0 10px 0;
  color: #303133;
  white-space: normal;
  word-wrap: break-word;
}

.header-card p {
  margin: 0;
  color: #909399;
  font-size: 14px;
  white-space: normal;
  word-wrap: break-word;
  overflow-wrap: break-word;
  line-height: 1.5;
  min-height: 20px; /* 确保有最小高度 */
}
</style>
