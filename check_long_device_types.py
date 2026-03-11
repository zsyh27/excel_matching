#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查设备类型名称较长的设备"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device

db_manager = DatabaseManager('sqlite:///data/devices.db')

with db_manager.session_scope() as session:
    # 查找设备类型名称较长的设备
    devices = session.query(Device).filter(
        Device.device_type.isnot(None)
    ).all()
    
    long_type_devices = []
    for device in devices:
        if device.device_type and len(device.device_type) > 20:
            long_type_devices.append({
                'device_id': device.device_id,
                'device_name': device.device_name,
                'device_type': device.device_type,
                'type_length': len(device.device_type)
            })
    
    print(f'找到 {len(long_type_devices)} 个设备类型名称超过20字符的设备:')
    for device in long_type_devices[:5]:  # 只显示前5个
        print(f'  - {device["device_id"]}: {device["device_type"]} (长度: {device["type_length"]})')
    
    if len(long_type_devices) > 5:
        print(f'  ... 还有 {len(long_type_devices) - 5} 个设备')