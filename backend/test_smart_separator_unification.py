"""
测试智能分隔符统一功能

验证数值范围中的空格被正确处理
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from modules.text_preprocessor import TextPreprocessor


def test_smart_separator_unification():
    """测试智能分隔符统一"""
    
    # 配置
    config = {
        'metadata_keywords': ['型号', '品牌', '规格', '参数', '名称'],
        'intelligent_extraction': {
            'enabled': True,
            'text_cleaning': {
                'enabled': True,
                'truncate_delimiters': [],
                'noise_section_patterns': []
            },
            'metadata_label_patterns': []
        },
        'feature_split_chars': ['+', '|', '；'],
        'normalization_map': {},
        'ignore_keywords': [],
        'global_config': {
            'remove_whitespace': True
        },
        'synonym_map': {},
        'brand_keywords': [],
        'device_type_keywords': []
    }
    
    preprocessor = TextPreprocessor(config)
    
    print("=" * 80)
    print("测试1: 数值范围中的空格应该被删除（不是替换成+）")
    print("=" * 80)
    
    test_cases = [
        {
            'input': '量程 0~ 250ppm',
            'expected_cleaned': '量程+0~250ppm',  # 空格被删除，不是变成 0~+250ppm
            'description': '波浪号范围'
        },
        {
            'input': '输出信号 4 - 20mA',
            'expected_cleaned': '输出信号+4-20mA',  # 空格被删除
            'description': '减号范围'
        },
        {
            'input': '电压 2 ~ 10V',
            'expected_cleaned': '电压+2~10V',
            'description': '波浪号范围（两边都有空格）'
        },
        {
            'input': '温度 -40 ~ 85',
            'expected_cleaned': '温度+-40~85',
            'description': '负数范围'
        },
    ]
    
    for test_case in test_cases:
        input_text = test_case['input']
        expected = test_case['expected_cleaned']
        description = test_case['description']
        
        result = preprocessor.preprocess(input_text, mode='matching')
        actual = result.cleaned
        
        status = "✓" if actual == expected else "✗"
        print(f"\n{status} {description}")
        print(f"  输入: '{input_text}'")
        print(f"  期望清理后: '{expected}'")
        print(f"  实际清理后: '{actual}'")
        
        if actual != expected:
            print(f"  ❌ 不匹配！")
    
    print("\n" + "=" * 80)
    print("测试2: 普通空格应该被替换成+")
    print("=" * 80)
    
    test_cases_normal = [
        {
            'input': 'CO浓度 探测器',
            'expected_cleaned': 'CO浓度+探测器',
            'description': '普通空格'
        },
        {
            'input': '室内 温度 传感器',
            'expected_cleaned': '室内+温度+传感器',
            'description': '多个空格'
        },
    ]
    
    for test_case in test_cases_normal:
        input_text = test_case['input']
        expected = test_case['expected_cleaned']
        description = test_case['description']
        
        result = preprocessor.preprocess(input_text, mode='matching')
        actual = result.cleaned
        
        status = "✓" if actual == expected else "✗"
        print(f"\n{status} {description}")
        print(f"  输入: '{input_text}'")
        print(f"  期望清理后: '{expected}'")
        print(f"  实际清理后: '{actual}'")
        
        if actual != expected:
            print(f"  ❌ 不匹配！")
    
    print("\n" + "=" * 80)
    print("测试3: 完整示例（用户提供的真实数据）")
    print("=" * 80)
    
    real_text = "CO浓度探测器 | 工作原理：电化学式； 量程 0~ 250ppm ；输出信号 4~20mA / 2~10VDC"
    print(f"输入: '{real_text}'")
    
    result = preprocessor.preprocess(real_text, mode='matching')
    print(f"\n清理后: '{result.cleaned}'")
    print(f"归一化后: '{result.normalized}'")
    print(f"提取特征: {result.features}")
    
    # 验证关键点
    print("\n验证关键点:")
    if '0~250' in result.normalized:
        print("  ✓ '0~ 250ppm' 正确处理为 '0~250'（空格被删除）")
    else:
        print(f"  ✗ '0~ 250ppm' 处理错误，结果中包含: {[f for f in result.features if '250' in f]}")
    
    if '4-20' in result.normalized:
        print("  ✓ '4 - 20mA' 正确处理为 '4-20'")
    else:
        print(f"  ✗ '4 - 20mA' 处理错误")
    
    if '2~10' in result.normalized or '2-10' in result.normalized:
        print("  ✓ '2~10VDC' 正确处理")
    else:
        print(f"  ✗ '2~10VDC' 处理错误")


if __name__ == '__main__':
    test_smart_separator_unification()
