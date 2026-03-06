#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
设备筛选功能最终测试
"""

import requests
import json

def test_brands_api():
    """测试品牌API"""
    print("\n" + "="*60)
    print("测试品牌筛选API")
    print("="*60)
    
    url = "http://127.0.0.1:5000/api/devices/brands?include_count=true"
    response = requests.get(url)
    data = response.json()
    
    print(f"\n状态码: {response.status_code}")
    print(f"成功: {data.get('success')}")
    
    if data.get('success'):
        brands = data.get('brands', [])
        counts = data.get('counts', {})
        
        print(f"品牌数量: {len(brands)}")
        print(f"\n品牌列表（前5个）:")
        for brand in brands[:5]:
            count = counts.get(brand, 0)
            print(f"  - {brand}: {count} 个设备")
        
        if len(brands) > 5:
            print(f"  ... 还有 {len(brands) - 5} 个品牌")
        
        return True
    else:
        print(f"✗ 失败: {data.get('error_message')}")
        return False


def test_device_types_api():
    """测试设备类型API"""
    print("\n" + "="*60)
    print("测试设备类型筛选API")
    print("="*60)
    
    url = "http://127.0.0.1:5000/api/devices/device-types?include_count=true"
    response = requests.get(url)
    data = response.json()
    
    print(f"\n状态码: {response.status_code}")
    print(f"成功: {data.get('success')}")
    
    if data.get('success'):
        device_types = data.get('device_types', [])
        counts = data.get('counts', {})
        
        print(f"设备类型数量: {len(device_types)}")
        print(f"\n设备类型列表（前10个）:")
        for device_type in device_types[:10]:
            count = counts.get(device_type, 0)
            print(f"  - {device_type}: {count} 个设备")
        
        if len(device_types) > 10:
            print(f"  ... 还有 {len(device_types) - 10} 个设备类型")
        
        # 验证是否包含配置中的关键类型
        expected_types = ['CO2传感器', '温度传感器', '座阀', '执行器', '控制器', '水泵']
        missing_types = [t for t in expected_types if t not in device_types]
        
        if missing_types:
            print(f"\n✗ 警告：缺少预期的设备类型: {missing_types}")
            return False
        else:
            print(f"\n✓ 包含所有预期的设备类型")
            return True
    else:
        print(f"✗ 失败: {data.get('error_message')}")
        return False


def test_device_list_with_filter():
    """测试设备列表筛选功能"""
    print("\n" + "="*60)
    print("测试设备列表筛选功能")
    print("="*60)
    
    # 测试品牌筛选
    print("\n1. 测试品牌筛选（霍尼韦尔）:")
    url = "http://127.0.0.1:5000/api/devices?brand=霍尼韦尔&page=1&page_size=5"
    response = requests.get(url)
    data = response.json()
    
    if data.get('success'):
        total = data.get('total', 0)
        devices = data.get('devices', [])
        print(f"  ✓ 找到 {total} 个霍尼韦尔设备")
        if devices:
            print(f"  示例: {devices[0].get('device_name', 'N/A')}")
    else:
        print(f"  ✗ 失败: {data.get('message')}")
        return False
    
    # 测试设备类型筛选
    print("\n2. 测试设备类型筛选（水泵）:")
    url = "http://127.0.0.1:5000/api/devices?device_type=水泵&page=1&page_size=5"
    response = requests.get(url)
    data = response.json()
    
    if data.get('success'):
        total = data.get('total', 0)
        devices = data.get('devices', [])
        print(f"  ✓ 找到 {total} 个水泵设备")
        if devices:
            print(f"  示例: {devices[0].get('device_name', 'N/A')}")
    else:
        print(f"  ✗ 失败: {data.get('message')}")
        return False
    
    # 测试组合筛选
    print("\n3. 测试组合筛选（霍尼韦尔 + 有规则）:")
    url = "http://127.0.0.1:5000/api/devices?brand=霍尼韦尔&has_rule=true&page=1&page_size=5"
    response = requests.get(url)
    data = response.json()
    
    if data.get('success'):
        total = data.get('total', 0)
        print(f"  ✓ 找到 {total} 个符合条件的设备")
    else:
        print(f"  ✗ 失败: {data.get('message')}")
        return False
    
    return True


def main():
    print("\n" + "="*60)
    print("设备筛选功能最终测试")
    print("="*60)
    
    results = []
    
    # 测试品牌API
    results.append(("品牌API", test_brands_api()))
    
    # 测试设备类型API
    results.append(("设备类型API", test_device_types_api()))
    
    # 测试设备列表筛选
    results.append(("设备列表筛选", test_device_list_with_filter()))
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ 所有测试通过！")
        print("\n前端验证步骤:")
        print("1. 打开浏览器访问 http://localhost:3000")
        print("2. 进入设备库管理页面")
        print("3. 点击筛选品牌下拉框 - 应该看到9个品牌")
        print("4. 点击筛选设备类型下拉框 - 应该看到36个设备类型")
        print("5. 选择筛选条件并查询 - 应该正常工作")
    else:
        print("\n✗ 部分测试失败，请检查错误信息")
    
    return all_passed


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
