<template>
  <div class="rule-statistics">
    <!-- 关键指标卡片 -->
    <el-row :gutter="20" class="metrics-row">
      <el-col :span="6">
        <el-card class="metric-card">
          <el-statistic title="总规则数" :value="metrics.total_rules">
            <template #suffix>
              <span class="metric-unit">条</span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="metric-card">
          <el-statistic title="平均阈值" :value="metrics.avg_threshold" :precision="2" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="metric-card">
          <el-statistic title="平均权重" :value="metrics.avg_weight" :precision="2" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="metric-card">
          <el-statistic title="匹配成功率" :value="metrics.success_rate" :precision="1">
            <template #suffix>
              <span class="metric-unit">%</span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 权重分布直方图 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>权重分布</span>
          <el-button size="small" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      <div ref="weightChartRef" class="chart-container"></div>
    </el-card>

    <!-- 阈值分布饼图 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>阈值分布</span>
        </div>
      </template>
      <div ref="thresholdChartRef" class="chart-container"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '@/api'

const weightChartRef = ref(null)
const thresholdChartRef = ref(null)

let weightChart = null
let thresholdChart = null

const metrics = reactive({
  total_rules: 0,
  avg_threshold: 0,
  avg_weight: 0,
  success_rate: 0
})

const loadStatistics = async () => {
  try {
    // 更新API路径到统计命名空间
    const response = await api.get('/statistics/rules')
    
    if (response.data.success) {
      const stats = response.data.statistics
      
      // 更新关键指标
      metrics.total_rules = stats.total_rules || 0
      metrics.avg_threshold = stats.avg_threshold || 0
      metrics.avg_weight = stats.avg_weight || 0
      metrics.success_rate = ((stats.match_success_rate?.overall || 0) * 100)
      
      // 渲染图表
      await nextTick()
      renderWeightChart(stats.weight_distribution || {})
      renderThresholdChart(stats.threshold_distribution || {})
    } else {
      ElMessage.error(response.data.message || '加载统计数据失败')
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败: ' + (error.response?.data?.message || error.message))
  }
}

const renderWeightChart = (distribution) => {
  if (!weightChartRef.value) return
  
  if (!weightChart) {
    weightChart = echarts.init(weightChartRef.value)
  }
  
  // 转换数据格式
  const rangeLabels = {
    'low': '低权重 (0-2)',
    'medium': '中权重 (2-4)',
    'high': '高权重 (4+)'
  }
  
  const ranges = Object.keys(distribution).sort()
  const data = ranges.map(range => ({
    name: rangeLabels[range] || range,
    value: distribution[range]
  }))
  
  const option = {
    title: {
      text: '特征权重分布',
      left: 'center',
      top: 5,
      textStyle: {
        fontSize: 16
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: '{b}<br/>特征数量: {c}'
    },
    grid: {
      left: 60,
      right: 40,
      top: 50,
      bottom: 60,
      containLabel: false
    },
    xAxis: {
      type: 'category',
      data: data.map(d => d.name),
      name: '权重范围',
      nameLocation: 'middle',
      nameGap: 35,
      nameTextStyle: {
        fontSize: 13
      },
      axisLabel: {
        interval: 0,
        rotate: 0,
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      name: '特征数量',
      nameLocation: 'middle',
      nameGap: 45,
      nameTextStyle: {
        fontSize: 13
      },
      axisLabel: {
        fontSize: 12
      }
    },
    series: [
      {
        name: '特征数量',
        type: 'bar',
        data: data.map(d => d.value),
        itemStyle: {
          color: '#409EFF'
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}',
          fontSize: 12
        }
      }
    ]
  }
  
  weightChart.setOption(option, true)
}

const renderThresholdChart = (distribution) => {
  if (!thresholdChartRef.value) return
  
  if (!thresholdChart) {
    thresholdChart = echarts.init(thresholdChartRef.value)
  }
  
  // 转换数据格式
  const thresholdLabels = {
    'low': '低阈值 (<3)',
    'medium': '中阈值 (3-5)',
    'high': '高阈值 (≥5)'
  }
  
  const data = Object.keys(distribution).map(threshold => ({
    name: thresholdLabels[threshold] || threshold,
    value: distribution[threshold]
  })).filter(d => d.value > 0) // 只显示有数据的项
  
  const option = {
    title: {
      text: '匹配阈值分布',
      left: 'center',
      top: 5,
      textStyle: {
        fontSize: 16
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}<br/>规则数量: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 20,
      top: 60,
      textStyle: {
        fontSize: 13
      }
    },
    series: [
      {
        name: '规则数量',
        type: 'pie',
        radius: ['35%', '65%'],
        center: ['60%', '52%'],
        data: data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          formatter: '{b}\n{c} ({d}%)',
          fontSize: 12,
          lineHeight: 18
        },
        labelLine: {
          length: 15,
          length2: 10
        }
      }
    ]
  }
  
  thresholdChart.setOption(option, true)
}

const refreshData = () => {
  loadStatistics()
}

const handleResize = () => {
  weightChart?.resize()
  thresholdChart?.resize()
}

onMounted(() => {
  loadStatistics()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  weightChart?.dispose()
  thresholdChart?.dispose()
})
</script>

<style scoped>
.rule-statistics {
  padding: 20px;
}

.metrics-row {
  margin-bottom: 20px;
}

.metric-card {
  text-align: center;
}

.metric-unit {
  font-size: 14px;
  color: #909399;
  margin-left: 4px;
}

.chart-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.chart-container {
  width: 100%;
  height: 400px;
}
</style>
