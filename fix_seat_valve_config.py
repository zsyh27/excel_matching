#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修正座阀配置 - 只保留纯座阀的核心参数"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 获取当前配置
device_params = db_loader.get_config_by_key('device_params')

if not device_params or 'device_types' not in device_params:
    print("❌ device_params 配置不存在")
    sys.exit(1)

print('=' * 80)
print('修正座阀设备类型参数配置')
print('=' * 80)

# 修正后的座阀配置（只保留纯座阀的核心参数）
corrected_seat_valve_config = {
    '座阀': {
        'keywords': ['座阀', '水阀', '球阀', 'seat valve'],
        'params': [
            # 核心参数（7个 - 所有座阀都有）
            {'name': '阀型', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '介质温度', 'type': 'string', 'required': False},
            # 可选参数（2个 - 部分座阀有）
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '流量特性', 'type': 'string', 'required': False},
            # 阀内件材质（部分座阀有）
            {'name': '阀内件材质', 'type': 'string', 'required': False},
        ]
    }
}

print('\n修正前的配置:')
old_config = device_params['device_types'].get('座阀', {})
print(f'  参数数量: {len(old_config.get("params", []))}')

# 更新配置
device_params['device_types']['座阀'] = corrected_seat_valve_config['座阀']

print('\n修正后的配置:')
new_config = device_params['device_types']['座阀']
print(f'  参数数量: {len(new_config["params"])}')
print(f'  参数列表:')
for i, param in enumerate(new_config['params'], 1):
    print(f'    {i}. {param["name"]}')

# 保存到数据库
success = db_loader.update_config('device_params', device_params)

if success:
    print('\n' + '=' * 80)
    print('✅ 配置更新成功')
    print('=' * 80)
    
    # 验证配置
    print('\n验证配置:')
    saved_config = device_params['device_types'].get('座阀')
    if saved_config:
        print(f'  ✅ 座阀: {len(saved_config["params"])} 个参数')
    else:
        print(f'  ❌ 座阀: 配置未找到')
    
    print('\n' + '=' * 80)
    print('说明:')
    print('=' * 80)
    print('1. 座阀配置已修正为10个核心参数')
    print('2. 这些参数覆盖了纯座阀设备的所有常见参数')
    print('3. 一体化电动座阀（如VH58S系列）应该作为独立设备类型处理')
    print('4. 如果需要，可以添加"一体化电动座阀"作为新的设备类型')
else:
    print('\n❌ 配置更新失败')
    sys.exit(1)
