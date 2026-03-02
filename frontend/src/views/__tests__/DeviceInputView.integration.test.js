import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
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

describe('DeviceInputView - 前后端集成测试', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    
    wrapper = mount(DeviceInputView, {
      global: {
        stubs: {
          'el-row': true,
          'el-col': true,
          'el-empty': true,
          'el-icon': true,
          'el-dialog': true,
          'el-button': true,
          DeviceInputForm: {
            template: '<div class="device-input-form-stub"></div>',
            methods: {
              setLoading: vi.fn(),
              resetForm: vi.fn(),
              getFormData: vi.fn(() => ({
                description: '西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA',
                price: 1250.00
              }))
            }
          },
          ParseResultDisplay: {
            template: '<div class="parse-result-display-stub"></div>'
          }
        }
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('解析API集成', () => {
    it('应该成功调用解析API并显示结果', async () => {
      // Mock API响应
      const mockParseResponse = {
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
      
      deviceApi.parseDeviceDescription.mockResolvedValue(mockParseResponse)

      // 触发解析
      const formData = {
        description: '西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA',
        price: 1250.00
      }
      
      await wrapper.vm.handleParse(formData)
      await flushPromises()

      // 验证API调用
      expect(deviceApi.parseDeviceDescription).toHaveBeenCalledWith(formData)
      expect(deviceApi.parseDeviceDescription).toHaveBeenCalledTimes(1)

      // 验证解析结果被设置（包含 _rawDescription 字段）
      expect(wrapper.vm.parseResult).toEqual({
        ...mockParseResponse.data.data,
        _rawDescription: formData.description
      })

      // 验证成功消息
      expect(ElMessage.success).toHaveBeenCalledWith('解析完成')
    })

    it('应该处理解析API错误 - 空描述', async () => {
      // Mock API错误响应
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

      // 触发解析
      const formData = {
        description: '',
        price: 1250.00
      }
      
      await wrapper.vm.handleParse(formData)
      await flushPromises()

      // 验证错误消息
      expect(ElMessage.warning).toHaveBeenCalledWith('设备描述不能为空')
    })

    it('应该处理解析API错误 - 无效价格', async () => {
      // Mock API错误响应
      const mockError = {
        response: {
          data: {
            success: false,
            error_code: 'INVALID_PRICE',
            message: '价格格式无效'
          }
        }
      }
      
      deviceApi.parseDeviceDescription.mockRejectedValue(mockError)

      // 触发解析
      const formData = {
        description: '测试设备',
        price: -100
      }
      
      await wrapper.vm.handleParse(formData)
      await flushPromises()

      // 验证错误消息
      expect(ElMessage.warning).toHaveBeenCalledWith('价格格式无效')
    })

    it('应该处理网络错误', async () => {
      // Mock网络错误
      const mockError = new Error('Network Error')
      deviceApi.parseDeviceDescription.mockRejectedValue(mockError)

      // 触发解析
      const formData = {
        description: '测试设备',
        price: 1000
      }
      
      await wrapper.vm.handleParse(formData)
      await flushPromises()

      // 验证错误消息
      expect(ElMessage.error).toHaveBeenCalledWith('网络错误，请检查连接')
    })

    it('应该在解析过程中显示加载状态', async () => {
      // 创建 mock setLoading 方法
      const mockSetLoading = vi.fn()
      wrapper.vm.inputFormRef = {
        setLoading: mockSetLoading,
        resetForm: vi.fn(),
        getFormData: vi.fn(() => ({
          description: '测试设备',
          price: 1000
        }))
      }

      // Mock API响应（延迟）
      deviceApi.parseDeviceDescription.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          data: {
            success: true,
            data: {
              brand: '西门子',
              device_type: 'CO2传感器',
              model: 'QAA2061',
              key_params: {},
              confidence_score: 0.8,
              unrecognized_text: []
            }
          }
        }), 100))
      )

      // 触发解析
      const formData = {
        description: '测试设备',
        price: 1000
      }
      
      const parsePromise = wrapper.vm.handleParse(formData)

      // 验证加载状态被设置
      expect(mockSetLoading).toHaveBeenCalledWith(true)

      // 等待解析完成
      await parsePromise
      await flushPromises()

      // 验证加载状态被清除
      expect(mockSetLoading).toHaveBeenCalledWith(false)
    })
  })

  describe('设备创建API集成', () => {
    beforeEach(() => {
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
    })

    it('应该成功调用创建设备API', async () => {
      // Mock API响应
      const mockCreateResponse = {
        data: {
          success: true,
          data: {
            id: 'ID_12345678',
            created_at: '2024-01-15T10:30:00Z'
          }
        }
      }
      
      deviceApi.createIntelligentDevice.mockResolvedValue(mockCreateResponse)

      // 触发保存
      await wrapper.vm.handleConfirmSave()
      await flushPromises()

      // 验证API调用
      expect(deviceApi.createIntelligentDevice).toHaveBeenCalledWith({
        raw_description: '西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA',
        brand: '西门子',
        device_type: 'CO2传感器',
        model: 'QAA2061',
        key_params: {
          '量程': '0-2000ppm',
          '输出信号': '4-20mA'
        },
        price: 1250.00,
        confidence_score: 0.92
      })

      // 验证成功对话框显示
      expect(wrapper.vm.successDialogVisible).toBe(true)
      expect(wrapper.vm.createdDeviceId).toBe('ID_12345678')
    })

    it('应该处理创建设备API错误', async () => {
      // Mock API错误响应
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

      // 触发保存
      await wrapper.vm.handleConfirmSave()
      await flushPromises()

      // 验证错误消息
      expect(ElMessage.error).toHaveBeenCalledWith('数据库操作失败')
      expect(wrapper.vm.successDialogVisible).toBe(false)
    })

    it('应该在保存过程中显示加载状态', async () => {
      // Mock API响应（延迟）
      deviceApi.createIntelligentDevice.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          data: {
            success: true,
            data: {
              id: 'ID_12345678',
              created_at: '2024-01-15T10:30:00Z'
            }
          }
        }), 100))
      )

      // 触发保存
      const savePromise = wrapper.vm.handleConfirmSave()

      // 验证加载状态
      expect(wrapper.vm.saving).toBe(true)

      // 等待保存完成
      await savePromise
      await flushPromises()

      // 验证加载状态被清除
      expect(wrapper.vm.saving).toBe(false)
    })

    it('当没有解析结果时应该显示警告', async () => {
      // 清空解析结果
      wrapper.vm.parseResult = null

      // 触发保存
      await wrapper.vm.handleConfirmSave()

      // 验证警告消息
      expect(ElMessage.warning).toHaveBeenCalledWith('没有可保存的解析结果')
      expect(deviceApi.createIntelligentDevice).not.toHaveBeenCalled()
    })
  })

  describe('完整流程集成测试', () => {
    it('应该完成从解析到保存的完整流程', async () => {
      // 创建 mock 方法
      const mockResetForm = vi.fn()
      wrapper.vm.inputFormRef = {
        setLoading: vi.fn(),
        resetForm: mockResetForm,
        getFormData: vi.fn(() => ({
          description: '霍尼韦尔 温度传感器 T7350A1008 量程-40~120℃ 输出4-20mA',
          price: 850.00
        }))
      }

      // Mock解析API响应
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
      
      // Mock创建API响应
      const mockCreateResponse = {
        data: {
          success: true,
          data: {
            id: 'ID_87654321',
            created_at: '2024-01-15T11:00:00Z'
          }
        }
      }
      
      deviceApi.parseDeviceDescription.mockResolvedValue(mockParseResponse)
      deviceApi.createIntelligentDevice.mockResolvedValue(mockCreateResponse)

      // 步骤1: 解析设备描述
      const formData = {
        description: '霍尼韦尔 温度传感器 T7350A1008 量程-40~120℃ 输出4-20mA',
        price: 850.00
      }
      
      await wrapper.vm.handleParse(formData)
      await flushPromises()

      // 验证解析成功
      expect(wrapper.vm.parseResult).toBeTruthy()
      expect(wrapper.vm.parseResult.brand).toBe('霍尼韦尔')
      expect(wrapper.vm.parseResult.device_type).toBe('温度传感器')

      // 步骤2: 保存设备
      await wrapper.vm.handleConfirmSave()
      await flushPromises()

      // 验证保存成功
      expect(wrapper.vm.successDialogVisible).toBe(true)
      expect(wrapper.vm.createdDeviceId).toBe('ID_87654321')

      // 步骤3: 继续录入（重置表单）
      wrapper.vm.handleContinueInput()

      // 验证状态被重置
      expect(wrapper.vm.successDialogVisible).toBe(false)
      expect(wrapper.vm.createdDeviceId).toBe('')
      expect(wrapper.vm.parseResult).toBeNull()
      expect(mockResetForm).toHaveBeenCalled()
    })

    it('应该支持编辑解析结果后保存', async () => {
      // Mock解析API响应
      const mockParseResponse = {
        data: {
          success: true,
          data: {
            brand: '西门子',
            device_type: 'CO2传感器',
            model: 'QAA2061',
            key_params: {
              '量程': '0-2000ppm'
            },
            confidence_score: 0.75,
            unrecognized_text: ['输出4-20mA'],
            price: 1250.00
          }
        }
      }
      
      deviceApi.parseDeviceDescription.mockResolvedValue(mockParseResponse)

      // 解析设备
      await wrapper.vm.handleParse({
        description: '西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA',
        price: 1250.00
      })
      await flushPromises()

      // 用户编辑解析结果
      const updatedResult = {
        ...wrapper.vm.parseResult,
        key_params: {
          '量程': '0-2000ppm',
          '输出信号': '4-20mA'  // 用户手动添加
        }
      }
      
      wrapper.vm.handleUpdateResult(updatedResult)

      // 验证解析结果被更新
      expect(wrapper.vm.parseResult.key_params['输出信号']).toBe('4-20mA')

      // Mock创建API响应
      const mockCreateResponse = {
        data: {
          success: true,
          data: {
            id: 'ID_99999999',
            created_at: '2024-01-15T12:00:00Z'
          }
        }
      }
      
      deviceApi.createIntelligentDevice.mockResolvedValue(mockCreateResponse)

      // 保存编辑后的结果
      await wrapper.vm.handleConfirmSave()
      await flushPromises()

      // 验证保存成功，包含编辑后的参数
      expect(deviceApi.createIntelligentDevice).toHaveBeenCalledWith(
        expect.objectContaining({
          key_params: {
            '量程': '0-2000ppm',
            '输出信号': '4-20mA'
          }
        })
      )
      expect(wrapper.vm.successDialogVisible).toBe(true)
    })

    it('应该支持重新解析功能', async () => {
      // 创建 mock 方法
      const mockGetFormData = vi.fn()
      wrapper.vm.inputFormRef = {
        setLoading: vi.fn(),
        resetForm: vi.fn(),
        getFormData: mockGetFormData
      }

      // Mock第一次解析
      const mockParseResponse1 = {
        data: {
          success: true,
          data: {
            brand: null,
            device_type: '传感器',
            model: null,
            key_params: {},
            confidence_score: 0.45,
            unrecognized_text: ['西门子', 'QAA2061'],
            price: 1250.00
          }
        }
      }
      
      deviceApi.parseDeviceDescription.mockResolvedValueOnce(mockParseResponse1)

      // 第一次解析
      await wrapper.vm.handleParse({
        description: '西门子 CO2传感器 QAA2061',
        price: 1250.00
      })
      await flushPromises()

      // 验证低置信度结果
      expect(wrapper.vm.parseResult.confidence_score).toBe(0.45)

      // Mock第二次解析（用户修改了描述）
      const mockParseResponse2 = {
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
      
      deviceApi.parseDeviceDescription.mockResolvedValueOnce(mockParseResponse2)

      // 设置 getFormData 返回新的表单数据
      mockGetFormData.mockReturnValue({
        description: '西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA',
        price: 1250.00
      })

      // 重新解析
      await wrapper.vm.handleReparse()
      await flushPromises()

      // 验证新的解析结果
      expect(wrapper.vm.parseResult.confidence_score).toBe(0.92)
      expect(wrapper.vm.parseResult.brand).toBe('西门子')
      expect(wrapper.vm.parseResult.model).toBe('QAA2061')
    })
  })

  describe('用户体验优化', () => {
    it('应该在解析失败时保持表单数据', async () => {
      // 创建 mock 方法
      const mockResetForm = vi.fn()
      wrapper.vm.inputFormRef = {
        setLoading: vi.fn(),
        resetForm: mockResetForm,
        getFormData: vi.fn(() => ({
          description: '测试设备',
          price: 1000
        }))
      }

      // Mock API错误
      const mockError = {
        response: {
          data: {
            success: false,
            error_code: 'PARSE_ERROR',
            message: '解析失败'
          }
        }
      }
      
      deviceApi.parseDeviceDescription.mockRejectedValue(mockError)

      // 触发解析
      const formData = {
        description: '测试设备',
        price: 1000
      }
      
      await wrapper.vm.handleParse(formData)
      await flushPromises()

      // 验证表单数据未被清空
      expect(mockResetForm).not.toHaveBeenCalled()
    })

    it('应该在保存失败时保持解析结果', async () => {
      // 设置解析结果
      wrapper.vm.parseResult = {
        brand: '西门子',
        device_type: 'CO2传感器',
        model: 'QAA2061',
        key_params: {},
        confidence_score: 0.8,
        unrecognized_text: []
      }

      // Mock API错误
      const mockError = {
        response: {
          data: {
            success: false,
            error_code: 'SAVE_ERROR',
            message: '保存失败'
          }
        }
      }
      
      deviceApi.createIntelligentDevice.mockRejectedValue(mockError)

      // 触发保存
      await wrapper.vm.handleConfirmSave()
      await flushPromises()

      // 验证解析结果未被清空
      expect(wrapper.vm.parseResult).toBeTruthy()
      expect(wrapper.vm.parseResult.brand).toBe('西门子')
    })

    it('应该在重置时清空所有状态', () => {
      // 设置一些状态
      wrapper.vm.parseResult = {
        brand: '西门子',
        device_type: 'CO2传感器',
        model: 'QAA2061',
        key_params: {},
        confidence_score: 0.8,
        unrecognized_text: []
      }

      // 触发重置
      wrapper.vm.handleReset()

      // 验证状态被清空
      expect(wrapper.vm.parseResult).toBeNull()
      expect(ElMessage.info).toHaveBeenCalledWith('表单已重置')
    })
  })
})
