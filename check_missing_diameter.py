#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查缺少公称通径的组合设备"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device
import json

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

print("=" * 80)
print("检查缺少公称通径的组合设备")
print("=" * 80)

device_types = [
    '蝶阀+开关型执行器',
    '蝶阀+调节型执行器'
]

with db_manager.session_scope() as session:
    for device_type in device_types:
        print(f"\n{'='*80}")
        print(f"设备类型: {device_type}")
        print(f"{'='*80}")
        
        devices = session.query(Device).filter(
            Device.device_type == device_type
        ).all()
        
        missing_diameter = []
        has_diameter = []
        
        for device in devices:
            if device.key_params:
                if '公称通径' in device.key_params:
                    has_diameter.append(device)
                else:
                    missing_diameter.append(device)
            else:
                missing_diameter.append(device)
        
        print(f"\n总设备数: {len(devices)}")
        print(f"有公称通径: {len(has_diameter)} 个")
        print(f"缺少公称通径: {len(missing_diameter)} 个")
        
        if missing_diameter:
            print(f"\n缺少公称通径的设备示例（前5个）:")
            for device in missing_diameter[:5]:
                print(f"  - {device.device_id}: {device.device_name}")
                print(f"    规格型号: {device.spec_model}")
                if device.key_params:
                    print(f"    参数数量: {len(device.key_params)}")
                    print(f"    参数列表: {list(device.key_params.keys())}")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)
