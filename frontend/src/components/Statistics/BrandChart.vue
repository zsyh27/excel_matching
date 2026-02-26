<template>
  <el-card class="brand-chart">
    <template #header>
      <div class="card-header">
        <span>品牌分布</span>
      </div>
    </template>
    <div ref="chartContainer" class="chart-container"></div>
  </el-card>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['brand-click'])

const chartContainer = ref(null)
let chartInstance = null

// 渲染图表
const renderChart = () => {
  if (!chartContainer.value || props.data.length === 0) return
  
  if (!chartInstance) {
    chartInstance = echarts.init(chartContainer.value)
    
    // 添加点击事件
    chartInstance.on('click', (params) => {
      emit('brand-click', params.name)
    })
  }
  
  const brands = props.data.map(item => item.brand)
  const counts = props.data.map(item => item.count)
  
  const option = {
    title: {
      text: `共 ${props.data.length} 个品牌`,
      left: 'center',
      top: 10,
      textStyle: {
        fontSize: 14,
        color: '#909399'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        const item = params[0]
        return `${item.name}<br/>设备数量: ${item.value}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: 60,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: brands,
      axisLabel: {
        interval: 0,
        rotate: 45,
        formatter: (value) => {
          return value.length > 8 ? value.substring(0, 8) + '...' : value
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '设备数量'
    },
    series: [
      {
        name: '设备数量',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#2378f7' },
              { offset: 0.7, color: '#2378f7' },
              { offset: 1, color: '#83bff6' }
            ])
          }
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}'
        }
      }
    ]
  }
  
  chartInstance.setOption(option)
}

// 监听数据变化
watch(() => props.data, () => {
  nextTick(() => {
    renderChart()
  })
}, { deep: true })

// 窗口大小变化处理
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 组件挂载
onMounted(() => {
  nextTick(() => {
    renderChart()
  })
  window.addEventListener('resize', handleResize)
})

// 组件卸载
onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.brand-chart {
  margin-bottom: 20px;
}

.card-header {
  font-weight: 600;
  font-size: 16px;
}

.chart-container {
  width: 100%;
  height: 400px;
}
</style>
