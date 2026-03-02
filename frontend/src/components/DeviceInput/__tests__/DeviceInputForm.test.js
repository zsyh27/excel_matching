import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage } from 'element-plus'
import DeviceInputForm from '../DeviceInputForm.vue'

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

describe('DeviceInputForm', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(DeviceInputForm, {
      global: {
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-input': true,
          'el-button': true,
          'el-icon': true
        }
      }
    })
  })

  describe('表单验证规则', () => {
    it('应该定义设备描述为必填项', () => {
      const rules = wrapper.vm.rules.description
      expect(rules).toBeDefined()
      expect(rules[0].required).toBe(true)
      expect(rules[0].message).toBe('请输入设备描述')
    })

    it('应该定义设备描述最小长度为5个字符', () => {
      const rules = wrapper.vm.rules.description
      expect(rules[1].min).toBe(5)
      expect(rules[1].message).toBe('设备描述至少需要5个字符')
    })

    it('应该验证设备描述不能只包含空白字符', () => {
      const rules = wrapper.vm.rules.description
      const validator = rules[2].validator
      
      const callback = vi.fn()
      validator(null, '   ', callback)
      expect(callback).toHaveBeenCalledWith(expect.any(Error))
      
      callback.mockClear()
      validator(null, '有效内容', callback)
      expect(callback).toHaveBeenCalledWith()
    })

    it('应该定义价格必须是数字类型', () => {
      const rules = wrapper.vm.rules.price
      expect(rules[0].type).toBe('number')
      expect(rules[0].message).toBe('价格必须是数字')
    })

    it('应该验证价格不能为负数', () => {
      const rules = wrapper.vm.rules.price
      const validator = rules[1].validator
      
      const callback = vi.fn()
      validator(null, -100, callback)
      expect(callback).toHaveBeenCalledWith(expect.any(Error))
      
      callback.mockClear()
      validator(null, 100, callback)
      expect(callback).toHaveBeenCalledWith()
    })

    it('应该允许价格为null或undefined', () => {
      const rules = wrapper.vm.rules.price
      const validator = rules[1].validator
      
      const callback = vi.fn()
      validator(null, null, callback)
      expect(callback).toHaveBeenCalledWith()
      
      callback.mockClear()
      validator(null, undefined, callback)
      expect(callback).toHaveBeenCalledWith()
    })
  })

  describe('canParse计算属性', () => {
    it('当描述为空时应该返回false', async () => {
      wrapper.vm.formData.description = ''
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.canParse).toBeFalsy()
    })

    it('当描述少于5个字符时应该返回false', () => {
      wrapper.vm.formData.description = 'test'
      expect(wrapper.vm.canParse).toBe(false)
    })

    it('当描述只包含空白字符时应该返回false', () => {
      wrapper.vm.formData.description = '     '
      expect(wrapper.vm.canParse).toBe(false)
    })

    it('当描述有效时应该返回true', () => {
      wrapper.vm.formData.description = '西门子 CO2传感器'
      expect(wrapper.vm.canParse).toBe(true)
    })

    it('当loading为true时应该返回false', () => {
      wrapper.vm.formData.description = '西门子 CO2传感器'
      wrapper.vm.loading = true
      expect(wrapper.vm.canParse).toBe(false)
    })
  })

  describe('事件触发', () => {
    it('应该在手动填写时触发manual-fill事件', async () => {
      wrapper.vm.formData.description = '测试描述'
      wrapper.vm.formData.price = 100
      
      await wrapper.vm.handleManualFill()
      
      expect(wrapper.emitted('manual-fill')).toBeTruthy()
      expect(wrapper.emitted('manual-fill')[0][0]).toEqual({
        description: '测试描述',
        price: 100
      })
    })
  })

  describe('暴露的方法', () => {
    it('应该暴露setLoading方法', () => {
      expect(wrapper.vm.setLoading).toBeDefined()
      wrapper.vm.setLoading(true)
      expect(wrapper.vm.loading).toBe(true)
      
      wrapper.vm.setLoading(false)
      expect(wrapper.vm.loading).toBe(false)
    })

    it('应该暴露getFormData方法', () => {
      expect(wrapper.vm.getFormData).toBeDefined()
      wrapper.vm.formData.description = '测试设备'
      wrapper.vm.formData.price = 100
      
      const data = wrapper.vm.getFormData()
      expect(data).toEqual({
        description: '测试设备',
        price: 100
      })
    })

    it('getFormData应该去除描述文本的首尾空白', () => {
      wrapper.vm.formData.description = '  测试设备  '
      wrapper.vm.formData.price = 100
      
      const data = wrapper.vm.getFormData()
      expect(data.description).toBe('测试设备')
    })
  })

  describe('初始数据', () => {
    it('应该使用initialData prop初始化表单', async () => {
      const initialData = {
        description: '初始描述',
        price: 500
      }
      
      const wrapperWithData = mount(DeviceInputForm, {
        props: { initialData },
        global: {
          stubs: {
            'el-card': true,
            'el-form': true,
            'el-form-item': true,
            'el-input': true,
            'el-button': true,
            'el-icon': true
          }
        }
      })
      
      expect(wrapperWithData.vm.formData.description).toBe('初始描述')
      expect(wrapperWithData.vm.formData.price).toBe(500)
    })

    it('当没有提供initialData时应该使用默认值', () => {
      expect(wrapper.vm.formData.description).toBe('')
      expect(wrapper.vm.formData.price).toBe(null)
    })
  })
})
