import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import MenuItem from '../MenuItem.vue';

describe('MenuItem.vue', () => {
  // 测试数据
  const simpleItem = {
    id: 'test-item',
    name: '测试菜单项'
  };

  const itemWithSubItems = {
    id: 'parent-item',
    name: '父菜单项',
    subItems: [
      { id: 'sub-1', name: '子项1' },
      { id: 'sub-2', name: '子项2' }
    ]
  };

  describe('基本渲染', () => {
    it('应该渲染简单菜单项', () => {
      const wrapper = mount(MenuItem, {
        props: { item: simpleItem }
      });

      expect(wrapper.find('.item-name').text()).toBe('测试菜单项');
      expect(wrapper.find('.submenu-indicator').exists()).toBe(false);
    });

    it('应该渲染带子项的菜单项', () => {
      const wrapper = mount(MenuItem, {
        props: { item: itemWithSubItems }
      });

      expect(wrapper.find('.item-name').text()).toBe('父菜单项');
      expect(wrapper.find('.submenu-indicator').exists()).toBe(true);
      expect(wrapper.find('.has-subitems').exists()).toBe(true);
    });

    it('应该在展开时显示子菜单项', async () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: itemWithSubItems,
          isExpanded: true
        }
      });

      await wrapper.vm.$nextTick();
      
      const subItems = wrapper.findAll('.sub-menu-item');
      expect(subItems).toHaveLength(2);
      expect(subItems[0].text()).toBe('子项1');
      expect(subItems[1].text()).toBe('子项2');
    });

    it('应该在折叠时隐藏子菜单项', () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: itemWithSubItems,
          isExpanded: false
        }
      });

      // 当折叠时，子菜单项不应该存在于 DOM 中
      expect(wrapper.find('.sub-items').exists()).toBe(false);
    });
  });

  describe('活动状态视觉指示 (Requirement 7.1)', () => {
    it('应该高亮显示活动的简单菜单项', () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: simpleItem,
          activeItemId: 'test-item'
        }
      });

      expect(wrapper.find('.menu-item').classes()).toContain('active');
    });

    it('应该高亮显示活动的子菜单项', async () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: itemWithSubItems,
          activeItemId: 'sub-1',
          isExpanded: true
        }
      });

      await wrapper.vm.$nextTick();

      const subItems = wrapper.findAll('.sub-menu-item');
      expect(subItems[0].classes()).toContain('active');
      expect(subItems[1].classes()).not.toContain('active');
    });

    it('应该高亮显示活动子项的父菜单', () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: itemWithSubItems,
          activeItemId: 'sub-1'
        }
      });

      expect(wrapper.find('.menu-item').classes()).toContain('parent-active');
    });

    it('不应该高亮非活动菜单项', () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: simpleItem,
          activeItemId: 'other-item'
        }
      });

      expect(wrapper.find('.menu-item').classes()).not.toContain('active');
    });
  });

  describe('点击行为 (Requirement 2.2, 2.3)', () => {
    it('点击简单菜单项应该触发 item-click 事件', async () => {
      const wrapper = mount(MenuItem, {
        props: { item: simpleItem }
      });

      await wrapper.find('.menu-item').trigger('click');

      expect(wrapper.emitted('item-click')).toBeTruthy();
      expect(wrapper.emitted('item-click')[0]).toEqual(['test-item']);
    });

    it('点击带子项的菜单项应该触发 toggle-expand 事件', async () => {
      const wrapper = mount(MenuItem, {
        props: { item: itemWithSubItems }
      });

      await wrapper.find('.menu-item').trigger('click');

      expect(wrapper.emitted('toggle-expand')).toBeTruthy();
      expect(wrapper.emitted('toggle-expand')[0]).toEqual(['parent-item']);
      expect(wrapper.emitted('item-click')).toBeFalsy();
    });

    it('点击子菜单项应该触发 subitem-click 事件', async () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: itemWithSubItems,
          isExpanded: true
        }
      });

      await wrapper.vm.$nextTick();
      await wrapper.findAll('.sub-menu-item')[0].trigger('click');

      expect(wrapper.emitted('subitem-click')).toBeTruthy();
      expect(wrapper.emitted('subitem-click')[0]).toEqual(['sub-1']);
    });

    it('点击子菜单项不应该触发父菜单的事件', async () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: itemWithSubItems,
          isExpanded: true
        }
      });

      await wrapper.vm.$nextTick();
      await wrapper.findAll('.sub-menu-item')[0].trigger('click');

      expect(wrapper.emitted('toggle-expand')).toBeFalsy();
    });
  });

  describe('父菜单自动展开逻辑 (Requirement 7.3)', () => {
    it('当子项被激活时应该自动展开父菜单', async () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: itemWithSubItems,
          activeItemId: null,
          isExpanded: false
        }
      });

      // 更新 activeItemId 为子项
      await wrapper.setProps({ activeItemId: 'sub-1' });

      expect(wrapper.emitted('toggle-expand')).toBeTruthy();
      expect(wrapper.emitted('toggle-expand')[0]).toEqual(['parent-item']);
    });

    it('当子项被激活且父菜单已展开时不应该重复触发展开', async () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: itemWithSubItems,
          activeItemId: null,
          isExpanded: true
        }
      });

      await wrapper.setProps({ activeItemId: 'sub-1' });

      expect(wrapper.emitted('toggle-expand')).toBeFalsy();
    });

    it('当非子项被激活时不应该展开父菜单', async () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: itemWithSubItems,
          activeItemId: null,
          isExpanded: false
        }
      });

      await wrapper.setProps({ activeItemId: 'other-item' });

      expect(wrapper.emitted('toggle-expand')).toBeFalsy();
    });

    it('初始化时如果子项已激活应该立即展开', () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: itemWithSubItems,
          activeItemId: 'sub-1',
          isExpanded: false
        }
      });

      expect(wrapper.emitted('toggle-expand')).toBeTruthy();
      expect(wrapper.emitted('toggle-expand')[0]).toEqual(['parent-item']);
    });
  });

  describe('展开指示器', () => {
    it('应该显示正确的展开指示器（折叠状态）', () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: itemWithSubItems,
          isExpanded: false
        }
      });

      expect(wrapper.find('.submenu-indicator').text()).toBe('▶');
    });

    it('应该显示正确的展开指示器（展开状态）', () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: itemWithSubItems,
          isExpanded: true
        }
      });

      expect(wrapper.find('.submenu-indicator').text()).toBe('▼');
    });
  });

  describe('边界情况', () => {
    it('应该处理空子项数组', () => {
      const itemWithEmptySubItems = {
        id: 'empty-parent',
        name: '空父项',
        subItems: []
      };

      const wrapper = mount(MenuItem, {
        props: { item: itemWithEmptySubItems }
      });

      expect(wrapper.find('.submenu-indicator').exists()).toBe(false);
      expect(wrapper.find('.has-subitems').exists()).toBe(false);
    });

    it('应该处理 null activeItemId', () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: simpleItem,
          activeItemId: null
        }
      });

      expect(wrapper.find('.menu-item').classes()).not.toContain('active');
    });

    it('应该处理 undefined activeItemId', () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: simpleItem,
          activeItemId: undefined
        }
      });

      expect(wrapper.find('.menu-item').classes()).not.toContain('active');
    });
  });

  describe('计算属性', () => {
    it('hasSubItems 应该正确判断是否有子项', () => {
      const wrapper1 = mount(MenuItem, {
        props: { item: simpleItem }
      });
      expect(wrapper1.vm.hasSubItems).toBeFalsy();

      const wrapper2 = mount(MenuItem, {
        props: { item: itemWithSubItems }
      });
      expect(wrapper2.vm.hasSubItems).toBeTruthy();
    });

    it('isActive 应该正确判断活动状态', () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: simpleItem,
          activeItemId: 'test-item'
        }
      });
      expect(wrapper.vm.isActive).toBe(true);
    });

    it('isParentOfActive 应该正确判断父菜单状态', () => {
      const wrapper = mount(MenuItem, {
        props: {
          item: itemWithSubItems,
          activeItemId: 'sub-1'
        }
      });
      expect(wrapper.vm.isParentOfActive).toBe(true);
    });
  });
});
