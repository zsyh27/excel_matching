#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""添加动态压差平衡阀设备类型参数配置"""

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

# 3. 定义动态压差平衡阀设备类型配置（基于Excel分析结果）
dynamic_balance_valve_config = {
    '动态压差平衡开关型执行器': {
        'keywords': ['动态压差平衡开关型执行器', '开关型执行器', '动态压差执行器'],
        'params': [
            {'name': '供电电压', 'type': 'string', 'required': False},
            {'name': '动作类型', 'type': 'string', 'required': False},
            {'name': '外壳材质', 'type': 'string', 'required': False},
            {'name': '工作温度', 'type': 'string', 'required': False},
            {'name': '恒定电流', 'type': 'string', 'required': False},
            {'name': '核心功能', 'type': 'string', 'required': False},
            {'name': '起始电流', 'type': 'string', 'required': False},
            {'name': '运行时间', 'type': 'string', 'required': False},
            {'name': '适配阀门', 'type': 'string', 'required': False},
            {'name': '阀门连接', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
            {'name': '额定功耗', 'type': 'string', 'required': False},
            {'name': '额定推力', 'type': 'string', 'required': False},
            {'name': '额定行程', 'type': 'string', 'required': False},
        ]
    },
    '风机盘管用动态压差平衡电动二通开关阀+动态压差平衡开关型执行器': {
        'keywords': ['风机盘管用动态压差平衡电动二通开关阀', '动态压差平衡电动二通开关阀', '组合阀门'],
        'params': [
            {'name': '介质温度', 'type': 'string', 'required': False},
            {'name': '供电电压', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '关闭压差', 'type': 'string', 'required': False},
            {'name': '动作类型', 'type': 'string', 'required': False},
            {'name': '外壳材质', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '工作温度', 'type': 'string', 'required': False},
            {'name': '恒定电流', 'type': 'string', 'required': False},
            {'name': '操作方式', 'type': 'string', 'required': False},
            {'name': '核心功能', 'type': 'string', 'required': False},
            {'name': '流量特性', 'type': 'string', 'required': False},
            {'name': '起始电流', 'type': 'string', 'required': False},
            {'name': '运行时间', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '适配阀门', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '阀门类型', 'type': 'string', 'required': False},
            {'name': '阀门连接', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
            {'name': '额定功耗', 'type': 'string', 'required': False},
            {'name': '额定推力', 'type': 'string', 'required': False},
            {'name': '额定行程', 'type': 'string', 'required': False},
        ]
    },
    '动态压差平衡电动调节阀': {
        'keywords': ['动态压差平衡电动调节阀', '电动调节阀', '动态压差调节阀'],
        'params': [
            {'name': '介质温度', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '压差控制范围', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '操作方式', 'type': 'string', 'required': False},
            {'name': '流量特性', 'type': 'string', 'required': False},
            {'name': '调节范围', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '阀门类型', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
        ]
    },
    '动态压差平衡电动调节阀+动态压差平衡调节型执行器': {
        'keywords': ['动态压差平衡电动调节阀+动态压差平衡调节型执行器', '调节阀+调节型执行器', '组合调节阀'],
        'params': [
            {'name': '介质温度', 'type': 'string', 'required': False},
            {'name': '供电电压', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '功耗', 'type': 'string', 'required': False},
            {'name': '压差控制范围', 'type': 'string', 'required': False},
            {'name': '反馈信号', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '工作环境温度', 'type': 'string', 'required': False},
            {'name': '弹簧复位时间', 'type': 'string', 'required': False},
            {'name': '操作方式', 'type': 'string', 'required': False},
            {'name': '核心功能', 'type': 'string', 'required': False},
            {'name': '流量特性', 'type': 'string', 'required': False},
            {'name': '电气保护等级', 'type': 'string', 'required': False},
            {'name': '调节范围', 'type': 'string', 'required': False},
            {'name': '输入信号', 'type': 'string', 'required': False},
            {'name': '输入阻抗', 'type': 'string', 'required': False},
            {'name': '运行时间', 'type': 'string', 'required': False},
            {'name': '运行速度', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '适配阀门', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '阀门类型', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
            {'name': '额定推力', 'type': 'string', 'required': False},
            {'name': '额定行程', 'type': 'string', 'required': False},
        ]
    },
    '动态压差平衡调节型执行器': {
        'keywords': ['动态压差平衡调节型执行器', '调节型执行器', '动态压差执行器'],
        'params': [
            {'name': '供电电压', 'type': 'string', 'required': False},
            {'name': '功耗', 'type': 'string', 'required': False},
            {'name': '反馈信号', 'type': 'string', 'required': False},
            {'name': '工作环境温度', 'type': 'string', 'required': False},
            {'name': '核心功能', 'type': 'string', 'required': False},
            {'name': '电气保护等级', 'type': 'string', 'required': False},
            {'name': '输入信号', 'type': 'string', 'required': False},
            {'name': '输入阻抗', 'type': 'string', 'required': False},
            {'name': '运行时间', 'type': 'string', 'required': False},
            {'name': '运行速度', 'type': 'string', 'required': False},
            {'name': '适配阀门', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
            {'name': '额定推力', 'type': 'string', 'required': False},
            {'name': '额定行程', 'type': 'string', 'required': False},
        ]
    }
}

# 4. 添加到配置中
for device_type, config in dynamic_balance_valve_config.items():
    print(f"添加设备类型: {device_type}")
    device_params['device_types'][device_type] = config
    print(f"  参数数量: {len(config['params'])}")
    print(f"  关键词: {config['keywords']}")

# 5. 保存到数据库
success = db_loader.update_config('device_params', device_params)

if success:
    print("\n✅ 动态压差平衡阀设备类型参数配置添加成功")
    print("配置详情:")
    for device_type, config in dynamic_balance_valve_config.items():
        print(f"  - {device_type}: {len(config['params'])} 个参数")
else:
    print("❌ 配置更新失败")