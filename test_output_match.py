import requests

# 测试输出信号匹配
response = requests.post('http://127.0.0.1:5000/api/intelligent-extraction/preview', 
    json={'text': 'CO浓度探测器 量程0-250ppm 输出信号4~20mA 精度5%'})

result = response.json()

if result['success']:
    data = result['data']
    candidate = data['step4_matching']['candidates'][0]
    
    print(f"设备名称: {candidate['device_name']}")
    print(f"匹配参数: {candidate['matched_params']}")
    
    print("\n参数匹配详情:")
    for detail in candidate['param_match_details']:
        status = "✅" if detail['matched'] else "❌"
        print(f"  {status} {detail['param_name']}: {detail['match_type']}")
        print(f"     输入: {detail['input_value']}")
        print(f"     设备: {detail['device_value']}")
        print(f"     原因: {detail['match_reason']}")
