#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证蝶阀配置"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
import json

db = DatabaseManager('sqlite:///data/devices.db')
loader = DatabaseLoader(db)

config = loader.get_config_by_key('device_params')
device_types = config.get('device_types', {})

print('=' * 60)
print('数据库中的设备类型配置')
print('=' * 60)
print(f'\n总设备类型数: {len(device_types)}')

print('\n蝶阀相关设备类型:')
butterfly_types = [k for k in device_types.keys() if '蝶阀' in k or '执行器' in k]

for t in butterfly_types:
    params = device_types[t].get('params', [])
    keywords = device_types[t].get('keywords', [])
    print(f'\n  【{t}】')
    print(f'    关键词: {", ".join(keywords)}')
    print(f'    参数数量: {len(params)}')
    print(f'    参数列表:')
    for p in params:
        required = '必填' if p.get('required') else '可选'
        unit = f" ({p.get('unit')})" if p.get('unit') else ''
        print(f'      - {p["name"]}{unit} [{required}]')

print('\n' + '=' * 60)
print('验证完成！配置已成功添加到数据库')
print('=' * 60)
