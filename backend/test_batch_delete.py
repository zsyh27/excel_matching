"""
测试批量删除设备功能
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

def test_batch_delete():
    """测试批量删除设备"""
    
    print("=" * 60)
    print("测试批量删除设备功能")
    print("=" * 60)
    
    # 1. 先获取设备列表，找到一些测试设备
    print("\n1. 获取设备列表...")
    response = requests.get(f'{BASE_URL}/devices', params={'page': 1, 'page_size': 5})
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            devices = data.get('devices', [])
            print(f"   找到 {len(devices)} 个设备")
            
            if len(devices) == 0:
                print("   没有设备可以测试，请先添加一些设备")
                return
            
            # 显示设备信息
            for device in devices:
                print(f"   - {device['device_id']}: {device['device_name']}")
        else:
            print(f"   获取设备列表失败: {data.get('message')}")
            return
    else:
        print(f"   请求失败: {response.status_code}")
        return
    
    # 2. 测试批量删除（使用前2个设备）
    if len(devices) >= 2:
        device_ids = [devices[0]['device_id'], devices[1]['device_id']]
        
        print(f"\n2. 测试批量删除 {len(device_ids)} 个设备...")
        print(f"   设备ID: {device_ids}")
        
        # 询问用户确认
        confirm = input("\n   确定要删除这些设备吗？(y/n): ")
        if confirm.lower() != 'y':
            print("   取消删除")
            return
        
        response = requests.post(
            f'{BASE_URL}/devices/batch-delete',
            json={'device_ids': device_ids},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('success'):
                print(f"\n   ✓ 批量删除成功")
                print(f"   - 成功删除: {data.get('deleted_count')} 个")
                print(f"   - 删除失败: {data.get('failed_count')} 个")
                
                if data.get('failed_devices'):
                    print(f"   - 失败设备:")
                    for failed in data['failed_devices']:
                        print(f"     * {failed['device_id']}: {failed['reason']}")
            else:
                print(f"   ✗ 批量删除失败: {data.get('message')}")
        else:
            print(f"   ✗ 请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
    
    # 3. 测试空数组
    print("\n3. 测试空设备ID数组...")
    response = requests.post(
        f'{BASE_URL}/devices/batch-delete',
        json={'device_ids': []},
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        if not data.get('success'):
            print(f"   ✓ 正确拒绝空数组: {data.get('message')}")
        else:
            print(f"   ✗ 应该拒绝空数组")
    else:
        print(f"   ✓ 正确返回错误状态码: {response.status_code}")
    
    # 4. 测试不存在的设备ID
    print("\n4. 测试不存在的设备ID...")
    response = requests.post(
        f'{BASE_URL}/devices/batch-delete',
        json={'device_ids': ['NONEXISTENT_001', 'NONEXISTENT_002']},
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if data.get('success'):
            print(f"   ✓ 正确处理不存在的设备")
            print(f"   - 成功删除: {data.get('deleted_count')} 个")
            print(f"   - 删除失败: {data.get('failed_count')} 个")
        else:
            print(f"   响应: {data.get('message')}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_batch_delete()
    except Exception as e:
        print(f"\n测试出错: {e}")
        import traceback
        traceback.print_exc()
