#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查所有座阀相关设备类型的配置参数数量"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

device_params = db_loader.get_config_by_key('device_params')

print('=' * 80)
print('座阀相关设备类型配置参数数量检查')
print('=' * 80)

# 需要检查的设备类型
device_types_to_check = [
    '座阀',
    '座阀开关型执行器',
    '座阀调节型执行器',
    '座阀+座阀开关型执行器',
    '座阀+座阀调节型执行器'
]

results = {}

for device_type in device_types_to_check:
    config = device_params['device_types'].get(device_type, {})
    params = config.get('params', [])
    results[device_type] = {
        'count': len(params),
        'params': [p['name'] for p in params]
    }
    
    print(f'\n{device_type}:')
    print(f'  参数数量: {len(params)}')
    print(f'  参数列表:')
    for i, param_name in enumerate(results[device_type]['params'], 1):
        print(f'    {i}. {param_name}')

# 验证组合设备的参数数量
print('\n' + '=' * 80)
print('参数数量验证')
print('=' * 80)

seat_valve_count = results['座阀']['count']
switch_actuator_count = results['座阀开关型执行器']['count']
modulating_actuator_count = results['座阀调节型执行器']['count']
combined_switch_count = results['座阀+座阀开关型执行器']['count']
combined_modulating_count = results['座阀+座阀调节型执行器']['count']

print(f'\n座阀: {seat_valve_count} 个参数')
print(f'座阀开关型执行器: {switch_actuator_count} 个参数')
print(f'座阀调节型执行器: {modulating_actuator_count} 个参数')

print(f'\n组合设备验证:')
print(f'座阀+座阀开关型执行器: {combined_switch_count} 个参数')
print(f'  预期: {seat_valve_count} + {switch_actuator_count} = {seat_valve_count + switch_actuator_count}')
if combined_switch_count == seat_valve_count + switch_actuator_count:
    print(f'  ✅ 正确')
else:
    print(f'  ❌ 错误！实际 {combined_switch_count} != 预期 {seat_valve_count + switch_actuator_count}')

print(f'\n座阀+座阀调节型执行器: {combined_modulating_count} 个参数')
print(f'  预期: {seat_valve_count} + {modulating_actuator_count} = {seat_valve_count + modulating_actuator_count}')
if combined_modulating_count == seat_valve_count + modulating_actuator_count:
    print(f'  ✅ 正确')
else:
    print(f'  ❌ 错误！实际 {combined_modulating_count} != 预期 {seat_valve_count + modulating_actuator_count}')

print('\n' + '=' * 80)
