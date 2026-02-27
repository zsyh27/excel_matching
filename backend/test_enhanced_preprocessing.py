# -*- coding: utf-8 -*-
"""
测试增强的预处理器

验证同义词映射和智能特征拆分
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
        'note': '简短描述 - 测试同义词映射'
    },
    {
        'description': '霍尼韦尔室内温度传感器，NTC10K，室内墙装',
        'note': '完整描述 - 测试智能拆分'
    },
    {
        'description': '霍尼韦尔温度传感器',
        'note': '品牌+类型 - 测试品牌识别'
    },
    {
        'description': '西门子DDC控制器，32点',
        'note': '品牌+设备类型 - 测试设备类型识别'
    },
    {
        'description': '室内温湿度传感器，4-20mA',
        'note': '修饰词+设备类型 - 测试修饰词提取'
    }
]

print("=" * 80)
print("增强预处理器测试")
print("=" * 80)

for i, test_case in enumerate(test_cases, 1):
    description = test_case['description']
    note = test_case['note']
    
    print(f"\n测试用例 {i}: {note}")
    print(f"输入: {description}")
    print("-" * 80)
    
    # 测试匹配模式
    result = preprocessor.preprocess(description, mode='matching')
    
    print(f"原始文本: {result.original}")
    print(f"清理后: {result.cleaned}")
    print(f"归一化: {result.normalized}")
    print(f"提取特征 ({len(result.features)} 个):")
    for j, feature in enumerate(result.features, 1):
        print(f"  {j}. {feature}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
