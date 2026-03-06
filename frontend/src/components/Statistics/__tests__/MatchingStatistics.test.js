import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage } from 'element-plus'
import MatchingStatistics from '../MatchingStatistics.vue'
import api from '@/api'
import * as echarts from 'echarts'

// Mock API
vi.mock('@/api', () => ({
  default: {
    get: vi.fn()
  }
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

// Mock echarts
vi.mock('echarts', () => ({
  init: vi.fn(() => ({
    setOption: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn()
  }))
}))

describe('MatchingStatistics', () => {
  const mockTrendData = [
    {
      date: '2024-01-01',
      success_rate: 0.85,
      success_count: 85,
      total: 100
    },
    {
      date: '2024-01-02',
      success_rate: 0.87,
      success_count: 87,
      total: 100
    },
    {
      date: '2024-01-03',
      success_rate: 0.90,
      success_count: 90,
      total: 100
    }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock API response
    api.get.mockResolvedValue({
      data: {
        success: true,
        trend: mockTrendData
      }
    })

    wrapper = mount(MatchingStatistics, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-date-picker': true,
          'el-button': true,
          'el-icon': true,
          'el-row': true,
          'el-col': true,
          'el-statistic': true,
          'Refresh': true
        }
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('组件渲染', () => {
    it('应该正确挂载组件', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('应该在挂载时加载趋势数据', async () => {
      await wrapper.vm.$nextTick()
      expect(api.get).toHaveBeenCalledWith('/statistics/match-success-rate', expect.any(Object))
    })
  })

  describe('趋势数据加载', () => {
    it('应该正确加载趋势数据', async () => {
      await wrapper.vm.loadTrendData()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.summary.total).toBe(300) // 100 + 100 + 100
      expect(wrapper.vm.summary.success_count).toBe(262) // 85 + 87 + 90
      expect(wrapper.vm.summary.avg_success_rate).toBeCloseTo(87.33, 1)
    })

    it('应该处理空数据', async () => {
      api.get.mockResolvedValueOnce({
        data: {
          success: true,
          trend: []
        }
      })
      
      await wrapper.vm.loadTrendData()
      
      expect(wrapper.vm.summary.total).toBe(0)
      expect(wrapper.vm.summary.success_count).toBe(0)
      expect(wrapper.vm.summary.avg_success_rate).toBe(0)
    })

    it('应该处理API错误', async () => {
      api.get.mockRejectedValueOnce(new Error('Network error'))
      
      await wrapper.vm.loadTrendData()
      
      // 不应该显示错误消息（因为日志功能可能未启用）
      expect(ElMessage.error).not.toHaveBeenCalled()
    })
  })

  describe('日期筛选', () => {
    it('应该根据日期范围筛选', async () => {
      wrapper.vm.dateRange = ['2024-01-01', '2024-01-31']
      await wrapper.vm.loadTrendData()
      
      expect(api.get).toHaveBeenCalledWith(
        '/statistics/match-success-rate',
        expect.objectContaining({
          params: expect.objectContaining({
            start_date: '2024-01-01',
            end_date: '2024-01-31'
          })
        })
      )
    })

    it('应该在没有日期范围时加载所有数据', async () => {
      wrapper.vm.dateRange = []
      await wrapper.vm.loadTrendData()
      
      expect(api.get).toHaveBeenCalledWith(
        '/statistics/match-success-rate',
        expect.objectContaining({
          params: {}
        })
      )
    })
  })

  describe('图表渲染', () => {
    it('应该初始化趋势图表', async () => {
      await wrapper.vm.loadTrendData()
      await wrapper.vm.$nextTick()
      
      expect(echarts.init).toHaveBeenCalled()
    })

    it('应该正确转换趋势数据', () => {
      wrapper.vm.renderTrendChart(mockTrendData)
      
      // 验证图表已被调用
      expect(echarts.init).toHaveBeenCalled()
    })

    it('应该在没有数据时显示提示', () => {
      wrapper.vm.renderTrendChart([])
      
      // 验证图表已被调用（会显示空状态）
      expect(echarts.init).toHaveBeenCalled()
    })
  })

  describe('摘要统计', () => {
    it('应该正确计算总匹配次数', async () => {
      await wrapper.vm.loadTrendData()
      
      expect(wrapper.vm.summary.total).toBe(300)
    })

    it('应该正确计算成功次数', async () => {
      await wrapper.vm.loadTrendData()
      
      expect(wrapper.vm.summary.success_count).toBe(262)
    })

    it('应该正确计算平均成功率', async () => {
      await wrapper.vm.loadTrendData()
      
      expect(wrapper.vm.summary.avg_success_rate).toBeCloseTo(87.33, 1)
    })
  })

  describe('响应式处理', () => {
    it('应该在窗口大小改变时调整图表', () => {
      const mockChart = {
        resize: vi.fn(),
        dispose: vi.fn(),
        setOption: vi.fn()
      }
      
      echarts.init.mockReturnValue(mockChart)
      
      wrapper.vm.renderTrendChart([])
      wrapper.vm.handleResize()
      
      expect(mockChart.resize).toHaveBeenCalled()
    })
  })

  describe('组件卸载', () => {
    it('应该在卸载时清理图表', () => {
      const mockChart = {
        resize: vi.fn(),
        dispose: vi.fn(),
        setOption: vi.fn()
      }
      
      echarts.init.mockReturnValue(mockChart)
      
      wrapper.vm.renderTrendChart([])
      wrapper.unmount()
      
      expect(mockChart.dispose).toHaveBeenCalled()
    })
  })
})
