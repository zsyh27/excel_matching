#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
步骤1：添加静态平衡阀设备参数配置
基于步骤0的Excel分析结果
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

print('=' * 80)
print('添加静态平衡阀设备参数配置')
print('=' * 80)

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 获取当前配置
device_params = db_loader.get_config_by_key('device_params')

if not device_params or 'device_types' not in device_params:
    print("❌ device_params 配置不存在")
    sys.exit(1)

# 定义新设备类型配置（基于步骤0的分析结果）
new_device_type_config = {
    "静态平衡阀": {
        "keywords": ["静态平衡阀", "平衡阀"],
        "params": [
            {"name": "公称通径", "type": "string", "required": False},
            {"name": "公称压力", "type": "string", "required": False},
            {"name": "连接方式", "type": "string", "required": False},
            {"name": "阀体材质", "type": "string", "required": False},
            {"name": "密封材质", "type": "string", "required": False},
            {"name": "适用介质", "type": "string", "required": False},
            {"name": "介质温度", "type": "string", "required": False},
            {"name": "操作方式", "type": "string", "required": False},
            {"name": "流量特性", "type": "string", "required": False},
        ]
    },
    "动态压差阀": {
        "keywords": ["动态压差阀", "压差阀"],
        "params": [
            {"name": "公称通径", "type": "string", "required": False},
            {"name": "公称压力", "type": "string", "required": False},
            {"name": "连接方式", "type": "string", "required": False},
            {"name": "阀体材质", "type": "string", "required": False},
            {"name": "密封材质", "type": "string", "required": False},
            {"name": "适用介质", "type": "string", "required": False},
            {"name": "介质温度", "type": "string", "required": False},
            {"name": "操作方式", "type": "string", "required": False},
            {"name": "流量特性", "type": "string", "required": False},
            {"name": "调节范围", "type": "string", "required": False},
        ]
    },
    "动态压差控制阀": {
        "keywords": ["动态压差控制阀", "压差控制阀"],
        "params": [
            {"name": "公称通径", "type": "string", "required": False},
            {"name": "公称压力", "type": "string", "required": False},
            {"name": "连接方式", "type": "string", "required": False},
            {"name": "阀体材质", "type": "string", "required": False},
            {"name": "密封材质", "type": "string", "required": False},
            {"name": "适用介质", "type": "string", "required": False},
            {"name": "介质温度", "type": "string", "required": False},
            {"name": "操作方式", "type": "string", "required": False},
            {"name": "流量特性", "type": "string", "required": False},
            {"name": "调节范围", "type": "string", "required": False},
        ]
    },
    "动态压差控制阀专用支架": {
        "keywords": ["动态压差控制阀专用支架", "压差阀支架", "阀门支架"],
        "params": [
            {"name": "适配阀门", "type": "string", "required": False},
            {"name": "适配通径", "type": "string", "required": False},
            {"name": "功能类型", "type": "string", "required": False},
            {"name": "安装方式", "type": "string", "required": False},
            {"name": "材质", "type": "string", "required": False},
            {"name": "适用温度", "type": "string", "required": False},
            {"name": "防护等级", "type": "string", "required": False},
        ]
    }
}

# 添加到配置中
print('\n添加设备类型配置:')
for device_type, config in new_device_type_config.items():
    if device_type in device_params['device_types']:
        print(f'  ⚠️  {device_type} - 已存在，跳过')
    else:
        device_params['device_types'][device_type] = config
        print(f'  ✅ {device_type} - 参数数量: {len(config["params"])}')

# 保存到数据库
print('\n保存配置到数据库...')
success = db_loader.update_config('device_params', device_params)

if success:
    print('✅ 配置更新成功')
    print('\n配置摘要:')
    for device_type in new_device_type_config.keys():
        config = device_params['device_types'].get(device_type, {})
        print(f'  - {device_type}: {len(config.get("params", []))} 个参数')
else:
    print('❌ 配置更新失败')
    sys.exit(1)

print('\n' + '=' * 80)
print('配置添加完成！')
print('=' * 80)
print('\n下一步：运行 import_static_balance_valve_devices.py 导入设备数据')
