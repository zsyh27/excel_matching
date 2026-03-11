#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试详细的设备类型识别显示

验证优化后的识别结果显示格式
"""

import requests
import json

def test_detailed_display():
    """测试详细显示效果"""
    base_url = "http://localhost:5000"
    
    test_cases = [
        {
            "input": "CO浓度探测器",
            "expected_display": {
                "设备类型": "空气质量传感器",
                "分类": "传感器",
                "识别模式": "类型推断 - 根据前缀关键词推断类型，置信度70%",
                "关键词": "co - 通过关键词\"co\"识别出设备类型"
            }
        },
        {
            "input": "温度传感器",
            "expected_display": {
                "设备类型": "温度传感器",
                "分类": "传感器", 
                "识别模式": "精确匹配 - 完全匹配设备类型名称，置信度100%",
                "关键词": "温度传感器 - 通过关键词\"温度传感器\"识别出设备类型"
            }
        },
        {
            "input": "蝶阀",
            "expected_display": {
                "设备类型": "蝶阀",
                "分类": "阀门",
                "识别模式": "精确匹配 - 完全匹配设备类型名称，置信度100%",
                "关键词": "蝶阀 - 通过关键词\"蝶阀\"识别出设备类型"
            }
        },
        {
            "input": "压力变送器",
            "expected_display": {
                "设备类型": "未识别",
                "分类": "未知",
                "识别模式": "无法识别设备类型",
                "关键词": "无关键词"
            }
        }
    ]
    
    print("=" * 80)
    print("详细设备类型识别显示测试")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        input_text = test_case["input"]
        expected = test_case["expected_display"]
        
        print(f"\n测试用例 {i}: {input_text}")
        print("-" * 60)
        
        try:
            # 调用API
            response = requests.post(
                f'{base_url}/api/intelligent-extraction/extract',
                json={'text': input_text},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    data = result['data']
                    device_type = data.get('device_type', {})
                    
                    # 模拟前端显示逻辑
                    display_device_type = device_type.get('sub_type') or device_type.get('main_type') or '未识别'
                    display_category = device_type.get('main_type') or '未知'
                    
                    # 识别模式描述
                    mode = device_type.get('mode', 'none')
                    mode_descriptions = {
                        'exact': '精确匹配 - 完全匹配设备类型名称，置信度100%',
                        'fuzzy': '模糊匹配 - 部分匹配设备类型名称，置信度90%',
                        'keyword': '关键词匹配 - 通过关键词组合匹配，置信度80%',
                        'inference': '类型推断 - 根据前缀关键词推断类型，置信度70%',
                        'none': '无法识别设备类型'
                    }
                    mode_description = mode_descriptions.get(mode, '未知识别模式')
                    
                    # 关键词描述
                    keywords = device_type.get('keywords', [])
                    if keywords:
                        keywords_description = f"通过关键词\"{', '.join(keywords)}\"识别出设备类型"
                    else:
                        keywords_description = "无关键词"
                    
                    print(f"✅ 实际显示效果:")
                    print(f"   设备类型: {display_device_type}")
                    print(f"   分类: {display_category}")
                    print(f"   置信度: {(device_type.get('confidence', 0) * 100):.1f}%")
                    print(f"   识别模式: {mode_description}")
                    print(f"   关键词: {keywords_description}")
                    
                    print(f"\n📋 期望显示效果:")
                    for key, value in expected.items():
                        print(f"   {key}: {value}")
                    
                    # 验证关键显示项
                    checks = []
                    checks.append(("设备类型", display_device_type, expected["设备类型"]))
                    checks.append(("分类", display_category, expected["分类"]))
                    
                    print(f"\n🔍 验证结果:")
                    all_passed = True
                    for check_name, actual, expected_val in checks:
                        if actual == expected_val:
                            print(f"   ✅ {check_name}: 匹配")
                        else:
                            print(f"   ❌ {check_name}: 不匹配 (实际: {actual}, 期望: {expected_val})")
                            all_passed = False
                    
                    if all_passed:
                        print(f"   🎉 整体验证: 通过")
                    else:
                        print(f"   ⚠️ 整体验证: 部分不匹配")
                    
                else:
                    print(f"❌ API返回错误: {result.get('error', {}).get('message', '未知错误')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print("\n" + "=" * 80)
    print("测试完成")

def show_frontend_display_guide():
    """显示前端显示指南"""
    print("\n" + "=" * 80)
    print("前端显示优化指南")
    print("=" * 80)
    
    print("\n📱 优化后的显示格式:")
    print("""
    🎯 设备类型识别结果                    置信度: 70.0%
    ┌─────────────────────────────────────────────────────┐
    │ 设备类型: 空气质量传感器                              │
    │ 分类: 传感器                                        │
    │                                                   │
    │ 识别模式: 类型推断                                   │
    │          根据前缀关键词推断类型，置信度70%            │
    │                                                   │
    │ 关键词: co                                         │
    │        通过关键词"co"识别出设备类型                  │
    └─────────────────────────────────────────────────────┘
    """)
    
    print("\n🔧 实现要点:")
    print("   1. 设备类型优先显示子类型（具体类型）")
    print("   2. 分类显示主类型（大分类）")
    print("   3. 识别模式包含详细说明和置信度信息")
    print("   4. 关键词显示具体匹配的词和解释")
    
    print("\n🎨 样式建议:")
    print("   - 识别模式使用两行显示：模式名称 + 详细说明")
    print("   - 关键词使用两行显示：关键词标签 + 匹配说明")
    print("   - 详细说明使用较小字体和斜体")
    print("   - 保持整体布局的清晰和美观")
    
    print("\n📋 测试验证:")
    print("   1. 输入 'CO浓度探测器' 验证类型推断模式")
    print("   2. 输入 '温度传感器' 验证精确匹配模式")
    print("   3. 输入 '蝶阀' 验证精确匹配模式")
    print("   4. 输入 '压力变送器' 验证无法识别情况")

if __name__ == "__main__":
    # 测试详细显示
    test_detailed_display()
    
    # 显示前端指南
    show_frontend_display_guide()