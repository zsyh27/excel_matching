#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""添加座阀设备类型参数配置 - Step 1"""

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
print('添加座阀设备类型参数配置')
print('=' * 80)

# 定义座阀设备类型配置（基于Excel分析结果）
seat_valve_config = {
    '座阀': {
        'keywords': ['座阀', '水阀', '球阀', 'seat valve'],
        'params': [
            {'name': '阀型', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '介质温度', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '流量特性', 'type': 'string', 'required': False},
            {'name': '阀内件材质', 'type': 'string', 'required': False},
            {'name': '供电电压', 'type': 'string', 'required': False},
            {'name': '控制类型', 'type': 'string', 'required': False},
            {'name': '控制信号', 'type': 'string', 'required': False},
            {'name': '响应时间', 'type': 'string', 'required': False},
            {'name': '复位方式', 'type': 'string', 'required': False},
            {'name': '运行角度', 'type': 'string', 'required': False},
            {'name': '适配阀门', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
            {'name': '额定扭矩', 'type': 'string', 'required': False},
        ]
    },
    '座阀开关型执行器': {
        'keywords': ['座阀开关型执行器', '开关型执行器', 'seat valve actuator'],
        'params': [
            {'name': '额定扭矩', 'type': 'string', 'required': False},
            {'name': '供电电压', 'type': 'string', 'required': False},
            {'name': '控制类型', 'type': 'string', 'required': False},
            {'name': '复位方式', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
            {'name': '运行角度', 'type': 'string', 'required': False},
            {'name': '适配阀门', 'type': 'string', 'required': False},
        ]
    },
    '座阀调节型执行器': {
        'keywords': ['座阀调节型执行器', '调节型执行器', 'modulating actuator'],
        'params': [
            {'name': '额定扭矩', 'type': 'string', 'required': False},
            {'name': '供电电压', 'type': 'string', 'required': False},
            {'name': '控制类型', 'type': 'string', 'required': False},
            {'name': '控制信号', 'type': 'string', 'required': False},
            {'name': '复位方式', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
            {'name': '运行角度', 'type': 'string', 'required': False},
            {'name': '适配阀门', 'type': 'string', 'required': False},
        ]
    },
    '座阀+座阀开关型执行器': {
        'keywords': ['座阀+座阀开关型执行器', '座阀开关型'],
        'params': [
            # 座阀参数（11个）
            {'name': '阀型', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '介质温度', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '流量特性', 'type': 'string', 'required': False},
            {'name': '阀内件材质', 'type': 'string', 'required': False},
            {'name': '适配阀门', 'type': 'string', 'required': False},
            # 执行器参数（7个）
            {'name': '额定扭矩', 'type': 'string', 'required': False},
            {'name': '供电电压', 'type': 'string', 'required': False},
            {'name': '控制类型', 'type': 'string', 'required': False},
            {'name': '复位方式', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
            {'name': '运行角度', 'type': 'string', 'required': False},
            {'name': '控制信号', 'type': 'string', 'required': False},
        ]
    },
    '座阀+座阀调节型执行器': {
        'keywords': ['座阀+座阀调节型执行器', '座阀调节型'],
        'params': [
            # 座阀参数（11个）
            {'name': '阀型', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '介质温度', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '流量特性', 'type': 'string', 'required': False},
            {'name': '阀内件材质', 'type': 'string', 'required': False},
            {'name': '适配阀门', 'type': 'string', 'required': False},
            # 执行器参数（7个）
            {'name': '额定扭矩', 'type': 'string', 'required': False},
            {'name': '供电电压', 'type': 'string', 'required': False},
            {'name': '控制类型', 'type': 'string', 'required': False},
            {'name': '控制信号', 'type': 'string', 'required': False},
            {'name': '复位方式', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
            {'name': '运行角度', 'type': 'string', 'required': False},
            {'name': '响应时间', 'type': 'string', 'required': False},
        ]
    }
}

# 添加配置
for device_type, config in seat_valve_config.items():
    print(f'\n添加设备类型: {device_type}')
    print(f'  参数数量: {len(config["params"])}')
    device_params['device_types'][device_type] = config

# 保存到数据库
success = db_loader.update_config('device_params', device_params)

if success:
    print('\n' + '=' * 80)
    print('✅ 配置更新成功')
    print('=' * 80)
    
    # 验证配置
    print('\n验证配置:')
    for device_type in seat_valve_config.keys():
        saved_config = device_params['device_types'].get(device_type)
        if saved_config:
            print(f'  ✅ {device_type}: {len(saved_config["params"])} 个参数')
        else:
            print(f'  ❌ {device_type}: 配置未找到')
else:
    print('\n❌ 配置更新失败')
    sys.exit(1)
