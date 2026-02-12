"""
测试 /api/devices 接口是否返回数据库中的设备
"""

import requests
import json

# 测试获取设备列表
response = requests.get('http://localhost:5000/api/devices')

if response.status_code == 200:
    data = response.json()
    if data['success']:
        devices = data['devices']
        print(f"✅ 成功获取设备列表")
        print(f"📊 设备总数: {len(devices)}")
        
        # 显示前5个设备
        print("\n前5个设备:")
        for i, device in enumerate(devices[:5], 1):
            print(f"\n{i}. {device.get('device_name', 'N/A')}")
            print(f"   品牌: {device.get('brand', 'N/A')}")
            print(f"   型号: {device.get('spec_model', 'N/A')}")
            print(f"   价格: ¥{device.get('unit_price', 0)}")
            print(f"   ID: {device.get('device_id', 'N/A')}")
        
        # 检查是否有数据库特有的设备（不在 static_device.json 中的）
        print("\n" + "="*50)
        print("检查数据库特有设备...")
        
        # 读取 JSON 文件中的设备 ID
        try:
            with open('../data/static_device.json', 'r', encoding='utf-8') as f:
                json_devices = json.load(f)
                json_device_ids = {d['device_id'] for d in json_devices}
            
            # 找出数据库中有但 JSON 中没有的设备
            db_only_devices = [d for d in devices if d['device_id'] not in json_device_ids]
            
            if db_only_devices:
                print(f"✅ 找到 {len(db_only_devices)} 个数据库特有设备（不在 JSON 中）")
                print("\n数据库特有设备示例（前3个）:")
                for i, device in enumerate(db_only_devices[:3], 1):
                    print(f"\n{i}. {device.get('device_name', 'N/A')}")
                    print(f"   品牌: {device.get('brand', 'N/A')}")
                    print(f"   型号: {device.get('spec_model', 'N/A')}")
                    print(f"   ID: {device.get('device_id', 'N/A')}")
                print("\n✅ 确认：API 返回的是数据库中的设备！")
            else:
                print("⚠️  警告：所有设备都在 JSON 文件中，可能仍在使用 JSON 模式")
                
        except Exception as e:
            print(f"⚠️  无法读取 JSON 文件: {e}")
    else:
        print(f"❌ API 返回失败: {data}")
else:
    print(f"❌ HTTP 请求失败: {response.status_code}")
    print(response.text)
