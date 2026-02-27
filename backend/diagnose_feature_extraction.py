#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断特征提取问题
"""

import json
import re

def diagnose():
    """诊断特征提取"""
    
    # 测试文本
    test_text = """型号：V5011N1040/U
 通径：1/2"(DN15)
 阀体类型：二通座阀 
 适用介质：水"""
    
    print("=" * 80)
    print("特征提取问题诊断")
    print("=" * 80)
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    from modules.text_preprocessor import TextPreprocessor
    preprocessor = TextPreprocessor(config)
    
    # 直接使用preprocess方法
    print("\n完整预处理:")
    result = preprocessor.preprocess(test_text)
    print(f"原始: {repr(result.original)}")
    print(f"清理后: {repr(result.cleaned)}")
    print(f"归一化后: {repr(result.normalized)}")
    
    # 使用归一化后的文本进行分析
    normalized = result.normalized
    
    # 步骤3: 特征提取 - 详细分析
    print("\n步骤3: 特征提取详细分析")
    
    # 3.1 括号处理
    print("\n3.1 括号处理:")
    bracket_pattern = r'([^()]+)\(([^)]+)\)'
    matches = list(re.finditer(bracket_pattern, normalized))
    print(f"   找到 {len(matches)} 个括号匹配:")
    for i, match in enumerate(matches, 1):
        print(f"   匹配{i}:")
        print(f"     - 括号外: {repr(match.group(1))}")
        print(f"     - 括号内: {repr(match.group(2))}")
    
    # 移除括号部分后的剩余文本
    remaining = re.sub(bracket_pattern, '', normalized)
    print(f"\n   移除括号后的剩余文本: {repr(remaining)}")
    
    # 3.2 分隔符拆分
    print("\n3.2 分隔符拆分:")
    print(f"   分隔符配置: {config.get('feature_split_chars')}")
    print(f"   分割模式: {preprocessor.split_pattern.pattern}")
    
    if preprocessor.split_pattern and remaining:
        split_features = preprocessor.split_pattern.split(remaining)
        print(f"   拆分结果 ({len(split_features)} 个):")
        for i, feature in enumerate(split_features, 1):
            print(f"     {i}. {repr(feature)}")
    
    # 完整的特征提取
    print("\n步骤4: 完整特征提取")
    features = preprocessor.extract_features(normalized)
    print(f"最终特征 ({len(features)} 个):")
    for i, feature in enumerate(features, 1):
        print(f"  {i}. {repr(feature)}")
    
    # 分析问题
    print("\n" + "=" * 80)
    print("问题分析")
    print("=" * 80)
    
    print("\n问题1: 括号处理")
    print("   当前逻辑: 先提取括号外的内容，再提取括号内的内容")
    print("   问题: '型号:v5011n1040/u+通径:1/2\"' 被当作括号外的内容")
    print("   原因: 括号匹配模式 ([^()]+)\\(([^)]+)\\) 会匹配到 '通径:1/2\"(dn15)'")
    print("         其中 '型号:v5011n1040/u+通径:1/2\"' 是括号外的内容")
    print("   期望: 应该先按分隔符拆分，再处理每个片段中的括号")
    
    print("\n问题2: 元数据关键词")
    print("   当前逻辑: 过滤掉完全匹配元数据关键词的特征")
    print("   问题: '型号:v5011n1040/u' 包含元数据关键词'型号'，但不会被过滤")
    print("   期望: 应该移除元数据关键词前缀，只保留值部分")
    print("         例如: '型号:v5011n1040/u' -> 'v5011n1040/u'")
    
    print("\n问题3: 分隔符识别")
    print("   当前逻辑: 在归一化后使用分隔符拆分")
    print("   问题: '+' 符号在清理阶段被添加，但在特征提取时没有正确处理")
    print("   期望: 应该在括号处理之前先按分隔符拆分")

if __name__ == '__main__':
    diagnose()
