#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试现有设备匹配是否正常"""

import sys
sys.path.insert(0, 'backend')
import requests
import json

print("🧪 测试现有设备匹配是否正常...")

# API基础URL
base_url = "http://localhost:5000"

# 测试一些已知存在的设备类型
test_cases = [
    "温度传感器",
    "压力传感器", 
    "蝶阀",
    "球阀",
    "座阀",
    "霍尼韦尔温度传感器",
    "DN50蝶阀"
]

for i, test_text in enumerate(test_cases, 1):
    print(f"\n测试 {i}: {test_text}")
    
    try:
        url = f"{base_url}/api/match"
        
        # 构造请求数据
        payload = {
            "rows": [
                {
                    "row_number": 1,
                    "original_text": test_text,
                    "device_description": test_text,
                    "preprocessed_text": test_text
                }
            ]
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                matched_rows = result.get('matched_rows', [])
                
                if matched_rows:
                    first_row = matched_rows[0]
                    candidates = first_row.get('candidates', [])
                    
                    if candidates:
                        print(f"  ✅ 找到 {len(candidates)} 个候选设备:")
                        for j, candidate in enumerate(candidates[:3]):
                            print(f"    {j+1}. {candidate.get('device_name')} (得分: {candidate.get('total_score', 0):.2f})")
                            print(f"       设备类型: {candidate.get('device_type')}")
                    else:
                        print(f"  ❌ 没有找到候选设备")
                else:
                    print(f"  ❌ 没有匹配结果")
            else:
                print(f"  ❌ API返回失败: {result.get('message', '未知错误')}")
        else:
            print(f"  ❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")

print(f"\n测试完成")