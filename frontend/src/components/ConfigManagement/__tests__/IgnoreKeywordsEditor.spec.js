import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import IgnoreKeywordsEditor from '../IgnoreKeywordsEditor.vue'

describe('IgnoreKeywordsEditor', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(IgnoreKeywordsEditor, {
      props: {
        modelValue: ['施工要求', '验收', '图纸']
      }
    })
  })

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('h2').text()).toBe('删除无关关键词')
  })

  it('displays all keywords', () => {
    const tags = wrapper.findAll('.keyword-tag')
    expect(tags).toHaveLength(3)
    expect(tags[0].text()).toContain('施工要求')
    expect(tags[1].text()).toContain('验收')
    expect(tags[2].text()).toContain('图纸')
  })

  it('displays keyword count', () => {
    const stats = wrapper.find('.stats')
    expect(stats.text()).toContain('共 3 个关键词')
  })

  it('adds new keyword', async () => {
    const input = wrapper.find('input[type="text"]')
    const addButton = wrapper.find('.btn-primary')

    await input.setValue('新关键词')
    await addButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted[0][0]).toContain('新关键词')
    expect(emitted[0][0]).toHaveLength(4)
  })

  it('does not add empty keyword', async () => {
    const input = wrapper.find('input[type="text"]')
    const addButton = wrapper.find('.btn-primary')

    await input.setValue('   ')
    await addButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeFalsy()
  })

  it('does not add duplicate keyword', async () => {
    const input = wrapper.find('input[type="text"]')
    const addButton = wrapper.find('.btn-primary')

    await input.setValue('施工要求')
    await addButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeFalsy()
  })

  it('removes keyword', async () => {
    const deleteButtons = wrapper.findAll('.btn-remove')
    await deleteButtons[0].trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted[0][0]).toHaveLength(2)
    expect(emitted[0][0]).not.toContain('施工要求')
  })

  it('clears input after adding keyword', async () => {
    const input = wrapper.find('input[type="text"]')
    const addButton = wrapper.find('.btn-primary')

    await input.setValue('新关键词')
    await addButton.trigger('click')
    
    // After emitting, the component should clear the input
    // We need to wait for the next tick
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.newKeyword).toBe('')
  })

  it('handles empty initial value', () => {
    const emptyWrapper = mount(IgnoreKeywordsEditor, {
      props: {
        modelValue: []
      }
    })

    expect(emptyWrapper.find('.stats').text()).toContain('共 0 个关键词')
    expect(emptyWrapper.findAll('.keyword-tag')).toHaveLength(0)
  })
})
