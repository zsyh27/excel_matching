/**
 * TypeScript 类型定义文件
 * 为菜单状态管理器提供类型支持
 */

import { MenuState } from '../config/menuStructure';

/**
 * 菜单状态管理器类
 */
export class MenuStateManager {
  /**
   * 保存菜单状态到 localStorage
   * @param state - 菜单状态
   */
  static saveState(state: MenuState): void;

  /**
   * 从 localStorage 加载菜单状态
   * @returns 菜单状态或 null（如果不存在或无效）
   */
  static loadState(): MenuState | null;

  /**
   * 获取默认菜单状态
   * @returns 默认菜单状态
   */
  static getDefaultState(): MenuState;

  /**
   * 清除保存的菜单状态
   */
  static clearState(): void;

  /**
   * 验证菜单状态对象是否有效
   * @param state - 待验证的状态对象
   * @returns 是否有效
   */
  static isValidState(state: any): state is MenuState;

  /**
   * 更新激活的菜单项
   * @param itemId - 菜单项ID
   * @returns 更新后的菜单状态
   */
  static updateActiveItem(itemId: string): MenuState;

  /**
   * 切换工作流阶段的展开状态
   * @param stageId - 工作流阶段ID
   * @returns 更新后的菜单状态
   */
  static toggleStage(stageId: string): MenuState;

  /**
   * 切换子菜单的展开状态
   * @param menuId - 菜单项ID
   * @returns 更新后的菜单状态
   */
  static toggleSubMenu(menuId: string): MenuState;

  /**
   * 检查工作流阶段是否已展开
   * @param stageId - 工作流阶段ID
   * @returns 是否已展开
   */
  static isStageExpanded(stageId: string): boolean;

  /**
   * 检查子菜单是否已展开
   * @param menuId - 菜单项ID
   * @returns 是否已展开
   */
  static isSubMenuExpanded(menuId: string): boolean;

  /**
   * 检查菜单项是否为激活状态
   * @param itemId - 菜单项ID
   * @returns 是否为激活状态
   */
  static isActive(itemId: string): boolean;
}

export default MenuStateManager;
