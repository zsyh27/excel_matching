"""
测试元数据前缀删除问题

验证"精度±5%"为什么没有被正确处理，以及修复后的效果
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from modules.text_preprocessor import TextPreprocessor
import json


def test_metadata_prefix_issue():
    """测试元数据前缀删除"""
    
    # 配置
    config = {
        'metadata_keywords': ['精度', '量程', '输出信号', '温度', '压力', '工作原理'],
        'intelligent_extraction': {
            'enabled': True,
            'text_cleaning': {
                'enabled': True,
                'truncate_delimiters': [],
                'noise_section_patterns': []
            },
            'metadata_label_patterns': [],
            'feature_quality_scoring': {
                'enabled': False  # 禁用质量评分，方便测试
            }
        },
        'feature_split_chars': ['+'],
        'normalization_map': {
            '~': '-',
            '±': ''
        },
        'ignore_keywords': [],
        'global_config': {
            'remove_whitespace': True,
            'min_feature_length': 1,
            'min_feature_length_chinese': 1
        },
        'synonym_map': {},
        'brand_keywords': [],
        'device_type_keywords': [],
        'location_words': [],
        'unit_removal': {
            'enabled': True,
            'units': ['ppm', 'ma', 'v', 'c', 'vdc']  # 不包含 '%'
        }
    }
    
    preprocessor = TextPreprocessor(config)
    
    print("=" * 80)
    print("测试1: 元数据标签删除（智能清理阶段 - 带冒号）")
    print("=" * 80)
    
    # 这个会被删除，因为有冒号
    test1 = "精度:±5%"
    print(f"\n输入: '{test1}'")
    result1 = preprocessor.remove_metadata_labels(test1)
    print(f"智能清理后: '{result1}'")
    print(f"期望: '±5%'")
    print(f"结果: {'✓' if result1 == '±5%' else '✗'}")
    
    print("\n" + "=" * 80)
    print("测试2: 元数据前缀删除（特征提取阶段 - 带冒号）")
    print("=" * 80)
    
    # 这个应该在特征提取阶段被删除
    test2 = "精度:±5%"
    print(f"\n输入: '{test2}'")
    result2 = preprocessor._remove_metadata_prefix(test2)
    print(f"删除前缀后: '{result2}'")
    print(f"期望: '±5%'")
    print(f"结果: {'✓' if result2 == '±5%' else '✗'}")
    
    print("\n" + "=" * 80)
    print("测试3: 智能拆分 - 删除元数据前缀（无冒号）")
    print("=" * 80)
    
    # 测试智能拆分是否能删除元数据前缀
    test3_cases = [
        ("精度±5%", ["5%"]),  # 删除"精度"前缀，归一化删除"±"，保留"%"
        ("量程0-250", ["0-250"]),
        ("输出信号4-20", ["4-20"]),
        ("温度25", ["25"]),
        ("压力100", ["100"])
    ]
    
    for input_text, expected in test3_cases:
        print(f"\n输入: '{input_text}'")
        result = preprocessor._smart_split_feature(input_text)
        print(f"智能拆分结果: {result}")
        print(f"期望: {expected}")
        print(f"结果: {'✓' if result == expected else '✗'}")
    
    print("\n" + "=" * 80)
    print("测试4: 完整流程 - 无冒号的元数据前缀")
    print("=" * 80)
    
    # 模拟真实场景（无冒号）
    test4 = "量程0~250ppm+输出信号4~20mA+精度±5%"
    print(f"\n输入: '{test4}'")
    
    result4 = preprocessor.preprocess(test4, mode='matching')
    print(f"\n清理后: '{result4.cleaned}'")
    print(f"归一化后: '{result4.normalized}'")
    print(f"提取特征: {result4.features}")
    
    print("\n验证:")
    # 期望: 元数据关键词被删除，"±"被归一化删除，"%"被保留
    expected_features = ['0-250', '4-20', '5%']
    if set(result4.features) == set(expected_features):
        print(f"  ✓ 无冒号时，元数据前缀被正确删除，±被删除，%被保留")
        print(f"  期望特征: {expected_features}")
        print(f"  实际特征: {result4.features}")
    else:
        print(f"  ✗ 处理失败")
        print(f"  期望特征: {expected_features}")
        print(f"  实际特征: {result4.features}")
    
    print("\n" + "=" * 80)
    print("测试5: 完整流程 - 带冒号的元数据前缀")
    print("=" * 80)
    
    test5 = "量程:0~250ppm+输出信号:4~20mA+精度:±5%"
    print(f"\n输入: '{test5}'")
    
    result5 = preprocessor.preprocess(test5, mode='matching')
    print(f"\n清理后: '{result5.cleaned}'")
    print(f"归一化后: '{result5.normalized}'")
    print(f"提取特征: {result5.features}")
    
    print("\n验证:")
    if set(result5.features) == set(expected_features):
        print(f"  ✓ 带冒号时，元数据前缀被正确删除，±被删除，%被保留")
        print(f"  期望特征: {expected_features}")
        print(f"  实际特征: {result5.features}")
    else:
        print(f"  ✗ 处理失败")
        print(f"  期望特征: {expected_features}")
        print(f"  实际特征: {result5.features}")
    
    print("\n" + "=" * 80)
    print("测试6: 真实数据测试")
    print("=" * 80)
    
    # 用户提供的真实数据
    test6 = "co浓度探测器+工作原理:电化学式+量程0~250ppm+输出信号4~20ma+2~10vdc+精度±5%@25c.50%rh(0~100ppm)"
    print(f"\n输入: '{test6}'")
    
    result6 = preprocessor.preprocess(test6, mode='matching')
    print(f"\n清理后: '{result6.cleaned}'")
    print(f"归一化后: '{result6.normalized}'")
    print(f"提取特征: {result6.features}")
    
    print("\n分析:")
    print("  实际结果:")
    print(f"    - 提取的特征: {result6.features}")
    print("\n  期望:")
    print("    - 'co浓度探测器' 被拆分为 ['co', '浓度', '探测器']")
    print("    - '工作原理:' 被删除（智能清理阶段）")
    print("    - '量程' 前缀被删除，保留 '0-250'")
    print("    - '输出信号' 前缀被删除，保留 '4-20' 和 '2-10'")
    print("    - '精度' 前缀被删除，保留 '±5'")
    print("    - 其他数值: '25', '50', '0-100'")
    
    # 检查关键特征是否存在
    has_co = 'co' in result6.features
    has_0_250 = '0-250' in result6.features
    has_4_20 = '4-20' in result6.features
    has_2_10 = '2-10' in result6.features
    no_metadata_prefix = not any('量程' in f or '输出信号' in f or '精度' in f for f in result6.features)
    
    print("\n  验证:")
    print(f"    ✓ 'co' 被提取: {has_co}")
    print(f"    ✓ '0-250' 被提取: {has_0_250}")
    print(f"    ✓ '4-20' 被提取: {has_4_20}")
    print(f"    ✓ '2-10' 被提取: {has_2_10}")
    print(f"    ✓ 元数据前缀被删除: {no_metadata_prefix}")
    
    if has_co and has_0_250 and has_4_20 and has_2_10 and no_metadata_prefix:
        print("\n  ✓ 所有关键特征都正确提取，元数据前缀被正确删除")
    else:
        print("\n  ✗ 部分特征提取失败")


if __name__ == '__main__':
    test_metadata_prefix_issue()
