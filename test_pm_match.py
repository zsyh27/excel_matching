import requests

# 测试新的参数候选提取
text = """1.名称:室内PM传感器 
2.规格：485传输方式，量程0～1000 ug/m3 ；输出信号 4~20mA / 2~10VDC；精度±10%  @25C；分辨率：1 ug/m3，485通讯 
3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。"""

response = requests.post('http://127.0.0.1:5000/api/intelligent-extraction/preview', 
    json={'text': text})

result = response.json()

if result['success']:
    data = result['data']
    
    # 检查辅助信息
    auxiliary = data['step3_auxiliary']
    print(f"辅助信息:")
    print(f"  品牌: {auxiliary.get('brand', '未识别')}")
    print(f"  介质: {auxiliary.get('medium', '未识别')}")
    print(f"  型号: {auxiliary.get('model', '未识别')}")
    
    # 检查匹配结果
    print(f"\n匹配结果:")
    c = data['step4_matching']['candidates'][0]
    print(f"  设备: {c['device_name']}")
    print(f"  总分: {c['total_score']}")
else:
    print(f"失败: {result.get('error', {}).get('message', '未知错误')}")
