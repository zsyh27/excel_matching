import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ParseResultDisplay from '../ParseResultDisplay.vue'

describe('ParseResultDisplay', () => {
  let wrapper
  const mockParseResult = {
    brand: '西门子',
    device_type: 'CO2传感器',
    model: 'QAA2061',
    key_params: {
      '量程': '0-2000ppm',
      '输出信号': '4-20mA'
    },
    price: 1250.00,
    confidence_score: 0.92,
    unrecognized_text: []
  }

  beforeEach(() => {
    wrapper = mount(ParseResultDisplay, {
      props: {
        parseResult: mockParseResult
      }
    })
  })

  describe('基本信息显示', () => {
    it('应该正确接收品牌信息', () => {
      expect(wrapper.vm.parseResult.brand).toBe('西门子')
    })

    it('应该正确接收设备类型', () => {
      expect(wrapper.vm.parseResult.device_type).toBe('CO2传感器')
    })

    it('应该正确接收型号', () => {
      expect(wrapper.vm.parseResult.model).toBe('QAA2061')
    })

    it('应该显示价格', () => {
      expect(wrapper.vm.formattedPrice).toBe('1250.00')
      expect(wrapper.vm.showPrice).toBe(true)
    })

    it('当品牌为空时应该正确处理', async () => {
      await wrapper.setProps({
        parseResult: { ...mockParseResult, brand: null }
      })
      expect(wrapper.vm.parseResult.brand).toBeNull()
    })

    it('当设备类型为空时应该正确处理', async () => {
      await wrapper.setProps({
        parseResult: { ...mockParseResult, device_type: null }
      })
      expect(wrapper.vm.parseResult.device_type).toBeNull()
    })

    it('当型号为空时应该正确处理', async () => {
      await wrapper.setProps({
        parseResult: { ...mockParseResult, model: null }
      })
      expect(wrapper.vm.parseResult.model).toBeNull()
    })
  })

  describe('关键参数显示', () => {
    it('应该显示关键参数列表', () => {
      expect(wrapper.vm.hasKeyParams).toBe(true)
    })

    it('当没有关键参数时不应该显示关键参数区域', async () => {
      await wrapper.setProps({
        parseResult: { ...mockParseResult, key_params: {} }
      })
      expect(wrapper.vm.hasKeyParams).toBe(false)
    })

    it('当key_params为null时不应该显示关键参数区域', async () => {
      await wrapper.setProps({
        parseResult: { ...mockParseResult, key_params: null }
      })
      expect(wrapper.vm.hasKeyParams).toBeFalsy()
    })
  })

  describe('置信度评分显示', () => {
    it('应该正确计算置信度百分比', () => {
      expect(wrapper.vm.confidencePercentage).toBe('92')
    })

    it('高置信度(>=0.8)应该显示success类型', () => {
      expect(wrapper.vm.confidenceType).toBe('success')
      expect(wrapper.vm.confidenceAlertType).toBe('success')
      expect(wrapper.vm.confidenceMessage).toContain('置信度高')
    })

    it('中等置信度(0.6-0.8)应该显示warning类型', async () => {
      await wrapper.setProps({
        parseResult: { ...mockParseResult, confidence_score: 0.7 }
      })
      expect(wrapper.vm.confidenceType).toBe('warning')
      expect(wrapper.vm.confidenceAlertType).toBe('warning')
      expect(wrapper.vm.confidenceMessage).toContain('置信度中等')
    })

    it('低置信度(<0.6)应该显示danger/error类型', async () => {
      await wrapper.setProps({
        parseResult: { ...mockParseResult, confidence_score: 0.5 }
      })
      expect(wrapper.vm.confidenceType).toBe('danger')
      expect(wrapper.vm.confidenceAlertType).toBe('error')
      expect(wrapper.vm.confidenceMessage).toContain('置信度较低')
    })

    it('应该正确处理边界值0.8', async () => {
      await wrapper.setProps({
        parseResult: { ...mockParseResult, confidence_score: 0.8 }
      })
      expect(wrapper.vm.confidenceType).toBe('success')
    })

    it('应该正确处理边界值0.6', async () => {
      await wrapper.setProps({
        parseResult: { ...mockParseResult, confidence_score: 0.6 }
      })
      expect(wrapper.vm.confidenceType).toBe('warning')
    })
  })

  describe('未识别内容显示', () => {
    it('当有未识别内容时应该正确处理', async () => {
      await wrapper.setProps({
        parseResult: {
          ...mockParseResult,
          unrecognized_text: ['未知文本1', '未知文本2']
        }
      })
      expect(wrapper.vm.hasUnrecognizedText).toBe(true)
      expect(wrapper.vm.parseResult.unrecognized_text).toHaveLength(2)
    })

    it('当没有未识别内容时不应该显示未识别区域', () => {
      expect(wrapper.vm.hasUnrecognizedText).toBe(false)
    })

    it('当unrecognized_text为空数组时不应该显示', async () => {
      await wrapper.setProps({
        parseResult: { ...mockParseResult, unrecognized_text: [] }
      })
      expect(wrapper.vm.hasUnrecognizedText).toBe(false)
    })

    it('当unrecognized_text为null时不应该显示', async () => {
      await wrapper.setProps({
        parseResult: { ...mockParseResult, unrecognized_text: null }
      })
      expect(wrapper.vm.hasUnrecognizedText).toBeFalsy()
    })
  })

  describe('事件触发', () => {
    it('点击确认保存按钮应该触发confirm事件', async () => {
      await wrapper.vm.handleConfirm()
      expect(wrapper.emitted('confirm')).toBeTruthy()
      expect(wrapper.emitted('confirm')[0][0]).toEqual(mockParseResult)
    })

    it('点击编辑按钮应该触发edit事件', async () => {
      await wrapper.vm.handleEdit()
      expect(wrapper.emitted('edit')).toBeTruthy()
      expect(wrapper.emitted('edit')[0][0]).toEqual(mockParseResult)
    })

    it('点击重新解析按钮应该触发reparse事件', async () => {
      await wrapper.vm.handleReparse()
      expect(wrapper.emitted('reparse')).toBeTruthy()
    })
  })

  describe('加载状态', () => {
    it('当loading为true时按钮应该被禁用', async () => {
      await wrapper.setProps({ loading: true })
      expect(wrapper.vm.loading).toBe(true)
    })

    it('当loading为false时按钮应该可用', () => {
      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('Props验证', () => {
    it('应该要求parseResult prop', () => {
      const prop = wrapper.vm.$options.props.parseResult
      expect(prop.required).toBe(true)
      expect(prop.type).toBe(Object)
    })

    it('应该验证parseResult包含confidence_score', () => {
      const validator = wrapper.vm.$options.props.parseResult.validator
      expect(validator({ confidence_score: 0.8 })).toBe(true)
      expect(validator({})).toBe(false)
      expect(validator({ other: 'value' })).toBe(false)
    })

    it('loading prop应该有默认值false', () => {
      const prop = wrapper.vm.$options.props.loading
      expect(prop.default).toBe(false)
    })
  })

  describe('价格格式化', () => {
    it('应该正确格式化价格为两位小数', () => {
      expect(wrapper.vm.formattedPrice).toBe('1250.00')
    })

    it('当价格为null时应该返回0.00', async () => {
      await wrapper.setProps({
        parseResult: { ...mockParseResult, price: null }
      })
      expect(wrapper.vm.formattedPrice).toBe('0.00')
      expect(wrapper.vm.showPrice).toBe(false)
    })

    it('当价格为undefined时应该返回0.00', async () => {
      await wrapper.setProps({
        parseResult: { ...mockParseResult, price: undefined }
      })
      expect(wrapper.vm.formattedPrice).toBe('0.00')
      expect(wrapper.vm.showPrice).toBe(false)
    })

    it('应该正确格式化整数价格', async () => {
      await wrapper.setProps({
        parseResult: { ...mockParseResult, price: 100 }
      })
      expect(wrapper.vm.formattedPrice).toBe('100.00')
    })

    it('应该正确格式化带小数的价格', async () => {
      await wrapper.setProps({
        parseResult: { ...mockParseResult, price: 99.99 }
      })
      expect(wrapper.vm.formattedPrice).toBe('99.99')
    })
  })
})
