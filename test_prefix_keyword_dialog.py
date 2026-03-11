#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试前缀关键词对话框功能"""

import sys
sys.path.insert(0, 'backend')

import requests
import json

def test_prefix_keyword_functionality():
    """测试前缀关键词功能"""
    
    print("=" * 80)
    print("测试前缀关键词对话框功能")
    print("=" * 80)
    
    base_url = 'http://localhost:5000'
    
    # 1. 测试获取基础设备类型
    print("\n1. 测试获取基础设备类型")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/devices/types-from-database")
        
        if response.status_code != 200:
            print(f"❌ API调用失败: {response.status_code}")
            return
            
        result = response.json()
        
        if not result.get('success'):
            print(f"❌ API返回错误: {result.get('error_message', '未知错误')}")
            return
        
        data = result.get('data', {})
        device_types = data.get('device_types', [])
        categorized = data.get('categorized', {})
        
        print(f"✅ 获取到 {len(device_types)} 种设备类型")
        
        # 显示分类统计
        for category, types in categorized.items():
            print(f"   {category}: {len(types)} 种")
            for device_type in types[:3]:  # 只显示前3个
                print(f"     - {device_type['type']} ({device_type['count']}个)")
            if len(types) > 3:
                print(f"     ... 还有 {len(types) - 3} 种")
        
        # 提取所有设备类型名称（用于前缀关键词选择）
        all_types = []
        for category in categorized.values():
            for item in category:
                if item['type'] not in all_types:
                    all_types.append(item['type'])
        
        all_types.sort()
        print(f"\n✅ 可用于前缀关键词的设备类型: {len(all_types)} 种")
        print(f"   示例: {all_types[:5]}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return
    
    # 2. 测试获取当前配置
    print("\n2. 测试获取当前前缀关键词配置")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/config")
        
        if response.status_code != 200:
            print(f"❌ API调用失败: {response.status_code}")
            return
            
        result = response.json()
        
        if not result.get('success'):
            print(f"❌ API返回错误: {result.get('error_message', '未知错误')}")
            return
        
        config = result.get('config', {})
        ie_config = config.get('intelligent_extraction', {})
        device_type_config = ie_config.get('device_type_recognition', {})
        prefix_keywords = device_type_config.get('prefix_keywords', {})
        
        print(f"✅ 当前前缀关键词配置: {len(prefix_keywords)} 个")
        
        for prefix, types in prefix_keywords.items():
            print(f"   {prefix} → {types}")
        
        if not prefix_keywords:
            print("   暂无前缀关键词配置")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return
    
    # 3. 测试前缀关键词识别效果
    print("\n3. 测试前缀关键词识别效果")
    print("-" * 40)
    
    test_cases = [
        "室内温度传感器",
        "室外CO浓度探测器", 
        "管道压力变送器",
        "电动蝶阀",
        "手动球阀"
    ]
    
    for test_text in test_cases:
        print(f"\n测试文本: {test_text}")
        
        try:
            response = requests.post(
                f"{base_url}/api/intelligent-extraction/extract",
                json={'text': test_text},
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
            
            print(f"   设备类型: {device_type.get('sub_type', device_type.get('main_type', '未识别'))}")
            print(f"   分类: {device_type.get('main_type', '未知')}")
            print(f"   置信度: {device_type.get('confidence', 0) * 100:.1f}%")
            print(f"   识别模式: {device_type.get('mode', 'unknown')}")
            print(f"   关键词: {device_type.get('keywords', [])}")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    print("\n" + "=" * 80)
    print("前缀关键词对话框功能测试完成")
    print("=" * 80)
    
    # 输出前端使用说明
    print("\n📋 前端对话框功能说明:")
    print("1. 点击'+ 添加前缀词'按钮打开对话框")
    print("2. 输入前缀关键词（如：室内、室外、管道）")
    print("3. 从下拉列表中选择一个或多个关联的设备类型")
    print("4. 设备类型列表来自数据库中的实际设备类型")
    print("5. 支持编辑和删除现有的前缀关键词")
    print("6. 前缀关键词用于提高设备类型识别的准确率")
    
    print("\n💡 使用建议:")
    print("- 添加常见的位置前缀：室内、室外、管道、风管等")
    print("- 添加功能前缀：电动、手动、自动、智能等") 
    print("- 添加材质前缀：不锈钢、铸铁、塑料等")
    print("- 每个前缀可以关联多个设备类型")

if __name__ == '__main__':
    test_prefix_keyword_functionality()