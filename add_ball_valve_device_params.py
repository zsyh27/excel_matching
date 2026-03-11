#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""添加球阀设备类型参数配置 - 步骤1"""

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

# 3. 定义球阀设备类型配置（基于Excel分析结果）
ball_valve_config = {
    '球阀': {
        'keywords': ['球阀', 'ball valve', '二通球阀', '三通球阀'],
        'params': [
            {'name': 'KVS', 'type': 'string', 'required': False},
            {'name': '介质温度', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '关断压差', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '操作方式', 'type': 'string', 'required': False},
            {'name': '流量特性', 'type': 'string', 'required': False},
            {'name': '版本号', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '阀型', 'type': 'string', 'required': False},
        ]
    },
    '球阀+球阀开关型执行器': {
        'keywords': ['球阀+球阀开关型执行器', '球阀开关型'],
        'params': [
            # 球阀参数（13个）
            {'name': 'KVS', 'type': 'string', 'required': False},
            {'name': '介质温度', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '关断压差', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '操作方式', 'type': 'string', 'required': False},
            {'name': '流量特性', 'type': 'string', 'required': False},
            {'name': '版本号', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '阀型', 'type': 'string', 'required': False},
            # 执行器参数（9个）
            {'name': '供电电压', 'type': 'string', 'required': False},
            {'name': '复位方式', 'type': 'string', 'required': False},
            {'name': '执行器类型', 'type': 'string', 'required': False},
            {'name': '控制类型', 'type': 'string', 'required': False},
            {'name': '特点', 'type': 'string', 'required': False},
            {'name': '辅助开关', 'type': 'string', 'required': False},
            {'name': '运行时间', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
            {'name': '额定扭矩', 'type': 'string', 'required': False},
        ]
    },
    '球阀+球阀调节型执行器': {
        'keywords': ['球阀+球阀调节型执行器', '球阀调节型'],
        'params': [
            # 球阀参数（13个）
            {'name': 'KVS', 'type': 'string', 'required': False},
            {'name': '介质温度', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '关断压差', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '操作方式', 'type': 'string', 'required': False},
            {'name': '流量特性', 'type': 'string', 'required': False},
            {'name': '版本号', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '阀型', 'type': 'string', 'required': False},
            # 执行器参数（9个）
            {'name': '供电电压', 'type': 'string', 'required': False},
            {'name': '功能', 'type': 'string', 'required': False},
            {'name': '复位方式', 'type': 'string', 'required': False},
            {'name': '执行器类型', 'type': 'string', 'required': False},
            {'name': '控制信号', 'type': 'string', 'required': False},
            {'name': '控制类型', 'type': 'string', 'required': False},
            {'name': '特点', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
            {'name': '额定扭矩', 'type': 'string', 'required': False},
        ]
    },
    '球阀开关型执行器': {
        'keywords': ['球阀开关型执行器', '开关型执行器'],
        'params': [
            {'name': '供电电压', 'type': 'string', 'required': False},
            {'name': '复位方式', 'type': 'string', 'required': False},
            {'name': '执行器类型', 'type': 'string', 'required': False},
            {'name': '控制类型', 'type': 'string', 'required': False},
            {'name': '特点', 'type': 'string', 'required': False},
            {'name': '辅助开关', 'type': 'string', 'required': False},
            {'name': '运行时间', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
            {'name': '额定扭矩', 'type': 'string', 'required': False},
        ]
    },
    '球阀调节型执行器': {
        'keywords': ['球阀调节型执行器', '调节型执行器'],
        'params': [
            {'name': '供电电压', 'type': 'string', 'required': False},
            {'name': '功能', 'type': 'string', 'required': False},
            {'name': '复位方式', 'type': 'string', 'required': False},
            {'name': '执行器类型', 'type': 'string', 'required': False},
            {'name': '控制信号', 'type': 'string', 'required': False},
            {'name': '控制类型', 'type': 'string', 'required': False},
            {'name': '特点', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
            {'name': '额定扭矩', 'type': 'string', 'required': False},
        ]
    }
}

# 4. 添加到配置中
print('=' * 80)
print('添加球阀设备类型参数配置')
print('=' * 80)

for device_type, config in ball_valve_config.items():
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
    print('1. 重启后端服务（清除Python缓存）')
    print('2. 运行导入脚本：python import_ball_valve_devices.py')
else:
    print('\n❌ 配置更新失败')
    sys.exit(1)
