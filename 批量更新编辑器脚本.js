// 批量更新编辑器信息卡片脚本
// 此文件记录需要更新的编辑器列表和更新内容

const editorsToUpdate = [
  // 6. MetadataRulesEditor - 元数据处理
  {
    file: 'frontend/src/components/ConfigManagement/MetadataRulesEditor.vue',
    configId: 'metadata',
    hasInfoBox: true,
    replaceStart: '<div class="editor-header">',
    replaceEnd: '</div>\n\n    <el-alert'
  },
  
  // 7. NormalizationEditor - 归一化映射
  {
    file: 'frontend/src/components/ConfigManagement/NormalizationEditor.vue',
    configId: 'normalization',
    hasInfoBox: true,
    replaceStart: '<div class="editor-header">',
    replaceEnd: '</div>\n\n    <div class="editor-body">'
  },
  
  // 8. SplitCharsEditor - 处理分隔符
  {
    file: 'frontend/src/components/ConfigManagement/SplitCharsEditor.vue',
    configId: 'separator-process',
    hasInfoBox: false,
    replaceStart: '<div class="editor-header">',
    replaceEnd: '</div>\n\n    <!-- 智能拆分配置 -->'
  },
  
  // 9. ComplexParamEditor - 复杂参数分解
  {
    file: 'frontend/src/components/ConfigManagement/ComplexParamEditor.vue',
    configId: 'param-decompose',
    hasInfoBox: true,
    replaceStart: '<div class="editor-header">',
    replaceEnd: '</div>\n\n    <el-alert'
  },
  
  // 10. QualityScoreEditor - 质量评分
  {
    file: 'frontend/src/components/ConfigManagement/QualityScoreEditor.vue',
    configId: 'quality-score',
    hasInfoBox: false
  },
  
  // 11. WhitelistEditor - 白名单
  {
    file: 'frontend/src/components/ConfigManagement/WhitelistEditor.vue',
    configId: 'whitelist',
    hasInfoBox: true
  },
  
  // 12. SynonymMapEditor - 同义词映射
  {
    file: 'frontend/src/components/ConfigManagement/SynonymMapEditor.vue',
    configId: 'synonym-map',
    hasInfoBox: false
  },
  
  // 13. DeviceTypeEditor - 设备类型关键词
  {
    file: 'frontend/src/components/ConfigManagement/DeviceTypeEditor.vue',
    configId: 'device-type',
    hasInfoBox: false
  },
  
  // 14. IntelligentCleaningEditor - 智能拆分
  {
    file: 'frontend/src/components/ConfigManagement/IntelligentCleaningEditor.vue',
    configId: 'smart-split',
    hasInfoBox: false
  },
  
  // 15. UnitRemovalEditor - 单位删除
  {
    file: 'frontend/src/components/ConfigManagement/UnitRemovalEditor.vue',
    configId: 'unit-remove',
    hasInfoBox: false
  },
  
  // 16. MatchThresholdEditor - 匹配阈值
  {
    file: 'frontend/src/components/ConfigManagement/MatchThresholdEditor.vue',
    configId: 'match-threshold',
    hasInfoBox: false
  },
  
  // 17. GlobalConfigEditor - 全局配置
  {
    file: 'frontend/src/components/ConfigManagement/GlobalConfigEditor.vue',
    configId: 'global-settings',
    hasInfoBox: false
  }
];

// 更新步骤：
// 1. 导入 ConfigInfoCard 和 getConfigInfo
// 2. 注册组件
// 3. 获取配置信息
// 4. 在模板中添加 ConfigInfoCard
// 5. 删除旧的 info-box 样式（如果有）

console.log(`需要更新 ${editorsToUpdate.length} 个编辑器`);
