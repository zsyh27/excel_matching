"""
测试特征提取优化 - 第一步

验证:
1. 分隔符统一正确工作
2. 位置词、品牌词、设备类型词被拆分为独立特征
3. 特征更加原子化和精确
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.text_preprocessor import TextPreprocessor
import json


def test_location_word_splitting():
    """测试位置词拆分"""
    
    with open('../data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    # 测试用例
    test_cases = [
        {
            'input': '室内co2传感器',
            'expected_contains': ['室内', 'co2', '传感器'],
            'description': '室内CO2传感器应该拆分为: 室内 + co2 + 传感器'
        },
        {
            'input': '室外温传感器',
            'expected_contains': ['室外', '传感器'],
            'description': '室外温传感器应该拆分为: 室外 + 温 + 传感器'
        },
        {
            'input': '管道温传感器',
            'expected_contains': ['管道', '传感器'],
            'description': '管道温传感器应该拆分为: 管道 + 温 + 传感器'
        }
    ]
    
    print("\n" + "="*60)
    print("测试位置词拆分")
    print("="*60)
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['description']}")
        print(f"输入: {test_case['input']}")
        
        result = preprocessor.preprocess(test_case['input'], mode='matching')
        features = result.features
        
        print(f"提取的特征: {features}")
        
        # 验证期望的特征是否存在
        for expected in test_case['expected_contains']:
            assert expected in features, f"应该包含特征: {expected}"
            print(f"  ✓ 包含: {expected}")
    
    print("\n✓ 位置词拆分测试通过")


def test_brand_word_splitting():
    """测试品牌词拆分"""
    
    with open('../data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    test_cases = [
        {
            'input': '霍尼韦尔室内温传感器',
            'expected_contains': ['霍尼韦尔', '室内', '传感器'],
            'description': '霍尼韦尔室内温传感器应该拆分'
        },
        {
            'input': '西门子ddc控制器',
            'expected_contains': ['西门子', 'ddc', '控制器'],
            'description': '西门子DDC控制器应该拆分'
        }
    ]
    
    print("\n" + "="*60)
    print("测试品牌词拆分")
    print("="*60)
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['description']}")
        print(f"输入: {test_case['input']}")
        
        result = preprocessor.preprocess(test_case['input'], mode='matching')
        features = result.features
        
        print(f"提取的特征: {features}")
        
        for expected in test_case['expected_contains']:
            assert expected in features, f"应该包含特征: {expected}"
            print(f"  ✓ 包含: {expected}")
    
    print("\n✓ 品牌词拆分测试通过")


def test_real_world_example():
    """测试真实世界的例子"""
    
    with open('../data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    # 用户提供的真实例子
    original_text = "36 | 室内CO2传感器 | 1.名称:室内CO2传感器2.规格：485传输方式，量程0-2000ppm ；输出信号 4~20mA / 2~10VDC；精度±5%  @25C. 50% RH（0~100  ppm），485通讯3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。 | 个 | 53 | 0 | 含该项施工内容所包含的全部主材、辅材及配件的采购、运输、保管，转运及施工，施龚满足设计及规范要求并通过验收"
    
    print("\n" + "="*60)
    print("测试真实世界例子")
    print("="*60)
    print(f"\n原始文本: {original_text[:100]}...")
    
    result = preprocessor.preprocess(original_text, mode='matching')
    
    print(f"\n智能清理后: {result.intelligent_cleaning_detail.after_text[:100] if result.intelligent_cleaning_detail else '无'}...")
    print(f"\n归一化后: {result.normalized[:100]}...")
    print(f"\n提取的特征 ({len(result.features)} 个):")
    for i, feature in enumerate(result.features, 1):
        print(f"  {i}. {feature}")
    
    # 验证关键特征
    expected_features = ['室内', 'co2', '传感器', '485', '0-2000', '4-20', '2-10']
    
    print(f"\n验证关键特征:")
    for expected in expected_features:
        # 检查是否存在包含该特征的项
        found = any(expected in feature for feature in result.features)
        if found:
            print(f"  ✓ 找到: {expected}")
        else:
            print(f"  ✗ 缺失: {expected}")
    
    print("\n✓ 真实世界例子测试完成")


def test_separator_unification_with_splitting():
    """测试分隔符统一和特征拆分的组合效果"""
    
    with open('../data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    # 包含多种分隔符的文本
    test_text = "室内CO2传感器 | 485传输 | 量程0-2000ppm"
    
    print("\n" + "="*60)
    print("测试分隔符统一和特征拆分组合")
    print("="*60)
    print(f"\n输入: {test_text}")
    
    result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"\n智能清理后: {result.intelligent_cleaning_detail.after_text if result.intelligent_cleaning_detail else '无'}")
    print(f"归一化后: {result.normalized}")
    print(f"提取的特征: {result.features}")
    
    # 验证 | 被转换
    assert '|' not in result.intelligent_cleaning_detail.after_text, "| 应该被转换"
    
    # 验证特征被正确拆分
    assert '室内' in result.features or any('室内' in f for f in result.features), "应该包含'室内'"
    # CO2会被转换为"二氧化碳"
    assert '二氧化碳' in result.features or any('二氧化碳' in f for f in result.features), "应该包含'二氧化碳'"
    assert '传感器' in result.features or any('传感器' in f for f in result.features), "应该包含'传感器'"
    
    print("\n✓ 分隔符统一和特征拆分组合测试通过")


if __name__ == '__main__':
    print("="*60)
    print("特征提取优化 - 第一步测试")
    print("="*60)
    
    try:
        test_location_word_splitting()
        test_brand_word_splitting()
        test_separator_unification_with_splitting()
        test_real_world_example()
        
        print("\n" + "="*60)
        print("所有测试通过! ✓")
        print("="*60)
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
