#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""最终修复CO₂"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device
from datetime import datetime

print("=" * 80)
print("开始修复CO₂")
print("=" * 80)

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

# CO₂的各种变体
co2_variants = ['CO₂', 'Co₂', 'co₂', 'CO2', 'Co2', 'co2']

updated_count = 0
updated_params = 0

with db_manager.session_scope() as session:
    devices = session.query(Device).filter(
        Device.device_type == '空气质量传感器'
    ).all()
    
    print(f"找到 {len(devices)} 个设备\n")
    
    for device in devices:
        if device.key_params:
            device_updated = False
            for param_name, param_data in device.key_params.items():
                if isinstance(param_data, dict) and 'value' in param_data:
                    original = param_data['value']
                    if isinstance(original, str):
                        new_value = original
                        for variant in co2_variants:
                            new_value = new_value.replace(variant, '二氧化碳')
                        
                        if new_value != original:
                            device.key_params[param_name]['value'] = new_value
                            device_updated = True
                            updated_params += 1
                            print(f"更新: {device.device_id} - {param_name}")
                            print(f"  原值: {original[:60]}...")
                            print(f"  新值: {new_value[:60]}...")
            
            if device_updated:
                device.updated_at = datetime.now()
                # 标记对象为已修改
                session.add(device)
                updated_count += 1
    
    # 显式提交
    print(f"\n提交更改...")
    session.commit()
    print(f"✅ 提交成功")

print(f"\n更新了 {updated_count} 个设备，共 {updated_params} 个参数值")
print("=" * 80)
print("修复完成")
print("=" * 80)
