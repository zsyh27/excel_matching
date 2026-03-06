#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试设备类型API响应
"""

import requests
import json

def test_device_types_api():
    """测试设备类型API"""
    print("\n" + "="*60)
    print("测试设备类型API响应")
    print("="*60)
    
    url = "http://127.0.0.1:5000/api/devices/device-types?include_count=true"
    
    try:
        response = requests.get(url)
        print(f"\n状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        # 获取原始响应文本
        print(f"\n原始响应文本:")
        print(response.text)
        
        # 解析JSON
        data = response.json()
        print(f"\n解析后的JSON:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
        # 检查数据
        if data.get('success'):
            device_types = data.get('device_types', [])
            counts = data.get('counts', {})
            
            print(f"\n✓ API调用成功")
            print(f"设备类型数量: {len(device_types)}")
            print(f"\n设备类型列表:")
            for dt in device_types:
                count = counts.get(dt, 0)
                print(f"  - {dt}: {count} 个设备")
        else:
            print(f"\n✗ API调用失败")
            print(f"错误信息: {data.get('error_message', '未知错误')}")
            
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        import traceback
        traceback.print_exc()


def test_brands_api():
    """测试品牌API"""
    print("\n" + "="*60)
    print("测试品牌API响应")
    print("="*60)
    
    url = "http://127.0.0.1:5000/api/devices/brands?include_count=true"
    
    try:
        response = requests.get(url)
        print(f"\n状态码: {response.status_code}")
        
        # 解析JSON
        data = response.json()
        print(f"\n解析后的JSON:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
        # 检查数据
        if data.get('success'):
            brands = data.get('brands', [])
            counts = data.get('counts', {})
            
            print(f"\n✓ API调用成功")
            print(f"品牌数量: {len(brands)}")
            print(f"\n品牌列表:")
            for brand in brands:
                count = counts.get(brand, 0)
                print(f"  - {brand}: {count} 个设备")
        else:
            print(f"\n✗ API调用失败")
            print(f"错误信息: {data.get('error_message', '未知错误')}")
            
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_device_types_api()
    test_brands_api()
