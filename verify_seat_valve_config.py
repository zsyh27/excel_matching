#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证座阀配置状态"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

device_params = db_loader.get_config_by_key('device_params')

if device_params and 'device_types' in device_params:
    seat_valve_config = device_params['device_types'].get('座阀', {})
    
    print('=' * 80)
    print('座阀配置验证')
    print('=' * 80)
    print(f'\n座阀参数数量: {len(seat_valve_config.get("params", []))}')
    print(f'\n参数列表:')
    for i, param in enumerate(seat_valve_config.get('params', []), 1):
        print(f'  {i}. {param["name"]}')
    
    print('\n' + '=' * 80)
    print('✅ 配置验证完成')
    print('=' * 80)
else:
    print('❌ 配置不存在')
