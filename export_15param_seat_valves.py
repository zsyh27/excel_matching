#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""导出15个参数的座阀设备详细数据"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device
import json

db_manager = DatabaseManager("sqlite:///data/devices.db")

print('=' * 80)
print('15个参数的座阀设备详细数据')
print('=' * 80)

with db_manager.session_scope() as session:
    # 查询所有"座阀"类型的设备
    devices = session.query(Device).filter(
        Device.device_type == '座阀'
    ).all()
    
    # 找出15个参数的设备
    devices_15_params = []
    for device in devices:
        if device.key_params and len(device.key_params) == 15:
            devices_15_params.append(device)
    
    print(f'\n找到 {len(devices_15_params)} 个15参数的座阀设备\n')
    
    # 显示所有设备的详细信息
    for i, device in enumerate(devices_15_params, 1):
        print(f'\n{"=" * 80}')
        print(f'设备 {i}/{len(devices_15_params)}')
        print(f'{"=" * 80}')
        print(f'设备ID: {device.device_id}')
        print(f'型号: {device.spec_model}')
        print(f'品牌: {device.brand}')
        print(f'单价: {device.unit_price}')
        print(f'参数数量: {len(device.key_params)}')
        
        print(f'\n详细说明（detailed_params）:')
        print(f'{device.detailed_params}')
        
        print(f'\nkey_params（JSON格式）:')
        for param_name, param_value in device.key_params.items():
            value = param_value.get('value', '') if isinstance(param_value, dict) else param_value
            print(f'  {param_name}: {value}')
        
        # 检查是否包含执行器参数
        actuator_params = ['额定扭矩', '供电电压', '控制类型', '控制信号', 
                         '复位方式', '防护等级', '运行角度', '适配阀门']
        has_actuator_params = [p for p in actuator_params if p in device.key_params]
        
        if has_actuator_params:
            print(f'\n⚠️  包含执行器参数: {has_actuator_params}')
        
        # 分析设备类型
        if '电动' in device.detailed_params or '电动' in device.spec_model:
            print(f'\n💡 分析: 这是一体化电动座阀（阀门+执行器集成）')
        elif '+' in device.spec_model:
            print(f'\n💡 分析: 型号中包含"+"，可能是组合设备')
        else:
            print(f'\n💡 分析: 需要进一步确认设备类型')
    
    # 生成CSV格式的数据
    print(f'\n\n{"=" * 80}')
    print('CSV格式数据（可复制到Excel）')
    print(f'{"=" * 80}\n')
    
    print('序号,型号,设备类型,参数数量,详细说明')
    for i, device in enumerate(devices_15_params, 1):
        # 转义逗号和引号
        description = device.detailed_params.replace('"', '""')
        print(f'{i},"{device.spec_model}",座阀,{len(device.key_params)},"{description}"')
    
    # 统计参数使用情况
    print(f'\n\n{"=" * 80}')
    print('参数使用统计')
    print(f'{"=" * 80}\n')
    
    all_params = {}
    for device in devices_15_params:
        for param_name in device.key_params.keys():
            if param_name not in all_params:
                all_params[param_name] = 0
            all_params[param_name] += 1
    
    print(f'参数名称 | 使用次数 | 使用率')
    print('-' * 50)
    for param_name in sorted(all_params.keys()):
        count = all_params[param_name]
        percentage = (count / len(devices_15_params)) * 100
        print(f'{param_name} | {count}/{len(devices_15_params)} | {percentage:.1f}%')
