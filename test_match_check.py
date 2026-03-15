import requests
import json

# 测试API返回的数据
text = """1.名称:室内PM传感器 
2.规格：485传输方式，量程0～1000 ug/m3 ；输出信号 4~20mA / 2~10VDC；精度±10%  @25C；分辨率：1 ug/m3，485通讯 
3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。"""

response = requests.post('http://127.0.0.1:5000/api/intelligent-extraction/preview', 
    json={'text': text})

result = response.json()

if result['success']:
    data = result['data']
    candidates = data['step4_matching']['candidates']
    
    if candidates:
        c = candidates[0]
        matched_params = c.get('matched_params', [])
        all_params = c.get('all_params', {})
        
        print(f"matched_params (参数名): {matched_params}")
        print(f"\n检查匹配情况:")
        
        for name, value in all_params.items():
            is_matched = name in matched_params
            
            if is_matched:
                print(f"  ✓ {name}: {value} - 匹配!")
            else:
                print(f"  ✗ {name}: {value}")
else:
    print(f"失败: {result.get('error', {}).get('message', '未知错误')}")
