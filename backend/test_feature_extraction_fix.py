#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证特征提取修复效果
"""

import json
import sys

def test_fix():
    """验证修复效果"""
    
    print("=" * 80)
    print("特征提取修复验证")
    print("=" * 80)
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    from modules.text_preprocessor import TextPreprocessor
    preprocessor = TextPreprocessor(config)
    
    # 测试用例
    test_cases = [
        {
            "name": "用户报告的问题",
            "input": "型号：V5011N1040/U\n通径：1/2\"(DN15)\n阀体类型：二通座阀\n适用介质：水",
            "expected": ["v5011n1040/u", "1/2\"", "dn15", "二通座阀", "水"],
            "should_not_contain": ["型号:", "通径:", "阀体类型:", "适用介质:"]
        },
        {
            "name": "品牌和设备类型",
            "input": "霍尼韦尔室内温度传感器+DC24V+4-20mA",
            "expected_contains": ["霍尼韦尔", "温度传感器", "dc24v", "4-20ma"],
            "should_not_contain": []
        },
        {
            "name": "多个元数据字段",
            "input": "品牌：西门子；型号：DDC-1000；通径：DN50",
            "expected": ["西门子", "ddc-1000", "dn50"],
            "should_not_contain": ["品牌:", "型号:", "通径:"]
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case['name']}")
        print(f"输入: {repr(test_case['input'])}")
        
        result = preprocessor.preprocess(test_case['input'])
        features = result.features
        
        print(f"提取特征: {features}")
        
        # 检查期望的特征
        if 'expected' in test_case:
            missing = []
            for expected in test_case['expected']:
                if expected not in features:
                    missing.append(expected)
            
            if missing:
                print(f"   ✗ 缺少期望的特征: {missing}")
                all_passed = False
            else:
                print(f"   ✓ 所有期望的特征都存在")
        
        if 'expected_contains' in test_case:
            missing = []
            for expected in test_case['expected_contains']:
                if expected not in features:
                    missing.append(expected)
            
            if missing:
                print(f"   ✗ 缺少期望的特征: {missing}")
                all_passed = False
            else:
                print(f"   ✓ 包含所有期望的特征")
        
        # 检查不应该出现的内容
        if test_case['should_not_contain']:
            found = []
            for should_not in test_case['should_not_contain']:
                for feature in features:
                    if should_not in feature:
                        found.append(feature)
                        break
            
            if found:
                print(f"   ✗ 发现不应该出现的内容: {found}")
                all_passed = False
            else:
                print(f"   ✓ 没有不应该出现的内容")
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✓ 所有测试通过！特征提取修复成功")
    else:
        print("✗ 部分测试失败")
    print("=" * 80)
    
    return all_passed

if __name__ == '__main__':
    try:
        success = test_fix()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
