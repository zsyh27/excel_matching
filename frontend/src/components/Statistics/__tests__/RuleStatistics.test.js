import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage } from 'element-plus'
import RuleStatistics from '../RuleStatistics.vue'
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

describe('RuleStatistics', () => {
  const mockStatistics = {
    total_rules: 100,
    avg_threshold: 5.2,
    avg_weight: 12.5,
    match_success_rate: {
      overall: 0.85
    },
    weight_distribution: {
      low: 20,
      medium: 50,
      high: 30
    },
    threshold_distribution: {
      low: 10,
      medium: 60,
      high: 30
    }
  }

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock API response
    api.get.mockResolvedValue({
      data: {
        success: true,
        statistics: mockStatistics
      }
    })

    wrapper = mount(RuleStatistics, {
      global: {
        stubs: {
          'el-row': true,
          'el-col': true,
          'el-card': true,
          'el-statistic': true,
          'el-button': true,
          'el-icon': true,
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

    it('应该在挂载时加载统计数据', async () => {
      await wrapper.vm.$nextTick()
      expect(api.get).toHaveBeenCalledWith('/statistics/rules')
    })
  })

  describe('统计数据加载', () => {
    it('应该正确加载统计数据', async () => {
      await wrapper.vm.loadStatistics()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.metrics.total_rules).toBe(100)
      expect(wrapper.vm.metrics.avg_threshold).toBe(5.2)
      expect(wrapper.vm.metrics.avg_weight).toBe(12.5)
      expect(wrapper.vm.metrics.success_rate).toBe(85)
    })

    it('应该处理API错误', async () => {
      api.get.mockRejectedValueOnce(new Error('Network error'))
      
      await wrapper.vm.loadStatistics()
      
      expect(ElMessage.error).toHaveBeenCalled()
    })

    it('应该处理空数据', async () => {
      api.get.mockResolvedValueOnce({
        data: {
          success: true,
          statistics: {
            total_rules: 0,
            avg_threshold: 0,
            avg_weight: 0,
            match_success_rate: { overall: 0 },
            weight_distribution: {},
            threshold_distribution: {}
          }
        }
      })
      
      await wrapper.vm.loadStatistics()
      
      expect(wrapper.vm.metrics.total_rules).toBe(0)
      expect(wrapper.vm.metrics.success_rate).toBe(0)
    })
  })

  describe('图表渲染', () => {
    it('应该初始化权重分布图表', async () => {
      await wrapper.vm.loadStatistics()
      await wrapper.vm.$nextTick()
      
      expect(echarts.init).toHaveBeenCalled()
    })

    it('应该初始化阈值分布图表', async () => {
      await wrapper.vm.loadStatistics()
      await wrapper.vm.$nextTick()
      
      expect(echarts.init).toHaveBeenCalled()
    })

    it('应该正确转换权重分布数据', () => {
      const distribution = {
        low: 20,
        medium: 50,
        high: 30
      }
      
      wrapper.vm.renderWeightChart(distribution)
      
      // 验证图表已被调用
      expect(echarts.init).toHaveBeenCalled()
    })

    it('应该正确转换阈值分布数据', () => {
      const distribution = {
        low: 10,
        medium: 60,
        high: 30
      }
      
      wrapper.vm.renderThresholdChart(distribution)
      
      // 验证图表已被调用
      expect(echarts.init).toHaveBeenCalled()
    })
  })

  describe('刷新功能', () => {
    it('应该刷新统计数据', async () => {
      await wrapper.vm.refreshData()
      
      expect(api.get).toHaveBeenCalledWith('/statistics/rules')
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
      
      wrapper.vm.renderWeightChart({})
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
      
      wrapper.vm.renderWeightChart({})
      wrapper.unmount()
      
      expect(mockChart.dispose).toHaveBeenCalled()
    })
  })
})
