#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修正座阀组合设备的参数配置"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

device_params = db_loader.get_config_by_key('device_params')

print('=' * 80)
print('修正座阀组合设备参数配置')
print('=' * 80)

# 修正前的状态
print('\n修正前:')
combined_switch = device_params['device_types']['座阀+座阀开关型执行器']
combined_modulating = device_params['device_types']['座阀+座阀调节型执行器']
print(f'座阀+座阀开关型执行器: {len(combined_switch["params"])} 个参数')
print(f'座阀+座阀调节型执行器: {len(combined_modulating["params"])} 个参数')

# 修正1: 座阀+座阀开关型执行器 - 删除"控制信号"
print('\n修正1: 座阀+座阀开关型执行器')
print('  删除多余参数: 控制信号')
combined_switch['params'] = [p for p in combined_switch['params'] if p['name'] != '控制信号']
print(f'  修正后参数数量: {len(combined_switch["params"])}')

# 修正2: 座阀+座阀调节型执行器 - 删除"响应时间"
print('\n修正2: 座阀+座阀调节型执行器')
print('  删除多余参数: 响应时间')
combined_modulating['params'] = [p for p in combined_modulating['params'] if p['name'] != '响应时间']
print(f'  修正后参数数量: {len(combined_modulating["params"])}')

# 保存到数据库
success = db_loader.update_config('device_params', device_params)

if success:
    print('\n' + '=' * 80)
    print('✅ 配置更新成功')
    print('=' * 80)
    
    # 验证修正结果
    print('\n验证修正结果:')
    device_params_new = db_loader.get_config_by_key('device_params')
    
    seat_valve = device_params_new['device_types']['座阀']
    switch_actuator = device_params_new['device_types']['座阀开关型执行器']
    modulating_actuator = device_params_new['device_types']['座阀调节型执行器']
    combined_switch_new = device_params_new['device_types']['座阀+座阀开关型执行器']
    combined_modulating_new = device_params_new['device_types']['座阀+座阀调节型执行器']
    
    print(f'  座阀: {len(seat_valve["params"])} 个参数')
    print(f'  座阀开关型执行器: {len(switch_actuator["params"])} 个参数')
    print(f'  座阀调节型执行器: {len(modulating_actuator["params"])} 个参数')
    print(f'  座阀+座阀开关型执行器: {len(combined_switch_new["params"])} 个参数 (预期: 17)')
    print(f'  座阀+座阀调节型执行器: {len(combined_modulating_new["params"])} 个参数 (预期: 18)')
    
    # 验证参数数量
    if len(combined_switch_new["params"]) == 17:
        print('\n  ✅ 座阀+座阀开关型执行器参数数量正确')
    else:
        print(f'\n  ❌ 座阀+座阀开关型执行器参数数量错误: {len(combined_switch_new["params"])} != 17')
    
    if len(combined_modulating_new["params"]) == 18:
        print('  ✅ 座阀+座阀调节型执行器参数数量正确')
    else:
        print(f'  ❌ 座阀+座阀调节型执行器参数数量错误: {len(combined_modulating_new["params"])} != 18')
    
    print('\n' + '=' * 80)
    print('说明:')
    print('=' * 80)
    print('1. 组合设备的参数 = 各组件参数的并集（去重）')
    print('2. "控制信号"属于调节型执行器，不属于开关型执行器')
    print('3. "响应时间"不属于座阀也不属于调节型执行器，是多余参数')
    print('4. 修正后的参数数量符合预期')
else:
    print('\n❌ 配置更新失败')
    sys.exit(1)
