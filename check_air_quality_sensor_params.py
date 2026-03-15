#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查空气质量传感器的参数"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

print("=" * 80)
print("检查空气质量传感器参数")
print("=" * 80)

with db_manager.session_scope() as session:
    # 查询所有空气质量传感器
    devices = session.query(Device).filter(
        Device.device_type == '空气质量传感器'
    ).all()
    
    print(f"\n找到 {len(devices)} 个空气质量传感器设备\n")
    
    if len(devices) == 0:
        print("没有找到空气质量传感器设备")
        sys.exit(0)
    
    # 统计所有参数名
    all_param_names = set()
    
    # 显示前5个设备的详细信息
    for i, device in enumerate(devices[:5], 1):
        print(f"设备 {i}: {device.device_id}")
        print(f"  设备名称: {device.device_name}")
        print(f"  规格型号: {device.spec_model}")
        
        if device.key_params:
            print(f"  key_params 参数数量: {len(device.key_params)}")
            print(f"  参数列表:")
            for param_name, param_data in device.key_params.items():
                all_param_names.add(param_name)
                if isinstance(param_data, dict) and 'value' in param_data:
                    print(f"    - {param_name}: {param_data['value']}")
                else:
                    print(f"    - {param_name}: {param_data}")
        else:
            print(f"  key_params: 无")
        
        if device.detailed_params:
            print(f"  detailed_params: {device.detailed_params[:100]}...")
        
        print()
    
    # 统计所有参数名
    print("=" * 80)
    print("所有空气质量传感器的参数名统计")
    print("=" * 80)
    
    param_count = {}
    for device in devices:
        if device.key_params:
            for param_name in device.key_params.keys():
                param_count[param_name] = param_count.get(param_name, 0) + 1
    
    print(f"\n参数名称列表（共 {len(param_count)} 个不同的参数）:\n")
    for param_name, count in sorted(param_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {param_name}: {count} 个设备")
    
    # 检查是否有包含"co"或"二氧化碳"的参数
    print("\n" + "=" * 80)
    print("检查CO2相关参数")
    print("=" * 80)
    
    co2_related = []
    for param_name in param_count.keys():
        param_lower = param_name.lower()
        if 'co' in param_lower or '二氧化碳' in param_name or 'dioxide' in param_lower:
            co2_related.append(param_name)
    
    if co2_related:
        print(f"\n找到 {len(co2_related)} 个CO2相关参数:")
        for param_name in co2_related:
            print(f"  - {param_name} ({param_count[param_name]} 个设备)")
    else:
        print("\n未找到CO2相关参数")

print("\n" + "=" * 80)
