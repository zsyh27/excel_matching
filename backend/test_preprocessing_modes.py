# -*- coding: utf-8 -*-
"""
测试预处理器的不同模式

验证设备库模式和匹配模式的区别
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.text_preprocessor import TextPreprocessor
import json

# 加载配置
config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'static_config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 创建预处理器
preprocessor = TextPreprocessor(config)

# 测试用例
test_cases = [
    {
        'description': '温度传感器，0-50℃，4-20mA',
        'expected_features_matching': ['温度传感器', '0-50', '4-20ma'],
        'expected_features_device': ['温度传感器', '0-50度', '4-20ma']
    },
    {
        'description': '温度传感器+0-50℃+4-20mA',
        'expected_features_device': ['温度传感器', '0-50度', '4-20ma']
    },
    {
        'description': 'DDC控制器，32点，霍尼韦尔',
        'expected_features_matching': ['ddc控制器', '32点', '霍尼韦尔']
    }
]

print("=" * 80)
print("预处理器模式测试")
print("=" * 80)

for i, test_case in enumerate(test_cases, 1):
    description = test_case['description']
    print(f"\n测试用例 {i}: {description}")
    print("-" * 80)
    
    # 测试匹配模式
    print("\n【匹配模式 (mode='matching')】")
    result_matching = preprocessor.preprocess(description, mode='matching')
    print(f"原始文本: {result_matching.original}")
    print(f"清理后: {result_matching.cleaned}")
    print(f"归一化: {result_matching.normalized}")
    print(f"提取特征: {result_matching.features}")
    
    # 测试设备库模式
    print("\n【设备库模式 (mode='device')】")
    result_device = preprocessor.preprocess(description, mode='device')
    print(f"原始文本: {result_device.original}")
    print(f"清理后: {result_device.cleaned}")
    print(f"归一化: {result_device.normalized}")
    print(f"提取特征: {result_device.features}")
    
    # 验证期望结果
    if 'expected_features_matching' in test_case:
        expected = test_case['expected_features_matching']
        actual = result_matching.features
        if actual == expected:
            print(f"\n✓ 匹配模式特征提取正确")
        else:
            print(f"\n✗ 匹配模式特征提取不符合预期")
            print(f"  期望: {expected}")
            print(f"  实际: {actual}")
    
    if 'expected_features_device' in test_case:
        expected = test_case['expected_features_device']
        actual = result_device.features
        if actual == expected:
            print(f"✓ 设备库模式特征提取正确")
        else:
            print(f"✗ 设备库模式特征提取不符合预期")
            print(f"  期望: {expected}")
            print(f"  实际: {actual}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
