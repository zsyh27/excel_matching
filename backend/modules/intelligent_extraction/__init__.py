"""
智能特征提取和匹配系统

本模块实现了基于规则的智能设备特征提取和匹配功能，包括：
- 设备类型识别
- 技术参数提取
- 辅助信息提取
- 智能匹配和评分
"""

# 延迟导入，避免循环依赖
__all__ = [
    'ExtractionResult',
    'DeviceTypeInfo',
    'ParameterInfo',
    'RangeParam',
    'OutputParam',
    'AccuracyParam',
    'AuxiliaryInfo',
    'MatchResult',
    'CandidateDevice',
    'ScoreDetails',
    'DeviceTypeRecognizer',
    'ParameterExtractor',
    'AuxiliaryExtractor',
    'IntelligentMatcher',
    'RuleGenerator'
]
