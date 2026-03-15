<template>
  <el-row :gutter="20" class="summary-cards">
    <el-col :span="8">
      <el-card shadow="hover" class="stat-card">
        <div class="card-content">
          <el-icon class="card-icon" color="#409EFF" :size="40">
            <Box />
          </el-icon>
          <div class="card-info">
            <div class="card-value">{{ statistics.total_devices || 0 }}</div>
            <div class="card-label">设备总数</div>
          </div>
        </div>
      </el-card>
    </el-col>

    <el-col :span="8">
      <el-card shadow="hover" class="stat-card">
        <div class="card-content">
          <el-icon class="card-icon" color="#E6A23C" :size="40">
            <Collection />
          </el-icon>
          <div class="card-info">
            <div class="card-value">{{ statistics.total_brands || 0 }}</div>
            <div class="card-label">品牌数量</div>
          </div>
        </div>
      </el-card>
    </el-col>

    <el-col :span="8">
      <el-card shadow="hover" class="stat-card">
        <div class="card-content">
          <el-icon class="card-icon" color="#67C23A" :size="40">
            <Histogram />
          </el-icon>
          <div class="card-info">
            <div class="card-value">{{ statistics.total_device_types || 0 }}</div>
            <div class="card-label">设备类型</div>
          </div>
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { Box, Collection, Histogram } from '@element-plus/icons-vue'

const props = defineProps({
  statistics: {
    type: Object,
    default: () => ({})
  }
})
</script>

<style scoped>
.summary-cards {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.card-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.card-icon {
  flex-shrink: 0;
}

.card-info {
  flex: 1;
}

.card-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 8px;
}

.card-label {
  font-size: 14px;
  color: #909399;
}
</style>
