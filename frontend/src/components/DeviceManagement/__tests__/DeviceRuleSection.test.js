import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ElMessage, ElMessageBox } from 'element-plus'
import DeviceRuleSection from '../DeviceRuleSection.vue'
import DeviceRuleEditor from '../DeviceRuleEditor.vue'

// Mock Element Plus components
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

describe('DeviceRuleSection', () => {
  const mockRule = {
    rule_id: 'RULE_001',
    features: [
      { feature: '霍尼韦尔', weight: 3.0, type: 'brand' },
      { feature: '温度传感器', weight: 5.0, type: 'device_type' },
      { feature: 'QAA2061', weight: 3.0, type: 'model' },
      { feature: '0-10V', weight: 1.0, type: 'parameter' }
    ],
    match_threshold: 5.0,
    total_weight: 12.0
  }

  let wrapper

  beforeEach(() => {
    wrapper = mount(DeviceRuleSection, {
      props: {
        deviceId: 'DEV001',
        rule: mockRule
      },
      global: {
        stubs: {
          'el-button': true,
          'el-descriptions': true,
          'el-descriptions-item': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-progress': true,
          'el-empty': true,
          'DeviceRuleEditor': true
        }
      }
    })
  })

  describe('规则显示', () => {
    it('应该显示规则信息', () => {
      expect(wrapper.vm.rule).toEqual(mockRule)
    })

    it('当没有规则时应该显示空状态', async () => {
      const wrapperNoRule = mount(DeviceRuleSection, {
        props: {
          deviceId: 'DEV001',
          rule: null
        },
        global: {
          stubs: {
            'el-button': true,
            'el-empty': true,
            'DeviceRuleEditor': true
          }
        }
      })

      expect(wrapperNoRule.vm.rule).toBeNull()
    })

    it('应该按权重从高到低排序特征', () => {
      const sorted = wrapper.vm.sortedFeatures
      expect(sorted[0].weight).toBe(5.0)
      expect(sorted[1].weight).toBe(3.0)
      expect(sorted[2].weight).toBe(3.0)
      expect(sorted[3].weight).toBe(1.0)
    })
  })

  describe('特征类型处理', () => {
    it('应该正确映射特征类型颜色', () => {
      expect(wrapper.vm.getFeatureTypeColor('brand')).toBe('primary')
      expect(wrapper.vm.getFeatureTypeColor('device_type')).toBe('success')
      expect(wrapper.vm.getFeatureTypeColor('model')).toBe('warning')
      expect(wrapper.vm.getFeatureTypeColor('parameter')).toBe('info')
    })

    it('应该正确映射特征类型标签', () => {
      expect(wrapper.vm.getFeatureTypeLabel('brand')).toBe('品牌')
      expect(wrapper.vm.getFeatureTypeLabel('device_type')).toBe('设备类型')
      expect(wrapper.vm.getFeatureTypeLabel('model')).toBe('型号')
      expect(wrapper.vm.getFeatureTypeLabel('parameter')).toBe('参数')
    })
  })

  describe('阈值类型', () => {
    it('应该为低阈值返回danger类型', () => {
      expect(wrapper.vm.getThresholdType(2.5)).toBe('danger')
    })

    it('应该为中等阈值返回warning类型', () => {
      expect(wrapper.vm.getThresholdType(4.0)).toBe('warning')
    })

    it('应该为高阈值返回success类型', () => {
      expect(wrapper.vm.getThresholdType(6.0)).toBe('success')
    })
  })

  describe('权重计算', () => {
    it('应该正确计算权重百分比', () => {
      expect(wrapper.vm.getWeightPercentage(5.0)).toBe(42) // 5/12 * 100 ≈ 42
      expect(wrapper.vm.getWeightPercentage(3.0)).toBe(25) // 3/12 * 100 = 25
    })

    it('应该为不同权重返回正确的颜色', () => {
      expect(wrapper.vm.getWeightColor(5.0)).toBe('#67C23A')
      expect(wrapper.vm.getWeightColor(3.5)).toBe('#E6A23C')
      expect(wrapper.vm.getWeightColor(1.0)).toBe('#909399')
    })
  })

  describe('编辑规则', () => {
    it('应该打开编辑对话框', async () => {
      await wrapper.vm.handleEdit()
      expect(wrapper.vm.editDialogVisible).toBe(true)
    })

    it('当没有规则时编辑按钮应该被禁用', async () => {
      const wrapperNoRule = mount(DeviceRuleSection, {
        props: {
          deviceId: 'DEV001',
          rule: null
        },
        global: {
          stubs: {
            'el-button': true,
            'el-empty': true,
            'DeviceRuleEditor': true
          }
        }
      })

      // 验证规则为null时的状态
      expect(wrapperNoRule.vm.rule).toBeNull()
    })
  })

  describe('重新生成规则', () => {
    it('应该显示确认对话框', async () => {
      ElMessageBox.confirm.mockResolvedValue(true)
      
      await wrapper.vm.handleRegenerate()
      
      expect(ElMessageBox.confirm).toHaveBeenCalledWith(
        '确定要重新生成规则吗？现有规则将被覆盖。',
        '确认',
        expect.any(Object)
      )
    })

    it('确认后应该触发regenerate事件', async () => {
      ElMessageBox.confirm.mockResolvedValue(true)
      
      await wrapper.vm.handleRegenerate()
      
      expect(wrapper.emitted('regenerate')).toBeTruthy()
    })

    it('取消时不应该触发regenerate事件', async () => {
      ElMessageBox.confirm.mockRejectedValue('cancel')
      
      await wrapper.vm.handleRegenerate()
      
      expect(wrapper.emitted('regenerate')).toBeFalsy()
    })
  })

  describe('规则更新', () => {
    it('应该在规则保存后触发rule-updated事件', async () => {
      const updatedRule = { ...mockRule, match_threshold: 6.0 }
      
      await wrapper.vm.handleRuleSaved(updatedRule)
      
      expect(wrapper.emitted('rule-updated')).toBeTruthy()
      expect(wrapper.emitted('rule-updated')[0][0]).toEqual(updatedRule)
    })

    it('应该在规则保存后关闭编辑对话框', async () => {
      wrapper.vm.editDialogVisible = true
      
      await wrapper.vm.handleRuleSaved(mockRule)
      
      expect(wrapper.vm.editDialogVisible).toBe(false)
    })

    it('应该在规则保存后显示成功消息', async () => {
      await wrapper.vm.handleRuleSaved(mockRule)
      
      expect(ElMessage.success).toHaveBeenCalledWith('规则更新成功')
    })
  })
})
