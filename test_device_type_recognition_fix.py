#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试设备类型识别功能修复

验证设备类型模式页面的测试区域专门测试设备类型识别功能
"""

import requests
import json

def test_device_type_recognition_api():
    """测试设备类型识别API"""
    base_url = "http://localhost:5000"
    
    test_cases = [
        "CO浓度探测器",
        "温度传感器", 
        "蝶阀",
        "座阀调节型执行器",
        "压力变送器",
        "流量计",
        "智能照明设备"
    ]
    
    print("=" * 80)
    print("设备类型识别API测试")
    print("=" * 80)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_text}")
        print("-" * 60)
        
        try:
            # 调用设备类型识别API
            response = requests.post(
                f'{base_url}/api/intelligent-extraction/extract',
                json={'text': test_text},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    data = result['data']
                    device_type = data.get('device_type', {})
                    
                    print(f"✅ 识别成功:")
                    print(f"   主类型: {device_type.get('main_type', '未识别')}")
                    print(f"   子类型: {device_type.get('sub_type', '未识别')}")
                    print(f"   置信度: {(device_type.get('confidence', 0) * 100):.1f}%")
                    print(f"   识别模式: {device_type.get('mode', '未知')}")
                    
                    keywords = device_type.get('keywords', [])
                    if keywords:
                        print(f"   关键词: {', '.join(keywords)}")
                    else:
                        print(f"   关键词: 无")
                    
                else:
                    print(f"❌ API返回错误: {result.get('error', {}).get('message', '未知错误')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"   响应: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
        except Exception as e:
            print(f"❌ 其他错误: {e}")
    
    print("\n" + "=" * 80)
    print("测试完成")

def test_frontend_functionality():
    """测试前端功能指南"""
    print("\n" + "=" * 80)
    print("前端功能测试指南")
    print("=" * 80)
    
    print("\n1. 页面访问:")
    print("   配置管理 → 智能特征提取 → 设备类型模式")
    
    print("\n2. 检查页面结构:")
    print("   ✅ 基础设备类型区域（只显示实际存在的分类）")
    print("   ✅ 前缀关键词管理区域")
    print("   ✅ 设备类型识别测试区域（专门测试设备类型识别）")
    
    print("\n3. 测试设备类型识别:")
    print("   ✅ 标题应该是 '设备类型识别测试'")
    print("   ✅ 输入框提示: '输入设备描述进行测试，例如：CO浓度探测器、温度传感器、蝶阀'")
    print("   ✅ 按钮文字: '🎯 测试识别'")
    
    print("\n4. 验证识别结果显示:")
    print("   ✅ 显示置信度进度条")
    print("   ✅ 显示主类型和子类型")
    print("   ✅ 显示识别模式（精确/模糊/关键词/推断）")
    print("   ✅ 显示关键词列表")
    
    print("\n5. 测试用例建议:")
    print("   - CO浓度探测器 → 应识别为空气质量传感器")
    print("   - 温度传感器 → 应识别为温度传感器")
    print("   - 蝶阀 → 应识别为蝶阀")
    print("   - 座阀调节型执行器 → 应识别为执行器")
    
    print("\n6. 功能对比:")
    print("   ❌ 不应该显示五步流程预览")
    print("   ❌ 不应该显示参数提取、匹配结果等")
    print("   ✅ 只专注于设备类型识别功能")
    print("   ✅ 界面简洁，功能明确")

def compare_with_full_preview():
    """对比完整预览功能"""
    print("\n" + "=" * 80)
    print("功能定位对比")
    print("=" * 80)
    
    print("\n📍 设备类型模式页面 - 设备类型识别测试:")
    print("   🎯 专门测试设备类型识别功能")
    print("   📊 显示识别结果：主类型、子类型、置信度、模式、关键词")
    print("   🔧 用于调试和验证设备类型识别配置")
    print("   💡 帮助用户理解设备类型识别的工作原理")
    
    print("\n📍 其他页面可能需要的完整五步预览:")
    print("   🔍 完整的五步智能提取流程展示")
    print("   📈 包含参数提取、辅助信息、智能匹配、UI预览")
    print("   ⚡ 性能统计和调试信息")
    print("   🎛️ 适合放在专门的'智能提取预览'或'系统测试'页面")
    
    print("\n✅ 修复后的优势:")
    print("   - 功能定位明确，专注于设备类型识别")
    print("   - 界面简洁，不会让用户困惑")
    print("   - 测试结果直观，便于配置调试")
    print("   - 符合页面的主要功能（设备类型模式配置）")

if __name__ == "__main__":
    # 测试API
    test_device_type_recognition_api()
    
    # 显示前端测试指南
    test_frontend_functionality()
    
    # 功能对比说明
    compare_with_full_preview()