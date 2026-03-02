import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { ElMessage } from 'element-plus'
import DeviceInputView from '../DeviceInputView.vue'
import * as deviceApi from '../../api/device'

// Mock Element Plus message
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

// Mock vue-router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn()
  })
}))

// Mock API
vi.mock('../../api/device', () => ({
  parseDeviceDescription: vi.fn(),
  createIntelligentDevice: vi.fn()
}))

describe('DeviceInputView - 简化集成测试', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    
    wrapper = mount(DeviceInputView, {
      global: {
        stubs: {
          'el-row': { template: '<div><slot /></div>' },
          'el-col': { template: '<div><slot /></div>' },
          'el-empty': { template: '<div>empty</div>' },
          'el-icon': { template: '<span><slot /></span>' },
          'el-dialog': { template: '<div v-if="modelValue"><slot /><slot name="footer" /></div>', props: ['modelValue'] },
          'el-button': { template: '<button @click="$emit(\'click\')"><slot /></button>' },
          DeviceInputForm: true,
          ParseResultDisplay: true
        }
      }
    })

    // 设置 mock inputFormRef
    wrapper.vm.inputFormRef = {
      setLoading: vi.fn(),
      resetForm: vi.fn(),
      getFormData: vi.fn(() => ({
        description: '测试设备',
        price: 1000
      }))
    }
  })

  describe('解析API集成', () => {
    it('应该成功调用解析API', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: {
            brand: '西门子',
            device_type: 'CO2传感器',
            model: 'QAA2061',
            key_params: {
              '量程': '0-2000ppm',
              '输出信号': '4-20mA'
            },
            confidence_score: 0.92,
            unrecognized_text: [],
            price: 1250.00
          }
        }
      }
      
      deviceApi.parseDeviceDescription.mockResolvedValue(mockResponse)

      const formData = {
        description: '西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA',
        price: 1250.00
      }
      
      await wrapper.vm.handleParse(formData)
      await flushPromises()

      expect(deviceApi.parseDeviceDescription).toHaveBeenCalledWith(formData)
      expect(wrapper.vm.parseResult).toBeTruthy()
      expect(wrapper.vm.parseResult.brand).toBe('西门子')
      expect(ElMessage.success).toHaveBeenCalledWith('解析完成')
    })

    it('应该处理解析错误', async () => {
      const mockError = {
        response: {
          data: {
            success: false,
            error_code: 'EMPTY_DESCRIPTION',
            message: '设备描述不能为空'
          }
        }
      }
      
      deviceApi.parseDeviceDescription.mockRejectedValue(mockError)

      await wrapper.vm.handleParse({ description: '', price: 1000 })
      await flushPromises()

      expect(ElMessage.warning).toHaveBeenCalledWith('设备描述不能为空')
    })
  })

  describe('设备创建API集成', () => {
    it('应该成功调用创建设备API', async () => {
      // 设置解析结果
      wrapper.vm.parseResult = {
        brand: '西门子',
        device_type: 'CO2传感器',
        model: 'QAA2061',
        key_params: {
          '量程': '0-2000ppm',
          '输出信号': '4-20mA'
        },
        confidence_score: 0.92,
        unrecognized_text: [],
        price: 1250.00,
        _rawDescription: '西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA'
      }

      const mockResponse = {
        data: {
          success: true,
          data: {
            id: 'ID_12345678',
            created_at: '2024-01-15T10:30:00Z'
          }
        }
      }
      
      deviceApi.createIntelligentDevice.mockResolvedValue(mockResponse)

      await wrapper.vm.handleConfirmSave()
      await flushPromises()

      expect(deviceApi.createIntelligentDevice).toHaveBeenCalled()
      expect(wrapper.vm.successDialogVisible).toBe(true)
      expect(wrapper.vm.createdDeviceId).toBe('ID_12345678')
    })

    it('应该处理创建设备错误', async () => {
      wrapper.vm.parseResult = {
        brand: '西门子',
        device_type: 'CO2传感器',
        model: 'QAA2061',
        key_params: {},
        confidence_score: 0.8,
        unrecognized_text: [],
        _rawDescription: '测试设备'
      }

      const mockError = {
        response: {
          data: {
            success: false,
            error_code: 'DB_ERROR',
            message: '数据库操作失败'
          }
        }
      }
      
      deviceApi.createIntelligentDevice.mockRejectedValue(mockError)

      await wrapper.vm.handleConfirmSave()
      await flushPromises()

      expect(ElMessage.error).toHaveBeenCalled()
      expect(wrapper.vm.successDialogVisible).toBe(false)
    })

    it('当没有解析结果时应该显示警告', async () => {
      wrapper.vm.parseResult = null

      await wrapper.vm.handleConfirmSave()

      expect(ElMessage.warning).toHaveBeenCalledWith('没有可保存的解析结果')
      expect(deviceApi.createIntelligentDevice).not.toHaveBeenCalled()
    })
  })

  describe('完整流程', () => {
    it('应该完成解析和保存的完整流程', async () => {
      // 步骤1: 解析
      const mockParseResponse = {
        data: {
          success: true,
          data: {
            brand: '霍尼韦尔',
            device_type: '温度传感器',
            model: 'T7350A1008',
            key_params: {
              '量程': '-40~120℃',
              '输出信号': '4-20mA'
            },
            confidence_score: 0.88,
            unrecognized_text: [],
            price: 850.00
          }
        }
      }
      
      deviceApi.parseDeviceDescription.mockResolvedValue(mockParseResponse)

      await wrapper.vm.handleParse({
        description: '霍尼韦尔 温度传感器 T7350A1008 量程-40~120℃ 输出4-20mA',
        price: 850.00
      })
      await flushPromises()

      expect(wrapper.vm.parseResult).toBeTruthy()
      expect(wrapper.vm.parseResult.brand).toBe('霍尼韦尔')

      // 步骤2: 保存
      const mockCreateResponse = {
        data: {
          success: true,
          data: {
            id: 'ID_87654321',
            created_at: '2024-01-15T11:00:00Z'
          }
        }
      }
      
      deviceApi.createIntelligentDevice.mockResolvedValue(mockCreateResponse)

      await wrapper.vm.handleConfirmSave()
      await flushPromises()

      expect(wrapper.vm.successDialogVisible).toBe(true)
      expect(wrapper.vm.createdDeviceId).toBe('ID_87654321')
    })
  })

  describe('用户体验', () => {
    it('应该在重置时清空状态', () => {
      wrapper.vm.parseResult = {
        brand: '西门子',
        device_type: 'CO2传感器',
        model: 'QAA2061',
        key_params: {},
        confidence_score: 0.8,
        unrecognized_text: []
      }

      wrapper.vm.handleReset()

      expect(wrapper.vm.parseResult).toBeNull()
      expect(ElMessage.info).toHaveBeenCalledWith('表单已重置')
    })

    it('应该在保存失败时保持解析结果', async () => {
      wrapper.vm.parseResult = {
        brand: '西门子',
        device_type: 'CO2传感器',
        model: 'QAA2061',
        key_params: {},
        confidence_score: 0.8,
        unrecognized_text: [],
        _rawDescription: '测试'
      }

      const mockError = {
        response: {
          data: {
            success: false,
            message: '保存失败'
          }
        }
      }
      
      deviceApi.createIntelligentDevice.mockRejectedValue(mockError)

      await wrapper.vm.handleConfirmSave()
      await flushPromises()

      expect(wrapper.vm.parseResult).toBeTruthy()
      expect(wrapper.vm.parseResult.brand).toBe('西门子')
    })
  })
})
