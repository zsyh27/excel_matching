#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""最终验证"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device

# 重新初始化数据库连接
db_manager = DatabaseManager("sqlite:///data/devices.db")

print("最终验证...")

co2_variants = ['CO₂', 'Co₂', 'co₂', 'CO2', 'Co2', 'co2']

with db_manager.session_scope() as session:
    devices = session.query(Device).filter(
        Device.device_type == '空气质量传感器'
    ).all()
    
    co2_count = 0
    eryang_count = 0
    
    for device in devices:
        if device.key_params:
            for param_name, param_data in device.key_params.items():
                value_str = ''
                if isinstance(param_data, dict) and 'value' in param_data:
                    value_str = str(param_data['value'])
                
                # 检查CO₂
                has_co2 = any(variant in value_str for variant in co2_variants)
                if has_co2:
                    co2_count += 1
                    print(f"CO₂: {device.device_id} - {param_name}: {value_str[:50]}")
                
                # 检查二氧化碳
                if '二氧化碳' in value_str:
                    eryang_count += 1
    
    print(f"\n包含CO₂的参数: {co2_count}")
    print(f"包含二氧化碳的参数: {eryang_count}")
    
    if co2_count == 0:
        print("\n✅ 修复成功！所有CO₂已替换为二氧化碳")
    else:
        print("\n⚠️  仍有CO₂未替换")
