#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查可能误分类的座阀设备"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device

db_manager = DatabaseManager("sqlite:///data/devices.db")

print('=' * 80)
print('检查可能误分类的座阀设备')
print('=' * 80)

with db_manager.session_scope() as session:
    # 查询所有"座阀"类型的设备
    devices = session.query(Device).filter(
        Device.device_type == '座阀'
    ).all()
    
    # 找出参数数量异常的设备（超过7个参数的）
    abnormal_devices = []
    for device in devices:
        if device.key_params and len(device.key_params) > 7:
            abnormal_devices.append(device)
    
    print(f'\n找到 {len(abnormal_devices)} 个参数数量异常的座阀设备\n')
    
    # 按参数数量分组
    by_param_count = {}
    for device in abnormal_devices:
        count = len(device.key_params)
        if count not in by_param_count:
            by_param_count[count] = []
        by_param_count[count].append(device)
    
    # 显示每组的详细信息
    for count in sorted(by_param_count.keys()):
        devices_in_group = by_param_count[count]
        print(f'\n{"=" * 80}')
        print(f'参数数量: {count} 个 ({len(devices_in_group)} 个设备)')
        print(f'{"=" * 80}')
        
        # 显示前5个设备
        for i, device in enumerate(devices_in_group[:5], 1):
            print(f'\n{i}. 型号: {device.spec_model}')
            print(f'   设备ID: {device.device_id}')
            print(f'   参数列表: {list(device.key_params.keys())}')
            
            # 检查是否包含执行器参数
            actuator_params = ['额定扭矩', '供电电压', '控制类型', '控制信号', 
                             '复位方式', '防护等级', '运行角度', '适配阀门']
            has_actuator_params = any(p in device.key_params for p in actuator_params)
            
            if has_actuator_params:
                found_params = [p for p in actuator_params if p in device.key_params]
                print(f'   ⚠️  包含执行器参数: {found_params}')
                print(f'   ⚠️  可能应该分类为组合设备')
            
            # 显示详细参数
            if device.detailed_params:
                print(f'   详细说明: {device.detailed_params[:150]}...')
        
        if len(devices_in_group) > 5:
            print(f'\n   ... 还有 {len(devices_in_group) - 5} 个设备')
    
    print('\n' + '=' * 80)
    print('建议:')
    print('=' * 80)
    print('1. 检查这些设备的型号，确认是否应该分类为组合设备')
    print('2. 如果是组合设备，应该重新分类为"座阀+座阀开关型执行器"或"座阀+座阀调节型执行器"')
    print('3. 如果确实是纯座阀，但包含执行器参数，需要清理数据')
