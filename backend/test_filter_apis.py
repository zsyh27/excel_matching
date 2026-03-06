#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试设备筛选API

测试新增的品牌和设备类型API端点
"""

import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
import json

def test_brands_api():
    """测试品牌列表API"""
    print("\n" + "="*60)
    print("测试品牌列表API")
    print("="*60)
    
    with app.test_client() as client:
        # 测试不包含数量
        print("\n1. 测试不包含数量:")
        response = client.get('/api/devices/brands')
        data = json.loads(response.data)
        
        print(f"状态码: {response.status_code}")
        print(f"成功: {data.get('success')}")
        print(f"品牌数量: {len(data.get('brands', []))}")
        print(f"品牌列表: {data.get('brands', [])[:10]}...")  # 只显示前10个
        
        # 测试包含数量
        print("\n2. 测试包含数量:")
        response = client.get('/api/devices/brands?include_count=true')
        data = json.loads(response.data)
        
        print(f"状态码: {response.status_code}")
        print(f"成功: {data.get('success')}")
        print(f"品牌数量: {len(data.get('brands', []))}")
        
        if 'counts' in data:
            counts = data['counts']
            print(f"统计信息:")
            for brand, count in list(counts.items())[:5]:  # 只显示前5个
                print(f"  - {brand}: {count} 个设备")
        
        return data.get('success', False)


def test_device_types_api():
    """测试设备类型列表API"""
    print("\n" + "="*60)
    print("测试设备类型列表API")
    print("="*60)
    
    with app.test_client() as client:
        # 测试不包含数量
        print("\n1. 测试不包含数量:")
        response = client.get('/api/devices/device-types')
        data = json.loads(response.data)
        
        print(f"状态码: {response.status_code}")
        print(f"成功: {data.get('success')}")
        print(f"设备类型数量: {len(data.get('device_types', []))}")
        print(f"设备类型列表: {data.get('device_types', [])[:10]}...")  # 只显示前10个
        
        # 测试包含数量
        print("\n2. 测试包含数量:")
        response = client.get('/api/devices/device-types?include_count=true')
        data = json.loads(response.data)
        
        print(f"状态码: {response.status_code}")
        print(f"成功: {data.get('success')}")
        print(f"设备类型数量: {len(data.get('device_types', []))}")
        
        if 'counts' in data:
            counts = data['counts']
            print(f"统计信息:")
            for device_type, count in list(counts.items())[:5]:  # 只显示前5个
                print(f"  - {device_type}: {count} 个设备")
        
        return data.get('success', False)


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("设备筛选API测试")
    print("="*60)
    
    try:
        # 测试品牌API
        brands_success = test_brands_api()
        
        # 测试设备类型API
        types_success = test_device_types_api()
        
        # 总结
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        print(f"品牌API: {'✓ 通过' if brands_success else '✗ 失败'}")
        print(f"设备类型API: {'✓ 通过' if types_success else '✗ 失败'}")
        
        if brands_success and types_success:
            print("\n✓ 所有测试通过！")
            return 0
        else:
            print("\n✗ 部分测试失败")
            return 1
            
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
