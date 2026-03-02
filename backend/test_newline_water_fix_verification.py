"""
验证换行符和"水"特征提取问题的修复

修复内容：
1. 换行符已在归一化阶段被正确处理（remove_whitespace配置）
2. 添加了medium_keywords配置项，包含常见介质关键词
3. 修改了_in_device_keywords()方法，检查介质关键词
4. "水"现在获得+15分加分，质量评分从30提升到65，通过过滤
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.text_preprocessor import TextPreprocessor
import json

# 加载配置
with open('data/static_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 创建预处理器
preprocessor = TextPreprocessor(config)

print("=" * 80)
print("验证：换行符和'水'特征提取问题修复")
print("=" * 80)

# 测试用例
test_cases = [
    {
        'name': '原始问题案例',
        'text': """型号：V5011N1040/U
 通径：1/2"(DN15)
 阀体类型：二通座阀 
 适用介质：水""",
        'expected_features': ['v5011n1040/u', '1/2"', 'dn15', '二通座阀', '水']
    },
    {
        'name': '其他介质测试',
        'text': '适用介质：蒸汽',
        'expected_features': ['蒸汽']
    },
    {
        'name': '多个介质测试',
        'text': '适用介质：水+气+油',
        'expected_features': ['水', '气', '油']
    },
    {
        'name': '换行符测试',
        'text': '型号：ABC123\n通径：DN20\n介质：冷冻水',
        'expected_features': ['abc123', 'dn20', '冷冻水']
    }
]

all_passed = True

for i, test_case in enumerate(test_cases, 1):
    print(f"\n【测试用例 {i}】: {test_case['name']}")
    print("-" * 80)
    
    result = preprocessor.preprocess(test_case['text'], mode='matching')
    
    print(f"原始文本: {repr(test_case['text'])}")
    print(f"提取特征: {result.features}")
    print(f"期望特征: {test_case['expected_features']}")
    
    # 检查是否包含所有期望的特征
    missing_features = []
    for expected in test_case['expected_features']:
        if expected not in result.features:
            missing_features.append(expected)
    
    # 检查是否有换行符
    has_newline = any('\n' in f for f in result.features)
    
    if missing_features:
        print(f"❌ 失败: 缺少特征 {missing_features}")
        all_passed = False
    elif has_newline:
        print(f"❌ 失败: 特征中包含换行符")
        all_passed = False
    else:
        print(f"✓ 通过")

print("\n" + "=" * 80)
print(f"总体结果: {'✓ 所有测试通过' if all_passed else '❌ 部分测试失败'}")
print("=" * 80)

# 显示配置信息
print("\n【配置信息】")
print(f"介质关键词: {config.get('medium_keywords', [])}")
print(f"特征质量评分启用: {config.get('intelligent_extraction', {}).get('feature_quality_scoring', {}).get('enabled', False)}")
print(f"最小质量分数: {config.get('intelligent_extraction', {}).get('feature_quality_scoring', {}).get('min_quality_score', 50)}")

# 显示"水"的质量评分
print("\n【'水'的质量评分】")
water_score = preprocessor._calculate_feature_quality('水')
print(f"质量分数: {water_score}")
print(f"是否在设备关键词中: {preprocessor._in_device_keywords('水')}")
print(f"是否通过质量检查: {water_score >= 50}")

print("\n" + "=" * 80)
