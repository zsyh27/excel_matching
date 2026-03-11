#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""带调试信息的匹配测试"""

import sys
sys.path.insert(0, 'backend')
import requests
import json

print("🧪 带调试信息的匹配测试...")

# API基础URL
base_url = "http://localhost:5000"

# 测试不同的文本
test_cases = [
    "KNX安全4路开关执行器",
    "霍尼韦尔 KNX安全4路开关执行器",
    "智能照明设备 KNX安全4路开关执行器",
    "HKX-R04-16-N-S",
    "开关执行器",
    "KNX",
    "4路开关"
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
                            print(f"       规格型号: {candidate.get('spec_model')}")
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