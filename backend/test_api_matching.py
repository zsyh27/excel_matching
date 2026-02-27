# -*- coding: utf-8 -*-
"""
测试匹配API
"""
import requests
import json

# 测试数据
test_cases = [
    {
        "description": "温度传感器，0-50℃，4-20mA",
        "note": "简短描述 - 预期匹配失败"
    },
    {
        "description": "霍尼韦尔室内温度传感器，NTC10K，室内墙装",
        "note": "完整描述 - 预期匹配成功"
    },
    {
        "description": "霍尼韦尔温度传感器",
        "note": "品牌+类型 - 测试部分匹配"
    }
]

for test_case in test_cases:
    test_description = test_case["description"]
    
    print("=" * 80)
    print(f"测试: {test_case['note']}")
    print(f"输入: {test_description}")
    print("=" * 80)
    
    # 调用API
    url = "http://localhost:5000/api/rules/management/test"
    response = requests.post(url, json={"description": test_description})
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get('success'):
            print("\n【预处理结果】")
            preprocessing = result.get('preprocessing', {})
            print(f"原始文本: {preprocessing.get('original')}")
            print(f"清理后: {preprocessing.get('cleaned')}")
            print(f"归一化: {preprocessing.get('normalized')}")
            print(f"提取特征: {preprocessing.get('features')}")
            
            print("\n【候选规则 (前5个)】")
            candidates = result.get('candidates', [])[:5]
            for i, candidate in enumerate(candidates, 1):
                print(f"\n{i}. {candidate.get('device_name')}")
                print(f"   得分: {candidate.get('score'):.1f} / 阈值: {candidate.get('threshold')}")
                print(f"   匹配: {'是' if candidate.get('is_match') else '否'}")
                matched_features = candidate.get('matched_features', [])
                if matched_features:
                    features_str = ', '.join(['{0}({1})'.format(f['feature'], f['weight']) for f in matched_features[:3]])
                    print(f"   匹配特征: {features_str}")
            
            print("\n【最终匹配结果】")
            final_match = result.get('final_match', {})
            print(f"状态: {final_match.get('match_status')}")
            if final_match.get('match_status') == 'success':
                print(f"设备: {final_match.get('device_text')}")
                print(f"得分: {final_match.get('score'):.1f}")
            print(f"原因: {final_match.get('match_reason')}")
        else:
            print(f"API返回失败: {result}")
    else:
        print(f"HTTP错误: {response.status_code}")
        print(response.text)
    
    print("\n" + "=" * 80)
    print()
