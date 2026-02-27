#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试元数据关键词提取问题
"""

import json
import sys

def test_metadata_extraction():
    """测试元数据关键词提取"""
    
    # 测试文本
    test_text = """型号：V5011N1040/U
 通径：1/2"(DN15)
 阀体类型：二通座阀 
 适用介质：水"""
    
    print("=" * 80)
    print("元数据关键词提取测试")
    print("=" * 80)
    
    print(f"\n原始文本:")
    print(test_text)
    print(f"\n原始文本（repr）:")
    print(repr(test_text))
    
    # 加载配置
    print("\n1. 加载配置")
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print(f"   - metadata_keywords: {config.get('metadata_keywords', [])}")
    print(f"   - feature_split_chars: {config.get('feature_split_chars', [])}")
    
    # 初始化预处理器
    print("\n2. 初始化预处理器")
    from modules.text_preprocessor import TextPreprocessor
    preprocessor = TextPreprocessor(config)
    
    print(f"   - metadata_keywords数量: {len(preprocessor.metadata_keywords)}")
    print(f"   - split_pattern: {preprocessor.split_pattern}")
    
    # 执行预处理
    print("\n3. 执行预处理")
    result = preprocessor.preprocess(test_text)
    
    print(f"\n预处理结果:")
    print(f"   - 原始: {result.original}")
    print(f"   - 清理后: {result.cleaned}")
    print(f"   - 归一化: {result.normalized}")
    print(f"   - 提取特征: {result.features}")
    
    # 分析问题
    print("\n4. 问题分析:")
    
    # 检查是否识别到元数据关键词
    metadata_found = []
    metadata_not_found = []
    
    expected_metadata = ["型号", "通径", "阀体类型", "适用介质"]
    for keyword in expected_metadata:
        if keyword in test_text:
            if any(keyword in feature for feature in result.features):
                metadata_found.append(keyword)
            else:
                metadata_not_found.append(keyword)
    
    if metadata_found:
        print(f"   ✓ 识别到的元数据关键词: {metadata_found}")
    
    if metadata_not_found:
        print(f"   ✗ 未识别的元数据关键词: {metadata_not_found}")
    
    # 检查分隔符
    print(f"\n5. 分隔符检查:")
    print(f"   - 原文中的换行符: {test_text.count(chr(10))} 个")
    print(f"   - 配置的分隔符: {config.get('feature_split_chars', [])}")
    
    # 检查"+"是否在分隔符中
    if '+' in config.get('feature_split_chars', []):
        print(f"   ✓ '+' 在分隔符配置中")
    else:
        print(f"   ✗ '+' 不在分隔符配置中")
    
    # 检查换行符
    if '\\n' in config.get('feature_split_chars', []) or '\n' in config.get('feature_split_chars', []):
        print(f"   ✓ 换行符在分隔符配置中")
    else:
        print(f"   ✗ 换行符不在分隔符配置中")
    
    # 详细分析特征提取过程
    print(f"\n6. 详细分析特征提取:")
    print(f"   清理后的文本: {repr(result.cleaned)}")
    print(f"   归一化后的文本: {repr(result.normalized)}")
    
    # 手动测试分割
    print(f"\n7. 手动测试分割:")
    import re
    split_chars = config.get('feature_split_chars', [])
    # 转义特殊字符
    escaped_chars = [re.escape(char) for char in split_chars]
    pattern = '|'.join(escaped_chars)
    print(f"   分割模式: {pattern}")
    
    manual_split = re.split(pattern, result.normalized)
    print(f"   手动分割结果: {manual_split}")
    
    return len(metadata_not_found) == 0

if __name__ == '__main__':
    try:
        success = test_metadata_extraction()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
