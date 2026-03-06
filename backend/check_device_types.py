#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查设备类型数据
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, data_loader, intelligent_config_manager
import json

def check_database_device_types():
    """检查数据库中的设备类型"""
    print("\n" + "="*60)
    print("数据库中的设备类型")
    print("="*60)
    
    all_devices = data_loader.get_all_devices()
    
    type_counts = {}
    for device_id, device in all_devices.items():
        device_type = device.device_type
        if device_type:
            type_counts[device_type] = type_counts.get(device_type, 0) + 1
    
    print(f"\n总共 {len(type_counts)} 个不同的设备类型:")
    for device_type in sorted(type_counts.keys()):
        print(f"  - {device_type}: {type_counts[device_type]} 个设备")
    
    return type_counts


def check_config_device_types():
    """检查配置中的设备类型"""
    print("\n" + "="*60)
    print("配置中定义的设备类型")
    print("="*60)
    
    try:
        if intelligent_config_manager:
            # 尝试不同的方式访问配置
            if hasattr(intelligent_config_manager, 'config'):
                device_types_config = intelligent_config_manager.config.get('device_types', {})
            elif hasattr(intelligent_config_manager, 'get_device_types'):
                device_types_config = intelligent_config_manager.get_device_types()
            else:
                # 直接读取配置文件
                import yaml
                config_file = os.path.join(os.path.dirname(__file__), 'config', 'device_params.yaml')
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    device_types_config = config.get('device_types', {})
            
            print(f"\n总共 {len(device_types_config)} 个配置的设备类型:")
            for device_type in sorted(device_types_config.keys()):
                print(f"  - {device_type}")
            
            return set(device_types_config.keys())
        else:
            print("\n配置管理器未初始化")
            return set()
    except Exception as e:
        print(f"\n读取配置失败: {e}")
        import traceback
        traceback.print_exc()
        return set()


def check_api_response():
    """检查API响应"""
    print("\n" + "="*60)
    print("API响应")
    print("="*60)
    
    with app.test_client() as client:
        response = client.get('/api/devices/device-types?include_count=true')
        data = json.loads(response.data)
        
        print(f"\n状态码: {response.status_code}")
        print(f"成功: {data.get('success')}")
        print(f"设备类型数量: {len(data.get('device_types', []))}")
        print(f"\n设备类型列表:")
        for device_type in data.get('device_types', []):
            count = data.get('counts', {}).get(device_type, 0)
            print(f"  - {device_type}: {count} 个设备")


def main():
    print("\n" + "="*60)
    print("设备类型数据检查")
    print("="*60)
    
    # 检查数据库
    db_types = check_database_device_types()
    
    # 检查配置
    config_types = check_config_device_types()
    
    # 检查API
    check_api_response()
    
    # 分析差异
    print("\n" + "="*60)
    print("数据分析")
    print("="*60)
    
    if config_types:
        print(f"\n配置中定义但数据库中不存在的类型:")
        missing = config_types - set(db_types.keys())
        if missing:
            for t in sorted(missing):
                print(f"  - {t}")
        else:
            print("  无")
        
        print(f"\n数据库中存在但配置中未定义的类型:")
        extra = set(db_types.keys()) - config_types
        if extra:
            for t in sorted(extra):
                print(f"  - {t}")
        else:
            print("  无")
    else:
        print("\n配置为空，API将返回所有数据库中的类型")


if __name__ == '__main__':
    main()
