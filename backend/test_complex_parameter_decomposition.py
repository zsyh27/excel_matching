"""
测试复杂参数分解功能
"""

import json
from modules.text_preprocessor import TextPreprocessor

def test_complex_parameter_decomposition():
    """测试复杂参数分解功能"""
    
    print("=" * 80)
    print("复杂参数分解测试")
    print("=" * 80)
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 创建预处理器
    preprocessor = TextPreprocessor(config)
    
    # 测试用例
    test_cases = [
        {
            'text': '室内CO2传感器,精度±5%@25C.50%RH(0~100ppm),485通讯',
            'description': '包含复杂精度参数'
        },
        {
            'text': '温度传感器,量程:-40~120℃,精度:±0.5℃',
            'description': '简单参数（不需要分解）'
        },
        {
            'text': '压力传感器,精度±2%@20C.45%RH(0~500pa)',
            'description': '另一个复杂精度参数'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n【测试用例 {i}】{test_case['description']}")
        print(f"原始文本: {test_case['text']}")
        
        # 预处理
        result = preprocessor.preprocess(test_case['text'], mode='matching')
        
        print(f"\n提取的特征 ({len(result.features)} 个):")
        for feature in result.features:
            print(f"  - {feature}")
        
        # 检查是否包含分解后的数值特征
        has_decomposed = any(
            feature in ['±5', '25', '50', '0-100', '±2', '20', '45', '0-500']
            for feature in result.features
        )
        
        if has_decomposed:
            print(f"\n✅ 复杂参数已成功分解")
        else:
            print(f"\n⚠️  未检测到分解后的特征（可能不是复杂参数）")
        
        print("-" * 80)
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == '__main__':
    test_complex_parameter_decomposition()
