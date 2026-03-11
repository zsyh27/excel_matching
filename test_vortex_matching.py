#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试涡街流量计匹配功能"""

import requests
import json

# 测试匹配API
test_cases = [
    "涡街流量计 DN25 PN16 液体介质 4-20mA输出",
    "华迈涡街流量计 HMF-VS16F025LMY",
    "流量计 DN15 普通型 一体式",
    "涡街 DN50 PN16 304不锈钢"
]

print("🧪 测试涡街流量计匹配功能...")

for i, test_text in enumerate(test_cases, 1):
    print(f"\n测试 {i}: {test_text}")
    
    try:
        response = requests.post(
            'http://localhost:5000/api/match',
            json={'text': test_text, 'top_k': 3},
            timeout=10
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            matches = result.get('matches', [])
            print(f"   匹配结果数量: {len(matches)}")
            
            if matches:
                for j, match in enumerate(matches[:2], 1):  # 显示前2个结果
                    print(f"   结果 {j}:")
                    print(f"     设备名称: {match.get('device_name', 'N/A')}")
                    print(f"     匹配得分: {match.get('score', 0):.2f}")
                    print(f"     设备类型: {match.get('device_type', 'N/A')}")
                    print(f"     规格型号: {match.get('spec_model', 'N/A')}")
            else:
                print("   ⚠️ 无匹配结果")
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