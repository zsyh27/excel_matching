#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""添加其他阀门设备类型参数配置 - 步骤1"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

# 1. 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 2. 获取当前配置
device_params = db_loader.get_config_by_key('device_params')

if not device_params or 'device_types' not in device_params:
    print("❌ device_params 配置不存在")
    sys.exit(1)

# 3. 定义其他阀门设备类型配置（基于Excel分析结果）
other_valves_config = {
    '减压阀': {
        'keywords': ['减压阀', 'pressure reducing valve', '减压'],
        'params': [
            {'name': '介质温度', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '操作方式', 'type': 'string', 'required': False},
            {'name': '调节范围', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '阀门类型', 'type': 'string', 'required': False},
        ]
    },
    '截止阀': {
        'keywords': ['截止阀', 'globe valve', '截止'],
        'params': [
            {'name': '介质温度', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '操作方式', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '阀门类型', 'type': 'string', 'required': False},
        ]
    },
    '手动球阀': {
        'keywords': ['手动球阀', 'manual ball valve', '手动球'],
        'params': [
            {'name': '介质温度', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '操作方式', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
        ]
    },
    '手动蝶阀': {
        'keywords': ['手动蝶阀', 'manual butterfly valve', '手动蝶'],
        'params': [
            {'name': '介质温度', 'type': 'string', 'required': False},
            {'name': '低泄漏认证', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '操作方式', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '阀体加厚', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '阀门类型', 'type': 'string', 'required': False},
            {'name': '防火认证', 'type': 'string', 'required': False},
        ]
    },
    '手动闸阀': {
        'keywords': ['手动闸阀', 'manual gate valve', '手动闸', '闸阀'],
        'params': [
            {'name': '介质温度', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '操作方式', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '阀门类型', 'type': 'string', 'required': False},
        ]
    },
    '排气阀': {
        'keywords': ['排气阀', 'air vent', '排气'],
        'params': [
            {'name': '介质温度', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '排气量', 'type': 'string', 'required': False},
            {'name': '操作方式', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '阀门类型', 'type': 'string', 'required': False},
        ]
    },
    '止回阀': {
        'keywords': ['止回阀', 'check valve', '止回', '逆止阀'],
        'params': [
            {'name': '介质温度', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '操作方式', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '阀门类型', 'type': 'string', 'required': False},
        ]
    },
    '过滤器': {
        'keywords': ['过滤器', 'filter', 'strainer', '滤网'],
        'params': [
            {'name': '介质温度', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '操作方式', 'type': 'string', 'required': False},
            {'name': '过滤精度', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '阀门类型', 'type': 'string', 'required': False},
        ]
    }
}

# 4. 添加到配置中
print('=' * 80)
print('添加其他阀门设备类型参数配置')
print('=' * 80)

for device_type, config in other_valves_config.items():
    if device_type in device_params['device_types']:
        print(f"⚠️  设备类型 '{device_type}' 已存在，跳过")
    else:
        print(f"✅ 添加设备类型: {device_type}")
        device_params['device_types'][device_type] = config
        print(f"   参数数量: {len(config['params'])}")

# 5. 保存到数据库
success = db_loader.update_config('device_params', device_params)

if success:
    print('\n' + '=' * 80)
    print('✅ 配置更新成功！')
    print('=' * 80)
    print('\n下一步：')
    print('运行导入脚本：python import_other_valves_devices.py')
else:
    print('\n❌ 配置更新失败')
    sys.exit(1)
