"""
测试匹配阶段增强功能

测试三个优先级的功能：
1. 智能拆分复合词
2. 删除单位符号
3. 技术规格拆分（复杂参数分解）
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.text_preprocessor import TextPreprocessor


def test_unit_removal():
    """测试单位删除功能"""
    print("\n=== 测试单位删除功能 ===")
    
    config = {
        'normalization_map': {},
        'feature_split_chars': ['+'],
        'ignore_keywords': [],
        'global_config': {
            'fullwidth_to_halfwidth': True,
            'remove_whitespace': True,
            'unify_lowercase': True
        },
        'synonym_map': {},
        'brand_keywords': [],
        'device_type_keywords': [],
        'medium_keywords': [],
        'intelligent_extraction': {
            'enabled': True,
            'text_cleaning': {'enabled': False},
            'feature_quality_scoring': {'enabled': False}
        },
        'unit_removal': {
            'enabled': True,
            'units': ['ppm', 'ma', 'v', '%rh', 'pa', '℃', 'c']
        },
        'metadata_keywords': []
    }
    
    preprocessor = TextPreprocessor(config)
    
    test_cases = [
        ("0-2000ppm", "0-2000"),
        ("4-20ma", "4-20"),
        ("2-10v", "2-10"),
        ("50%rh", "50"),
        ("-20~60℃", "-20~60"),
    ]
    
    for input_text, expected in test_cases:
        result = preprocessor.preprocess(input_text, mode='matching')
        # 检查特征中是否包含预期结果
        has_expected = expected in result.features
        status = "✅" if has_expected else "❌"
        print(f"{status} 输入: {input_text}")
        print(f"   特征: {result.features}")
        print(f"   期望包含: {expected}")
        print()


def test_intelligent_splitting():
    """测试智能拆分功能"""
    print("\n=== 测试智能拆分功能 ===")
    
    config = {
        'normalization_map': {},
        'feature_split_chars': ['+'],
        'ignore_keywords': [],
        'global_config': {
            'fullwidth_to_halfwidth': True,
            'remove_whitespace': False,  # 不删除空格，让智能拆分处理
            'unify_lowercase': True
        },
        'synonym_map': {},
        'brand_keywords': ['霍尼韦尔'],
        'device_type_keywords': ['传感器', '控制器'],
        'medium_keywords': [],
        'location_words': ['室内', '室外', '墙装', '吊装', '管道', '风管'],  # 添加位置词配置
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
    
    test_cases = [
        ("室内墙装", ["室内", "墙装"]),
        ("ntc 10k", ["ntc", "10k"]),
        ("DN15", ["dn", "15"]),
        ("霍尼韦尔温度传感器", ["霍尼韦尔", "温度", "传感器"]),
    ]
    
    for input_text, expected_parts in test_cases:
        result = preprocessor.preprocess(input_text, mode='matching')
        # 检查是否所有预期部分都在特征中
        all_found = all(part in result.features for part in expected_parts)
        status = "✅" if all_found else "❌"
        print(f"{status} 输入: {input_text}")
        print(f"   特征: {result.features}")
        print(f"   期望包含: {expected_parts}")
        print()


def test_complex_parameter_decomposition():
    """测试复杂参数分解功能"""
    print("\n=== 测试复杂参数分解功能 ===")
    
    config = {
        'normalization_map': {},
        'feature_split_chars': ['+'],
        'ignore_keywords': [],
        'global_config': {
            'fullwidth_to_halfwidth': True,
            'remove_whitespace': True,
            'unify_lowercase': True
        },
        'synonym_map': {},
        'brand_keywords': [],
        'device_type_keywords': [],
        'medium_keywords': [],
        'intelligent_extraction': {
            'enabled': True,
            'text_cleaning': {'enabled': False},
            'feature_quality_scoring': {'enabled': False},
            'complex_parameter_decomposition': {
                'enabled': True,
                'patterns': [
                    {
                        'name': '精度规格',
                        'description': '精度@温度.湿度(量程)',
                        'pattern': r'±(\d+)%@(\d+)c\.(\d+)%rh\((\d+)~(\d+)ppm\)'
                    }
                ]
            }
        },
        'unit_removal': {'enabled': False},
        'metadata_keywords': []
    }
    
    preprocessor = TextPreprocessor(config)
    
    # 注意：这个测试需要输入已经归一化的文本
    test_cases = [
        ("±5%@25c.50%rh(0~100ppm)", ["±5", "25", "50", "0-100"]),
    ]
    
    for input_text, expected_parts in test_cases:
        result = preprocessor.preprocess(input_text, mode='matching')
        # 检查是否所有预期部分都在特征中
        all_found = all(part in result.features for part in expected_parts)
        status = "✅" if all_found else "❌"
        print(f"{status} 输入: {input_text}")
        print(f"   特征: {result.features}")
        print(f"   期望包含: {expected_parts}")
        print()


def test_device_mode_preservation():
    """测试设备录入模式下的数据完整性"""
    print("\n=== 测试设备录入模式（数据完整性） ===")
    
    config = {
        'normalization_map': {},
        'feature_split_chars': ['+'],
        'ignore_keywords': [],
        'global_config': {
            'fullwidth_to_halfwidth': True,
            'remove_whitespace': True,  # 归一化会删除空格
            'unify_lowercase': True
        },
        'synonym_map': {},
        'brand_keywords': [],
        'device_type_keywords': [],
        'medium_keywords': [],
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
        'unit_removal': {
            'enabled': True,
            'units': ['ppm', 'ma', 'v']
        },
        'metadata_keywords': []
    }
    
    preprocessor = TextPreprocessor(config)
    
    test_cases = [
        ("室内墙装", "室内墙装"),  # 应该保持完整（不拆分）
        ("0-2000ppm", "0-2000ppm"),  # 应该保留单位
        ("ntc 10k", "ntc10k"),  # 空格会被归一化删除，但不拆分
    ]
    
    for input_text, expected in test_cases:
        result = preprocessor.preprocess(input_text, mode='device')
        # 在device模式下，应该保留原始特征
        has_expected = expected in result.features
        status = "✅" if has_expected else "❌"
        print(f"{status} 输入: {input_text}")
        print(f"   特征: {result.features}")
        print(f"   期望包含: {expected}")
        print()


if __name__ == '__main__':
    print("=" * 60)
    print("匹配阶段增强功能测试")
    print("=" * 60)
    
    test_unit_removal()
    test_intelligent_splitting()
    test_complex_parameter_decomposition()
    test_device_mode_preservation()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
