import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ConfigManagementView from '../ConfigManagementView.vue'
import configApi from '../../api/config'

// Mock the API
vi.mock('../../api/config', () => ({
  default: {
    getConfig: vi.fn(),
    saveConfig: vi.fn(),
    testConfig: vi.fn(),
    getHistory: vi.fn(),
    rollback: vi.fn(),
    exportConfig: vi.fn(),
    importConfig: vi.fn()
  }
}))

// Mock alert and prompt
global.alert = vi.fn()
global.prompt = vi.fn()
global.confirm = vi.fn()

describe('ConfigManagementView', () => {
  let wrapper
  const mockConfig = {
    ignore_keywords: ['施工要求', '验收'],
    feature_split_chars: ['+', ';'],
    synonym_map: { '温度传感器': '温传感器' },
    normalization_map: { '℃': '' },
    global_config: {
      default_match_threshold: 3.0,
      unify_lowercase: true,
      remove_whitespace: true,
      fullwidth_to_halfwidth: true
    },
    brand_keywords: ['霍尼韦尔', '西门子'],
    device_type_keywords: ['传感器', '控制器']
  }

  beforeEach(async () => {
    vi.clearAllMocks()
    
    // Setup default mock responses
    configApi.getConfig.mockResolvedValue({
      data: {
        success: true,
        config: mockConfig
      }
    })
    
    configApi.getHistory.mockResolvedValue({
      data: {
        success: true,
        history: []
      }
    })

    wrapper = mount(ConfigManagementView, {
      global: {
        stubs: {
          IgnoreKeywordsEditor: true,
          SplitCharsEditor: true,
          SynonymMapEditor: true,
          NormalizationEditor: true,
          GlobalConfigEditor: true,
          BrandKeywordsEditor: true,
          DeviceTypeEditor: true
        }
      }
    })

    await flushPromises()
  })

  describe('Page Loading', () => {
    it('renders correctly', () => {
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('h1').text()).toBe('配置管理')
    })

    it('loads configuration on mount', () => {
      expect(configApi.getConfig).toHaveBeenCalled()
    })

    it('loads history on mount', () => {
      expect(configApi.getHistory).toHaveBeenCalled()
    })

    it('displays navigation menu', () => {
      const navItems = wrapper.findAll('.nav-item')
      expect(navItems.length).toBe(7)
    })

    it('displays action buttons', () => {
      expect(wrapper.find('.btn-primary').text()).toBe('保存')
      expect(wrapper.findAll('.btn-secondary').length).toBeGreaterThanOrEqual(3)
    })
  })

  describe('Navigation', () => {
    it('switches between config tabs', async () => {
      const navItems = wrapper.findAll('.nav-item')
      
      await navItems[1].trigger('click')
      await wrapper.vm.$nextTick()
      
      expect(navItems[1].classes()).toContain('active')
    })

    it('displays correct editor for active tab', async () => {
      expect(wrapper.vm.currentEditor).toBeTruthy()
    })
  })

  describe('Configuration Editing', () => {
    it('detects configuration changes', async () => {
      expect(wrapper.vm.hasChanges).toBe(false)
      
      // Simulate config change
      wrapper.vm.config.ignore_keywords = ['新关键词']
      wrapper.vm.handleConfigChange()
      
      expect(wrapper.vm.hasChanges).toBe(true)
    })

    it('enables save button when changes detected', async () => {
      wrapper.vm.hasChanges = true
      await wrapper.vm.$nextTick()
      
      const saveButton = wrapper.find('.btn-primary')
      expect(saveButton.attributes('disabled')).toBeUndefined()
    })
  })

  describe('Configuration Save', () => {
    it('saves configuration successfully', async () => {
      global.prompt.mockReturnValue('测试备注')
      configApi.saveConfig.mockResolvedValue({
        data: { success: true }
      })

      wrapper.vm.hasChanges = true
      await wrapper.vm.$nextTick()

      const saveButton = wrapper.find('.btn-primary')
      await saveButton.trigger('click')
      await flushPromises()

      expect(configApi.saveConfig).toHaveBeenCalledWith(
        expect.any(Object),
        '测试备注'
      )
      // 检查消息提示而不是alert
      expect(wrapper.vm.message.show).toBe(true)
      expect(wrapper.vm.message.text).toContain('配置保存成功')
      expect(wrapper.vm.message.type).toBe('success')
    })

    it('handles save cancellation', async () => {
      global.prompt.mockReturnValue(null)

      wrapper.vm.hasChanges = true
      await wrapper.vm.$nextTick()

      const saveButton = wrapper.find('.btn-primary')
      await saveButton.trigger('click')

      expect(configApi.saveConfig).not.toHaveBeenCalled()
    })

    it('handles save failure', async () => {
      global.prompt.mockReturnValue('测试')
      configApi.saveConfig.mockResolvedValue({
        data: {
          success: false,
          error_message: '验证失败'
        }
      })

      wrapper.vm.hasChanges = true
      await wrapper.vm.$nextTick()

      const saveButton = wrapper.find('.btn-primary')
      await saveButton.trigger('click')
      await flushPromises()

      // 检查消息提示而不是alert
      expect(wrapper.vm.message.show).toBe(true)
      expect(wrapper.vm.message.text).toContain('验证失败')
      expect(wrapper.vm.message.type).toBe('error')
    })
  })

  describe('Configuration Reset', () => {
    it('resets configuration with confirmation', async () => {
      global.confirm.mockReturnValue(true)

      wrapper.vm.config.ignore_keywords = ['修改后']
      wrapper.vm.hasChanges = true
      await wrapper.vm.$nextTick()

      const resetButton = wrapper.findAll('.btn-secondary')[0]
      await resetButton.trigger('click')
      await wrapper.vm.$nextTick()

      expect(wrapper.vm.config.ignore_keywords).toEqual(['测试1', '测试2'])
      expect(wrapper.vm.hasChanges).toBe(false)
    })

    it('cancels reset when user declines', async () => {
      global.confirm.mockReturnValue(false)

      const originalConfig = { ...wrapper.vm.config }
      wrapper.vm.config.ignore_keywords = ['修改后']

      const resetButton = wrapper.findAll('.btn-secondary')[0]
      await resetButton.trigger('click')

      expect(wrapper.vm.config.ignore_keywords).toEqual(['修改后'])
    })
  })

  describe('Real-time Preview', () => {
    it('displays preview input', () => {
      const previewInput = wrapper.find('.preview-input input')
      expect(previewInput.exists()).toBe(true)
    })

    it('calls test API when text is entered', async () => {
      configApi.testConfig.mockResolvedValue({
        data: {
          success: true,
          preprocessing: {
            original: '测试文本',
            cleaned: '测试文本',
            normalized: '测试文本',
            features: ['测试', '文本']
          },
          match_result: {
            match_status: 'success',
            device_text: '测试设备',
            score: 8.0
          }
        }
      })

      const input = wrapper.find('.preview-input input')
      await input.setValue('测试文本')
      
      // Wait for debounce (500ms)
      await new Promise(resolve => setTimeout(resolve, 600))
      await flushPromises()

      expect(configApi.testConfig).toHaveBeenCalled()
    })

    it('displays preview results', async () => {
      wrapper.vm.previewResult = {
        preprocessing: {
          original: '测试',
          cleaned: '测试',
          normalized: '测试',
          features: ['测试']
        },
        match_result: {
          match_status: 'success',
          device_text: '测试设备',
          score: 8.0
        }
      }
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.preview-result').exists()).toBe(true)
    })
  })

  describe('Version History', () => {
    it('opens history modal', async () => {
      const historyButton = wrapper.find('.sidebar-footer button')
      await historyButton.trigger('click')

      expect(wrapper.vm.showHistory).toBe(true)
      expect(wrapper.find('.modal').exists()).toBe(true)
    })

    it('closes history modal', async () => {
      wrapper.vm.showHistory = true
      await wrapper.vm.$nextTick()

      const modal = wrapper.find('.modal')
      await modal.trigger('click')

      expect(wrapper.vm.showHistory).toBe(false)
    })

    it('displays history list', async () => {
      wrapper.vm.history = [
        {
          version: 1,
          created_at: '2026-02-27T10:00:00',
          remark: '初始配置'
        }
      ]
      wrapper.vm.showHistory = true
      await wrapper.vm.$nextTick()

      const historyItems = wrapper.findAll('.history-item')
      expect(historyItems.length).toBe(1)
    })

    it('performs rollback', async () => {
      global.confirm.mockReturnValue(true)
      configApi.rollback.mockResolvedValue({
        data: { success: true }
      })

      wrapper.vm.history = [
        { version: 1, created_at: '2026-02-27T10:00:00', remark: '测试' }
      ]
      wrapper.vm.showHistory = true
      await wrapper.vm.$nextTick()

      const rollbackButton = wrapper.find('.history-item button')
      await rollbackButton.trigger('click')
      await flushPromises()

      expect(configApi.rollback).toHaveBeenCalledWith(1)
      // 检查消息提示而不是alert
      expect(wrapper.vm.message.show).toBe(true)
      expect(wrapper.vm.message.text).toContain('配置回滚成功')
      expect(wrapper.vm.message.type).toBe('success')
    })
  })

  describe('Import/Export', () => {
    it('exports configuration', async () => {
      const mockBlob = new Blob(['{}'], { type: 'application/json' })
      configApi.exportConfig.mockResolvedValue({
        data: mockBlob
      })

      // Mock URL.createObjectURL
      global.URL.createObjectURL = vi.fn(() => 'blob:mock-url')
      
      const exportButton = wrapper.findAll('.btn-secondary')[1]
      await exportButton.trigger('click')
      await flushPromises()

      expect(configApi.exportConfig).toHaveBeenCalled()
    })

    it('opens file dialog for import', async () => {
      const importButton = wrapper.findAll('.btn-secondary')[2]
      await importButton.trigger('click')

      // File input should be triggered (can't fully test file selection)
      expect(wrapper.vm.fileInput).toBeTruthy()
    })
  })
})
