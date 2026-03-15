#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证CO₂修复"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

print("验证修复结果...")

# CO₂的各种变体
co2_variants = ['CO₂', 'Co₂', 'co₂', 'CO2', 'Co2', 'co2']

with db_manager.session_scope() as session:
    devices = session.query(Device).filter(
        Device.device_type == '空气质量传感器'
    ).all()
    
    print(f"找到 {len(devices)} 个设备\n")
    
    co2_count = 0
    eryang_count = 0
    
    for device in devices:
        if device.key_params:
            has_co2 = False
            has_eryang = False
            
            for param_name, param_data in device.key_params.items():
                value_str = ''
                if isinstance(param_data, dict) and 'value' in param_data:
                    value_str = str(param_data['value'])
                elif isinstance(param_data, str):
                    value_str = param_data
                
                # 检查CO₂
                for variant in co2_variants:
                    if variant in value_str:
                        has_co2 = True
                        print(f"仍有CO₂: {device.device_id} - {param_name}: {value_str[:50]}")
                        break
                
                # 检查二氧化碳
                if '二氧化碳' in value_str:
                    has_eryang = True
            
            if has_co2:
                co2_count += 1
            if has_eryang:
                eryang_count += 1
    
    print(f"\n包含CO₂的设备: {co2_count}")
    print(f"包含二氧化碳的设备: {eryang_count}")
    
    if co2_count == 0 and eryang_count > 0:
        print("\n✅ 修复成功！")
    else:
        print("\n⚠️  可能需要重新运行修复脚本")
