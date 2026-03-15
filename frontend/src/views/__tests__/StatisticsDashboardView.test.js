import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage } from 'element-plus'
import StatisticsDashboardView from '../StatisticsDashboardView.vue'
import * as databaseApi from '@/api/database'

// Mock database API
vi.mock('@/api/database', () => ({
  getStatistics: vi.fn(),
  getBrandDistribution: vi.fn(),
  getPriceDistribution: vi.fn(),
  getRecentDevices: vi.fn()
}))

// Mock Element Plus
vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      warning: vi.fn(),
      success: vi.fn(),
      error: vi.fn(),
      info: vi.fn()
    }
  }
})

// Mock router
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  }),
  useRoute: () => ({
    query: {}
  })
}))

describe('StatisticsDashboardView', () => {
  const mockStatistics = {
    total_devices: 100,
    total_rules: 80,
    devices_without_rules: 20
  }

  const mockBrands = [
    { brand: '霍尼韦尔', count: 30 },
    { brand: '西门子', count: 25 }
  ]

  const mockPriceRanges = [
    { range: '0-1000', count: 20 },
    { range: '1000-5000', count: 50 }
  ]

  const mockRecentDevices = [
    {
      device_id: 'DEV001',
      brand: '霍尼韦尔',
      device_name: '温度传感器'
    }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock API responses
    databaseApi.getStatistics.mockResolvedValue({
      data: {
        success: true,
        data: mockStatistics
      }
    })

    databaseApi.getBrandDistribution.mockResolvedValue({
      data: {
        success: true,
        data: { brands: mockBrands }
      }
    })

    databaseApi.getPriceDistribution.mockResolvedValue({
      data: {
        success: true,
        data: { price_ranges: mockPriceRanges }
      }
    })

    databaseApi.getRecentDevices.mockResolvedValue({
      data: {
        success: true,
        data: { devices: mockRecentDevices }
      }
    })

    wrapper = mount(StatisticsDashboardView, {
      global: {
        stubs: {
          'el-card': true,
          'el-tabs': true,
          'el-tab-pane': true,
          'el-row': true,
          'el-col': true,
          'SummaryCards': true,
          'BrandChart': true,
          'PriceChart': true,
          'RecentDevices': true,
          'DeviceDetail': true,
          'MatchLogs': true,
          'MatchingStatistics': true
        }
      }
    })
  })

  describe('组件渲染', () => {
    it('应该正确挂载组件', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('应该显示标签页', () => {
      expect(wrapper.vm.activeTab).toBeDefined()
    })

    it('应该默认显示概览标签页', () => {
      expect(wrapper.vm.activeTab).toBe('overview')
    })
  })

  describe('数据加载', () => {
    it('应该在概览标签页加载所有数据', async () => {
      await wrapper.vm.$nextTick()
      
      expect(databaseApi.getStatistics).toHaveBeenCalled()
      expect(databaseApi.getBrandDistribution).toHaveBeenCalled()
      expect(databaseApi.getPriceDistribution).toHaveBeenCalled()
      expect(databaseApi.getRecentDevices).toHaveBeenCalled()
    })

    it('应该正确加载统计数据', async () => {
      await wrapper.vm.fetchStatistics()
      
      expect(wrapper.vm.statistics).toEqual(mockStatistics)
    })

    it('应该正确加载品牌分布', async () => {
      await wrapper.vm.fetchBrandDistribution()
      
      expect(wrapper.vm.brandData).toEqual(mockBrands)
    })

    it('应该正确加载价格分布', async () => {
      await wrapper.vm.fetchPriceDistribution()
      
      expect(wrapper.vm.priceData).toEqual(mockPriceRanges)
    })

    it('应该正确加载最近设备', async () => {
      await wrapper.vm.fetchRecentDevices()
      
      expect(wrapper.vm.recentDevices).toEqual(mockRecentDevices)
    })
  })

  describe('错误处理', () => {
    it('应该处理统计数据加载错误', async () => {
      databaseApi.getStatistics.mockRejectedValueOnce(new Error('Network error'))
      
      await wrapper.vm.fetchStatistics()
      
      expect(ElMessage.error).toHaveBeenCalled()
    })

    it('应该处理品牌分布加载错误', async () => {
      databaseApi.getBrandDistribution.mockRejectedValueOnce(new Error('Network error'))
      
      await wrapper.vm.fetchBrandDistribution()
      
      // 不应该显示错误消息（静默失败）
      expect(wrapper.vm.brandData).toEqual([])
    })
  })

  describe('标签页切换', () => {
    it('应该支持切换到匹配日志标签页', async () => {
      wrapper.vm.activeTab = 'logs'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.activeTab).toBe('logs')
    })

    it('应该支持切换到匹配统计标签页', async () => {
      wrapper.vm.activeTab = 'matching'
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.activeTab).toBe('matching')
    })
  })

  describe('交互功能', () => {
    it('应该处理品牌点击', async () => {
      await wrapper.vm.handleBrandClick('霍尼韦尔')
      
      expect(mockPush).toHaveBeenCalledWith({
        name: 'DeviceManagement',
        query: { brand: '霍尼韦尔' }
      })
    })

    it('应该处理价格区间点击', async () => {
      await wrapper.vm.handleRangeClick('0-1000')
      
      expect(mockPush).toHaveBeenCalledWith({
        name: 'DeviceManagement',
        query: { priceRange: '0-1000' }
      })
    })

    it('应该处理查看设备详情', async () => {
      await wrapper.vm.handleViewDevice(mockRecentDevices[0])
      
      expect(wrapper.vm.currentDeviceId).toBe('DEV001')
      expect(wrapper.vm.detailDialogVisible).toBe(true)
    })

    it('应该处理编辑设备', async () => {
      await wrapper.vm.handleEditDevice()
      
      expect(mockPush).toHaveBeenCalledWith({ name: 'DeviceManagement' })
    })

    it('应该在删除设备后刷新数据', async () => {
      const loadAllDataSpy = vi.spyOn(wrapper.vm, 'loadAllData')
      
      await wrapper.vm.handleDeleteDevice()
      
      expect(loadAllDataSpy).toHaveBeenCalled()
    })
  })

  describe('加载状态', () => {
    it('应该在加载时显示loading状态', async () => {
      const loadPromise = wrapper.vm.fetchStatistics()
      expect(wrapper.vm.loading).toBe(true)
      
      await loadPromise
      expect(wrapper.vm.loading).toBe(false)
    })

    it('应该在加载最近设备时显示loading状态', async () => {
      const loadPromise = wrapper.vm.fetchRecentDevices()
      expect(wrapper.vm.loadingRecent).toBe(true)
      
      await loadPromise
      expect(wrapper.vm.loadingRecent).toBe(false)
    })
  })
})
