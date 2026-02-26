<template>
  <el-card class="devices-without-rules">
    <template #header>
      <div class="card-header">
        <span>无规则设备</span>
        <el-badge
          v-if="devices.length > 0"
          :value="devices.length"
          type="danger"
        />
      </div>
    </template>
    
    <div v-if="devices.length > 0">
      <el-alert
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 15px"
      >
        <template #title>
          发现 {{ devices.length }} 个设备没有匹配规则，建议为这些设备生成规则
        </template>
      </el-alert>
      
      <el-table
        v-loading="loading"
        :data="devices"
        stripe
        style="width: 100%"
        max-height="400"
      >
        <el-table-column prop="device_id" label="设备ID" width="120" />
        <el-table-column prop="brand" label="品牌" width="120" />
        <el-table-column prop="device_name" label="设备名称" width="180" />
        <el-table-column prop="spec_model" label="规格型号" width="150" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="handleView(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="action-section">
        <el-button
          type="primary"
          :loading="generating"
          @click="handleGenerateRules"
        >
          批量生成规则
        </el-button>
      </div>
    </div>
    
    <el-empty v-else description="所有设备都有匹配规则" />
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { batchGenerateRules } from '../../api/database'

const props = defineProps({
  devices: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['view', 'generated'])

const generating = ref(false)

const handleView = (device) => {
  emit('view', device)
}

const handleGenerateRules = async () => {
  ElMessageBox.confirm(
    `确定要为 ${props.devices.length} 个设备生成规则吗？`,
    '确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(async () => {
    generating.value = true
    try {
      const deviceIds = props.devices.map(d => d.device_id)
      const response = await batchGenerateRules({
        device_ids: deviceIds,
        force_regenerate: false
      })
      
      if (response.data.success) {
        const data = response.data.data
        ElMessage.success(`规则生成完成：成功 ${data.generated} 条，失败 ${data.failed} 条`)
        emit('generated')
      } else {
        ElMessage.error(response.data.message || '规则生成失败')
      }
    } catch (error) {
      console.error('规则生成失败:', error)
      ElMessage.error('规则生成失败，请稍后重试')
    } finally {
      generating.value = false
    }
  }).catch(() => {
    // 取消操作
  })
}
</script>

<style scoped>
.devices-without-rules {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  font-size: 16px;
}

.action-section {
  margin-top: 20px;
  text-align: right;
}
</style>
