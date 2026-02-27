import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import DeviceTypeEditor from '../DeviceTypeEditor.vue'

describe('DeviceTypeEditor', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(DeviceTypeEditor, {
      props: {
        modelValue: ['传感器', '控制器', 'DDC', '阀门', '执行器']
      }
    })
  })

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('h2').text()).toBe('设备类型关键词')
  })

  it('displays all device types', () => {
    const tags = wrapper.findAll('.keyword-tag')
    expect(tags).toHaveLength(5)
    expect(tags[0].text()).toContain('传感器')
    expect(tags[2].text()).toContain('DDC')
  })

  it('displays type count', () => {
    const stats = wrapper.find('.stats')
    expect(stats.text()).toContain('共 5 个设备类型')
  })

  it('adds new device type', async () => {
    const input = wrapper.find('input[type="text"]')
    const addButton = wrapper.find('.btn-primary')

    await input.setValue('变送器')
    await addButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted[0][0]).toContain('变送器')
    expect(emitted[0][0]).toHaveLength(6)
  })

  it('does not add empty device type', async () => {
    const input = wrapper.find('input[type="text"]')
    const addButton = wrapper.find('.btn-primary')

    await input.setValue('   ')
    await addButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeFalsy()
  })

  it('does not add duplicate device type', async () => {
    const input = wrapper.find('input[type="text"]')
    const addButton = wrapper.find('.btn-primary')

    await input.setValue('传感器')
    await addButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeFalsy()
  })

  it('removes device type', async () => {
    const deleteButtons = wrapper.findAll('.btn-remove')
    await deleteButtons[0].trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted[0][0]).toHaveLength(4)
    expect(emitted[0][0]).not.toContain('传感器')
  })

  it('uses orange theme for type tags', () => {
    const tag = wrapper.find('.keyword-tag')
    expect(tag.classes()).toContain('keyword-tag')
  })

  it('handles empty initial value', () => {
    const emptyWrapper = mount(DeviceTypeEditor, {
      props: {
        modelValue: []
      }
    })

    expect(emptyWrapper.find('.stats').text()).toContain('共 0 个设备类型')
    expect(emptyWrapper.findAll('.keyword-tag')).toHaveLength(0)
  })
})
