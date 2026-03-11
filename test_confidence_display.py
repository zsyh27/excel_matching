#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试置信度显示功能"""

import sys
sys.path.insert(0, 'backend')

import requests
import json

def test_confidence_display():
    """测试置信度显示功能"""
    
    print("=" * 80)
    print("测试置信度显示功能")
    print("=" * 80)
    
    # 测试用例
    test_cases = [
        {
            'text': 'CO浓度探测器',
            'expected_mode': 'inference',
            'expected_confidence_range': (0.6, 0.8)
        },
        {
            'text': '温度传感器',
            'expected_mode': 'exact',
            'expected_confidence_range': (0.9, 1.0)
        },
        {
            'text': '蝶阀',
            'expected_mode': 'exact',
            'expected_confidence_range': (0.9, 1.0)
        },
        {
            'text': '压力变送器',
            'expected_mode': 'fuzzy',
            'expected_confidence_range': (0.8, 1.0)
        }
    ]
    
    base_url = 'http://localhost:5000'
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {case['text']}")
        print("-" * 40)
        
        try:
            # 调用智能提取API
            response = requests.post(
                f"{base_url}/api/intelligent-extraction/extract",
                json={'text': case['text']},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                print(f"❌ API调用失败: {response.status_code}")
                continue
                
            result = response.json()
            
            if not result.get('success'):
                print(f"❌ API返回错误: {result.get('error', {}).get('message', '未知错误')}")
                continue
            
            device_type = result.get('data', {}).get('device_type', {})
            
            # 检查结果
            confidence = device_type.get('confidence', 0)
            mode = device_type.get('mode', 'unknown')
            main_type = device_type.get('main_type', '')
            sub_type = device_type.get('sub_type', '')
            keywords = device_type.get('keywords', [])
            
            print(f"✅ 识别结果:")
            print(f"   设备类型: {sub_type or main_type}")
            print(f"   分类: {main_type}")
            print(f"   置信度: {confidence * 100:.1f}%")
            print(f"   识别模式: {mode}")
            print(f"   关键词: {keywords}")
            
            # 验证置信度范围
            min_conf, max_conf = case['expected_confidence_range']
            if min_conf <= confidence <= max_conf:
                print(f"✅ 置信度在预期范围内: {min_conf * 100:.1f}% - {max_conf * 100:.1f}%")
            else:
                print(f"⚠️ 置信度超出预期范围: 预期 {min_conf * 100:.1f}% - {max_conf * 100:.1f}%, 实际 {confidence * 100:.1f}%")
            
            # 验证识别模式
            if mode == case['expected_mode']:
                print(f"✅ 识别模式符合预期: {mode}")
            else:
                print(f"⚠️ 识别模式不符合预期: 预期 {case['expected_mode']}, 实际 {mode}")
            
            # 测试置信度分级
            if confidence >= 0.9:
                level = "高"
                css_class = "high"
            elif confidence >= 0.7:
                level = "中"
                css_class = "medium"
            else:
                level = "低"
                css_class = "low"
            
            print(f"✅ 置信度分级: {level} (CSS类: {css_class})")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    print("\n" + "=" * 80)
    print("置信度显示功能测试完成")
    print("=" * 80)
    
    # 输出前端使用说明
    print("\n📋 前端使用说明:")
    print("1. 置信度显示在单独的结果项中")
    print("2. 置信度值根据等级显示不同颜色:")
    print("   - 高 (≥90%): 绿色 (#4caf50)")
    print("   - 中 (70%-89%): 橙色 (#ff9800)")
    print("   - 低 (<70%): 红色 (#f44336)")
    print("3. 鼠标悬停在❓图标上显示详细解释")
    print("4. 解释包含识别模式、置信度数值和准确度评价")

if __name__ == '__main__':
    test_confidence_display()