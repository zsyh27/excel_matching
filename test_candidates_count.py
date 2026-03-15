import requests

# 测试API返回的候选设备数量
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
    print(f"\n前5个候选设备:")
    for i, c in enumerate(candidates[:5]):
        print(f"  #{i+1} {c['device_name']} - {c['total_score']:.1f}分")
else:
    print(f"失败: {result.get('error', {}).get('message', '未知错误')}")
