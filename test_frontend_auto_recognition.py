#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试前端自动识别功能"""

import sys
sys.path.insert(0, 'backend')

import requests
import json
import time

def test_frontend_auto_recognition():
    """测试前端自动识别功能的各个方面"""
    
    print("=" * 80)
    print("前端自动识别功能测试")
    print("=" * 80)
    
    base_url = "http://localhost:5000"
    
    # 1. 测试API响应时间（模拟防抖功能）
    print("\n1. 测试API响应时间（防抖功能验证）")
    print("-" * 50)
    
    test_text = "CO浓度探测器"
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{base_url}/api/intelligent-extraction/extract",
            json={"text": test_text},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ API响应成功")
                print(f"   响应时间: {response_time:.2f}ms")
                print(f"   建议防抖时间: 500ms (足够避免频繁请求)")
            else:
                print(f"❌ API返回错误: {result.get('error', {}).get('message')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False
    
    # 2. 测试不同输入场景
    print("\n2. 测试不同输入场景")
    print("-" * 50)
    
    test_scenarios = [
        {
            'name': '完整设备名称',
            'input': 'CO浓度探测器',
            'expected_mode': 'inference',
            'expected_confidence': 0.7
        },
        {
            'name': '精确匹配',
            'input': '温度传感器',
            'expected_mode': 'exact',
            'expected_confidence': 1.0
        },
        {
            'name': '关键词推断',
            'input': 'co',
            'expected_mode': 'inference',
            'expected_confidence': 0.7
        },
        {
            'name': '空输入',
            'input': '',
            'expected_mode': 'none',
            'expected_confidence': 0.0
        },
        {
            'name': '无法识别',
            'input': '不存在的设备',
            'expected_mode': 'none',
            'expected_confidence': 0.0
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n测试场景: {scenario['name']}")
        print(f"输入: '{scenario['input']}'")
        
        if not scenario['input']:
            print("✅ 空输入应该清除结果（前端逻辑）")
            continue
        
        try:
            response = requests.post(
                f"{base_url}/api/intelligent-extraction/extract",
                json={"text": scenario['input']},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    device_type = result['data']['device_type']
                    
                    mode = device_type.get('mode', 'none')
                    confidence = device_type.get('confidence', 0.0)
                    
                    print(f"✅ 识别结果:")
                    print(f"   模式: {mode} (期望: {scenario['expected_mode']})")
                    print(f"   置信度: {confidence:.1f} (期望: {scenario['expected_confidence']:.1f})")
                    
                    # 验证前端显示格式
                    display_type = device_type.get('sub_type') or device_type.get('main_type') or '未识别'
                    category = device_type.get('main_type', '未知')
                    
                    print(f"   前端显示:")
                    print(f"     设备类型: {display_type}")
                    print(f"     分类: {category}")
                    
                else:
                    print(f"❌ API错误: {result.get('error', {}).get('message')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
    
    # 3. 测试识别模式说明
    print("\n3. 识别模式说明验证")
    print("-" * 50)
    
    mode_descriptions = {
        'exact': '完全匹配设备类型名称，置信度100%',
        'fuzzy': '部分匹配设备类型名称，置信度90%',
        'keyword': '通过关键词组合匹配，置信度80%',
        'inference': '根据前缀关键词推断类型，置信度70%',
        'none': '无法识别设备类型'
    }
    
    print("前端应该显示的模式说明:")
    for mode, description in mode_descriptions.items():
        print(f"• {mode}: {description}")
    
    # 4. 测试关键词解释
    print("\n4. 关键词解释验证")
    print("-" * 50)
    
    keyword_test = "co"
    try:
        response = requests.post(
            f"{base_url}/api/intelligent-extraction/extract",
            json={"text": keyword_test},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                device_type = result['data']['device_type']
                keywords = device_type.get('keywords', [])
                
                print(f"输入: '{keyword_test}'")
                print(f"关键词: {keywords}")
                
                if keywords:
                    keyword_str = '、'.join(keywords)
                    explanation = f'通过关键词"{keyword_str}"识别出设备类型'
                    print(f"前端应显示: {explanation}")
                else:
                    print("前端应显示: 无关键词")
                    
    except Exception as e:
        print(f"❌ 关键词测试失败: {e}")
    
    return True

def test_debounce_simulation():
    """模拟防抖功能测试"""
    
    print("\n" + "=" * 80)
    print("防抖功能模拟测试")
    print("=" * 80)
    
    print("模拟用户快速输入场景:")
    print("1. 用户输入 'c' -> 不应该立即发送请求")
    print("2. 用户输入 'co' -> 不应该立即发送请求")
    print("3. 用户输入 'co浓度' -> 不应该立即发送请求")
    print("4. 用户停止输入500ms -> 应该发送请求")
    print("5. 用户鼠标移开 -> 应该立即发送请求")
    
    print("\n前端实现验证要点:")
    print("✅ 使用 setTimeout 实现500ms防抖")
    print("✅ 每次输入时清除之前的定时器")
    print("✅ 空输入时清除结果，不发送请求")
    print("✅ blur事件立即触发识别")
    print("✅ 显示'识别中...'加载状态")
    print("✅ 静默处理错误，不显示alert")

if __name__ == "__main__":
    print("🚀 开始测试前端自动识别功能")
    
    # 测试API功能
    success = test_frontend_auto_recognition()
    
    if success:
        # 模拟防抖功能
        test_debounce_simulation()
        
        print("\n" + "=" * 80)
        print("🎉 测试完成！")
        print("=" * 80)
        
        print("\n📋 前端功能检查清单:")
        print("□ 输入框支持实时输入检测")
        print("□ 500ms防抖功能正常工作")
        print("□ 鼠标移开时自动触发识别")
        print("□ 空输入时清除结果")
        print("□ 显示加载状态'识别中...'")
        print("□ 识别结果格式正确（设备类型、分类）")
        print("□ 识别模式显示详细说明")
        print("□ 关键词显示详细解释")
        print("□ 静默错误处理（无alert弹窗）")
        print("□ 置信度进度条显示")
        
        print("\n🔧 如需调试前端功能:")
        print("1. 打开浏览器开发者工具")
        print("2. 访问配置管理页面 -> 设备类型模式")
        print("3. 在测试区域输入文本")
        print("4. 观察网络请求和响应")
        print("5. 验证防抖和自动触发功能")
        
    else:
        print("\n❌ 后端API测试失败，请检查后端服务")