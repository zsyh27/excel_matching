"""调试智能拆分功能"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.text_preprocessor import TextPreprocessor


config = {
    'normalization_map': {},
    'feature_split_chars': ['+'],
    'ignore_keywords': [],
    'global_config': {
        'fullwidth_to_halfwidth': True,
        'remove_whitespace': False,
        'unify_lowercase': True
    },
    'synonym_map': {},
    'brand_keywords': [],
    'device_type_keywords': [],
    'medium_keywords': [],
    'location_words': ['室内', '室外', '墙装', '吊装'],
    'intelligent_extraction': {
        'enabled': True,
        'text_cleaning': {'enabled': False},
        'feature_quality_scoring': {'enabled': False}
    },
    'intelligent_splitting': {
        'enabled': True,
        'split_compound_words': True,
        'split_technical_specs': True,
        'split_by_space': True
    },
    'unit_removal': {'enabled': False},
    'metadata_keywords': []
}

preprocessor = TextPreprocessor(config)

# 测试 _smart_split_feature 方法
print("测试 _smart_split_feature 方法:")
print(f"location_words配置: {preprocessor.config.get('location_words', [])}")

feature = "室内墙装"
print(f"\n输入特征: {feature}")
print(f"特征长度: {len(feature)}")

sub_features = preprocessor._smart_split_feature(feature)
print(f"拆分结果: {sub_features}")

# 测试完整的预处理流程
print("\n\n测试完整的预处理流程:")
result = preprocessor.preprocess("室内墙装", mode='matching')
print(f"原始文本: {result.original}")
print(f"清理后: {result.cleaned}")
print(f"归一化后: {result.normalized}")
print(f"特征列表: {result.features}")
