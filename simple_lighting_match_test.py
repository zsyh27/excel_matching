#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简单的智能照明设备匹配测试"""

import sys
sys.path.insert(0, 'backend')
import requests
import json

print("🧪 简单智能照明设备匹配测试...")

# API基础URL
base_url = "http://localhost:5000"

# 使用更精确的测试文本（直接使用数据库中的设备名称）
test_text = "KNX安全4路开关执行器"

print(f"测试文本: {test_text}")

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
    
    print(f"发送请求到: {url}")
    print(f"请求数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    response = requests.post(url, json=payload, timeout=10)
    
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('success'):
            matched_rows = result.get('matched_rows', [])
            print(f"匹配行数: {len(matched_rows)}")
            
            if matched_rows:
                first_row = matched_rows[0]
                candidates = first_row.get('candidates', [])
                print(f"候选设备数: {len(candidates)}")
                
                if candidates:
                    print(f"\n前3个匹配结果:")
                    for i, candidate in enumerate(candidates[:3]):
                        print(f"  {i+1}. {candidate.get('device_name')} (得分: {candidate.get('total_score', 0):.2f})")
                        print(f"     规格型号: {candidate.get('spec_model')}")
                        print(f"     设备类型: {candidate.get('device_type')}")
                else:
                    print("没有找到候选设备")
            else:
                print("没有匹配的行")
        else:
            print(f"API返回失败: {result.get('message', '未知错误')}")
    else:
        print(f"HTTP错误: {response.status_code}")
        print(f"错误内容: {response.text}")

except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()