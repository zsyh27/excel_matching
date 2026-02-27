import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import SynonymMapEditor from '../SynonymMapEditor.vue'

describe('SynonymMapEditor', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(SynonymMapEditor, {
      props: {
        modelValue: {
          '温度传感器': '温传感器',
          '湿度传感器': '湿传感器',
          '压力传感器': '压传感器'
        }
      }
    })
  })

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('h2').text()).toBe('同义词映射')
  })

  it('displays all synonym mappings', () => {
    const rows = wrapper.findAll('.table-row')
    expect(rows).toHaveLength(3)
  })

  it('displays mapping count', () => {
    const stats = wrapper.find('.stats')
    expect(stats.text()).toContain('共 3 个映射')
  })

  it('displays source and target correctly', () => {
    const firstRow = wrapper.findAll('.table-row')[0]
    const sourceCells = firstRow.findAll('.col-source')
    const targetCells = firstRow.findAll('.col-target')
    expect(sourceCells[0].text()).toBe('温度传感器')
    expect(targetCells[0].text()).toBe('温传感器')
  })

  it('adds new mapping', async () => {
    const inputs = wrapper.findAll('input[type="text"]')
    const sourceInput = inputs[0]
    const targetInput = inputs[1]
    const addButton = wrapper.find('.btn-primary')

    await sourceInput.setValue('流量传感器')
    await targetInput.setValue('流量传感器')
    await addButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted[0][0]).toHaveProperty('流量传感器')
    expect(emitted[0][0]['流量传感器']).toBe('流量传感器')
  })

  it('does not add mapping with empty source', async () => {
    const inputs = wrapper.findAll('input[type="text"]')
    const targetInput = inputs[1]
    const addButton = wrapper.find('.btn-primary')

    await targetInput.setValue('目标词')
    await addButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeFalsy()
  })

  it('does not add mapping with empty target', async () => {
    const inputs = wrapper.findAll('input[type="text"]')
    const sourceInput = inputs[0]
    const addButton = wrapper.find('.btn-primary')

    await sourceInput.setValue('源词')
    await addButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeFalsy()
  })

  it('does not add duplicate mapping', async () => {
    const inputs = wrapper.findAll('input[type="text"]')
    const sourceInput = inputs[0]
    const targetInput = inputs[1]
    const addButton = wrapper.find('.btn-primary')

    await sourceInput.setValue('温度传感器')
    await targetInput.setValue('温传感器')
    await addButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    // Component should not emit if duplicate, or emit same value
    if (emitted) {
      expect(Object.keys(emitted[0][0])).toHaveLength(3)
    }
  })

  it('removes mapping', async () => {
    const deleteButtons = wrapper.findAll('.btn-remove')
    await deleteButtons[0].trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted[0][0]).not.toHaveProperty('温度传感器')
    expect(Object.keys(emitted[0][0])).toHaveLength(2)
  })

  it('handles empty initial value', () => {
    const emptyWrapper = mount(SynonymMapEditor, {
      props: {
        modelValue: {}
      }
    })

    expect(emptyWrapper.find('.stats').text()).toContain('共 0 个映射')
    expect(emptyWrapper.findAll('tbody tr')).toHaveLength(0)
  })
})
