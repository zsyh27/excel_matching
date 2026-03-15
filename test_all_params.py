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
    
    print(f"候选设备数量: {len(candidates)}")
    
    if candidates:
        c = candidates[0]
        print(f"\n第一个候选设备:")
        print(f"  device_id: {c.get('device_id')}")
        print(f"  device_name: {c.get('device_name')}")
        print(f"  matched_params: {c.get('matched_params', [])}")
        print(f"  all_params: {c.get('all_params', {})}")
        print(f"  all_params 类型: {type(c.get('all_params'))}")
        print(f"  all_params 长度: {len(c.get('all_params', {}))}")
else:
    print(f"失败: {result.get('error', {}).get('message', '未知错误')}")
