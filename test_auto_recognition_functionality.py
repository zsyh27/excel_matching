#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试自动识别功能"""

import sys
sys.path.insert(0, 'backend')

import requests
import json
import time

def test_device_type_recognition():
    """测试设备类型识别功能"""
    
    print("=" * 80)
    print("测试设备类型识别功能")
    print("=" * 80)
    
    # 测试用例
    test_cases = [
        "CO浓度探测器",
        "温度传感器",
        "蝶阀",
        "压力变送器",
        "空气质量传感器",
        "温湿度传感器",
        "co",  # 测试关键词推断
        "温度",  # 测试前缀关键词
        "不存在的设备类型"
    ]
    
    base_url = "http://localhost:5000"
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. 测试文本: '{text}'")
        print("-" * 50)
        
        try:
            # 调用智能提取API
            response = requests.post(
                f"{base_url}/api/intelligent-extraction/extract",
                json={"text": text},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    device_type = result['data']['device_type']
                    
                    print(f"✅ 识别成功")
                    print(f"   设备类型: {device_type.get('sub_type', '未识别')}")
                    print(f"   分类: {device_type.get('main_type', '未知')}")
                    print(f"   置信度: {device_type.get('confidence', 0) * 100:.1f}%")
                    print(f"   识别模式: {device_type.get('mode', '未知')}")
                    print(f"   关键词: {device_type.get('keywords', [])}")
                    
                    # 验证显示格式
                    display_type = device_type.get('sub_type') or device_type.get('main_type') or '未识别'
                    category = device_type.get('main_type', '未知')
                    
                    print(f"   前端显示格式:")
                    print(f"     设备类型: {display_type}")
                    print(f"     分类: {category}")
                    
                else:
                    print(f"❌ 识别失败: {result.get('error', {}).get('message', '未知错误')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接失败: 后端服务未启动 (http://localhost:5000)")
            break
        except Exception as e:
            print(f"❌ 请求失败: {e}")
        
        # 模拟防抖延迟
        if i < len(test_cases):
            time.sleep(0.1)
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

def test_mode_descriptions():
    """测试识别模式描述"""
    
    print("\n" + "=" * 80)
    print("识别模式说明")
    print("=" * 80)
    
    modes = {
        'exact': '精确匹配 - 完全匹配设备类型名称，置信度100%',
        'fuzzy': '模糊匹配 - 部分匹配设备类型名称，置信度90%',
        'keyword': '关键词匹配 - 通过关键词组合匹配，置信度80%',
        'inference': '类型推断 - 根据前缀关键词推断类型，置信度70%',
        'none': '无法识别 - 无法识别设备类型'
    }
    
    for mode, description in modes.items():
        print(f"• {mode}: {description}")

def test_keyword_explanations():
    """测试关键词解释"""
    
    print("\n" + "=" * 80)
    print("关键词解释示例")
    print("=" * 80)
    
    examples = [
        {
            'keywords': ['CO'],
            'explanation': '通过关键词"CO"识别出设备类型'
        },
        {
            'keywords': ['温度'],
            'explanation': '通过关键词"温度"识别出设备类型'
        },
        {
            'keywords': ['压力传感器'],
            'explanation': '通过关键词"压力传感器"识别出设备类型'
        },
        {
            'keywords': [],
            'explanation': '无关键词'
        }
    ]
    
    for example in examples:
        keywords = example['keywords']
        explanation = example['explanation']
        
        print(f"关键词: {keywords}")
        print(f"解释: {explanation}")
        print()

if __name__ == "__main__":
    print("🚀 开始测试自动识别功能")
    
    # 测试设备类型识别
    test_device_type_recognition()
    
    # 显示模式说明
    test_mode_descriptions()
    
    # 显示关键词解释
    test_keyword_explanations()
    
    print("\n🎉 测试完成！")
    print("\n📝 前端功能验证:")
    print("1. 在设备类型模式页面的测试区域输入文本")
    print("2. 验证500ms防抖功能是否正常工作")
    print("3. 验证鼠标移开时自动触发识别")
    print("4. 验证识别结果显示格式是否正确")
    print("5. 验证识别模式和关键词的详细说明")