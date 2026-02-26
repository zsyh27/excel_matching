<template>
  <el-row :gutter="20" class="summary-cards">
    <el-col :span="6">
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

    <el-col :span="6">
      <el-card shadow="hover" class="stat-card">
        <div class="card-content">
          <el-icon class="card-icon" color="#67C23A" :size="40">
            <Document />
          </el-icon>
          <div class="card-info">
            <div class="card-value">{{ statistics.total_rules || 0 }}</div>
            <div class="card-label">规则总数</div>
          </div>
        </div>
      </el-card>
    </el-col>

    <el-col :span="6">
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

    <el-col :span="6">
      <el-card shadow="hover" class="stat-card">
        <div class="card-content">
          <el-icon class="card-icon" :color="getCoverageColor()" :size="40">
            <PieChart />
          </el-icon>
          <div class="card-info">
            <div class="card-value">{{ getCoverageRate() }}%</div>
            <div class="card-label">规则覆盖率</div>
          </div>
        </div>
        <el-progress
          :percentage="parseFloat(getCoverageRate())"
          :color="getCoverageColor()"
          :show-text="false"
          style="margin-top: 10px"
        />
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { computed } from 'vue'
import { Box, Document, Collection, PieChart } from '@element-plus/icons-vue'

const props = defineProps({
  statistics: {
    type: Object,
    default: () => ({})
  }
})

// 计算覆盖率
const getCoverageRate = () => {
  const total = props.statistics.total_devices || 0
  const rules = props.statistics.total_rules || 0
  if (total === 0) return '0.0'
  return ((rules / total) * 100).toFixed(1)
}

// 获取覆盖率颜色
const getCoverageColor = () => {
  const rate = parseFloat(getCoverageRate())
  if (rate < 50) return '#F56C6C'
  if (rate < 80) return '#E6A23C'
  return '#67C23A'
}
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
