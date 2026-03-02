"""
测试API是否正确处理元数据前缀（如"精度±5%"）
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from modules.text_preprocessor import TextPreprocessor


def test_api_metadata_prefix():
    """测试API处理元数据前缀"""
    
    print("=" * 80)
    print("测试 - 元数据前缀处理（使用数据库配置）")
    print("=" * 80)
    
    try:
        # 直接从配置文件加载
        import json
        config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'static_config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 创建预处理器
        preprocessor = TextPreprocessor(config)
        
        # 测试用例1: 无冒号的元数据前缀
        test_text = "量程0~250ppm+输出信号4~20mA+精度±5%"
        
        print(f"\n输入文本: '{test_text}'")
        
        # 预处理文本
        result = preprocessor.preprocess(test_text, mode='matching')
        
        print(f"\n预处理结果:")
        print(f"  原始文本: {result.original}")
        print(f"  清理后: {result.cleaned}")
        print(f"  归一化后: {result.normalized}")
        print(f"  提取特征: {result.features}")
        
        # 验证
        features = result.features
        expected_features = ['0-250', '4-20', '5%']
        
        print(f"\n验证:")
        print(f"  期望特征: {expected_features}")
        print(f"  实际特征: {features}")
        
        if set(features) == set(expected_features):
            print(f"  ✓ 测试通过 - 元数据前缀被正确删除，±被删除，%被保留")
        else:
            print(f"  ✗ 测试失败 - 特征不匹配")
        
        # 测试用例2: 真实数据
        print("\n" + "=" * 80)
        print("测试 - 真实数据")
        print("=" * 80)
        
        test_text2 = "co浓度探测器+工作原理:电化学式+量程0~250ppm+输出信号4~20ma+2~10vdc+精度±5%@25c.50%rh(0~100ppm)"
        
        print(f"\n输入文本: '{test_text2}'")
        
        # 预处理文本
        result2 = preprocessor.preprocess(test_text2, mode='matching')
        
        print(f"\n预处理结果:")
        print(f"  原始文本: {result2.original}")
        print(f"  清理后: {result2.cleaned}")
        print(f"  归一化后: {result2.normalized}")
        print(f"  提取特征: {result2.features}")
        
        # 验证关键特征
        features = result2.features
        
        has_co = 'co' in features
        has_0_250 = '0-250' in features
        has_4_20 = '4-20' in features
        has_2_10 = '2-10' in features
        no_metadata_prefix = not any('量程' in f or '输出信号' in f or '精度' in f for f in features)
        
        print(f"\n验证:")
        print(f"  ✓ 'co' 被提取: {has_co}")
        print(f"  ✓ '0-250' 被提取: {has_0_250}")
        print(f"  ✓ '4-20' 被提取: {has_4_20}")
        print(f"  ✓ '2-10' 被提取: {has_2_10}")
        print(f"  ✓ 元数据前缀被删除: {no_metadata_prefix}")
        
        if has_co and has_0_250 and has_4_20 and has_2_10 and no_metadata_prefix:
            print(f"\n  ✓ 测试通过 - 所有关键特征都正确提取")
        else:
            print(f"\n  ✗ 测试失败 - 部分特征提取失败")
            
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_api_metadata_prefix()
