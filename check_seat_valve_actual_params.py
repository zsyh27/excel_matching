#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查实际导入的座阀设备参数"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device
from collections import Counter

db_manager = DatabaseManager("sqlite:///data/devices.db")

print('=' * 80)
print('检查实际导入的座阀设备参数')
print('=' * 80)

with db_manager.session_scope() as session:
    # 查询所有"座阀"类型的设备
    devices = session.query(Device).filter(
        Device.device_type == '座阀'
    ).all()
    
    print(f'\n找到 {len(devices)} 个座阀设备\n')
    
    # 统计参数数量分布
    param_count_dist = Counter()
    all_params = set()
    
    # 查看前10个设备的详细信息
    print('前10个设备的参数详情:')
    print('-' * 80)
    for i, device in enumerate(devices[:10], 1):
        if device.key_params:
            param_count = len(device.key_params)
            param_count_dist[param_count] += 1
            all_params.update(device.key_params.keys())
            
            print(f'\n{i}. 设备ID: {device.device_id}')
            print(f'   型号: {device.spec_model}')
            print(f'   参数数量: {param_count}')
            print(f'   参数列表: {list(device.key_params.keys())}')
    
    # 统计所有设备的参数数量
    for device in devices:
        if device.key_params:
            param_count_dist[len(device.key_params)] += 1
            all_params.update(device.key_params.keys())
    
    print('\n' + '=' * 80)
    print('参数数量分布统计:')
    print('=' * 80)
    for count in sorted(param_count_dist.keys()):
        print(f'  {count} 个参数: {param_count_dist[count]} 个设备')
    
    print('\n' + '=' * 80)
    print(f'所有座阀设备使用的参数（共 {len(all_params)} 个）:')
    print('=' * 80)
    for param in sorted(all_params):
        print(f'  - {param}')
    
    # 统计每个参数的使用频率
    param_usage = Counter()
    for device in devices:
        if device.key_params:
            for param in device.key_params.keys():
                param_usage[param] += 1
    
    print('\n' + '=' * 80)
    print('参数使用频率（从高到低）:')
    print('=' * 80)
    for param, count in param_usage.most_common():
        percentage = (count / len(devices)) * 100
        print(f'  {param}: {count}/{len(devices)} ({percentage:.1f}%)')
