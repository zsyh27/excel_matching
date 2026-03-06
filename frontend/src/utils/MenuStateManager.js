/**
 * 菜单状态管理器
 * 
 * 负责管理配置菜单的状态持久化，包括：
 * - 当前激活的菜单项
 * - 已展开的工作流阶段
 * - 已展开的子菜单
 */

import { getDefaultMenuState, findMenuItemById, getParentMenuId } from '../config/menuStructure';

const STORAGE_KEY = 'config_menu_state';

/**
 * 菜单状态管理器类
 */
export class MenuStateManager {
  /**
   * 保存菜单状态到 localStorage
   * @param {import('../config/menuStructure').MenuState} state - 菜单状态
   */
  static saveState(state) {
    try {
      const stateJson = JSON.stringify(state);
      localStorage.setItem(STORAGE_KEY, stateJson);
    } catch (error) {
      console.error('Failed to save menu state:', error);
    }
  }

  /**
   * 从 localStorage 加载菜单状态
   * @returns {import('../config/menuStructure').MenuState | null}
   */
  static loadState() {
    try {
      const stateJson = localStorage.getItem(STORAGE_KEY);
      
      if (!stateJson) {
        return null;
      }

      const state = JSON.parse(stateJson);
      
      // 验证状态对象的结构
      if (!this.isValidState(state)) {
        console.warn('Invalid menu state in localStorage, clearing...');
        this.clearState();
        return null;
      }

      return state;
    } catch (error) {
      console.error('Failed to load menu state:', error);
      this.clearState();
      return null;
    }
  }

  /**
   * 获取默认菜单状态
   * @returns {import('../config/menuStructure').MenuState}
   */
  static getDefaultState() {
    return getDefaultMenuState();
  }

  /**
   * 清除保存的菜单状态
   */
  static clearState() {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('Failed to clear menu state:', error);
    }
  }

  /**
   * 验证菜单状态对象是否有效
   * @param {any} state - 待验证的状态对象
   * @returns {boolean}
   */
  static isValidState(state) {
    if (!state || typeof state !== 'object') {
      return false;
    }

    // 检查必需的字段
    if (typeof state.activeItemId !== 'string') {
      return false;
    }

    if (!Array.isArray(state.expandedStages)) {
      return false;
    }

    if (!Array.isArray(state.expandedSubMenus)) {
      return false;
    }

    return true;
  }

  /**
   * 更新激活的菜单项
   * @param {string} itemId - 菜单项ID
   * @returns {import('../config/menuStructure').MenuState}
   */
  static updateActiveItem(itemId) {
    const currentState = this.loadState() || this.getDefaultState();
    
    // 验证菜单项是否存在
    const menuItem = findMenuItemById(itemId);
    if (!menuItem) {
      console.warn(`Menu item not found: ${itemId}`);
      return currentState;
    }

    // 更新激活项
    currentState.activeItemId = itemId;

    // 自动展开父菜单（如果是子菜单项）
    const parentId = getParentMenuId(itemId);
    if (parentId && !currentState.expandedSubMenus.includes(parentId)) {
      currentState.expandedSubMenus.push(parentId);
    }

    // 自动展开所属的工作流阶段
    const stageId = menuItem.stage.id;
    if (!currentState.expandedStages.includes(stageId)) {
      currentState.expandedStages.push(stageId);
    }

    this.saveState(currentState);
    return currentState;
  }

  /**
   * 切换工作流阶段的展开状态
   * @param {string} stageId - 工作流阶段ID
   * @returns {import('../config/menuStructure').MenuState}
   */
  static toggleStage(stageId) {
    const currentState = this.loadState() || this.getDefaultState();
    
    const index = currentState.expandedStages.indexOf(stageId);
    
    if (index === -1) {
      // 展开阶段
      currentState.expandedStages.push(stageId);
    } else {
      // 折叠阶段
      currentState.expandedStages.splice(index, 1);
    }

    this.saveState(currentState);
    return currentState;
  }

  /**
   * 切换子菜单的展开状态
   * @param {string} menuId - 菜单项ID
   * @returns {import('../config/menuStructure').MenuState}
   */
  static toggleSubMenu(menuId) {
    const currentState = this.loadState() || this.getDefaultState();
    
    const index = currentState.expandedSubMenus.indexOf(menuId);
    
    if (index === -1) {
      // 展开子菜单
      currentState.expandedSubMenus.push(menuId);
    } else {
      // 折叠子菜单
      currentState.expandedSubMenus.splice(index, 1);
    }

    this.saveState(currentState);
    return currentState;
  }

  /**
   * 检查工作流阶段是否已展开
   * @param {string} stageId - 工作流阶段ID
   * @returns {boolean}
   */
  static isStageExpanded(stageId) {
    const currentState = this.loadState() || this.getDefaultState();
    return currentState.expandedStages.includes(stageId);
  }

  /**
   * 检查子菜单是否已展开
   * @param {string} menuId - 菜单项ID
   * @returns {boolean}
   */
  static isSubMenuExpanded(menuId) {
    const currentState = this.loadState() || this.getDefaultState();
    return currentState.expandedSubMenus.includes(menuId);
  }

  /**
   * 检查菜单项是否为激活状态
   * @param {string} itemId - 菜单项ID
   * @returns {boolean}
   */
  static isActive(itemId) {
    const currentState = this.loadState() || this.getDefaultState();
    return currentState.activeItemId === itemId;
  }
}

export default MenuStateManager;
