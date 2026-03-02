"""
调试复杂参数分解
"""

import json
from modules.text_preprocessor import TextPreprocessor

def debug_complex_param():
    """调试复杂参数处理流程"""
    
    print("=" * 80)
    print("复杂参数处理流程调试")
    print("=" * 80)
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 创建预处理器
    preprocessor = TextPreprocessor(config)
    
    # 测试文本
    text = "室内CO2传感器,精度±5%@25C.50%RH(0~100ppm),485通讯"
    
    print(f"\n原始文本: {text}")
    
    # 执行预处理
    result = preprocessor.preprocess(text, mode='matching')
    
    print(f"\n处理流程:")
    print(f"1. 原始文本: {result.original}")
    print(f"2. 清理后: {result.cleaned}")
    print(f"3. 归一化: {result.normalized}")
    print(f"4. 提取特征: {result.features}")
    
    # 手动测试复杂参数分解
    print(f"\n手动测试复杂参数分解:")
    test_strings = [
        "±5%@25c.50%rh(0~100ppm)",
        "±5%@25c.50%rh",
        "0-100ppm"
    ]
    
    for test_str in test_strings:
        decomposed = preprocessor._decompose_complex_parameter(test_str)
        print(f"  输入: {test_str}")
        print(f"  输出: {decomposed}")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    debug_complex_param()
