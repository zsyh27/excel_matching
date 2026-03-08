#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查所有组合设备的key_params"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device
import json

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

print("=" * 80)
print("检查所有组合设备的key_params")
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
        
        if not devices:
            print(f"⚠️ 没有找到该类型的设备")
            continue
        
        print(f"\n找到 {len(devices)} 个设备")
        
        # 统计key_params参数数量
        param_counts = {}
        for device in devices:
            if device.key_params:
                count = len(device.key_params)
                param_names = list(device.key_params.keys())
            else:
                count = 0
                param_names = []
            
            if count not in param_counts:
                param_counts[count] = {
                    'count': 0,
                    'example_device': device.device_id,
                    'param_names': param_names
                }
            param_counts[count]['count'] += 1
        
        print(f"\nkey_params参数数量统计:")
        for count in sorted(param_counts.keys()):
            info = param_counts[count]
            print(f"  {count}个参数: {info['count']}个设备")
            if count > 0:
                print(f"    参数列表: {info['param_names']}")
                print(f"    示例设备: {info['example_device']}")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)

print("\n问题总结:")
print("  组合设备的key_params中只包含蝶阀的参数（6-7个）")
print("  缺少执行器的参数（8-9个）")
print("  这导致特征提取时只能提取到蝶阀的参数特征")
print("  需要为这些设备补充完整的key_params数据")
