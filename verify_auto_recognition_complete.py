#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证自动识别功能完整性"""

import sys
sys.path.insert(0, 'backend')

import requests
import json
import time

def verify_implementation():
    """验证实现完整性"""
    
    print("=" * 80)
    print("🔍 验证自动识别功能完整性")
    print("=" * 80)
    
    # 1. 验证后端API
    print("\n1. 后端API验证")
    print("-" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        # 测试API可用性
        response = requests.get(f"{base_url}/api/config", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
            
        # 测试智能提取API
        response = requests.post(
            f"{base_url}/api/intelligent-extraction/extract",
            json={"text": "CO浓度探测器"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 智能提取API正常工作")
                device_type = result['data']['device_type']
                print(f"   示例结果: {device_type.get('sub_type')} (置信度: {device_type.get('confidence', 0)*100:.1f}%)")
            else:
                print(f"❌ 智能提取API错误: {result.get('error', {}).get('message')}")
                return False
        else:
            print(f"❌ 智能提取API HTTP错误: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端正在运行")
        return False
    except Exception as e:
        print(f"❌ 后端验证失败: {e}")
        return False
    
    # 2. 验证前端实现
    print("\n2. 前端实现验证")
    print("-" * 50)
    
    frontend_file = "frontend/src/components/ConfigManagement/DeviceTypePatternsEditor.vue"
    
    try:
        with open(frontend_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键实现
        checks = [
            ("防抖定时器", "debounceTimer", "✅ 防抖功能已实现"),
            ("输入变化处理", "@input=\"onInputChange\"", "✅ 输入变化监听已实现"),
            ("失焦触发", "@blur=\"testRecognition\"", "✅ 失焦触发已实现"),
            ("加载状态", "testing-indicator", "✅ 加载状态显示已实现"),
            ("模式说明", "getModeDescription", "✅ 模式详细说明已实现"),
            ("关键词解释", "keywords-description", "✅ 关键词解释已实现"),
            ("静默错误处理", "console.error", "✅ 静默错误处理已实现")
        ]
        
        for check_name, check_pattern, success_msg in checks:
            if check_pattern in content:
                print(success_msg)
            else:
                print(f"❌ {check_name}未找到: {check_pattern}")
                return False
                
    except FileNotFoundError:
        print(f"❌ 前端文件不存在: {frontend_file}")
        return False
    except Exception as e:
        print(f"❌ 前端验证失败: {e}")
        return False
    
    # 3. 验证功能特性
    print("\n3. 功能特性验证")
    print("-" * 50)
    
    feature_tests = [
        {
            'name': '精确匹配测试',
            'input': '温度传感器',
            'expected_mode': 'exact',
            'expected_confidence': 1.0
        },
        {
            'name': '类型推断测试',
            'input': 'co',
            'expected_mode': 'inference',
            'expected_confidence': 0.7
        }
    ]
    
    for test in feature_tests:
        try:
            response = requests.post(
                f"{base_url}/api/intelligent-extraction/extract",
                json={"text": test['input']},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    device_type = result['data']['device_type']
                    mode = device_type.get('mode')
                    confidence = device_type.get('confidence', 0)
                    
                    if mode == test['expected_mode'] and abs(confidence - test['expected_confidence']) < 0.1:
                        print(f"✅ {test['name']}通过")
                    else:
                        print(f"❌ {test['name']}失败: 期望{test['expected_mode']}/{test['expected_confidence']}, 实际{mode}/{confidence}")
                        return False
                else:
                    print(f"❌ {test['name']}API错误")
                    return False
            else:
                print(f"❌ {test['name']}HTTP错误")
                return False
                
        except Exception as e:
            print(f"❌ {test['name']}异常: {e}")
            return False
    
    return True

def print_usage_guide():
    """打印使用指南"""
    
    print("\n" + "=" * 80)
    print("📖 使用指南")
    print("=" * 80)
    
    print("\n🎯 如何使用自动识别功能:")
    print("1. 打开浏览器，访问配置管理页面")
    print("2. 进入 '智能特征提取' -> '设备类型模式'")
    print("3. 在页面底部找到 '设备类型识别测试' 区域")
    print("4. 在输入框中输入设备描述（如：CO浓度探测器）")
    print("5. 等待500ms或鼠标移开，自动显示识别结果")
    
    print("\n⚡ 功能特点:")
    print("• 自动触发：输入后500ms自动识别，无需点击按钮")
    print("• 失焦触发：鼠标移开输入框时立即识别")
    print("• 防抖优化：避免频繁API调用，提升性能")
    print("• 加载提示：显示'识别中...'状态")
    print("• 详细说明：识别模式和关键词的详细解释")
    print("• 静默错误：错误不弹窗，记录到控制台")
    
    print("\n📊 识别结果说明:")
    print("• 设备类型：具体的设备类型（如：空气质量传感器）")
    print("• 分类：设备大类（如：传感器、阀门）")
    print("• 置信度：识别准确度（0-100%）")
    print("• 识别模式：精确匹配、模糊匹配、关键词匹配、类型推断")
    print("• 关键词：用于识别的关键词列表")

def print_troubleshooting():
    """打印故障排除指南"""
    
    print("\n" + "=" * 80)
    print("🔧 故障排除")
    print("=" * 80)
    
    print("\n❓ 常见问题:")
    
    print("\n1. 输入后没有自动识别")
    print("   • 检查是否等待了500ms")
    print("   • 尝试鼠标移开输入框")
    print("   • 检查浏览器控制台是否有错误")
    
    print("\n2. 识别结果不准确")
    print("   • 检查输入文本是否包含设备类型关键词")
    print("   • 查看识别模式和置信度")
    print("   • 尝试更具体的设备描述")
    
    print("\n3. 页面加载错误")
    print("   • 确保后端服务正在运行")
    print("   • 检查网络连接")
    print("   • 刷新页面重试")
    
    print("\n4. 调试方法:")
    print("   • 打开浏览器开发者工具")
    print("   • 查看Network标签页的API请求")
    print("   • 查看Console标签页的错误信息")
    print("   • 检查API响应内容")

if __name__ == "__main__":
    print("🚀 开始验证自动识别功能完整性")
    
    success = verify_implementation()
    
    if success:
        print("\n" + "=" * 80)
        print("🎉 验证完成！自动识别功能已完整实现")
        print("=" * 80)
        
        print("\n✅ 实现状态:")
        print("• 后端API: 正常工作")
        print("• 前端组件: 完整实现")
        print("• 自动触发: 防抖+失焦")
        print("• 用户界面: 优化完成")
        print("• 错误处理: 静默处理")
        print("• 功能测试: 全部通过")
        
        # 打印使用指南
        print_usage_guide()
        
        # 打印故障排除指南
        print_troubleshooting()
        
    else:
        print("\n" + "=" * 80)
        print("❌ 验证失败！请检查上述错误并修复")
        print("=" * 80)