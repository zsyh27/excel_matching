#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简单验证霍尼韦尔传感器导入结果"""

import sys
sys.path.insert(0, 'backend')
from modules.database import DatabaseManager
from modules.models import Device

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

print("🔍 验证霍尼韦尔传感器导入结果...")

with db_manager.session_scope() as session:
    # 查询霍尼韦尔传感器设备
    sensor_devices = session.query(Device).filter(
        Device.brand == '霍尼韦尔',
        Device.device_type.in_(['温度传感器', '温湿度传感器'])
    ).all()
    
    print(f"📊 霍尼韦尔传感器设备总数: {len(sensor_devices)}")
    
    # 统计设备类型
    temp_count = 0
    humidity_count = 0
    
    for device in sensor_devices:
        if device.device_type == '温度传感器':
            temp_count += 1
        elif device.device_type == '温湿度传感器':
            humidity_count += 1
    
    print(f"   温度传感器: {temp_count} 个设备")
    print(f"   温湿度传感器: {humidity_count} 个设备")
    
    # 检查第一个设备的参数
    if sensor_devices:
        first_device = sensor_devices[0]
        print(f"\n🔍 第一个设备示例:")
        print(f"   设备名称: {first_device.device_name}")
        print(f"   设备类型: {first_device.device_type}")
        print(f"   规格型号: {first_device.spec_model}")
        
        if first_device.key_params:
            print(f"   参数数量: {len(first_device.key_params)}")
            
            # 检查是否包含检测对象
            if '检测对象' in first_device.key_params:
                print(f"   ✅ 包含检测对象: {first_device.key_params['检测对象']['value']}")
            else:
                print(f"   ❌ 缺少检测对象参数")
                
            # 显示前5个参数
            print(f"   前5个参数:")
            for i, (key, value) in enumerate(list(first_device.key_params.items())[:5]):
                print(f"     {key}: {value['value']}")
        else:
            print(f"   ❌ 没有key_params数据")

print(f"\n✅ 验证完成！")