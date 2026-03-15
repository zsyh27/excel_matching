/**
 * 配置菜单结构定义
 * 
 * 本文件定义了配置管理菜单的5个工作流阶段结构：
 * 1. 设备信息录入前配置 (Pre-entry Configuration)
 * 2. 数据导入阶段 (Data Import Stage)
 * 3. 预处理配置 (Preprocessing Configuration)
 * 4. 匹配配置阶段 (Matching Configuration)
 * 5. 全局配置 (Global Configuration)
 */

/**
 * @typedef {Object} SubMenuItem
 * @property {string} id - 子菜单项唯一标识符
 * @property {string} name - 子菜单项显示名称
 * @property {string} component - 对应的编辑器组件名称
 */

/**
 * @typedef {Object} MenuItem
 * @property {string} id - 菜单项唯一标识符
 * @property {string} name - 菜单项显示名称
 * @property {string} [component] - 对应的编辑器组件名称（如果没有子项）
 * @property {SubMenuItem[]} [subItems] - 子菜单项列表（如果有子项）
 */

/**
 * @typedef {Object} WorkflowStage
 * @property {string} id - 工作流阶段唯一标识符
 * @property {string} name - 工作流阶段显示名称（包含图标）
 * @property {string} icon - 工作流阶段图标
 * @property {MenuItem[]} items - 该阶段的菜单项列表
 */

/**
 * @typedef {Object} MenuState
 * @property {string} activeItemId - 当前激活的菜单项ID
 * @property {string[]} expandedStages - 已展开的工作流阶段ID列表
 * @property {string[]} expandedSubMenus - 已展开的子菜单ID列表
 */

/**
 * 菜单结构定义
 * @type {WorkflowStage[]}
 */
export const MENU_STRUCTURE = [
  {
    id: 'pre-entry',
    name: '设备信息录入前配置',
    icon: '📝',
    items: [
      {
        id: 'brand-keywords',
        name: '品牌关键词',
        component: 'BrandKeywordsEditor'
      },
      {
        id: 'device-params',
        name: '设备参数配置',
        component: 'DeviceParamsEditor'
      },
      {
        id: 'feature-weights',
        name: '特征权重',
        component: 'FeatureWeightEditor'
      }
    ]
  },
  {
    id: 'import',
    name: '数据导入阶段',
    icon: '📥',
    items: [
      {
        id: 'device-row',
        name: '设备行识别',
        component: 'DeviceRowRecognitionEditor'
      }
    ]
  },
  {
    id: 'intelligent-extraction',
    name: '智能特征提取',
    icon: '🧠',
    items: [
      {
        id: 'device-type-patterns',
        name: '设备类型模式',
        component: 'DeviceTypePatternsEditor'
      },
      {
        id: 'parameter-patterns',
        name: '参数提取正则模式',
        component: 'ParameterPatternsEditor'
      },
      {
        id: 'auxiliary-info',
        name: '辅助信息模式',
        component: 'AuxiliaryInfoEditor'
      },
      {
        id: 'synonym-map',
        name: '同义词映射',
        component: 'SynonymMapEditor'
      }
    ]
  },
  {
    id: 'global',
    name: '全局配置',
    icon: '⚙️',
    items: [
      {
        id: 'global-settings',
        name: '全局配置',
        component: 'GlobalConfigEditor'
      },
      {
        id: 'match-weights',
        name: '匹配权重配置',
        component: 'MatchWeightsEditor'
      }
    ]
  }
];

/**
 * 获取默认菜单状态
 * @returns {MenuState}
 */
export function getDefaultMenuState() {
  return {
    activeItemId: 'brand-keywords', // 默认选中第一个菜单项
    expandedStages: ['pre-entry'], // 默认展开第一个阶段
    expandedSubMenus: [] // 默认不展开子菜单
  };
}

/**
 * 根据菜单项ID查找菜单项
 * @param {string} itemId - 菜单项ID
 * @returns {{stage: WorkflowStage, item: MenuItem, subItem?: SubMenuItem} | null}
 */
export function findMenuItemById(itemId) {
  for (const stage of MENU_STRUCTURE) {
    for (const item of stage.items) {
      // 检查顶级菜单项
      if (item.id === itemId) {
        return { stage, item };
      }
      
      // 检查子菜单项
      if (item.subItems) {
        for (const subItem of item.subItems) {
          if (subItem.id === itemId) {
            return { stage, item, subItem };
          }
        }
      }
    }
  }
  
  return null;
}

/**
 * 获取菜单项的组件名称
 * @param {string} itemId - 菜单项ID
 * @returns {string | null}
 */
export function getComponentNameById(itemId) {
  const result = findMenuItemById(itemId);
  
  if (!result) {
    return null;
  }
  
  // 如果是子菜单项，返回子菜单项的组件
  if (result.subItem) {
    return result.subItem.component;
  }
  
  // 如果是顶级菜单项，返回顶级菜单项的组件
  return result.item.component || null;
}

/**
 * 检查菜单项是否有子项
 * @param {string} itemId - 菜单项ID
 * @returns {boolean}
 */
export function hasSubItems(itemId) {
  const result = findMenuItemById(itemId);
  
  if (!result || result.subItem) {
    return false;
  }
  
  return !!(result.item.subItems && result.item.subItems.length > 0);
}

/**
 * 获取菜单项的父菜单ID（如果是子菜单项）
 * @param {string} itemId - 菜单项ID
 * @returns {string | null}
 */
export function getParentMenuId(itemId) {
  const result = findMenuItemById(itemId);
  
  if (!result || !result.subItem) {
    return null;
  }
  
  return result.item.id;
}

/**
 * 获取所有菜单项ID列表（包括子菜单项）
 * @returns {string[]}
 */
export function getAllMenuItemIds() {
  const ids = [];
  
  for (const stage of MENU_STRUCTURE) {
    for (const item of stage.items) {
      ids.push(item.id);
      
      if (item.subItems) {
        for (const subItem of item.subItems) {
          ids.push(subItem.id);
        }
      }
    }
  }
  
  return ids;
}
