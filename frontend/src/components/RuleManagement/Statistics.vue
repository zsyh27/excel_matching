<template>
  <div class="statistics">
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

    <!-- 匹配成功率趋势图 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>匹配成功率趋势</span>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            size="small"
            @change="loadTrendData"
          />
        </div>
      </template>
      <div ref="trendChartRef" class="chart-container"></div>
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
const trendChartRef = ref(null)

let weightChart = null
let thresholdChart = null
let trendChart = null

const dateRange = ref([])

const metrics = reactive({
  total_rules: 0,
  avg_threshold: 0,
  avg_weight: 0,
  success_rate: 0
})

const loadStatistics = async () => {
  try {
    const response = await api.get('/rules/management/statistics')
    
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

const loadTrendData = async () => {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0].toISOString()
      params.end_date = dateRange.value[1].toISOString()
    }
    
    const response = await api.get('/match-logs/statistics', { params })
    
    if (response.data.success) {
      // 当前后端只返回总体统计，不返回每日趋势
      // 如果有总体数据，显示单点数据
      const stats = response.data
      if (stats.total > 0) {
        const dailyStats = [{
          date: new Date().toISOString().split('T')[0],
          success_rate: stats.success_count / stats.total
        }]
        renderTrendChart(dailyStats)
      } else {
        renderTrendChart([])
      }
    } else {
      // 如果日志功能未启用，显示空图表
      renderTrendChart([])
    }
  } catch (error) {
    console.error('加载趋势数据失败:', error)
    // 不显示错误消息，因为日志功能可能未启用
    renderTrendChart([])
  }
}

const renderWeightChart = (distribution) => {
  if (!weightChartRef.value) return
  
  if (!weightChart) {
    weightChart = echarts.init(weightChartRef.value)
  }
  
  // 转换数据格式
  const ranges = Object.keys(distribution).sort()
  const values = ranges.map(range => distribution[range])
  
  const option = {
    title: {
      text: '特征权重分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: ranges,
      name: '权重范围'
    },
    yAxis: {
      type: 'value',
      name: '特征数量'
    },
    series: [
      {
        name: '特征数量',
        type: 'bar',
        data: values,
        itemStyle: {
          color: '#409EFF'
        }
      }
    ]
  }
  
  weightChart.setOption(option)
}

const renderThresholdChart = (distribution) => {
  if (!thresholdChartRef.value) return
  
  if (!thresholdChart) {
    thresholdChart = echarts.init(thresholdChartRef.value)
  }
  
  // 转换数据格式
  const data = Object.keys(distribution).map(threshold => ({
    name: `阈值 ${threshold}`,
    value: distribution[threshold]
  }))
  
  const option = {
    title: {
      text: '匹配阈值分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle'
    },
    series: [
      {
        name: '规则数量',
        type: 'pie',
        radius: '60%',
        data: data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  thresholdChart.setOption(option)
}

const renderTrendChart = (dailyStats) => {
  if (!trendChartRef.value) return
  
  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value)
  }
  
  // 转换数据格式
  const dates = dailyStats.map(stat => stat.date)
  const successRates = dailyStats.map(stat => (stat.success_rate * 100).toFixed(1))
  
  const option = {
    title: {
      text: '匹配成功率趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>{a}: {c}%'
    },
    xAxis: {
      type: 'category',
      data: dates,
      name: '日期'
    },
    yAxis: {
      type: 'value',
      name: '成功率 (%)',
      min: 0,
      max: 100
    },
    series: [
      {
        name: '成功率',
        type: 'line',
        data: successRates,
        smooth: true,
        itemStyle: {
          color: '#67C23A'
        },
        areaStyle: {
          color: 'rgba(103, 194, 58, 0.2)'
        }
      }
    ]
  }
  
  // 如果没有数据，显示提示
  if (dailyStats.length === 0) {
    option.title.subtext = '暂无匹配日志数据'
    option.graphic = {
      type: 'text',
      left: 'center',
      top: 'middle',
      style: {
        text: '暂无数据\n请先进行设备匹配以生成日志',
        fontSize: 14,
        fill: '#999',
        textAlign: 'center'
      }
    }
  }
  
  trendChart.setOption(option)
}

const refreshData = () => {
  loadStatistics()
  loadTrendData()
}

const handleResize = () => {
  weightChart?.resize()
  thresholdChart?.resize()
  trendChart?.resize()
}

onMounted(() => {
  loadStatistics()
  loadTrendData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  weightChart?.dispose()
  thresholdChart?.dispose()
  trendChart?.dispose()
})
</script>

<style scoped>
.statistics {
  max-width: 1400px;
  margin: 0 auto;
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
