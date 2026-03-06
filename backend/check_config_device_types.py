#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查配置中的设备类型数据
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, data_loader
import json

def check_config_device_types():
    """检查配置中的设备类型"""
    print("\n" + "="*60)
    print("检查配置中的设备类型数据")
    print("="*60)
    
    try:
        # 从数据库读取配置
        config = data_loader.load_config()
        
        print(f"\n配置键列表:")
        for key in config.keys():
            print(f"  - {key}")
        
        # 获取device_params配置
        device_params = config.get('device_params', {})
        
        if device_params:
            print(f"\n✓ 找到 device_params 配置")
            print(f"设备类型数量: {len(device_params)}")
            print(f"\n设备类型列表:")
            for device_type in sorted(device_params.keys()):
                print(f"  - {device_type}")
        else:
            print(f"\n✗ 未找到 device_params 配置")
            print(f"这意味着配置管理页面的设备参数配置数据不在数据库中")
        
        return device_params
        
    except Exception as e:
        print(f"\n✗ 读取配置失败: {e}")
        import traceback
        traceback.print_exc()
        return {}


def check_api_response():
    """检查API响应"""
    print("\n" + "="*60)
    print("检查 /api/device-types API响应")
    print("="*60)
    
    with app.test_client() as client:
        response = client.get('/api/device-types')
        data = json.loads(response.data)
        
        print(f"\n状态码: {response.status_code}")
        print(f"成功: {data.get('success')}")
        
        if data.get('success'):
            device_types = data.get('data', {}).get('device_types', [])
            print(f"设备类型数量: {len(device_types)}")
            print(f"\n设备类型列表:")
            for device_type in device_types:
                print(f"  - {device_type}")
        else:
            print(f"错误: {data.get('error_message')}")


if __name__ == '__main__':
    device_params = check_config_device_types()
    check_api_response()
    
    print("\n" + "="*60)
    print("结论")
    print("="*60)
    
    if device_params:
        print("\n✓ 设备参数配置存在于数据库中")
        print("  应该使用 /api/device-types API 获取设备类型列表")
        print("  而不是从 device_params.yaml 文件读取")
    else:
        print("\n✗ 设备参数配置不在数据库中")
        print("  需要运行脚本将 device_params.yaml 导入数据库")
        print("  或者直接从 device_params.yaml 文件读取")
