<template>
  <el-dialog
    v-model="visible"
    title="设备详情"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-if="deviceData" v-loading="loading" class="device-detail">
      <!-- 设备基本信息 -->
      <h4>基本信息</h4>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="设备ID">{{ deviceData.device_id }}</el-descriptions-item>
        <el-descriptions-item label="品牌">{{ deviceData.brand }}</el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ deviceData.device_name }}</el-descriptions-item>
        <el-descriptions-item label="单价">¥{{ deviceData.unit_price }}</el-descriptions-item>
        <el-descriptions-item label="规格型号" :span="2">{{ deviceData.spec_model }}</el-descriptions-item>
        <el-descriptions-item label="详细参数" :span="2">{{ deviceData.detailed_params }}</el-descriptions-item>
      </el-descriptions>

      <!-- 关联规则信息 -->
      <h4>关联规则</h4>
      <div v-if="deviceData.rules && deviceData.rules.length > 0">
        <el-table :data="deviceData.rules" stripe style="width: 100%">
          <el-table-column prop="rule_id" label="规则ID" width="150" />
          <el-table-column prop="match_threshold" label="匹配阈值" width="100">
            <template #default="{ row }">
              <el-tag :type="getThresholdType(row.match_threshold)">
                {{ row.match_threshold }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="特征数量" width="100">
            <template #default="{ row }">
              {{ row.auto_extracted_features?.length || 0 }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="handleViewRule(row)">
                查看规则
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-empty v-else description="该设备暂无关联规则" />
    </div>
    
    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="primary" @click="handleEdit">编辑设备</el-button>
      <el-button
        v-if="!deviceData?.rules || deviceData.rules.length === 0"
        type="success"
        @click="handleGenerateRule"
      >
        生成规则
      </el-button>
      <el-button
        v-else
        type="warning"
        @click="handleRegenerateRule"
      >
        重新生成规则
      </el-button>
      <el-button type="danger" @click="handleDelete">删除设备</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDeviceById, deleteDevice } from '../../api/database'
import { batchGenerateRules } from '../../api/database'

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

// 获取阈值标签类型
const getThresholdType = (threshold) => {
  if (threshold < 0.5) return 'danger'
  if (threshold < 0.7) return 'warning'
  return 'success'
}

// 编辑设备
const handleEdit = () => {
  emit('edit', deviceData.value)
  handleClose()
}

// 删除设备
const handleDelete = () => {
  const hasRules = deviceData.value.rules && deviceData.value.rules.length > 0
  ElMessageBox.confirm(
    `确定要删除设备 "${deviceData.value.device_name}" 吗？${hasRules ? `关联的 ${deviceData.value.rules.length} 条规则也将被删除。` : ''}`,
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

// 生成规则
const handleGenerateRule = async () => {
  try {
    const response = await batchGenerateRules({
      device_ids: [deviceData.value.device_id],
      force_regenerate: false
    })
    
    if (response.data.success) {
      ElMessage.success('规则生成成功')
      fetchDeviceDetail()
    } else {
      ElMessage.error(response.data.message || '规则生成失败')
    }
  } catch (error) {
    console.error('规则生成失败:', error)
    ElMessage.error('规则生成失败，请稍后重试')
  }
}

// 重新生成规则
const handleRegenerateRule = async () => {
  ElMessageBox.confirm(
    '确定要重新生成规则吗？现有规则将被覆盖。',
    '确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await batchGenerateRules({
        device_ids: [deviceData.value.device_id],
        force_regenerate: true
      })
      
      if (response.data.success) {
        ElMessage.success('规则重新生成成功')
        fetchDeviceDetail()
      } else {
        ElMessage.error(response.data.message || '规则重新生成失败')
      }
    } catch (error) {
      console.error('规则重新生成失败:', error)
      ElMessage.error('规则重新生成失败，请稍后重试')
    }
  }).catch(() => {
    // 取消操作
  })
}

// 查看规则详情
const handleViewRule = (rule) => {
  emit('view-rule', rule)
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
.device-detail h4 {
  margin: 20px 0 10px 0;
  color: #303133;
}

.device-detail h4:first-child {
  margin-top: 0;
}
</style>
