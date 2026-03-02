"""
测试换行符作为分隔符的处理

问题: 用户在配置中添加了 "/n",但实际需要的是换行符 "\n"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.text_preprocessor import TextPreprocessor
import json


def test_current_config():
    """测试当前配置"""
    
    with open('../data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("="*60)
    print("当前配置测试")
    print("="*60)
    print(f"\n当前分隔符配置: {config.get('feature_split_chars', [])}")
    
    # 测试包含换行符的文本
    test_text = "传感器\n2.规格："
    
    print(f"\n测试文本: {repr(test_text)}")
    print(f"文本显示: {test_text}")
    
    preprocessor = TextPreprocessor(config)
    result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"\n智能清理后: {repr(result.intelligent_cleaning_detail.after_text if result.intelligent_cleaning_detail else '无')}")
    print(f"归一化后: {repr(result.normalized)}")
    print(f"提取的特征: {result.features}")
    
    # 检查换行符是否被转换
    if result.intelligent_cleaning_detail:
        after_text = result.intelligent_cleaning_detail.after_text
        if '\n' in after_text:
            print("\n✗ 换行符未被转换")
        else:
            print("\n✓ 换行符已被处理")


def test_with_correct_newline():
    """测试正确的换行符配置"""
    
    with open('../data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 手动修改配置,添加真正的换行符
    config['feature_split_chars'] = ['+', '|', '；', '\n']
    
    print("\n" + "="*60)
    print("使用正确换行符的测试")
    print("="*60)
    print(f"\n修改后的分隔符配置: {repr(config.get('feature_split_chars', []))}")
    
    test_text = "传感器\n2.规格："
    
    print(f"\n测试文本: {repr(test_text)}")
    
    preprocessor = TextPreprocessor(config)
    result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"\n智能清理后: {repr(result.intelligent_cleaning_detail.after_text if result.intelligent_cleaning_detail else '无')}")
    print(f"归一化后: {repr(result.normalized)}")
    print(f"提取的特征: {result.features}")
    
    # 检查换行符是否被转换
    if result.intelligent_cleaning_detail:
        after_text = result.intelligent_cleaning_detail.after_text
        if '\n' in after_text:
            print("\n✗ 换行符未被转换")
        else:
            print("\n✓ 换行符已被转换为 +")


if __name__ == '__main__':
    test_current_config()
    test_with_correct_newline()
