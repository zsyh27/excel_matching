<template>
  <el-card class="recent-devices">
    <template #header>
      <div class="card-header">
        <span>最近添加的设备</span>
        <el-tag size="small">最新 {{ devices.length }} 条</el-tag>
      </div>
    </template>
    
    <el-table
      v-loading="loading"
      :data="devices"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="device_id" label="设备ID" width="120" />
      <el-table-column prop="brand" label="品牌" width="120" />
      <el-table-column prop="device_name" label="设备名称" width="180" />
      <el-table-column prop="unit_price" label="单价" width="100">
        <template #default="{ row }">
          ¥{{ row.unit_price }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="handleView(row)">
            查看详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-empty v-if="!loading && devices.length === 0" description="暂无数据" />
  </el-card>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

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

const emit = defineEmits(['view'])

const handleView = (device) => {
  emit('view', device)
}
</script>

<style scoped>
.recent-devices {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}
</style>
