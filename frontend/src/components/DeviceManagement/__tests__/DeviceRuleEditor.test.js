import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage } from 'element-plus'
import DeviceRuleEditor from '../DeviceRuleEditor.vue'
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
    }
  }
})

// Mock API
vi.mock('../../../api/database', () => ({
  updateDeviceRule: vi.fn()
}))

describe('DeviceRuleEditor', () => {
  const mockRule = {
    rule_id: 'RULE_001',
    features: [
      { feature: '霍尼韦尔', weight: 3.0, type: 'brand' },
      { feature: '温度传感器', weight: 5.0, type: 'device_type' }
    ],
    match_threshold: 5.0,
    total_weight: 8.0
  }

  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    
    wrapper = mount(DeviceRuleEditor, {
      props: {
        modelValue: true,
        deviceId: 'DEV001',
        rule: mockRule
      },
      global: {
        stubs: {
          'el-dialog': true,
          'el-alert': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'el-input-number': true,
          'el-tag': true,
          'el-button': true,
          'el-table': true,
          'el-table-column': true,
          'el-input': true,
          'el-select': true,
          'el-option': true,
          'el-slider': true,
          'el-icon': true
        }
      }
    })
  })

  describe('表单初始化', () => {
    it('应该使用规则数据初始化表单', () => {
      expect(wrapper.vm.editForm.features).toHaveLength(2)
      expect(wrapper.vm.editForm.match_threshold).toBe(5.0)
    })

    it('当没有规则时应该初始化为空表单', async () => {
      const wrapperNoRule = mount(DeviceRuleEditor, {
        props: {
          modelValue: true,
          deviceId: 'DEV001',
          rule: null
        },
        global: {
          stubs: {
            'el-dialog': true,
            'el-alert': true,
            'el-button': true
          }
        }
      })

      expect(wrapperNoRule.vm.editForm.features).toHaveLength(0)
      expect(wrapperNoRule.vm.editForm.match_threshold).toBe(5.0)
    })
  })

  describe('总权重计算', () => {
    it('应该正确计算总权重', () => {
      expect(wrapper.vm.totalWeight).toBe('8.0')
    })

    it('添加特征后应该更新总权重', async () => {
      wrapper.vm.editForm.features.push({
        feature: '新特征',
        weight: 2.0,
        type: 'parameter'
      })
      
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.totalWeight).toBe('10.0')
    })
  })

  describe('特征管理', () => {
    it('应该能够添加新特征', async () => {
      const initialLength = wrapper.vm.editForm.features.length
      
      await wrapper.vm.handleAddFeature()
      
      expect(wrapper.vm.editForm.features).toHaveLength(initialLength + 1)
      expect(wrapper.vm.editForm.features[initialLength]).toEqual({
        feature: '',
        type: 'parameter',
        weight: 1.0
      })
    })

    it('应该能够删除特征', async () => {
      const initialLength = wrapper.vm.editForm.features.length
      
      await wrapper.vm.handleDeleteFeature(0)
      
      expect(wrapper.vm.editForm.features).toHaveLength(initialLength - 1)
    })
  })

  describe('匹配难度评估', () => {
    it('应该为低阈值比率返回success类型', () => {
      wrapper.vm.editForm.match_threshold = 2.0 // 2/8 = 0.25
      expect(wrapper.vm.getMatchDifficultyType()).toBe('success')
    })

    it('应该为中等阈值比率返回warning类型', () => {
      wrapper.vm.editForm.match_threshold = 3.5 // 3.5/8 = 0.4375
      expect(wrapper.vm.getMatchDifficultyType()).toBe('warning')
    })

    it('应该为高阈值比率返回danger类型', () => {
      wrapper.vm.editForm.match_threshold = 5.0 // 5/8 = 0.625
      expect(wrapper.vm.getMatchDifficultyType()).toBe('danger')
    })

    it('应该返回正确的匹配难度标签', () => {
      wrapper.vm.editForm.match_threshold = 2.0
      expect(wrapper.vm.getMatchDifficultyLabel()).toBe('容易')
      
      wrapper.vm.editForm.match_threshold = 3.5
      expect(wrapper.vm.getMatchDifficultyLabel()).toBe('中等')
      
      wrapper.vm.editForm.match_threshold = 5.0
      expect(wrapper.vm.getMatchDifficultyLabel()).toBe('困难')
    })

    it('应该返回正确的匹配建议', () => {
      wrapper.vm.editForm.match_threshold = 2.0
      expect(wrapper.vm.getMatchSuggestion()).toContain('阈值较低')
      
      wrapper.vm.editForm.match_threshold = 3.5
      expect(wrapper.vm.getMatchSuggestion()).toContain('阈值适中')
      
      wrapper.vm.editForm.match_threshold = 5.0
      expect(wrapper.vm.getMatchSuggestion()).toContain('阈值较高')
    })
  })

  describe('表单验证', () => {
    it('当没有特征时应该显示警告', async () => {
      wrapper.vm.editForm.features = []
      
      await wrapper.vm.handleSave()
      
      expect(ElMessage.warning).toHaveBeenCalledWith('请至少添加一个特征')
      expect(databaseApi.updateDeviceRule).not.toHaveBeenCalled()
    })

    it('当特征为空时应该显示警告', async () => {
      wrapper.vm.editForm.features = [
        { feature: '', weight: 1.0, type: 'brand' }
      ]
      
      await wrapper.vm.handleSave()
      
      expect(ElMessage.warning).toHaveBeenCalledWith('第 1 个特征不能为空')
      expect(databaseApi.updateDeviceRule).not.toHaveBeenCalled()
    })

    it('当特征类型未选择时应该显示警告', async () => {
      wrapper.vm.editForm.features = [
        { feature: '测试', weight: 1.0, type: '' }
      ]
      
      await wrapper.vm.handleSave()
      
      expect(ElMessage.warning).toHaveBeenCalledWith('第 1 个特征必须选择类型')
      expect(databaseApi.updateDeviceRule).not.toHaveBeenCalled()
    })
  })

  describe('保存规则', () => {
    it('应该调用API更新规则', async () => {
      const mockResponse = {
        data: {
          success: true,
          rule: mockRule
        }
      }
      databaseApi.updateDeviceRule.mockResolvedValue(mockResponse)
      
      await wrapper.vm.handleSave()
      
      expect(databaseApi.updateDeviceRule).toHaveBeenCalledWith(
        'DEV001',
        {
          features: wrapper.vm.editForm.features,
          match_threshold: wrapper.vm.editForm.match_threshold
        }
      )
    })

    it('保存成功后应该触发saved事件', async () => {
      const mockResponse = {
        data: {
          success: true,
          rule: mockRule
        }
      }
      databaseApi.updateDeviceRule.mockResolvedValue(mockResponse)
      
      await wrapper.vm.handleSave()
      
      expect(wrapper.emitted('saved')).toBeTruthy()
      expect(wrapper.emitted('saved')[0][0]).toEqual(mockRule)
    })

    it('保存失败时应该显示错误消息', async () => {
      const mockResponse = {
        data: {
          success: false,
          message: '保存失败'
        }
      }
      databaseApi.updateDeviceRule.mockResolvedValue(mockResponse)
      
      await wrapper.vm.handleSave()
      
      expect(ElMessage.error).toHaveBeenCalledWith('保存失败')
      expect(wrapper.emitted('saved')).toBeFalsy()
    })

    it('API调用失败时应该显示错误消息', async () => {
      databaseApi.updateDeviceRule.mockRejectedValue(new Error('Network error'))
      
      await wrapper.vm.handleSave()
      
      expect(ElMessage.error).toHaveBeenCalledWith('保存规则失败，请稍后重试')
      expect(wrapper.emitted('saved')).toBeFalsy()
    })
  })

  describe('对话框控制', () => {
    it('应该在关闭时更新modelValue', async () => {
      await wrapper.vm.handleClose()
      
      expect(wrapper.emitted('update:modelValue')).toBeTruthy()
      expect(wrapper.emitted('update:modelValue')[0][0]).toBe(false)
    })

    it('应该在modelValue变化时初始化表单', async () => {
      const newRule = {
        features: [{ feature: '新特征', weight: 2.0, type: 'brand' }],
        match_threshold: 6.0
      }
      
      await wrapper.setProps({ modelValue: false })
      await wrapper.setProps({ modelValue: true, rule: newRule })
      
      expect(wrapper.vm.editForm.features).toHaveLength(1)
      expect(wrapper.vm.editForm.match_threshold).toBe(6.0)
    })
  })
})
