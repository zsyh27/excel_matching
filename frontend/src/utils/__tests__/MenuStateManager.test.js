/**
 * 菜单状态管理器测试
 * 验证菜单状态的保存、加载和管理功能
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { MenuStateManager } from '../MenuStateManager';

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

describe('MenuStateManager', () => {
  beforeEach(() => {
    // 清空 localStorage
    localStorage.clear();
    // 清除控制台警告/错误的 mock
    vi.clearAllMocks();
  });

  describe('saveState 和 loadState', () => {
    it('应该能保存和加载菜单状态', () => {
      const state = {
        activeItemId: 'brand-keywords',
        expandedStages: ['pre-entry'],
        expandedSubMenus: []
      };

      MenuStateManager.saveState(state);
      const loadedState = MenuStateManager.loadState();

      expect(loadedState).toEqual(state);
    });

    it('当 localStorage 为空时应该返回 null', () => {
      const loadedState = MenuStateManager.loadState();
      expect(loadedState).toBeNull();
    });

    it('当状态无效时应该返回 null 并清除状态', () => {
      // 保存无效的状态
      localStorage.setItem('config_menu_state', 'invalid json');
      
      const loadedState = MenuStateManager.loadState();
      expect(loadedState).toBeNull();
      
      // 验证状态已被清除
      expect(localStorage.getItem('config_menu_state')).toBeNull();
    });

    it('应该验证状态对象的结构', () => {
      // 缺少必需字段的状态
      const invalidState = {
        activeItemId: 'test'
        // 缺少 expandedStages 和 expandedSubMenus
      };

      localStorage.setItem('config_menu_state', JSON.stringify(invalidState));
      
      const loadedState = MenuStateManager.loadState();
      expect(loadedState).toBeNull();
    });
  });

  describe('getDefaultState', () => {
    it('应该返回有效的默认状态', () => {
      const defaultState = MenuStateManager.getDefaultState();

      expect(defaultState).toHaveProperty('activeItemId');
      expect(defaultState).toHaveProperty('expandedStages');
      expect(defaultState).toHaveProperty('expandedSubMenus');
      
      expect(typeof defaultState.activeItemId).toBe('string');
      expect(Array.isArray(defaultState.expandedStages)).toBe(true);
      expect(Array.isArray(defaultState.expandedSubMenus)).toBe(true);
    });
  });

  describe('clearState', () => {
    it('应该清除保存的菜单状态', () => {
      const state = {
        activeItemId: 'brand-keywords',
        expandedStages: ['pre-entry'],
        expandedSubMenus: []
      };

      MenuStateManager.saveState(state);
      expect(MenuStateManager.loadState()).not.toBeNull();

      MenuStateManager.clearState();
      expect(MenuStateManager.loadState()).toBeNull();
    });
  });

  describe('isValidState', () => {
    it('有效状态应该返回 true', () => {
      const validState = {
        activeItemId: 'test',
        expandedStages: ['stage1'],
        expandedSubMenus: ['menu1']
      };

      expect(MenuStateManager.isValidState(validState)).toBe(true);
    });

    it('null 应该返回 false', () => {
      expect(MenuStateManager.isValidState(null)).toBe(false);
    });

    it('非对象应该返回 false', () => {
      expect(MenuStateManager.isValidState('string')).toBe(false);
      expect(MenuStateManager.isValidState(123)).toBe(false);
      expect(MenuStateManager.isValidState([])).toBe(false);
    });

    it('缺少必需字段应该返回 false', () => {
      expect(MenuStateManager.isValidState({})).toBe(false);
      expect(MenuStateManager.isValidState({ activeItemId: 'test' })).toBe(false);
      expect(MenuStateManager.isValidState({ 
        activeItemId: 'test',
        expandedStages: []
      })).toBe(false);
    });

    it('字段类型错误应该返回 false', () => {
      expect(MenuStateManager.isValidState({
        activeItemId: 123, // 应该是 string
        expandedStages: [],
        expandedSubMenus: []
      })).toBe(false);

      expect(MenuStateManager.isValidState({
        activeItemId: 'test',
        expandedStages: 'not-array', // 应该是 array
        expandedSubMenus: []
      })).toBe(false);
    });
  });

  describe('updateActiveItem', () => {
    it('应该更新激活的菜单项', () => {
      const state = MenuStateManager.updateActiveItem('brand-keywords');
      
      expect(state.activeItemId).toBe('brand-keywords');
    });

    it('应该自动展开所属的工作流阶段', () => {
      const state = MenuStateManager.updateActiveItem('brand-keywords');
      
      expect(state.expandedStages).toContain('pre-entry');
    });

    it('应该自动展开父菜单（如果是子菜单项）', () => {
      const state = MenuStateManager.updateActiveItem('noise-filter');
      
      expect(state.expandedSubMenus).toContain('text-cleaning');
      expect(state.expandedStages).toContain('preprocessing');
    });

    it('应该保存更新后的状态', () => {
      MenuStateManager.updateActiveItem('brand-keywords');
      
      const loadedState = MenuStateManager.loadState();
      expect(loadedState.activeItemId).toBe('brand-keywords');
    });

    it('无效的菜单项ID应该返回当前状态', () => {
      // 先设置一个有效状态
      MenuStateManager.updateActiveItem('brand-keywords');
      
      // 尝试更新为无效ID
      const state = MenuStateManager.updateActiveItem('invalid-id');
      
      // 应该保持原状态
      expect(state.activeItemId).toBe('brand-keywords');
    });
  });

  describe('toggleStage', () => {
    it('应该展开未展开的阶段', () => {
      const state = MenuStateManager.toggleStage('preprocessing');
      
      expect(state.expandedStages).toContain('preprocessing');
    });

    it('应该折叠已展开的阶段', () => {
      // 先展开
      MenuStateManager.toggleStage('preprocessing');
      
      // 再折叠
      const state = MenuStateManager.toggleStage('preprocessing');
      
      expect(state.expandedStages).not.toContain('preprocessing');
    });

    it('应该保存更新后的状态', () => {
      MenuStateManager.toggleStage('preprocessing');
      
      const loadedState = MenuStateManager.loadState();
      expect(loadedState.expandedStages).toContain('preprocessing');
    });
  });

  describe('toggleSubMenu', () => {
    it('应该展开未展开的子菜单', () => {
      const state = MenuStateManager.toggleSubMenu('text-cleaning');
      
      expect(state.expandedSubMenus).toContain('text-cleaning');
    });

    it('应该折叠已展开的子菜单', () => {
      // 先展开
      MenuStateManager.toggleSubMenu('text-cleaning');
      
      // 再折叠
      const state = MenuStateManager.toggleSubMenu('text-cleaning');
      
      expect(state.expandedSubMenus).not.toContain('text-cleaning');
    });

    it('应该保存更新后的状态', () => {
      MenuStateManager.toggleSubMenu('text-cleaning');
      
      const loadedState = MenuStateManager.loadState();
      expect(loadedState.expandedSubMenus).toContain('text-cleaning');
    });
  });

  describe('isStageExpanded', () => {
    it('已展开的阶段应该返回 true', () => {
      MenuStateManager.toggleStage('preprocessing');
      
      expect(MenuStateManager.isStageExpanded('preprocessing')).toBe(true);
    });

    it('未展开的阶段应该返回 false', () => {
      expect(MenuStateManager.isStageExpanded('preprocessing')).toBe(false);
    });
  });

  describe('isSubMenuExpanded', () => {
    it('已展开的子菜单应该返回 true', () => {
      MenuStateManager.toggleSubMenu('text-cleaning');
      
      expect(MenuStateManager.isSubMenuExpanded('text-cleaning')).toBe(true);
    });

    it('未展开的子菜单应该返回 false', () => {
      expect(MenuStateManager.isSubMenuExpanded('text-cleaning')).toBe(false);
    });
  });

  describe('isActive', () => {
    it('激活的菜单项应该返回 true', () => {
      MenuStateManager.updateActiveItem('brand-keywords');
      
      expect(MenuStateManager.isActive('brand-keywords')).toBe(true);
    });

    it('未激活的菜单项应该返回 false', () => {
      MenuStateManager.updateActiveItem('brand-keywords');
      
      expect(MenuStateManager.isActive('device-params')).toBe(false);
    });
  });

  describe('状态持久化', () => {
    it('应该在多次操作后保持状态一致', () => {
      // 执行一系列操作
      MenuStateManager.updateActiveItem('noise-filter');
      MenuStateManager.toggleStage('matching');
      MenuStateManager.toggleSubMenu('feature-extraction');

      // 加载状态
      const state = MenuStateManager.loadState();

      // 验证所有操作都被保存
      expect(state.activeItemId).toBe('noise-filter');
      expect(state.expandedStages).toContain('preprocessing'); // 自动展开
      expect(state.expandedStages).toContain('matching'); // 手动展开
      expect(state.expandedSubMenus).toContain('text-cleaning'); // 自动展开
      expect(state.expandedSubMenus).toContain('feature-extraction'); // 手动展开
    });
  });
});
