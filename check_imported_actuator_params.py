#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查已导入的执行器设备的实际参数"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device

db_manager = DatabaseManager("sqlite:///data/devices.db")

print("=" * 80)
print("检查已导入的执行器设备参数")
print("=" * 80)

with db_manager.session_scope() as session:
    # 检查蝶阀开关型执行器
    print("\n蝶阀开关型执行器:")
    print("-" * 80)
    device = session.query(Device).filter(
        Device.device_type == "蝶阀开关型执行器"
    ).first()
    
    if device:
        print(f"设备ID: {device.device_id}")
        print(f"设备名称: {device.device_name}")
        print(f"规格型号: {device.spec_model}")
        print(f"\nkey_params 参数数量: {len(device.key_params) if device.key_params else 0}")
        
        if device.key_params:
            print("参数列表:")
            for idx, (key, value) in enumerate(device.key_params.items(), 1):
                print(f"  {idx}. {key}: {value.get('value', '')}")
        
        print(f"\ndetailed_params:")
        print(f"  {device.detailed_params}")
    
    # 检查蝶阀调节型执行器
    print("\n\n蝶阀调节型执行器:")
    print("-" * 80)
    device = session.query(Device).filter(
        Device.device_type == "蝶阀调节型执行器"
    ).first()
    
    if device:
        print(f"设备ID: {device.device_id}")
        print(f"设备名称: {device.device_name}")
        print(f"规格型号: {device.spec_model}")
        print(f"\nkey_params 参数数量: {len(device.key_params) if device.key_params else 0}")
        
        if device.key_params:
            print("参数列表:")
            for idx, (key, value) in enumerate(device.key_params.items(), 1):
                print(f"  {idx}. {key}: {value.get('value', '')}")
        
        print(f"\ndetailed_params:")
        print(f"  {device.detailed_params}")

print("\n" + "=" * 80)
