/**
 * 菜单结构测试
 * 验证菜单结构符合需求规范
 */

import { describe, it, expect } from 'vitest';
import {
  MENU_STRUCTURE,
  getDefaultMenuState,
  findMenuItemById,
  getComponentNameById,
  hasSubItems,
  getParentMenuId,
  getAllMenuItemIds
} from '../menuStructure';

describe('菜单结构定义', () => {
  describe('MENU_STRUCTURE 常量', () => {
    it('应该包含5个工作流阶段', () => {
      expect(MENU_STRUCTURE).toHaveLength(5);
    });

    it('应该按正确顺序包含所有阶段', () => {
      const stageIds = MENU_STRUCTURE.map(stage => stage.id);
      expect(stageIds).toEqual([
        'pre-entry',
        'import',
        'preprocessing',
        'matching',
        'global'
      ]);
    });

    it('每个阶段应该有正确的图标', () => {
      const icons = MENU_STRUCTURE.map(stage => stage.icon);
      expect(icons).toEqual(['📝', '📥', '🔍', '🎯', '⚙️']);
    });

    it('每个阶段应该有名称和菜单项', () => {
      MENU_STRUCTURE.forEach(stage => {
        expect(stage.id).toBeTruthy();
        expect(stage.name).toBeTruthy();
        expect(stage.icon).toBeTruthy();
        expect(Array.isArray(stage.items)).toBe(true);
        expect(stage.items.length).toBeGreaterThan(0);
      });
    });
  });

  describe('设备信息录入前配置阶段', () => {
    const preEntryStage = MENU_STRUCTURE[0];

    it('应该包含3个菜单项', () => {
      expect(preEntryStage.items).toHaveLength(3);
    });

    it('应该包含品牌关键词、设备参数配置和特征权重', () => {
      const itemIds = preEntryStage.items.map(item => item.id);
      expect(itemIds).toEqual([
        'brand-keywords',
        'device-params',
        'feature-weights'
      ]);
    });
  });

  describe('数据导入阶段', () => {
    const importStage = MENU_STRUCTURE[1];

    it('应该包含1个菜单项', () => {
      expect(importStage.items).toHaveLength(1);
    });

    it('应该包含设备行识别', () => {
      expect(importStage.items[0].id).toBe('device-row');
    });
  });

  describe('预处理配置阶段', () => {
    const preprocessingStage = MENU_STRUCTURE[2];

    it('应该包含4个菜单项', () => {
      expect(preprocessingStage.items).toHaveLength(4);
    });

    it('应该包含文本清理、归一化映射、特征提取和特征质量', () => {
      const itemIds = preprocessingStage.items.map(item => item.id);
      expect(itemIds).toEqual([
        'text-cleaning',
        'normalization',
        'feature-extraction',
        'feature-quality'
      ]);
    });

    it('文本清理应该有3个子项', () => {
      const textCleaning = preprocessingStage.items.find(
        item => item.id === 'text-cleaning'
      );
      expect(textCleaning.subItems).toHaveLength(3);
      
      const subItemIds = textCleaning.subItems.map(sub => sub.id);
      expect(subItemIds).toEqual([
        'noise-filter',
        'metadata',
        'separator-unify'
      ]);
    });

    it('特征提取应该有4个子项', () => {
      const featureExtraction = preprocessingStage.items.find(
        item => item.id === 'feature-extraction'
      );
      expect(featureExtraction.subItems).toHaveLength(4);
      
      const subItemIds = featureExtraction.subItems.map(sub => sub.id);
      expect(subItemIds).toEqual([
        'separator-process',
        'param-decompose',
        'smart-split',
        'unit-remove'
      ]);
    });

    it('特征质量应该有2个子项', () => {
      const featureQuality = preprocessingStage.items.find(
        item => item.id === 'feature-quality'
      );
      expect(featureQuality.subItems).toHaveLength(2);
      
      const subItemIds = featureQuality.subItems.map(sub => sub.id);
      expect(subItemIds).toEqual([
        'quality-score',
        'whitelist'
      ]);
    });

    it('归一化映射不应该有子项', () => {
      const normalization = preprocessingStage.items.find(
        item => item.id === 'normalization'
      );
      expect(normalization.subItems).toBeUndefined();
      expect(normalization.component).toBe('NormalizationEditor');
    });
  });

  describe('匹配配置阶段', () => {
    const matchingStage = MENU_STRUCTURE[3];

    it('应该包含3个菜单项', () => {
      expect(matchingStage.items).toHaveLength(3);
    });

    it('应该包含同义词映射、设备类型关键词和匹配阈值', () => {
      const itemIds = matchingStage.items.map(item => item.id);
      expect(itemIds).toEqual([
        'synonym-map',
        'device-type',
        'match-threshold'
      ]);
    });

    it('应该包含同义词映射（不是智能清理）', () => {
      const hasSynonymMap = matchingStage.items.some(
        item => item.id === 'synonym-map'
      );
      expect(hasSynonymMap).toBe(true);
    });
  });

  describe('全局配置阶段', () => {
    const globalStage = MENU_STRUCTURE[4];

    it('应该包含1个菜单项', () => {
      expect(globalStage.items).toHaveLength(1);
    });

    it('应该包含全局配置', () => {
      expect(globalStage.items[0].id).toBe('global-settings');
    });
  });

  describe('不应该包含的菜单项', () => {
    it('不应该包含"智能清理"菜单项', () => {
      const allItemIds = getAllMenuItemIds();
      expect(allItemIds).not.toContain('intelligent-cleaning');
    });

    it('不应该包含"技术术语扩展"菜单项', () => {
      const allItemIds = getAllMenuItemIds();
      expect(allItemIds).not.toContain('technical-term-expansion');
    });
  });
});

describe('getDefaultMenuState', () => {
  it('应该返回有效的默认状态', () => {
    const state = getDefaultMenuState();
    
    expect(state).toHaveProperty('activeItemId');
    expect(state).toHaveProperty('expandedStages');
    expect(state).toHaveProperty('expandedSubMenus');
    
    expect(typeof state.activeItemId).toBe('string');
    expect(Array.isArray(state.expandedStages)).toBe(true);
    expect(Array.isArray(state.expandedSubMenus)).toBe(true);
  });

  it('默认应该选中第一个菜单项', () => {
    const state = getDefaultMenuState();
    expect(state.activeItemId).toBe('brand-keywords');
  });

  it('默认应该展开第一个阶段', () => {
    const state = getDefaultMenuState();
    expect(state.expandedStages).toContain('pre-entry');
  });
});

describe('findMenuItemById', () => {
  it('应该能找到顶级菜单项', () => {
    const result = findMenuItemById('brand-keywords');
    
    expect(result).not.toBeNull();
    expect(result.stage.id).toBe('pre-entry');
    expect(result.item.id).toBe('brand-keywords');
    expect(result.subItem).toBeUndefined();
  });

  it('应该能找到子菜单项', () => {
    const result = findMenuItemById('noise-filter');
    
    expect(result).not.toBeNull();
    expect(result.stage.id).toBe('preprocessing');
    expect(result.item.id).toBe('text-cleaning');
    expect(result.subItem.id).toBe('noise-filter');
  });

  it('找不到菜单项时应该返回 null', () => {
    const result = findMenuItemById('non-existent-item');
    expect(result).toBeNull();
  });
});

describe('getComponentNameById', () => {
  it('应该返回顶级菜单项的组件名', () => {
    const componentName = getComponentNameById('brand-keywords');
    expect(componentName).toBe('BrandKeywordsEditor');
  });

  it('应该返回子菜单项的组件名', () => {
    const componentName = getComponentNameById('noise-filter');
    expect(componentName).toBe('NoiseFilterEditor');
  });

  it('找不到菜单项时应该返回 null', () => {
    const componentName = getComponentNameById('non-existent-item');
    expect(componentName).toBeNull();
  });
});

describe('hasSubItems', () => {
  it('有子项的菜单项应该返回 true', () => {
    expect(hasSubItems('text-cleaning')).toBe(true);
    expect(hasSubItems('feature-extraction')).toBe(true);
    expect(hasSubItems('feature-quality')).toBe(true);
  });

  it('没有子项的菜单项应该返回 false', () => {
    expect(hasSubItems('brand-keywords')).toBe(false);
    expect(hasSubItems('normalization')).toBe(false);
    expect(hasSubItems('synonym-map')).toBe(false);
  });

  it('子菜单项应该返回 false', () => {
    expect(hasSubItems('noise-filter')).toBe(false);
    expect(hasSubItems('separator-process')).toBe(false);
  });

  it('不存在的菜单项应该返回 false', () => {
    expect(hasSubItems('non-existent-item')).toBe(false);
  });
});

describe('getParentMenuId', () => {
  it('子菜单项应该返回父菜单ID', () => {
    expect(getParentMenuId('noise-filter')).toBe('text-cleaning');
    expect(getParentMenuId('separator-process')).toBe('feature-extraction');
    expect(getParentMenuId('quality-score')).toBe('feature-quality');
  });

  it('顶级菜单项应该返回 null', () => {
    expect(getParentMenuId('brand-keywords')).toBeNull();
    expect(getParentMenuId('text-cleaning')).toBeNull();
    expect(getParentMenuId('synonym-map')).toBeNull();
  });

  it('不存在的菜单项应该返回 null', () => {
    expect(getParentMenuId('non-existent-item')).toBeNull();
  });
});

describe('getAllMenuItemIds', () => {
  it('应该返回所有菜单项ID（包括子菜单项）', () => {
    const allIds = getAllMenuItemIds();
    
    // 验证包含顶级菜单项
    expect(allIds).toContain('brand-keywords');
    expect(allIds).toContain('text-cleaning');
    expect(allIds).toContain('synonym-map');
    
    // 验证包含子菜单项
    expect(allIds).toContain('noise-filter');
    expect(allIds).toContain('separator-process');
    expect(allIds).toContain('quality-score');
  });

  it('应该返回正确数量的菜单项', () => {
    const allIds = getAllMenuItemIds();
    
    // 计算预期数量：
    // Pre-entry: 3
    // Import: 1
    // Preprocessing: 4 + 3 (text-cleaning) + 4 (feature-extraction) + 2 (feature-quality) = 13
    // Matching: 3
    // Global: 1
    // Total: 21
    expect(allIds).toHaveLength(21);
  });

  it('所有ID应该是唯一的', () => {
    const allIds = getAllMenuItemIds();
    const uniqueIds = new Set(allIds);
    expect(uniqueIds.size).toBe(allIds.length);
  });
});
