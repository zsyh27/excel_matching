#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试CO₂修复"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

print("开始测试...")

with db_manager.session_scope() as session:
    # 查询所有空气质量传感器
    devices = session.query(Device).filter(
        Device.device_type == '空气质量传感器'
    ).all()
    
    print(f"找到 {len(devices)} 个空气质量传感器")
    
    # CO₂的各种变体
    co2_variants = ['CO₂', 'Co₂', 'co₂', 'CO2', 'Co2', 'co2']
    
    found_count = 0
    for device in devices:
        if device.key_params:
            for param_name, param_data in device.key_params.items():
                value_str = ''
                if isinstance(param_data, dict) and 'value' in param_data:
                    value_str = str(param_data['value'])
                elif isinstance(param_data, str):
                    value_str = param_data
                
                # 检查是否包含CO₂
                for variant in co2_variants:
                    if variant in value_str:
                        found_count += 1
                        print(f"\n设备: {device.device_id}")
                        print(f"  参数: {param_name}")
                        print(f"  值: {value_str[:100]}")
                        break

    print(f"\n总共找到 {found_count} 个包含CO₂的参数值")

print("测试完成")
