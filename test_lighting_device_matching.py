#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试智能照明设备匹配功能"""

import sys
sys.path.insert(0, 'backend')
import requests
import json

# 测试用例
test_cases = [
    {
        "name": "KNX开关执行器测试",
        "text": "KNX安全4路开关执行器 通道数量：4路 输出类型：继电器输出 额定电流：16A",
        "expected_device_type": "智能照明设备"
    },
    {
        "name": "调光控制器测试", 
        "text": "4通道调光控制器 1-10V调光 16A额定电流",
        "expected_device_type": "智能照明设备"
    },
    {
        "name": "KNX网关测试",
        "text": "KNX/DALI网关 单通道 协议转换",
        "expected_device_type": "智能照明设备"
    },
    {
        "name": "智能面板测试",
        "text": "KNX智能面板 4键 触摸控制",
        "expected_device_type": "智能照明设备"
    },
    {
        "name": "红外传感器测试",
        "text": "KNX红外移动传感器 探测功能",
        "expected_device_type": "智能照明设备"
    }
]

print("🧪 测试智能照明设备匹配功能...")

# API基础URL
base_url = "http://localhost:5000"

def test_intelligent_matching(text, expected_device_type):
    """测试智能匹配API"""
    try:
        url = f"{base_url}/api/intelligent-extraction/match"
        payload = {
            "text": text,
            "top_k": 5
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success') and result.get('data'):
                candidates = result['data'].get('candidates', [])
                
                if candidates:
                    best_match = candidates[0]
                    print(f"  ✅ 找到匹配设备:")
                    print(f"     设备名称: {best_match.get('device_name')}")
                    print(f"     设备类型: {best_match.get('device_type')}")
                    print(f"     匹配得分: {best_match.get('total_score', 0):.2f}")
                    print(f"     规格型号: {best_match.get('spec_model')}")
                    
                    # 验证设备类型
                    if best_match.get('device_type') == expected_device_type:
                        print(f"     类型匹配: ✅")
                        return True
                    else:
                        print(f"     类型匹配: ❌ (期望: {expected_device_type})")
                        return False
                else:
                    print(f"  ❌ 没有找到匹配的设备")
                    return False
            else:
                print(f"  ❌ API返回错误: {result.get('message', '未知错误')}")
                return False
        else:
            print(f"  ❌ API请求失败: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ 网络请求失败: {e}")
        return False
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False

# 执行测试
print(f"\n开始测试 {len(test_cases)} 个用例...")

success_count = 0
total_count = len(test_cases)

for i, test_case in enumerate(test_cases, 1):
    print(f"\n测试用例 {i}: {test_case['name']}")
    print(f"输入文本: {test_case['text']}")
    
    success = test_intelligent_matching(test_case['text'], test_case['expected_device_type'])
    
    if success:
        success_count += 1

# 测试结果统计
print(f"\n📊 测试结果统计:")
print(f"   成功: {success_count}/{total_count}")
print(f"   成功率: {(success_count/total_count)*100:.1f}%")

if success_count == total_count:
    print(f"\n🎉 所有测试用例通过！智能照明设备匹配功能正常工作")
elif success_count >= total_count * 0.8:
    print(f"\n✅ 大部分测试用例通过，匹配功能基本正常")
else:
    print(f"\n⚠️ 部分测试用例失败，可能需要调整配置或规则")

print(f"\n智能照明设备导入和匹配测试完成！")