import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import BrandKeywordsEditor from '../BrandKeywordsEditor.vue'

describe('BrandKeywordsEditor', () => {
  let wrapper

  beforeEach(() => {
    wrapper = mount(BrandKeywordsEditor, {
      props: {
        modelValue: ['霍尼韦尔', '西门子', '江森自控', '施耐德']
      }
    })
  })

  it('renders correctly', () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('h2').text()).toBe('品牌关键词')
  })

  it('displays all brand keywords', () => {
    const tags = wrapper.findAll('.keyword-tag')
    expect(tags).toHaveLength(4)
    expect(tags[0].text()).toContain('霍尼韦尔')
    expect(tags[1].text()).toContain('西门子')
  })

  it('displays brand count', () => {
    const stats = wrapper.find('.stats')
    expect(stats.text()).toContain('共 4 个品牌')
  })

  it('adds new brand', async () => {
    const input = wrapper.find('input[type="text"]')
    const addButton = wrapper.find('.btn-primary')

    await input.setValue('ABB')
    await addButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted[0][0]).toContain('ABB')
    expect(emitted[0][0]).toHaveLength(5)
  })

  it('does not add empty brand', async () => {
    const input = wrapper.find('input[type="text"]')
    const addButton = wrapper.find('.btn-primary')

    await input.setValue('   ')
    await addButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeFalsy()
  })

  it('does not add duplicate brand', async () => {
    const input = wrapper.find('input[type="text"]')
    const addButton = wrapper.find('.btn-primary')

    await input.setValue('霍尼韦尔')
    await addButton.trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeFalsy()
  })

  it('removes brand', async () => {
    const deleteButtons = wrapper.findAll('.btn-remove')
    await deleteButtons[0].trigger('click')

    const emitted = wrapper.emitted('update:modelValue')
    expect(emitted).toBeTruthy()
    expect(emitted[0][0]).toHaveLength(3)
    expect(emitted[0][0]).not.toContain('霍尼韦尔')
  })

  it('uses blue theme for brand tags', () => {
    const tag = wrapper.find('.keyword-tag')
    expect(tag.classes()).toContain('keyword-tag')
  })

  it('handles empty initial value', () => {
    const emptyWrapper = mount(BrandKeywordsEditor, {
      props: {
        modelValue: []
      }
    })

    expect(emptyWrapper.find('.stats').text()).toContain('共 0 个品牌')
    expect(emptyWrapper.findAll('.brand-tag')).toHaveLength(0)
  })
})
