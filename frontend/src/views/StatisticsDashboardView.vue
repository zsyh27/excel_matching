<template>
  <div class="statistics-dashboard-view">
    <el-card class="header-card">
      <h2>统计仪表板</h2>
      <p>查看设备库的统计信息和数据分析</p>
    </el-card>

    <div v-loading="loading" class="dashboard-content">
      <!-- 概览卡片 -->
      <SummaryCards :statistics="statistics" />

      <!-- 图表区域 -->
      <el-row :gutter="20">
        <el-col :span="12">
          <BrandChart :data="brandData" @brand-click="handleBrandClick" />
        </el-col>
        <el-col :span="12">
          <PriceChart :data="priceData" @range-click="handleRangeClick" />
        </el-col>
      </el-row>

      <!-- 列表区域 -->
      <el-row :gutter="20">
        <el-col :span="12">
          <RecentDevices
            :devices="recentDevices"
            :loading="loadingRecent"
            @view="handleViewDevice"
          />
        </el-col>
        <el-col :span="12">
          <DevicesWithoutRules
            :devices="devicesWithoutRules"
            :loading="loadingWithoutRules"
            @view="handleViewDevice"
            @generated="handleRulesGenerated"
          />
        </el-col>
      </el-row>
    </div>

    <!-- 设备详情对话框 -->
    <DeviceDetail
      v-model="detailDialogVisible"
      :device-id="currentDeviceId"
      @edit="handleEditDevice"
      @delete="handleDeleteDevice"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import SummaryCards from '../components/Statistics/SummaryCards.vue'
import BrandChart from '../components/Statistics/BrandChart.vue'
import PriceChart from '../components/Statistics/PriceChart.vue'
import RecentDevices from '../components/Statistics/RecentDevices.vue'
import DevicesWithoutRules from '../components/Statistics/DevicesWithoutRules.vue'
import DeviceDetail from '../components/DeviceManagement/DeviceDetail.vue'
import {
  getStatistics,
  getBrandDistribution,
  getPriceDistribution,
  getRecentDevices,
  getDevicesWithoutRules
} from '../api/database'

const router = useRouter()

// 数据状态
const loading = ref(false)
const loadingRecent = ref(false)
const loadingWithoutRules = ref(false)

const statistics = ref({})
const brandData = ref([])
const priceData = ref([])
const recentDevices = ref([])
const devicesWithoutRules = ref([])

// 对话框状态
const detailDialogVisible = ref(false)
const currentDeviceId = ref('')

// 获取统计数据
const fetchStatistics = async () => {
  loading.value = true
  try {
    const response = await getStatistics()
    
    if (response.data.success) {
      statistics.value = response.data.data
    } else {
      ElMessage.error(response.data.message || '获取统计数据失败')
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 获取品牌分布
const fetchBrandDistribution = async () => {
  try {
    const response = await getBrandDistribution()
    
    if (response.data.success) {
      // 提取 brands 数组
      brandData.value = response.data.data.brands || []
    } else {
      ElMessage.error(response.data.message || '获取品牌分布失败')
    }
  } catch (error) {
    console.error('获取品牌分布失败:', error)
  }
}

// 获取价格分布
const fetchPriceDistribution = async () => {
  try {
    const response = await getPriceDistribution()
    
    if (response.data.success) {
      // 提取 price_ranges 数组
      priceData.value = response.data.data.price_ranges || []
    } else {
      ElMessage.error(response.data.message || '获取价格分布失败')
    }
  } catch (error) {
    console.error('获取价格分布失败:', error)
  }
}

// 获取最近添加的设备
const fetchRecentDevices = async () => {
  loadingRecent.value = true
  try {
    const response = await getRecentDevices(10)
    
    if (response.data.success) {
      // 提取 devices 数组
      recentDevices.value = response.data.data.devices || []
    } else {
      ElMessage.error(response.data.message || '获取最近设备失败')
    }
  } catch (error) {
    console.error('获取最近设备失败:', error)
  } finally {
    loadingRecent.value = false
  }
}

// 获取无规则设备
const fetchDevicesWithoutRules = async () => {
  loadingWithoutRules.value = true
  try {
    const response = await getDevicesWithoutRules()
    
    if (response.data.success) {
      // 提取 devices 数组
      devicesWithoutRules.value = response.data.data.devices || []
    } else {
      ElMessage.error(response.data.message || '获取无规则设备失败')
    }
  } catch (error) {
    console.error('获取无规则设备失败:', error)
  } finally {
    loadingWithoutRules.value = false
  }
}

// 加载所有数据
const loadAllData = async () => {
  await Promise.all([
    fetchStatistics(),
    fetchBrandDistribution(),
    fetchPriceDistribution(),
    fetchRecentDevices(),
    fetchDevicesWithoutRules()
  ])
}

// 品牌点击处理
const handleBrandClick = (brand) => {
  // 跳转到设备管理页面并筛选该品牌
  router.push({
    name: 'DeviceManagement',
    query: { brand }
  })
}

// 价格区间点击处理
const handleRangeClick = (range) => {
  // 跳转到设备管理页面并筛选该价格区间
  router.push({
    name: 'DeviceManagement',
    query: { priceRange: range }
  })
}

// 查看设备详情
const handleViewDevice = (device) => {
  currentDeviceId.value = device.device_id
  detailDialogVisible.value = true
}

// 编辑设备
const handleEditDevice = () => {
  // 跳转到设备管理页面
  router.push({ name: 'DeviceManagement' })
}

// 删除设备
const handleDeleteDevice = () => {
  // 刷新数据
  loadAllData()
}

// 规则生成完成
const handleRulesGenerated = () => {
  // 刷新数据
  loadAllData()
}

// 组件挂载时加载数据
onMounted(() => {
  loadAllData()
})
</script>

<style scoped>
.statistics-dashboard-view {
  max-width: 1400px;
  margin: 0 auto;
}

.header-card {
  margin-bottom: 20px;
}

.header-card h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.header-card p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.dashboard-content {
  min-height: 600px;
}
</style>
