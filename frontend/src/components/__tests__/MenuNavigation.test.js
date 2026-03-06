/**
 * MenuNavigation 组件测试
 * 验证菜单导航组件的渲染和交互功能
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import MenuNavigation from '../MenuNavigation.vue';
import { MENU_STRUCTURE } from '../../config/menuStructure';
import MenuStateManager from '../../utils/MenuStateManager';

// Mock localStorage
const localStorageMock = (() => {
  let store = {};

  return {
    getItem: (key) => store[key] || null,
    setItem: (key, value) => {
      store[key] = value.toString();
    },
    removeItem: (key) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    }
  };
})();

global.localStorage = localStorageMock;

describe('MenuNavigation', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe('组件渲染', () => {
    it('应该渲染所有工作流阶段', () => {
      const wrapper = mount(MenuNavigation);
      
      const stages = wrapper.findAll('.workflow-stage');
      expect(stages).toHaveLength(MENU_STRUCTURE.length);
    });

    it('应该显示阶段图标和名称', () => {
      const wrapper = mount(MenuNavigation);
      
      const firstStage = wrapper.find('.stage-header');
      expect(firstStage.find('.stage-icon').text()).toBe(MENU_STRUCTURE[0].icon);
      expect(firstStage.find('.stage-name').text()).toBe(MENU_STRUCTURE[0].name);
    });

    it('应该渲染默认展开阶段的菜单项', () => {
      const wrapper = mount(MenuNavigation);
      
      // 默认展开第一个阶段
      const menuItems = wrapper.findAll('.menu-item');
      expect(menuItems.length).toBeGreaterThan(0);
    });

    it('应该高亮显示活动菜单项', () => {
      const wrapper = mount(MenuNavigation);
      
      // 默认第一个菜单项应该是活动的
      const activeItem = wrapper.find('.menu-item.active');
      expect(activeItem.exists()).toBe(true);
    });
  });

  describe('阶段展开/折叠', () => {
    it('点击阶段标题应该切换展开状态', async () => {
      const wrapper = mount(MenuNavigation);
      
      // 找到第二个阶段（默认未展开）
      const stages = wrapper.findAll('.stage-header');
      const secondStage = stages[1];
      
      // 点击展开
      await secondStage.trigger('click');
      
      // 验证展开状态
      expect(secondStage.classes()).toContain('expanded');
    });

    it('展开阶段应该显示菜单项', async () => {
      const wrapper = mount(MenuNavigation);
      
      const stages = wrapper.findAll('.stage-header');
      const secondStage = stages[1];
      
      // 点击展开
      await secondStage.trigger('click');
      await wrapper.vm.$nextTick();
      
      // 验证菜单项可见
      const stageItems = wrapper.findAll('.stage-items')[1];
      expect(stageItems.isVisible()).toBe(true);
    });

    it('再次点击应该折叠阶段', async () => {
      const wrapper = mount(MenuNavigation);
      
      const firstStage = wrapper.findAll('.stage-header')[0];
      
      // 第一次点击折叠（默认展开）
      await firstStage.trigger('click');
      expect(firstStage.classes()).not.toContain('expanded');
      
      // 第二次点击展开
      await firstStage.trigger('click');
      expect(firstStage.classes()).toContain('expanded');
    });
  });

  describe('菜单项点击行为', () => {
    it('点击无子项的菜单项应该触发选择事件', async () => {
      const wrapper = mount(MenuNavigation);
      
      // 找到无子项的菜单项（第一个阶段的第一个项）
      const menuItem = wrapper.find('.menu-item');
      
      await menuItem.trigger('click');
      
      // 验证事件被触发
      expect(wrapper.emitted('menu-item-selected')).toBeTruthy();
      expect(wrapper.emitted('menu-item-selected')[0]).toEqual(['brand-keywords']);
    });

    it('点击有子项的菜单项应该展开子菜单', async () => {
      const wrapper = mount(MenuNavigation);
      
      // 展开预处理阶段
      const stages = wrapper.findAll('.stage-header');
      await stages[2].trigger('click'); // preprocessing stage
      await wrapper.vm.$nextTick();
      
      // 找到有子项的菜单项（text-cleaning）
      const menuItems = wrapper.findAll('.menu-item');
      const textCleaningItem = menuItems.find(item => 
        item.text().includes('文本清理')
      );
      
      await textCleaningItem.trigger('click');
      await wrapper.vm.$nextTick();
      
      // 验证子菜单展开
      const subItems = wrapper.find('.sub-items');
      expect(subItems.exists()).toBe(true);
    });

    it('点击子菜单项应该触发选择事件', async () => {
      const wrapper = mount(MenuNavigation);
      
      // 展开预处理阶段
      const stages = wrapper.findAll('.stage-header');
      await stages[2].trigger('click');
      await wrapper.vm.$nextTick();
      
      // 展开文本清理子菜单
      const menuItems = wrapper.findAll('.menu-item');
      const textCleaningItem = menuItems.find(item => 
        item.text().includes('文本清理')
      );
      await textCleaningItem.trigger('click');
      await wrapper.vm.$nextTick();
      
      // 点击子菜单项
      const subItem = wrapper.find('.sub-menu-item');
      await subItem.trigger('click');
      
      // 验证事件被触发
      expect(wrapper.emitted('menu-item-selected')).toBeTruthy();
    });
  });

  describe('活动状态管理', () => {
    it('选择菜单项应该更新活动状态', async () => {
      const wrapper = mount(MenuNavigation);
      
      const menuItems = wrapper.findAll('.menu-item');
      const secondItem = menuItems[1];
      
      await secondItem.trigger('click');
      await wrapper.vm.$nextTick();
      
      // 验证新项被激活
      expect(secondItem.classes()).toContain('active');
    });

    it('只有一个菜单项应该处于活动状态', async () => {
      const wrapper = mount(MenuNavigation);
      
      const menuItems = wrapper.findAll('.menu-item');
      await menuItems[1].trigger('click');
      await wrapper.vm.$nextTick();
      
      // 验证只有一个活动项
      const activeItems = wrapper.findAll('.menu-item.active, .sub-item.active');
      expect(activeItems.length).toBe(1);
    });
  });

  describe('状态持久化', () => {
    it('应该从 MenuStateManager 加载初始状态', () => {
      // 设置保存的状态
      MenuStateManager.updateActiveItem('device-params');
      
      const wrapper = mount(MenuNavigation);
      
      // 验证状态被加载
      expect(wrapper.vm.menuState.activeItemId).toBe('device-params');
    });

    it('选择菜单项应该保存状态', async () => {
      const wrapper = mount(MenuNavigation);
      
      const menuItems = wrapper.findAll('.menu-item');
      await menuItems[1].trigger('click');
      
      // 验证状态被保存
      const savedState = MenuStateManager.loadState();
      expect(savedState.activeItemId).toBe('device-params');
    });
  });

  describe('外部 activeItemId prop', () => {
    it('应该接受外部传入的 activeItemId', () => {
      const wrapper = mount(MenuNavigation, {
        props: {
          activeItemId: 'feature-weights'
        }
      });
      
      expect(wrapper.vm.menuState.activeItemId).toBe('feature-weights');
    });

    it('activeItemId 变化时应该更新状态', async () => {
      const wrapper = mount(MenuNavigation, {
        props: {
          activeItemId: 'brand-keywords'
        }
      });
      
      await wrapper.setProps({ activeItemId: 'device-params' });
      await wrapper.vm.$nextTick();
      
      expect(wrapper.vm.menuState.activeItemId).toBe('device-params');
    });
  });

  describe('子菜单自动展开', () => {
    it('选择子菜单项应该自动展开父菜单', async () => {
      const wrapper = mount(MenuNavigation);
      
      // 直接选择子菜单项
      wrapper.vm.selectMenuItem('noise-filter');
      await wrapper.vm.$nextTick();
      
      // 验证父菜单和阶段都被展开
      expect(wrapper.vm.menuState.expandedSubMenus).toContain('text-cleaning');
      expect(wrapper.vm.menuState.expandedStages).toContain('preprocessing');
    });
  });

  describe('视觉指示器', () => {
    it('展开的阶段应该显示向下箭头', () => {
      const wrapper = mount(MenuNavigation);
      
      const firstStage = wrapper.find('.stage-header');
      const indicator = firstStage.find('.expand-indicator');
      
      expect(indicator.text()).toBe('▼');
    });

    it('折叠的阶段应该显示向右箭头', async () => {
      const wrapper = mount(MenuNavigation);
      
      const firstStage = wrapper.find('.stage-header');
      
      // 折叠阶段
      await firstStage.trigger('click');
      await wrapper.vm.$nextTick();
      
      const indicator = firstStage.find('.expand-indicator');
      expect(indicator.text()).toBe('▶');
    });

    it('有子项的菜单项应该显示子菜单指示器', async () => {
      const wrapper = mount(MenuNavigation);
      
      // 展开预处理阶段
      const stages = wrapper.findAll('.stage-header');
      await stages[2].trigger('click');
      await wrapper.vm.$nextTick();
      
      // 找到有子项的菜单项
      const menuItems = wrapper.findAll('.menu-item.has-subitems');
      expect(menuItems.length).toBeGreaterThan(0);
      
      const indicator = menuItems[0].find('.submenu-indicator');
      expect(indicator.exists()).toBe(true);
    });
  });
});
