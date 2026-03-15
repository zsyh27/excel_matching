<template>
  <el-dialog
    v-model="visible"
    title="设备详情"
    width="900px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-if="deviceData" v-loading="loading" class="device-detail">
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 基本信息标签页 -->
        <el-tab-pane label="基本信息" name="basic">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="设备ID">{{ deviceData.device_id }}</el-descriptions-item>
            <el-descriptions-item label="品牌">{{ deviceData.brand }}</el-descriptions-item>
            <el-descriptions-item label="设备名称">{{ deviceData.device_name }}</el-descriptions-item>
            <el-descriptions-item label="设备类型">
              <el-tag v-if="deviceData.device_type" type="info" size="small">
                {{ deviceData.device_type }}
              </el-tag>
              <span v-else style="color: #909399">-</span>
            </el-descriptions-item>
            <el-descriptions-item label="单价">¥{{ deviceData.unit_price }}</el-descriptions-item>
            <el-descriptions-item label="规格型号">{{ deviceData.spec_model || '-' }}</el-descriptions-item>
            
            <!-- 关键参数显示 -->
            <el-descriptions-item v-if="deviceData.key_params && Object.keys(deviceData.key_params).length > 0" label="关键参数" :span="2">
              <div class="key-params-display">
                <el-tag
                  v-for="(param, key) in deviceData.key_params"
                  :key="key"
                  type="success"
                  size="small"
                  style="margin-right: 8px; margin-bottom: 8px"
                >
                  {{ key }}: {{ getParamValue(param) }}
                </el-tag>
              </div>
            </el-descriptions-item>
            
            <el-descriptions-item label="详细参数" :span="2">
              {{ deviceData.detailed_params || '-' }}
            </el-descriptions-item>
            
            <!-- 录入方式和时间 -->
            <el-descriptions-item label="录入方式">
              <el-tag v-if="deviceData.input_method === 'manual'" type="info" size="small">手动录入</el-tag>
              <el-tag v-else-if="deviceData.input_method === 'intelligent'" type="success" size="small">智能解析</el-tag>
              <el-tag v-else-if="deviceData.input_method === 'excel'" type="warning" size="small">Excel导入</el-tag>
              <span v-else style="color: #909399">-</span>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ deviceData.created_at ? new Date(deviceData.created_at).toLocaleString('zh-CN') : '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="primary" @click="handleEdit">编辑设备</el-button>
      <el-button type="danger" @click="handleDelete">删除设备</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDeviceById, deleteDevice } from '../../api/database'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  deviceId: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'edit', 'delete', 'view-rule'])

const visible = ref(props.modelValue)
const loading = ref(false)
const deviceData = ref(null)
const activeTab = ref('basic')

// 监听 modelValue 变化
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.deviceId) {
    fetchDeviceDetail()
  }
})

// 监听 visible 变化
watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 获取设备详情
const fetchDeviceDetail = async () => {
  loading.value = true
  try {
    const response = await getDeviceById(props.deviceId)
    
    if (response.data.success) {
      deviceData.value = response.data.data
    } else {
      ElMessage.error(response.data.message || '获取设备详情失败')
    }
  } catch (error) {
    console.error('获取设备详情失败:', error)
    ElMessage.error('获取设备详情失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 编辑设备
const handleEdit = () => {
  emit('edit', deviceData.value)
  handleClose()
}

// 删除设备
const handleDelete = () => {
  ElMessageBox.confirm(
    `确定要删除设备 "${deviceData.value.device_name}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await deleteDevice(deviceData.value.device_id)
      
      if (response.data.success) {
        ElMessage.success(response.data.message || '设备删除成功')
        emit('delete')
        handleClose()
      } else {
        ElMessage.error(response.data.message || '设备删除失败')
      }
    } catch (error) {
      console.error('设备删除失败:', error)
      ElMessage.error('设备删除失败，请稍后重试')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 获取参数值（处理简单值和结构化值）
const getParamValue = (param) => {
  if (typeof param === 'object' && param !== null) {
    // 结构化格式: { value: '蒸汽', unit: '' }
    const value = param.value || ''
    const unit = param.unit || ''
    return value + unit
  }
  // 简单值格式: '蒸汽'
  return param || '-'
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
  activeTab.value = 'basic'
}
</script>

<style scoped>
.device-detail {
  min-height: 400px;
}

:deep(.el-tabs__content) {
  padding: 20px;
}

.key-params-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
