"""
测试批量导入API
"""
import requests
import os

# API地址
BASE_URL = "http://localhost:5000"

# Excel文件路径
excel_path = "../data/设备导出_2026-03-05T08-02-07.xlsx"

print("=" * 80)
print("测试批量导入API")
print("=" * 80)

# 检查文件是否存在
if not os.path.exists(excel_path):
    print(f"✗ Excel文件不存在: {excel_path}")
    exit(1)

print(f"\n✓ Excel文件存在: {excel_path}")

# 准备请求
print("\n发送批量导入请求...")
print(f"  URL: {BASE_URL}/api/devices/batch")
print(f"  auto_generate_rules: True")

try:
    with open(excel_path, 'rb') as f:
        files = {'file': f}
        data = {'auto_generate_rules': 'true'}  # 注意：FormData中的布尔值是字符串
        
        response = requests.post(
            f"{BASE_URL}/api/devices/batch",
            files=files,
            data=data
        )
    
    print(f"\n响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n响应内容:")
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if result.get('success'):
            data = result.get('data', {})
            print(f"\n✓ 导入成功")
            print(f"  成功导入: {data.get('inserted', 0)} 个设备")
            print(f"  生成规则: {data.get('generated_rules', 0)} 条")
            
            if data.get('generated_rules', 0) > 0:
                print(f"\n✓ 规则自动生成成功！")
            else:
                print(f"\n✗ 规则没有生成！")
        else:
            print(f"\n✗ 导入失败: {result.get('message')}")
    else:
        print(f"\n✗ 请求失败")
        print(f"响应内容: {response.text}")

except requests.exceptions.ConnectionError:
    print(f"\n✗ 无法连接到后端服务")
    print(f"  请确保后端服务正在运行: python backend/app.py")
except Exception as e:
    print(f"\n✗ 请求失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
