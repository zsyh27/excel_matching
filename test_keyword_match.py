import requests
import json

# 测试CO浓度探测器
print("=== 测试：CO浓度探测器 ===")
response = requests.post('http://127.0.0.1:5000/api/intelligent-extraction/preview', 
    json={'text': 'CO浓度探测器 量程0-250ppm 输出信号4-20mA'})

result = response.json()

if result['success']:
    data = result['data']
    print(f"关键词: {data['step1_device_type']['keywords']}")
    
    print("\n前3个候选设备:")
    for i, candidate in enumerate(data['step4_matching']['candidates'][:3]):
        print(f"\n#{i+1} {candidate['device_name']} ({candidate['total_score']:.1f}分)")
        print(f"  检测对象: {candidate['all_params'].get('检测对象', '无')}")
        print(f"  评分明细: 类型{candidate['score_details']['device_type_score']:.1f} + 参数{candidate['score_details']['parameter_score']:.1f}")
        
        # 检查关键词匹配
        keyword_matches = [d for d in candidate['param_match_details'] if '关键词' in d['param_name']]
        if keyword_matches:
            print(f"  ✓ 关键词匹配成功")
        else:
            print(f"  ✗ 无关键词匹配")
