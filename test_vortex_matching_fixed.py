#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试涡街流量计匹配功能 - 修正版"""

import requests
import json

# 测试匹配API
test_cases = [
    {
        "text": "涡街流量计 DN25 PN16 液体介质 4-20mA输出",
        "description": "基本涡街流量计描述"
    },
    {
        "text": "华迈涡街流量计 HMF-VS16F025LMY",
        "description": "带品牌和型号的涡街流量计"
    },
    {
        "text": "流量计 DN15 普通型 一体式",
        "description": "简化的流量计描述"
    }
]

print("🧪 测试涡街流量计匹配功能...")

for i, test_case in enumerate(test_cases, 1):
    test_text = test_case["text"]
    description = test_case["description"]
    
    print(f"\n测试 {i}: {description}")
    print(f"   输入文本: {test_text}")
    
    try:
        # 使用正确的API格式
        payload = {
            'rows': [{'text': test_text}],
            'top_k': 3
        }
        
        response = requests.post(
            'http://localhost:5000/api/match',
            json=payload,
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if 'results' in result and result['results']:
                matches = result['results'][0].get('matches', [])
                print(f"   匹配结果数量: {len(matches)}")
                
                if matches:
                    for j, match in enumerate(matches[:2], 1):  # 显示前2个结果
                        print(f"   结果 {j}:")
                        print(f"     设备名称: {match.get('device_name', 'N/A')}")
                        print(f"     匹配得分: {match.get('score', 0):.2f}")
                        print(f"     设备类型: {match.get('device_type', 'N/A')}")
                        print(f"     规格型号: {match.get('spec_model', 'N/A')}")
                        
                        # 检查是否匹配到涡街流量计
                        if match.get('device_type') == '涡街流量计':
                            print(f"     ✅ 成功匹配到涡街流量计")
                        else:
                            print(f"     ⚠️ 匹配到其他设备类型")
                else:
                    print("   ⚠️ 无匹配结果")
            else:
                print("   ⚠️ 响应格式异常")
                print(f"   响应内容: {result}")
        else:
            print(f"   ❌ API错误")
            try:
                error_detail = response.json()
                print(f"   错误详情: {error_detail}")
            except:
                print(f"   错误内容: {response.text}")
                
    except Exception as e:
        print(f"   ❌ 请求失败: {str(e)}")

print("\n✅ 匹配测试完成！")