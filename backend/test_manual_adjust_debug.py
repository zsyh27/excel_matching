"""
调试手动调整API的问题

测试场景：
1. 上传Excel文件
2. 分析设备行
3. 执行手动调整
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

print("=" * 80)
print("手动调整API调试")
print("=" * 80)
print()
print("⚠️  请确保后端服务正在运行: cd backend && python app.py")
print("⚠️  后端地址: http://localhost:5000")
print()
print("=" * 80)
print()

# 1. 上传并分析Excel文件（合并接口）
print("1. 上传并分析Excel文件...")
excel_file_path = '../data/示例设备清单.xlsx'

try:
    with open(excel_file_path, 'rb') as f:
        files = {'file': ('示例设备清单.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        response = requests.post(f"{BASE_URL}/excel/analyze", files=files)
        
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code != 200:
        print("   ❌ 上传分析失败")
        exit(1)
    
    result = response.json()
    excel_id = result['excel_id']
    print(f"   ✅ 上传分析成功，excel_id: {excel_id}")
    print(f"   总行数: {result['total_rows']}")
    print(f"   高概率设备行: {result['statistics']['high_probability']}")
    print()
    
    # 获取第一个高概率设备行的行号
    test_row_number = None
    for row in result['analysis_results']:
        if row['probability_level'] == 'high':
            test_row_number = row['row_number']
            break
    
    if not test_row_number:
        print("   ⚠️  没有找到高概率设备行，使用第一行")
        test_row_number = result['analysis_results'][0]['row_number']
    
    print(f"   测试行号: {test_row_number}")
    print()
    
except Exception as e:
    print(f"   ❌ 分析失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# 2. 测试手动调整 - 单行
print("2. 测试手动调整（单行）...")
try:
    data = {
        "excel_id": excel_id,
        "adjustments": [
            {
                "row_number": test_row_number,
                "action": "mark_as_device"
            }
        ]
    }
    
    print(f"   请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/excel/manual-adjust",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code != 200:
        print("   ❌ 手动调整失败")
        
        # 打印详细错误信息
        if 'error_message' in response.json():
            print(f"   错误信息: {response.json()['error_message']}")
        if 'details' in response.json():
            print(f"   详细信息: {response.json()['details']}")
    else:
        print("   ✅ 手动调整成功")
    print()
    
except Exception as e:
    print(f"   ❌ 手动调整失败: {e}")
    import traceback
    traceback.print_exc()

# 3. 测试手动调整 - 批量
print("3. 测试手动调整（批量）...")
try:
    # 获取前3个行号
    test_rows = [row['row_number'] for row in result['analysis_results'][:3]]
    
    data = {
        "excel_id": excel_id,
        "adjustments": [
            {"row_number": row_num, "action": "mark_as_device"}
            for row_num in test_rows
        ]
    }
    
    print(f"   请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/excel/manual-adjust",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    if response.status_code != 200:
        print("   ❌ 批量调整失败")
    else:
        print("   ✅ 批量调整成功")
    print()
    
except Exception as e:
    print(f"   ❌ 批量调整失败: {e}")
    import traceback
    traceback.print_exc()

# 4. 获取最终设备行
print("4. 获取最终设备行...")
try:
    response = requests.get(
        f"{BASE_URL}/excel/final-device-rows",
        params={"excel_id": excel_id}
    )
    
    print(f"   状态码: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        print("   ❌ 获取失败")
    else:
        result = response.json()
        print(f"   ✅ 获取成功")
        print(f"   总设备行数: {result['statistics']['total_device_rows']}")
        print(f"   自动识别: {result['statistics']['auto_identified']}")
        print(f"   手动调整: {result['statistics']['manually_adjusted']}")
    print()
    
except Exception as e:
    print(f"   ❌ 获取失败: {e}")
    import traceback
    traceback.print_exc()

print("=" * 80)
print("调试完成")
print("=" * 80)
