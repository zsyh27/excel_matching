"""
测试统一的元数据处理功能

验证用户只需要在 metadata_keywords 中添加关键词，
系统就能自动处理两种格式：
1. 简单格式: "型号:QAA2061"
2. 带序号格式: "2.型号:QAA2061"
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from modules.text_preprocessor import TextPreprocessor


def test_unified_metadata_processing():
    """测试统一的元数据处理"""
    
    # 配置
    config = {
        'metadata_keywords': [
            '型号', '品牌', '规格', '参数', '名称', 
            '规格参数', '工作原理'  # 新增的关键词
        ],
        'intelligent_extraction': {
            'enabled': True,
            'text_cleaning': {
                'enabled': True,
                'truncate_delimiters': [],
                'noise_section_patterns': []
            },
            'metadata_label_patterns': []  # 不再需要正则表达式
        },
        'feature_split_chars': ['+'],
        'normalization_map': {},
        'ignore_keywords': [],
        'global_config': {},
        'synonym_map': {},
        'brand_keywords': [],
        'device_type_keywords': []
    }
    
    preprocessor = TextPreprocessor(config)
    
    print("=" * 80)
    print("测试1: 简单格式（不带序号）")
    print("=" * 80)
    
    test_cases_simple = [
        ("型号:QAA2061", "QAA2061"),
        ("品牌:霍尼韦尔", "霍尼韦尔"),
        ("规格参数:0-2000ppm", "0-2000ppm"),
        ("工作原理:电化学式", "电化学式"),
    ]
    
    for input_text, expected in test_cases_simple:
        result = preprocessor.remove_metadata_labels(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} 输入: '{input_text}'")
        print(f"  期望: '{expected}'")
        print(f"  实际: '{result}'")
        print()
    
    print("=" * 80)
    print("测试2: 带序号格式")
    print("=" * 80)
    
    test_cases_numbered = [
        ("1.型号:QAA2061", "QAA2061"),
        ("2.品牌:霍尼韦尔", "霍尼韦尔"),
        ("3.规格参数:0-2000ppm", "0-2000ppm"),
        ("10.工作原理:电化学式", "电化学式"),
        ("1型号:QAA2061", "QAA2061"),  # 没有点号
        ("2规格参数:0-2000ppm", "0-2000ppm"),  # 没有点号
    ]
    
    for input_text, expected in test_cases_numbered:
        result = preprocessor.remove_metadata_labels(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} 输入: '{input_text}'")
        print(f"  期望: '{expected}'")
        print(f"  实际: '{result}'")
        print()
    
    print("=" * 80)
    print("测试3: 中文冒号")
    print("=" * 80)
    
    test_cases_chinese_colon = [
        ("型号：QAA2061", "QAA2061"),
        ("1.品牌：霍尼韦尔", "霍尼韦尔"),
        ("2规格参数：0-2000ppm", "0-2000ppm"),
    ]
    
    for input_text, expected in test_cases_chinese_colon:
        result = preprocessor.remove_metadata_labels(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} 输入: '{input_text}'")
        print(f"  期望: '{expected}'")
        print(f"  实际: '{result}'")
        print()
    
    print("=" * 80)
    print("测试4: 复杂示例（完整预处理流程）")
    print("=" * 80)
    
    complex_text = "2.规格参数:工作原理:电化学式+量程:0-2000ppm"
    print(f"输入: '{complex_text}'")
    
    result = preprocessor.preprocess(complex_text, mode='matching')
    print(f"清理后: '{result.cleaned}'")
    print(f"归一化后: '{result.normalized}'")
    print(f"提取特征: {result.features}")
    print()
    
    # 验证智能清理详情
    if result.intelligent_cleaning_detail:
        print("智能清理详情:")
        print(f"  应用规则: {result.intelligent_cleaning_detail.applied_rules}")
        print(f"  元数据标签匹配: {len(result.intelligent_cleaning_detail.metadata_tag_matches)} 个")
        for match in result.intelligent_cleaning_detail.metadata_tag_matches:
            print(f"    - 标签: '{match.tag}', 匹配文本: '{match.matched_text}'")
    
    print("\n" + "=" * 80)
    print("测试5: 不应该被删除的文本")
    print("=" * 80)
    
    test_cases_keep = [
        ("室内CO2传感器", "室内CO2传感器"),  # 没有冒号
        ("0-2000ppm", "0-2000ppm"),  # 纯数值
        ("霍尼韦尔传感器", "霍尼韦尔传感器"),  # 没有冒号
    ]
    
    for input_text, expected in test_cases_keep:
        result = preprocessor.remove_metadata_labels(input_text)
        status = "✓" if result == expected else "✗"
        print(f"{status} 输入: '{input_text}'")
        print(f"  期望: '{expected}'")
        print(f"  实际: '{result}'")
        print()


if __name__ == '__main__':
    test_unified_metadata_processing()
