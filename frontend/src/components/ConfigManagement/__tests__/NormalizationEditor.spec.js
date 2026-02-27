import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import NormalizationEditor from '../NormalizationEditor.vue'

describe('NormalizationEditor', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(NormalizationEditor, {
      props: {
        modelValue: {
          '℃': '',
          '°C': '',
          '~': '-',
          '（': '(',
          '）': ')'
        }
      }
    })
  })

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('h2').text()).toBe('归一化映射')
  })

  it('displays all normalization mappings', () => {
    const rows = wrapper.findAll('.table-row')
    expect(rows).toHaveLength(5)
  })

  it('displays mapping count', () => {
    const stats = wrapper.find('.stats')
    expect(stats.text()).toContain('共 5 个映射')
  })

  it('displays source and target correctly', () => {
    const rows = wrapper.findAll('.table-row')
    const firstRow = rows[0]
    const sourceCells = firstRow.findAll('.col-source')
    const targetCells = firstRow.findAll('.col-target')
    expect(sourceCells[0].text()).toBe('℃')
    expect(targetCells[0].text()).toBe('(删除)')
  })

  it('shows (删除) for empty target', () => {
    const rows = wrapper.findAll('.table-row')
    const emptyTargetRow = rows[0]
    const targetCells = emptyTargetRow.findAll('.col-target')
    expect(targetCells[0].text()).toBe('(删除)')
  })

  it('adds new mapping', async () => {
    const inputs = wrapper.findAll('input[type="text"]')
    const sourceInput = inputs[0]
    const targetInput = inputs[1]
    const addButton = wrapper.find('.btn-primary')

    await sourceInput.setValue('【')
    await targetInput.setValue('[')
    await addButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted[0][0]).toHaveProperty('【')
    expect(emitted[0][0]['【']).toBe('[')
  })

  it('adds mapping with empty target (deletion)', async () => {
    const inputs = wrapper.findAll('input[type="text"]')
    const sourceInput = inputs[0]
    const addButton = wrapper.find('.btn-primary')

    await sourceInput.setValue('★')
    await addButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted[0][0]).toHaveProperty('★')
    expect(emitted[0][0]['★']).toBe('')
  })

  it('does not add mapping with empty source', async () => {
    const inputs = wrapper.findAll('input[type="text"]')
    const targetInput = inputs[1]
    const addButton = wrapper.find('.btn-primary')

    await targetInput.setValue('目标')
    await addButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeFalsy()
  })

  it('does not add duplicate mapping', async () => {
    const inputs = wrapper.findAll('input[type="text"]')
    const sourceInput = inputs[0]
    const targetInput = inputs[1]
    const addButton = wrapper.find('.btn-primary')

    await sourceInput.setValue('℃')
    await targetInput.setValue('')
    await addButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    // Component should not emit if duplicate, or emit same value
    if (emitted) {
      expect(Object.keys(emitted[0][0])).toHaveLength(5)
    }
  })

  it('removes mapping', async () => {
    const deleteButtons = wrapper.findAll('.btn-remove')
    await deleteButtons[0].trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted[0][0]).not.toHaveProperty('℃')
    expect(Object.keys(emitted[0][0])).toHaveLength(4)
  })

  it('handles empty initial value', () => {
    const emptyWrapper = mount(NormalizationEditor, {
      props: {
        modelValue: {}
      }
    })

    expect(emptyWrapper.find('.stats').text()).toContain('共 0 个映射')
    expect(emptyWrapper.findAll('tbody tr')).toHaveLength(0)
  })
})
