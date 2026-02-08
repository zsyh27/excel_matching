"""
测试匹配 API 修复

验证匹配 API 能否正确处理从设备行识别传递过来的数据
"""

import requests
import json

# 测试数据：模拟从设备行识别传递过来的数据
test_device_rows = [
    {
        "row_number": 6,
        "row_content": ["1", "CO传感器", "霍尼韦尔", "HSCM-R100U", "0-100PPM", "4-20mA", "台", "1"],
        "source": "auto",
        "confidence": 85.5
    },
    {
        "row_number": 7,
        "row_content": ["2", "温度传感器", "西门子", "QAA2061", "0~50℃", "4-20mA", "台", "2"],
        "source": "auto",
        "confidence": 82.0
    },
    {
        "row_number": 8,
        "row_content": ["3", "DDC控制器", "江森自控", "FX-PCV3624E", "24点位", "以太网", "台", "1"],
        "source": "auto",
        "confidence": 88.0
    }
]

# 转换为匹配 API 需要的格式
rows = []
for device_row in test_device_rows:
    rows.append({
        "row_number": device_row["row_number"],
        "raw_data": device_row["row_content"],
        "row_type": "device"
    })

# 调用匹配 API
url = "http://localhost:5000/api/match"
payload = {"rows": rows}

print("=" * 80)
print("测试匹配 API 修复")
print("=" * 80)
print()

try:
    print("发送请求到:", url)
    print("请求数据:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print()
    
    response = requests.post(url, json=payload, timeout=10)
    
    print(f"响应状态码: {response.status_code}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get('success'):
            print("✅ 匹配成功！")
            print()
            
            # 显示统计信息
            stats = result.get('statistics', {})
            print("统计信息:")
            print(f"  总设备数: {stats.get('total_devices')}")
            print(f"  匹配成功: {stats.get('matched')}")
            print(f"  匹配失败: {stats.get('unmatched')}")
            print(f"  准确率: {stats.get('accuracy_rate')}%")
            print()
            
            # 显示匹配结果
            print("匹配结果:")
            for row in result.get('matched_rows', []):
                row_num = row.get('row_number')
                desc = row.get('device_description')
                match_result = row.get('match_result')
                
                if match_result and match_result.get('match_status') == 'success':
                    device_text = match_result.get('matched_device_text')
                    score = match_result.get('match_score')
                    price = match_result.get('unit_price')
                    print(f"  行 {row_num}: {desc[:50]}...")
                    print(f"    ✅ 匹配: {device_text} (得分: {score}, 单价: {price})")
                else:
                    print(f"  行 {row_num}: {desc[:50]}...")
                    print(f"    ❌ 匹配失败")
                print()
        else:
            print("❌ 匹配失败")
            print(f"错误信息: {result.get('error_message')}")
    else:
        print(f"❌ HTTP 错误: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ 无法连接到服务器")
    print("请确保后端服务正在运行: python backend/app.py")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
