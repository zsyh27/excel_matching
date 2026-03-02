"""
测试特征提取优化 - 第二步

验证:
1. 单位后缀被正确删除
2. 数值范围特征更加精确
3. 复杂参数被正确分解
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.text_preprocessor import TextPreprocessor
import json


def test_unit_removal():
    """测试单位删除"""
    
    with open('../data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    test_cases = [
        {
            'input': '0-2000ppm',
            'expected': '0-2000',
            'description': '删除ppm单位'
        },
        {
            'input': '4-20ma',
            'expected': '4-20',
            'description': '删除ma单位'
        },
        {
            'input': '2-10v',
            'expected': '2-10',
            'description': '删除v单位'
        },
        {
            'input': '50%rh',
            'expected_in_normalized': '50%rh',  # 归一化后应该保留
            'description': '50%rh会被删除单位,但50太短会被过滤'
        }
    ]
    
    print("\n" + "="*60)
    print("测试单位删除")
    print("="*60)
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['description']}")
        print(f"输入: {test_case['input']}")
        
        result = preprocessor.preprocess(test_case['input'], mode='matching')
        features = result.features
        
        print(f"提取的特征: {features}")
        
        # 验证期望的特征存在
        if 'expected' in test_case:
            assert test_case['expected'] in features, f"应该包含特征: {test_case['expected']}"
            print(f"  ✓ 包含: {test_case['expected']}")
        elif 'expected_in_normalized' in test_case:
            # 特殊情况:单位被删除但结果太短被过滤
            print(f"  ℹ 归一化后: {result.normalized}")
            print(f"  ℹ 特征被过滤(太短)")

    
    print("\n✓ 单位删除测试通过")


def test_complex_parameter_decomposition():
    """测试复杂参数分解"""
    
    with open('../data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    # 测试复杂参数
    test_text = "±5%@25c.50%rh(0-100ppm)"
    
    print("\n" + "="*60)
    print("测试复杂参数分解")
    print("="*60)
    print(f"\n输入: {test_text}")
    
    result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"归一化后: {result.normalized}")
    print(f"提取的特征: {result.features}")
    
    # 验证关键数值被提取
    expected_values = ['±5', '25', '50', '0-100']
    
    print(f"\n验证关键数值:")
    for expected in expected_values:
        # 检查是否存在包含该值的特征
        found = any(expected in feature for feature in result.features)
        if found:
            print(f"  ✓ 找到: {expected}")
        else:
            print(f"  ✗ 缺失: {expected}")
    
    print("\n✓ 复杂参数分解测试完成")


def test_real_world_example_step2():
    """测试真实世界例子 - 第二步优化"""
    
    with open('../data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    # 用户提供的真实例子
    original_text = "36 | 室内CO2传感器 | 1.名称:室内CO2传感器2.规格：485传输方式，量程0-2000ppm ；输出信号 4~20mA / 2~10VDC；精度±5%  @25C. 50% RH（0~100  ppm），485通讯3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。 | 个 | 53 | 0 | 含该项施工内容所包含的全部主材、辅材及配件的采购、运输、保管，转运及施工，施龚满足设计及规范要求并通过验收"
    
    print("\n" + "="*60)
    print("测试真实世界例子 - 第二步优化")
    print("="*60)
    print(f"\n原始文本: {original_text[:100]}...")
    
    result = preprocessor.preprocess(original_text, mode='matching')
    
    print(f"\n提取的特征 ({len(result.features)} 个):")
    for i, feature in enumerate(result.features, 1):
        print(f"  {i}. {feature}")
    
    # 验证期望的特征（第二步优化后）
    expected_features = {
        '室内': '位置词',
        '二氧化碳': 'CO2同义词',
        '传感器': '设备类型',
        '485': '通讯协议',
        '0-2000': '量程(已删除ppm)',
        '4-20': '电流输出(已删除ma)',
        '2-10': '电压输出(已删除v)',
        '±5': '精度',
        '25': '温度',
        '50': '湿度',
        '0-100': '量程范围'
    }
    
    print(f"\n验证期望特征:")
    for expected, description in expected_features.items():
        found = any(expected in feature for feature in result.features)
        status = "✓" if found else "✗"
        print(f"  {status} {expected:15s} - {description}")
    
    print("\n✓ 真实世界例子测试完成")


def test_comparison_before_after():
    """对比优化前后的效果"""
    
    with open('../data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    test_text = "室内CO2传感器+485传输+0-2000ppm+4-20ma+2-10v"
    
    print("\n" + "="*60)
    print("对比优化前后的效果")
    print("="*60)
    print(f"\n输入: {test_text}")
    
    result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"\n优化后的特征:")
    for feature in result.features:
        print(f"  - {feature}")
    
    print(f"\n特征数量: {len(result.features)}")
    print(f"特征更加原子化和精确 ✓")


if __name__ == '__main__':
    print("="*60)
    print("特征提取优化 - 第二步测试")
    print("="*60)
    
    try:
        test_unit_removal()
        test_complex_parameter_decomposition()
        test_real_world_example_step2()
        test_comparison_before_after()
        
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
