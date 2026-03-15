<template>
  <div class="matching-statistics">
    <!-- 筛选区域 -->
    <el-card class="filter-card">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="loadTrendData"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadTrendData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 匹配成功率趋势图 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>匹配成功率趋势</span>
        </div>
      </template>
      <div ref="trendChartRef" class="chart-container"></div>
    </el-card>

    <!-- 统计摘要 -->
    <el-row :gutter="20" class="summary-row">
      <el-col :span="8">
        <el-card class="summary-card">
          <el-statistic title="总匹配次数" :value="summary.total">
            <template #suffix>
              <span class="metric-unit">次</span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="summary-card">
          <el-statistic title="成功次数" :value="summary.success_count">
            <template #suffix>
              <span class="metric-unit">次</span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="summary-card">
          <el-statistic title="平均成功率" :value="summary.avg_success_rate" :precision="1">
            <template #suffix>
              <span class="metric-unit">%</span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '@/api'

const trendChartRef = ref(null)
let trendChart = null

const dateRange = ref([])

const summary = reactive({
  total: 0,
  success_count: 0,
  avg_success_rate: 0
})

const loadTrendData = async () => {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    // 调用统计API获取匹配成功率趋势
    const response = await api.get('/statistics/match-success-rate', { params })
    
    if (response.data.success) {
      const trend = response.data.trend || []
      const overall = response.data.overall || {}
      
      // 优先用 overall 数据，trend 为空时也能显示
      summary.total = overall.total || trend.reduce((sum, item) => sum + (item.total || 0), 0)
      summary.success_count = overall.success || trend.reduce((sum, item) => sum + (item.success || 0), 0)
      summary.avg_success_rate = summary.total > 0
        ? (summary.success_count / summary.total * 100)
        : 0
      
      // 渲染图表
      await nextTick()
      renderTrendChart(trend)
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
      text: '每日匹配成功率',
      left: 'center',
      top: 5,
      textStyle: {
        fontSize: 16
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const param = params[0]
        const dataIndex = param.dataIndex
        const stat = dailyStats[dataIndex]
        return `${param.name}<br/>
                成功率: ${param.value}%<br/>
                成功: ${stat.success || 0}次<br/>
                总计: ${stat.total || 0}次`
      }
    },
    grid: {
      left: 20,
      right: 20,
      top: 60,
      bottom: 20,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: dates.length > 7 ? 45 : 0,
        fontSize: 12
      },
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      name: '成功率 (%)',
      nameLocation: 'middle',
      nameGap: 50,
      min: 0,
      max: 100,
      axisLabel: {
        formatter: '{value}%',
        fontSize: 12
      }
    },
    series: [
      {
        name: '成功率',
        type: 'line',
        data: successRates,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: {
          color: '#67C23A'
        },
        areaStyle: {
          color: 'rgba(103, 194, 58, 0.2)'
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}%',
          fontSize: 12,
          color: '#67C23A'
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
  
  trendChart.setOption(option, true)
}

const handleResize = () => {
  trendChart?.resize()
}

onMounted(() => {
  loadTrendData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
})
</script>

<style scoped>
.matching-statistics {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  margin-bottom: 0;
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

.summary-row {
  margin-top: 20px;
}

.summary-card {
  text-align: center;
}

.metric-unit {
  font-size: 14px;
  color: #909399;
  margin-left: 4px;
}
</style>
