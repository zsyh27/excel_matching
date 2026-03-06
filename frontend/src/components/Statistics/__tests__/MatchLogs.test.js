import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import MatchLogs from '../MatchLogs.vue'
import api from '@/api'

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
    },
    ElMessageBox: {
      confirm: vi.fn()
    }
  }
})

// Mock router
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: mockPush
  })
}))

describe('MatchLogs', () => {
  const mockLogs = [
    {
      log_id: 'LOG001',
      timestamp: '2024-01-01 10:00:00',
      input_description: '霍尼韦尔温度传感器',
      match_status: 'success',
      matched_device_id: 'DEV001',
      match_score: 8.5,
      extracted_features: ['霍尼韦尔', '温度传感器'],
      match_threshold: 5.0,
      match_reason: '匹配成功'
    },
    {
      log_id: 'LOG002',
      timestamp: '2024-01-01 11:00:00',
      input_description: '未知设备',
      match_status: 'failed',
      matched_device_id: null,
      match_score: 2.0,
      extracted_features: ['未知'],
      match_threshold: 5.0,
      match_reason: '得分低于阈值'
    }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock API response
    api.get.mockResolvedValue({
      data: {
        success: true,
        logs: mockLogs,
        total: 2
      }
    })

    wrapper = mount(MatchLogs, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-date-picker': true,
          'el-select': true,
          'el-option': true,
          'el-input': true,
          'el-button': true,
          'el-icon': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-pagination': true,
          'el-dialog': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'Search': true,
          'Refresh': true,
          'Download': true,
          'View': true
        }
      }
    })
  })

  describe('组件渲染', () => {
    it('应该正确挂载组件', () => {
      expect(wrapper.exists()).toBe(true)
    })

    it('应该在挂载时加载日志', async () => {
      await wrapper.vm.$nextTick()
      expect(api.get).toHaveBeenCalledWith('/statistics/match-logs', expect.any(Object))
    })
  })

  describe('日志加载', () => {
    it('应该正确加载日志数据', async () => {
      await wrapper.vm.loadLogs()
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.logs).toHaveLength(2)
      expect(wrapper.vm.total).toBe(2)
    })

    it('应该处理API错误', async () => {
      api.get.mockRejectedValueOnce(new Error('Network error'))
      
      await wrapper.vm.loadLogs()
      
      expect(ElMessage.error).toHaveBeenCalled()
    })

    it('应该在加载时显示loading状态', async () => {
      const loadPromise = wrapper.vm.loadLogs()
      expect(wrapper.vm.loading).toBe(true)
      
      await loadPromise
      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('筛选功能', () => {
    it('应该根据日期范围筛选', async () => {
      wrapper.vm.dateRange = ['2024-01-01', '2024-01-31']
      await wrapper.vm.handleDateChange(['2024-01-01', '2024-01-31'])
      
      expect(wrapper.vm.filters.start_date).toBe('2024-01-01')
      expect(wrapper.vm.filters.end_date).toBe('2024-01-31')
    })

    it('应该根据状态筛选', async () => {
      wrapper.vm.filters.status = 'success'
      await wrapper.vm.loadLogs()
      
      expect(api.get).toHaveBeenCalledWith(
        '/statistics/match-logs',
        expect.objectContaining({
          params: expect.objectContaining({
            status: 'success'
          })
        })
      )
    })

    it('应该重置筛选条件', async () => {
      wrapper.vm.filters.status = 'success'
      wrapper.vm.filters.device_type = '传感器'
      wrapper.vm.dateRange = ['2024-01-01', '2024-01-31']
      
      await wrapper.vm.resetFilters()
      
      expect(wrapper.vm.filters.status).toBe('')
      expect(wrapper.vm.filters.device_type).toBe('')
      expect(wrapper.vm.dateRange).toEqual([])
    })
  })

  describe('日志详情', () => {
    it('应该显示日志详情', async () => {
      api.get.mockResolvedValueOnce({
        data: {
          success: true,
          log: mockLogs[0]
        }
      })
      
      await wrapper.vm.viewDetail(mockLogs[0])
      
      expect(wrapper.vm.selectedLog).toEqual(mockLogs[0])
      expect(wrapper.vm.detailDialogVisible).toBe(true)
    })

    it('应该处理详情加载错误', async () => {
      api.get.mockRejectedValueOnce(new Error('Not found'))
      
      await wrapper.vm.viewDetail(mockLogs[0])
      
      expect(ElMessage.error).toHaveBeenCalled()
    })
  })

  describe('重测功能', () => {
    it('应该跳转到测试页面', async () => {
      ElMessageBox.confirm.mockResolvedValueOnce(true)
      
      await wrapper.vm.retestLog(mockLogs[0])
      
      expect(mockPush).toHaveBeenCalledWith({
        path: '/match-tester',
        query: { description: mockLogs[0].input_description }
      })
    })

    it('取消时不应该跳转', async () => {
      ElMessageBox.confirm.mockRejectedValueOnce('cancel')
      
      await wrapper.vm.retestLog(mockLogs[0])
      
      expect(mockPush).not.toHaveBeenCalled()
    })
  })

  describe('导出功能', () => {
    it('应该导出日志', async () => {
      const mockBlob = new Blob(['test'], { type: 'application/vnd.ms-excel' })
      api.get.mockResolvedValueOnce({ data: mockBlob })
      
      // Mock DOM methods
      const createElementSpy = vi.spyOn(document, 'createElement')
      const appendChildSpy = vi.spyOn(document.body, 'appendChild')
      const removeChildSpy = vi.spyOn(document.body, 'removeChild')
      
      await wrapper.vm.exportLogs()
      
      expect(api.get).toHaveBeenCalledWith(
        '/match-logs/export',
        expect.objectContaining({
          responseType: 'blob'
        })
      )
      expect(ElMessage.success).toHaveBeenCalledWith('导出成功')
      
      createElementSpy.mockRestore()
      appendChildSpy.mockRestore()
      removeChildSpy.mockRestore()
    })

    it('应该处理导出错误', async () => {
      api.get.mockRejectedValueOnce(new Error('Export failed'))
      
      await wrapper.vm.exportLogs()
      
      expect(ElMessage.error).toHaveBeenCalled()
    })
  })

  describe('分页功能', () => {
    it('应该正确处理分页', async () => {
      wrapper.vm.pagination.page = 2
      await wrapper.vm.loadLogs()
      
      expect(api.get).toHaveBeenCalledWith(
        '/statistics/match-logs',
        expect.objectContaining({
          params: expect.objectContaining({
            page: 2
          })
        })
      )
    })

    it('应该正确处理每页大小变化', async () => {
      wrapper.vm.pagination.page_size = 50
      await wrapper.vm.loadLogs()
      
      expect(api.get).toHaveBeenCalledWith(
        '/statistics/match-logs',
        expect.objectContaining({
          params: expect.objectContaining({
            page_size: 50
          })
        })
      )
    })
  })
})
