#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试识别模式描述功能"""

import sys
sys.path.insert(0, 'backend')

import requests
import json

def test_recognition_mode_description():
    """测试识别模式描述功能"""
    
    print("=" * 80)
    print("测试识别模式描述功能")
    print("=" * 80)
    
    # 测试用例 - 覆盖不同的识别模式
    test_cases = [
        {
            'text': '温度传感器',
            'expected_mode': 'exact',
            'description': '精确匹配 - 完全匹配设备类型名称'
        },
        {
            'text': '温湿度传感器',
            'expected_mode': 'exact',
            'description': '精确匹配 - 完全匹配设备类型名称'
        },
        {
            'text': 'CO浓度探测器',
            'expected_mode': 'inference',
            'description': '类型推断 - 根据前缀关键词推断类型'
        },
        {
            'text': '蝶阀',
            'expected_mode': 'exact',
            'description': '精确匹配 - 完全匹配设备类型名称'
        },
        {
            'text': '不存在的设备类型',
            'expected_mode': 'none',
            'description': '无法识别设备类型'
        }
    ]
    
    base_url = 'http://localhost:5000'
    
    print("🎯 识别模式及置信度说明:")
    print("   精确匹配: 100% - 完全匹配设备类型名称")
    print("   模糊匹配: 90% - 部分匹配设备类型名称")
    print("   关键词匹配: 80% - 通过关键词组合匹配")
    print("   类型推断: 70% - 根据前缀关键词推断类型")
    print("   无法识别: 0% - 未找到匹配的设备类型")
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {case['text']}")
        print("-" * 50)
        
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
            
            # 提取结果
            confidence = device_type.get('confidence', 0)
            mode = device_type.get('mode', 'unknown')
            main_type = device_type.get('main_type', '')
            sub_type = device_type.get('sub_type', '')
            keywords = device_type.get('keywords', [])
            
            print(f"✅ 识别结果:")
            print(f"   设备类型: {sub_type or main_type or '未识别'}")
            print(f"   分类: {main_type or '未知'}")
            print(f"   置信度: {confidence * 100:.1f}%")
            print(f"   识别模式: {get_mode_text(mode)}")
            print(f"   关键词: {keywords}")
            
            # 显示新的模式描述（统一显示所有模式的置信度）
            mode_description = "精确匹配100% > 模糊匹配90% > 关键词匹配80% > 类型推断70%"
            print(f"   模式说明: {mode_description}")
            
            # 验证识别模式
            if mode == case['expected_mode']:
                print(f"✅ 识别模式符合预期: {mode}")
            else:
                print(f"⚠️ 识别模式不符合预期: 预期 {case['expected_mode']}, 实际 {mode}")
            
            # 验证置信度与模式的对应关系
            expected_confidence = get_expected_confidence(mode)
            if abs(confidence - expected_confidence) < 0.01:  # 允许小的浮点误差
                print(f"✅ 置信度与模式匹配: {confidence * 100:.1f}%")
            else:
                print(f"⚠️ 置信度与模式不匹配: 预期 {expected_confidence * 100:.1f}%, 实际 {confidence * 100:.1f}%")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    print("\n" + "=" * 80)
    print("识别模式描述功能测试完成")
    print("=" * 80)
    
    # 输出前端显示效果说明
    print("\n📋 前端显示效果:")
    print("1. 识别模式显示当前使用的模式（如：精确匹配、类型推断）")
    print("2. 模式描述统一显示所有模式的置信度层级关系")
    print("3. 描述格式：'精确匹配100% > 模糊匹配90% > 关键词匹配80% > 类型推断70%'")
    print("4. 用户可以清楚了解系统支持的所有识别模式及其优先级")
    print("5. 不再针对单个模式显示重复的置信度信息")

def get_mode_text(mode):
    """获取模式显示文本"""
    mode_map = {
        'exact': '精确匹配',
        'fuzzy': '模糊匹配', 
        'keyword': '关键词匹配',
        'inference': '类型推断',
        'none': '无法识别',
        'unknown': '未知'
    }
    return mode_map.get(mode, '未知')

def get_expected_confidence(mode):
    """获取模式对应的预期置信度"""
    confidence_map = {
        'exact': 1.0,
        'fuzzy': 0.9,
        'keyword': 0.8,
        'inference': 0.7,
        'none': 0.0,
        'unknown': 0.0
    }
    return confidence_map.get(mode, 0.0)

if __name__ == '__main__':
    test_recognition_mode_description()