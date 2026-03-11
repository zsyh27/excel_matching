#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""分析座阀组合设备参数重复问题"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

device_params = db_loader.get_config_by_key('device_params')

print('=' * 80)
print('座阀组合设备参数重复分析')
print('=' * 80)

# 获取各设备类型的参数
seat_valve_params = set([p['name'] for p in device_params['device_types']['座阀']['params']])
switch_actuator_params = set([p['name'] for p in device_params['device_types']['座阀开关型执行器']['params']])
modulating_actuator_params = set([p['name'] for p in device_params['device_types']['座阀调节型执行器']['params']])
combined_switch_params = set([p['name'] for p in device_params['device_types']['座阀+座阀开关型执行器']['params']])
combined_modulating_params = set([p['name'] for p in device_params['device_types']['座阀+座阀调节型执行器']['params']])

print('\n【座阀+座阀开关型执行器】分析:')
print(f'座阀参数: {len(seat_valve_params)} 个')
print(f'座阀开关型执行器参数: {len(switch_actuator_params)} 个')
print(f'组合设备配置参数: {len(combined_switch_params)} 个')

# 检查重复参数
overlap_switch = seat_valve_params & switch_actuator_params
print(f'\n重复参数: {len(overlap_switch)} 个')
if overlap_switch:
    print(f'  {overlap_switch}')

# 检查组合设备中多余的参数
expected_switch = seat_valve_params | switch_actuator_params
extra_switch = combined_switch_params - expected_switch
missing_switch = expected_switch - combined_switch_params

print(f'\n预期参数总数（去重后）: {len(expected_switch)} 个')
print(f'实际配置参数: {len(combined_switch_params)} 个')

if extra_switch:
    print(f'\n⚠️  多余的参数: {extra_switch}')
if missing_switch:
    print(f'\n⚠️  缺少的参数: {missing_switch}')

print('\n' + '=' * 80)
print('\n【座阀+座阀调节型执行器】分析:')
print(f'座阀参数: {len(seat_valve_params)} 个')
print(f'座阀调节型执行器参数: {len(modulating_actuator_params)} 个')
print(f'组合设备配置参数: {len(combined_modulating_params)} 个')

# 检查重复参数
overlap_modulating = seat_valve_params & modulating_actuator_params
print(f'\n重复参数: {len(overlap_modulating)} 个')
if overlap_modulating:
    print(f'  {overlap_modulating}')

# 检查组合设备中多余的参数
expected_modulating = seat_valve_params | modulating_actuator_params
extra_modulating = combined_modulating_params - expected_modulating
missing_modulating = expected_modulating - combined_modulating_params

print(f'\n预期参数总数（去重后）: {len(expected_modulating)} 个')
print(f'实际配置参数: {len(combined_modulating_params)} 个')

if extra_modulating:
    print(f'\n⚠️  多余的参数: {extra_modulating}')
if missing_modulating:
    print(f'\n⚠️  缺少的参数: {missing_modulating}')

print('\n' + '=' * 80)
print('\n总结:')
print('=' * 80)

if overlap_switch or overlap_modulating:
    print('\n✅ 发现重复参数是正常的（如"适配阀门"）')
    print('   组合设备的参数应该是两个组件参数的并集（去重）')
    print('   而不是简单相加')

if extra_switch or extra_modulating:
    print('\n❌ 发现多余参数，需要修正配置')
    print('   建议：')
    print('   1. 座阀+座阀开关型执行器应该有 {} 个参数（去重后）'.format(len(expected_switch)))
    print('   2. 座阀+座阀调节型执行器应该有 {} 个参数（去重后）'.format(len(expected_modulating)))

print('\n' + '=' * 80)
