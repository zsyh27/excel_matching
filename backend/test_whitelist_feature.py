"""
测试白名单功能

测试场景：
1. 没有白名单时，低质量分数的特征被过滤
2. 添加到白名单后，即使质量分数低也不会被过滤
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
from modules.text_preprocessor import TextPreprocessor

print("=" * 80)
print("测试白名单功能")
print("=" * 80)

# 加载配置
with open('../data/static_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 创建预处理器
preprocessor = TextPreprocessor(config)

# 获取白名单配置
whitelist = config.get('intelligent_extraction', {}).get('feature_quality_scoring', {}).get('whitelist_features', [])
print(f"\n当前白名单: {whitelist}")

# 测试用例
test_cases = [
    ("水", "介质关键词，在白名单中"),
    ("气", "介质关键词，在白名单中"),
    ("阀", "设备类型关键词，在白名单中"),
    ("个", "常见词，不在白名单中，应该被过滤"),
]

print("\n" + "=" * 80)
print("测试结果")
print("=" * 80)

for feature, description in test_cases:
    quality_score = preprocessor._calculate_feature_quality(feature)
    min_score = config.get('intelligent_extraction', {}).get('feature_quality_scoring', {}).get('min_quality_score', 50)
    is_whitelisted = feature in whitelist
    
    # 模拟过滤逻辑
    would_be_filtered = quality_score < min_score and not is_whitelisted
    
    print(f"\n特征: {feature}")
    print(f"  描述: {description}")
    print(f"  质量评分: {quality_score}")
    print(f"  最小阈值: {min_score}")
    print(f"  在白名单中: {'是' if is_whitelisted else '否'}")
    print(f"  会被过滤: {'是' if would_be_filtered else '否'}")
    
    if is_whitelisted and quality_score < min_score:
        print(f"  ✓ 白名单保护生效：虽然质量评分({quality_score})低于阈值({min_score})，但因为在白名单中而不被过滤")
    elif not is_whitelisted and quality_score < min_score:
        print(f"  ✗ 不在白名单中，质量评分低于阈值，会被过滤")
    else:
        print(f"  ✓ 质量评分达到阈值，正常通过")

# 测试完整的预处理流程
print("\n" + "=" * 80)
print("测试完整的预处理流程")
print("=" * 80)

test_text = "水+气+阀+个"
result = preprocessor.preprocess(test_text, mode='device')

print(f"\n输入文本: {test_text}")
print(f"提取的特征: {result.features}")

expected_features = ['水', '气', '阀']  # "个"应该被过滤
actual_features = result.features

print(f"\n预期特征: {expected_features}")
print(f"实际特征: {actual_features}")

if set(expected_features) == set(actual_features):
    print("\n✓ 白名单功能正常工作")
else:
    print("\n✗ 白名单功能异常")
    missing = set(expected_features) - set(actual_features)
    extra = set(actual_features) - set(expected_features)
    if missing:
        print(f"  缺少的特征: {missing}")
    if extra:
        print(f"  多余的特征: {extra}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
