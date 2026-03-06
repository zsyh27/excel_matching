import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage } from 'element-plus'
import DeviceList from '../DeviceList.vue'
import * as databaseApi from '../../../api/database'

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

// Mock API
vi.mock('../../../api/database', () => ({
  getDevices: vi.fn(),
  deleteDevice: vi.fn(),
  batchGenerateRules: vi.fn()
}))

describe('DeviceList - 规则摘要功能', () => {
  const mockDevicesWithRules = [
    {
      device_id: 'DEV001',
      brand: '霍尼韦尔',
      device_name: '温度传感器',
      device_type: '传感器',
      spec_model: 'QAA2061',
      unit_price: 1200.00,
      rule_summary: {
        has_rule: true,
        feature_count: 5,
        match_threshold: 5.0,
        total_weight: 12.0
      }
    },
    {
      device_id: 'DEV002',
      brand: '西门子',
      device_name: '压力传感器',
      device_type: '传感器',
      spec_model: 'QBE2002',
      unit_price: 1500.00,
      rule_summary: {
        has_rule: false,
        feature_count: 0,
        match_threshold: 0,
        total_weight: 0
      }
    }
  ]

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    
    databaseApi.getDevices.mockResolvedValue({
      data: {
        success: true,
        devices: mockDevicesWithRules,
        total: 2
      }
    })

    wrapper = mount(DeviceList, {
      global: {
        stubs: {
          'el-row': true,
          'el-col': true,
          'el-input': true,
          'el-button': true,
          'el-select': true,
          'el-option': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-pagination': true,
          'el-icon': true
        }
      }
    })
  })

  describe('规则摘要显示', () => {
    it('应该在设备列表中显示规则摘要', async () => {
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.deviceList).toHaveLength(2)
      expect(wrapper.vm.deviceList[0].rule_summary.has_rule).toBe(true)
      expect(wrapper.vm.deviceList[1].rule_summary.has_rule).toBe(false)
    })

    it('应该显示有规则设备的特征数量', async () => {
      await wrapper.vm.$nextTick()
      
      const deviceWithRule = wrapper.vm.deviceList[0]
      expect(deviceWithRule.rule_summary.feature_count).toBe(5)
    })

    it('应该显示有规则设备的匹配阈值', async () => {
      await wrapper.vm.$nextTick()
      
      const deviceWithRule = wrapper.vm.deviceList[0]
      expect(deviceWithRule.rule_summary.match_threshold).toBe(5.0)
    })
  })

  describe('规则状态筛选', () => {
    it('应该支持按规则状态筛选', async () => {
      wrapper.vm.filters.has_rule = 'true'
      
      await wrapper.vm.handleSearch()
      
      expect(databaseApi.getDevices).toHaveBeenCalledWith(
        expect.objectContaining({
          has_rule: 'true'
        })
      )
    })

    it('应该在重置时清除规则状态筛选', async () => {
      wrapper.vm.filters.has_rule = 'true'
      
      await wrapper.vm.handleReset()
      
      expect(wrapper.vm.filters.has_rule).toBe('')
    })
  })

  describe('生成规则功能', () => {
    it('应该为无规则设备调用生成规则API', async () => {
      databaseApi.batchGenerateRules.mockResolvedValue({
        data: {
          success: true,
          message: '规则生成成功'
        }
      })

      const deviceWithoutRule = mockDevicesWithRules[1]
      await wrapper.vm.handleGenerateRule(deviceWithoutRule)
      
      expect(databaseApi.batchGenerateRules).toHaveBeenCalledWith({
        device_ids: ['DEV002'],
        force_regenerate: false
      })
    })

    it('生成规则成功后应该刷新列表', async () => {
      databaseApi.batchGenerateRules.mockResolvedValue({
        data: {
          success: true,
          message: '规则生成成功'
        }
      })

      const deviceWithoutRule = mockDevicesWithRules[1]
      await wrapper.vm.handleGenerateRule(deviceWithoutRule)
      
      expect(ElMessage.success).toHaveBeenCalledWith('规则生成成功')
      expect(databaseApi.getDevices).toHaveBeenCalledTimes(2) // 初始加载 + 刷新
    })

    it('生成规则失败时应该显示错误消息', async () => {
      databaseApi.batchGenerateRules.mockResolvedValue({
        data: {
          success: false,
          message: '生成失败'
        }
      })

      const deviceWithoutRule = mockDevicesWithRules[1]
      await wrapper.vm.handleGenerateRule(deviceWithoutRule)
      
      expect(ElMessage.error).toHaveBeenCalledWith('生成失败')
    })

    it('API调用失败时应该显示错误消息', async () => {
      databaseApi.batchGenerateRules.mockRejectedValue(new Error('Network error'))

      const deviceWithoutRule = mockDevicesWithRules[1]
      await wrapper.vm.handleGenerateRule(deviceWithoutRule)
      
      expect(ElMessage.error).toHaveBeenCalledWith('规则生成失败，请稍后重试')
    })
  })

  describe('设备列表加载', () => {
    it('应该在挂载时加载设备列表', async () => {
      expect(databaseApi.getDevices).toHaveBeenCalled()
    })

    it('应该传递所有筛选参数到API', async () => {
      wrapper.vm.searchKeyword = '温度'
      wrapper.vm.filters.brand = '霍尼韦尔'
      wrapper.vm.filters.device_type = '传感器'
      wrapper.vm.filters.has_rule = 'true'
      wrapper.vm.filters.minPrice = '1000'
      wrapper.vm.filters.maxPrice = '2000'
      
      await wrapper.vm.handleSearch()
      
      expect(databaseApi.getDevices).toHaveBeenCalledWith({
        page: 1,
        page_size: 20,
        name: '温度',
        brand: '霍尼韦尔',
        device_type: '传感器',
        has_rule: 'true',
        min_price: '1000',
        max_price: '2000'
      })
    })
  })

  describe('事件触发', () => {
    it('应该在查看设备时触发view事件', async () => {
      const device = mockDevicesWithRules[0]
      await wrapper.vm.handleView(device)
      
      expect(wrapper.emitted('view')).toBeTruthy()
      expect(wrapper.emitted('view')[0][0]).toEqual(device)
    })

    it('应该在编辑设备时触发edit事件', async () => {
      const device = mockDevicesWithRules[0]
      await wrapper.vm.handleEdit(device)
      
      expect(wrapper.emitted('edit')).toBeTruthy()
      expect(wrapper.emitted('edit')[0][0]).toEqual(device)
    })
  })

  describe('暴露的方法', () => {
    it('应该暴露refresh方法', () => {
      expect(wrapper.vm.refresh).toBeDefined()
    })

    it('refresh方法应该重新加载设备列表', async () => {
      vi.clearAllMocks()
      
      await wrapper.vm.refresh()
      
      expect(databaseApi.getDevices).toHaveBeenCalled()
    })
  })
})
