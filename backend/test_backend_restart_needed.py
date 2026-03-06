"""
测试后端是否需要重启才能使用新的配置
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.text_preprocessor import TextPreprocessor
import json

# 加载配置
with open('../data/static_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 创建预处理器
preprocessor = TextPreprocessor(config)

print("=" * 60)
print("测试配置是否已加载")
print("=" * 60)

print(f"\nmedium_keywords配置: {preprocessor.medium_keywords}")
print(f"min_feature_length: {preprocessor.min_feature_length}")
print(f"min_feature_length_chinese: {preprocessor.min_feature_length_chinese}")

# 测试"水"
test_text = "水"
result = preprocessor.preprocess(test_text, mode='device')

print(f"\n测试文本: {test_text}")
print(f"提取的特征: {result.features}")
print(f"质量评分: {preprocessor._calculate_feature_quality(test_text)}")

if result.features and '水' in result.features:
    print("\n✓ 配置已生效，'水'特征可以正常提取")
else:
    print("\n✗ 配置未生效，'水'特征被过滤")
    print("  需要重启后端服务才能使配置生效")
