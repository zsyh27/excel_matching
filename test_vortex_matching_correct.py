#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试涡街流量计匹配功能 - 正确格式"""

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
            'rows': [
                {
                    'row_number': 1,
                    'row_type': 'device',
                    'device_description': test_text,
                    'raw_data': [test_text]
                }
            ],
            'record_detail': True
        }
        
        response = requests.post(
            'http://localhost:5000/api/match',
            json=payload,
            timeout=15
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success') and 'matched_rows' in result:
                matched_rows = result['matched_rows']
                statistics = result.get('statistics', {})
                
                print(f"   匹配统计:")
                print(f"     总设备数: {statistics.get('total_devices', 0)}")
                print(f"     匹配成功: {statistics.get('matched', 0)}")
                print(f"     匹配失败: {statistics.get('unmatched', 0)}")
                print(f"     准确率: {statistics.get('accuracy_rate', 0):.1%}")
                
                if matched_rows and matched_rows[0].get('match_result'):
                    match_result = matched_rows[0]['match_result']
                    
                    print(f"   匹配结果:")
                    print(f"     状态: {match_result.get('match_status', 'N/A')}")
                    
                    if match_result.get('match_status') == 'success':
                        matched_device = match_result.get('matched_device', {})
                        print(f"     最佳匹配:")
                        print(f"       设备名称: {matched_device.get('device_name', 'N/A')}")
                        print(f"       匹配得分: {matched_device.get('match_score', 0):.2f}")
                        print(f"       设备类型: {matched_device.get('device_type', 'N/A')}")
                        print(f"       规格型号: {matched_device.get('spec_model', 'N/A')}")
                        print(f"       品牌: {matched_device.get('brand', 'N/A')}")
                        
                        # 检查是否匹配到涡街流量计
                        if matched_device.get('device_type') == '涡街流量计':
                            print(f"       ✅ 成功匹配到涡街流量计")
                        else:
                            print(f"       ⚠️ 匹配到其他设备类型")
                    else:
                        print(f"     ❌ 匹配失败: {match_result.get('error_message', 'Unknown error')}")
                        
                    # 显示候选设备
                    candidates = matched_rows[0].get('candidates', [])
                    if candidates:
                        print(f"   候选设备 (前3个):")
                        for j, candidate in enumerate(candidates[:3], 1):
                            print(f"     {j}. {candidate.get('matched_device_text', 'N/A')} (得分: {candidate.get('match_score', 0):.2f})")
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