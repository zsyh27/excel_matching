/**
 * TypeScript 类型定义文件
 * 为菜单结构提供类型支持
 */

/**
 * 子菜单项接口
 */
export interface SubMenuItem {
  /** 子菜单项唯一标识符 */
  id: string;
  /** 子菜单项显示名称 */
  name: string;
  /** 对应的编辑器组件名称 */
  component: string;
}

/**
 * 菜单项接口
 */
export interface MenuItem {
  /** 菜单项唯一标识符 */
  id: string;
  /** 菜单项显示名称 */
  name: string;
  /** 对应的编辑器组件名称（如果没有子项） */
  component?: string;
  /** 子菜单项列表（如果有子项） */
  subItems?: SubMenuItem[];
}

/**
 * 工作流阶段接口
 */
export interface WorkflowStage {
  /** 工作流阶段唯一标识符 */
  id: string;
  /** 工作流阶段显示名称 */
  name: string;
  /** 工作流阶段图标 */
  icon: string;
  /** 该阶段的菜单项列表 */
  items: MenuItem[];
}

/**
 * 菜单状态接口
 */
export interface MenuState {
  /** 当前激活的菜单项ID */
  activeItemId: string;
  /** 已展开的工作流阶段ID列表 */
  expandedStages: string[];
  /** 已展开的子菜单ID列表 */
  expandedSubMenus: string[];
}

/**
 * 菜单项查找结果接口
 */
export interface MenuItemFindResult {
  /** 所属的工作流阶段 */
  stage: WorkflowStage;
  /** 菜单项 */
  item: MenuItem;
  /** 子菜单项（如果是子菜单项） */
  subItem?: SubMenuItem;
}

/**
 * 菜单结构常量
 */
export const MENU_STRUCTURE: WorkflowStage[];

/**
 * 获取默认菜单状态
 */
export function getDefaultMenuState(): MenuState;

/**
 * 根据菜单项ID查找菜单项
 * @param itemId - 菜单项ID
 */
export function findMenuItemById(itemId: string): MenuItemFindResult | null;

/**
 * 获取菜单项的组件名称
 * @param itemId - 菜单项ID
 */
export function getComponentNameById(itemId: string): string | null;

/**
 * 检查菜单项是否有子项
 * @param itemId - 菜单项ID
 */
export function hasSubItems(itemId: string): boolean;

/**
 * 获取菜单项的父菜单ID（如果是子菜单项）
 * @param itemId - 菜单项ID
 */
export function getParentMenuId(itemId: string): string | null;

/**
 * 获取所有菜单项ID列表（包括子菜单项）
 */
export function getAllMenuItemIds(): string[];
