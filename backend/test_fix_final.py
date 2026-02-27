#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终验证测试
"""

import json
import sys
import importlib

# 强制重新加载模块
if 'modules.text_preprocessor' in sys.modules:
    del sys.modules['modules.text_preprocessor']

from modules.text_preprocessor import TextPreprocessor

def test():
    """测试"""
    
    test_text = """型号：V5011N1040/U
 通径：1/2"(DN15)
 阀体类型：二通座阀 
 适用介质：水"""
    
    print("=" * 80)
    print("特征提取最终验证")
    print("=" * 80)
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    print(f"\n输入文本:")
    print(test_text)
    
    result = preprocessor.preprocess(test_text)
    
    print(f"\n归一化后: {repr(result.normalized)}")
    print(f"\n提取特征:")
    for i, feature in enumerate(result.features, 1):
        print(f"  {i}. {repr(feature)}")
    
    # 验证
    print(f"\n验证结果:")
    
    expected = ['v5011n1040/u', '1/2"', 'dn15', '二通座阀', '水']
    should_not_have = ['型号:', '通径:', '阀体类型:', '适用介质:']
    
    # 检查期望特征
    all_found = True
    for exp in expected:
        if exp in result.features:
            print(f"  ✓ 找到: {repr(exp)}")
        else:
            print(f"  ✗ 缺失: {repr(exp)}")
            all_found = False
    
    # 检查不应该有的内容
    no_bad = True
    for bad in should_not_have:
        found_in = []
        for feature in result.features:
            if bad in feature:
                found_in.append(feature)
        
        if found_in:
            print(f"  ✗ 不应该包含 {repr(bad)}，但在这些特征中找到: {found_in}")
            no_bad = False
    
    if no_bad:
        print(f"  ✓ 没有元数据前缀")
    
    success = all_found and no_bad
    
    print("\n" + "=" * 80)
    if success:
        print("✓ 修复成功！")
    else:
        print("✗ 还有问题")
    print("=" * 80)
    
    return success

if __name__ == '__main__':
    try:
        success = test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
