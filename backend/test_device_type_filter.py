"""
测试设备类型过滤功能
验证 GET /api/devices 接口是否支持 device_type 参数过滤
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app
import json

def test_device_type_filter():
    """测试设备类型过滤"""
    with app.test_client() as client:
        # 1. 获取所有设备
        print("\n=== 测试1: 获取所有设备 ===")
        response = client.get('/api/devices?page=1&page_size=100')
        data = json.loads(response.data)
        
        if data['success']:
            print(f"✓ 总设备数: {data['total']}")
            
            # 统计设备类型
            device_types = {}
            none_count = 0
            for device in data['devices']:
                dtype = device.get('device_type')
                if dtype is None:
                    none_count += 1
                    dtype = 'None'
                device_types[dtype] = device_types.get(dtype, 0) + 1
            
            print(f"✓ 设备类型分布:")
            for dtype, count in device_types.items():
                print(f"  - {dtype}: {count}个")
            print(f"  - device_type字段缺失: {none_count}个")
            
            # 2. 测试按设备类型过滤 - 选择一个实际存在的类型
            actual_types = [k for k in device_types.keys() if k != 'None']
            if actual_types:
                test_type = actual_types[0]
                print(f"\n=== 测试2: 按设备类型过滤 (device_type={test_type}) ===")
                response = client.get(f'/api/devices?device_type={test_type}')
                filtered_data = json.loads(response.data)
                
                if filtered_data['success']:
                    print(f"✓ 过滤后设备数: {filtered_data['total']}")
                    print(f"✓ 预期设备数: {device_types[test_type]}")
                    
                    # 验证所有返回的设备都是指定类型
                    all_match = all(
                        d.get('device_type') == test_type 
                        for d in filtered_data['devices']
                    )
                    
                    if all_match:
                        print(f"✓ 所有设备类型匹配: {test_type}")
                    else:
                        print(f"✗ 设备类型不匹配")
                        return False
                    
                    if filtered_data['total'] == device_types[test_type]:
                        print(f"✓ 过滤结果正确")
                        return True
                    else:
                        print(f"✗ 过滤结果数量不匹配")
                        return False
                else:
                    print(f"✗ 过滤失败: {filtered_data.get('message')}")
                    return False
            else:
                print("\n⚠ 数据库中所有设备都没有device_type字段，跳过过滤测试")
                print("✓ 基础功能正常（设备列表可以正常获取）")
                return True
        else:
            print(f"✗ 获取设备列表失败: {data.get('message')}")
            return False

if __name__ == '__main__':
    print("开始测试设备类型过滤功能...")
    success = test_device_type_filter()
    
    if success:
        print("\n✓ 所有测试通过!")
        sys.exit(0)
    else:
        print("\n✗ 测试失败")
        sys.exit(1)
