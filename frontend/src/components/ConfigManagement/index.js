// 配置管理编辑器组件导出

// 设备信息录入前配置
export { default as BrandKeywordsEditor } from './BrandKeywordsEditor.vue'
export { default as DeviceParamsEditor } from './DeviceParamsEditor.vue'
export { default as FeatureWeightEditor } from './FeatureWeightEditor.vue'

// 智能提取配置
export { default as DeviceTypePatternsEditor } from './DeviceTypePatternsEditor.vue'
export { default as ParameterExtractionEditor } from './ParameterExtractionEditor.vue'
export { default as AuxiliaryInfoEditor } from './AuxiliaryInfoEditor.vue'
export { default as SynonymMapEditor } from './SynonymMapEditor.vue'

// 数据导入阶段
export { default as DeviceRowRecognitionEditor } from './DeviceRowRecognitionEditor.vue'

// 预处理配置（待简化/合并）
export { default as MetadataRulesEditor } from './MetadataRulesEditor.vue'
export { default as NormalizationEditor } from './NormalizationEditor.vue'
export { default as SplitCharsEditor } from './SplitCharsEditor.vue'

// 全局配置
export { default as GlobalConfigEditor } from './GlobalConfigEditor.vue'

// 其他组件
export { default as ConfigInfoCard } from './ConfigInfoCard.vue'

// ============================================
// 以下组件已废弃 - 根据 requirements.md 第5.3节
// ============================================

// 废弃原因：智能提取自动处理，容易误删有用信息
// export { default as IgnoreKeywordsEditor } from './IgnoreKeywordsEditor.vue'

// 废弃原因：与智能拆分重复，智能提取器自动处理
// export { default as ComplexParamEditor } from './ComplexParamEditor.vue'

// 废弃原因：规则复杂难配置，智能提取器内置质量评估
// export { default as QualityScoreEditor } from './QualityScoreEditor.vue'

// 废弃原因：与质量评分耦合，智能提取器自动识别重要特征
// export { default as WhitelistEditor } from './WhitelistEditor.vue'

// 废弃原因：简单的关键词列表不够智能，由设备类型模式替代
// export { default as DeviceTypeEditor } from './DeviceTypeEditor.vue'

// 废弃原因：功能重复，移到全局配置
// export { default as IntelligentCleaningEditor } from './IntelligentCleaningEditor.vue'

// 废弃原因：可能导致信息丢失，参数提取器智能处理
// export { default as UnitRemovalEditor } from './UnitRemovalEditor.vue'

// 废弃原因：不需要单独页面，移到全局配置
// export { default as MatchThresholdEditor } from './MatchThresholdEditor.vue'

