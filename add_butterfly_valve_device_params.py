#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
步骤1：添加蝶阀设备类型参数配置

根据步骤0的Excel分析结果，添加5种设备类型的参数配置：
1. 蝶阀 - 7个参数
2. 蝶阀开关型执行器 - 8个参数
3. 蝶阀调节型执行器 - 9个参数
4. 蝶阀+蝶阀开关型执行器 - 15个参数
5. 蝶阀+蝶阀调节型执行器 - 16个参数
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

print('=' * 80)
print('步骤1：添加蝶阀设备类型参数配置')
print('=' * 80)

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 获取当前配置
device_params = db_loader.get_config_by_key('device_params')

if not device_params or 'device_types' not in device_params:
    print("❌ device_params 配置不存在")
    sys.exit(1)

print(f'当前设备类型数量: {len(device_params["device_types"])}\n')

# 定义新设备类型配置（基于步骤0的分析结果）
new_device_types = {
    # 蝶阀 配置 - 7个参数
    '蝶阀': {
        'keywords': ['蝶阀', 'butterfly valve', '对夹式蝶阀'],
        'params': [
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '介质温度', 'type': 'string', 'required': False},
        ]
    },
    
    # 蝶阀开关型执行器 配置 - 8个参数
    '蝶阀开关型执行器': {
        'keywords': ['蝶阀开关型执行器', '开关型执行器', '蝶阀执行器'],
        'params': [
            {'name': '额定扭矩', 'type': 'string', 'required': False},
            {'name': '供电电压', 'type': 'string', 'required': False},
            {'name': '控制类型', 'type': 'string', 'required': False},
            {'name': '复位方式', 'type': 'string', 'required': False},
            {'name': '断电状态', 'type': 'string', 'required': False},
            {'name': '运行角度', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
            {'name': '适配阀门', 'type': 'string', 'required': False},
        ]
    },
    
    # 蝶阀调节型执行器 配置 - 9个参数
    '蝶阀调节型执行器': {
        'keywords': ['蝶阀调节型执行器', '调节型执行器', '蝶阀执行器'],
        'params': [
            {'name': '额定扭矩', 'type': 'string', 'required': False},
            {'name': '供电电压', 'type': 'string', 'required': False},
            {'name': '控制类型', 'type': 'string', 'required': False},
            {'name': '控制信号', 'type': 'string', 'required': False},
            {'name': '复位方式', 'type': 'string', 'required': False},
            {'name': '断电状态', 'type': 'string', 'required': False},
            {'name': '运行角度', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
            {'name': '适配阀门', 'type': 'string', 'required': False},
        ]
    },
    
    # 蝶阀+蝶阀开关型执行器 配置 - 15个参数（7+8）
    '蝶阀+蝶阀开关型执行器': {
        'keywords': ['蝶阀+蝶阀开关型执行器', '蝶阀开关型', '蝶阀+开关型'],
        'params': [
            # 蝶阀参数（7个）
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '介质温度', 'type': 'string', 'required': False},
            # 执行器参数（8个）
            {'name': '额定扭矩', 'type': 'string', 'required': False},
            {'name': '供电电压', 'type': 'string', 'required': False},
            {'name': '控制类型', 'type': 'string', 'required': False},
            {'name': '复位方式', 'type': 'string', 'required': False},
            {'name': '断电状态', 'type': 'string', 'required': False},
            {'name': '运行角度', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
            {'name': '适配阀门', 'type': 'string', 'required': False},
        ]
    },
    
    # 蝶阀+蝶阀调节型执行器 配置 - 16个参数（7+9）
    '蝶阀+蝶阀调节型执行器': {
        'keywords': ['蝶阀+蝶阀调节型执行器', '蝶阀调节型', '蝶阀+调节型'],
        'params': [
            # 蝶阀参数（7个）
            {'name': '公称通径', 'type': 'string', 'required': False},
            {'name': '公称压力', 'type': 'string', 'required': False},
            {'name': '连接方式', 'type': 'string', 'required': False},
            {'name': '阀体材质', 'type': 'string', 'required': False},
            {'name': '密封材质', 'type': 'string', 'required': False},
            {'name': '适用介质', 'type': 'string', 'required': False},
            {'name': '介质温度', 'type': 'string', 'required': False},
            # 执行器参数（9个）
            {'name': '额定扭矩', 'type': 'string', 'required': False},
            {'name': '供电电压', 'type': 'string', 'required': False},
            {'name': '控制类型', 'type': 'string', 'required': False},
            {'name': '控制信号', 'type': 'string', 'required': False},
            {'name': '复位方式', 'type': 'string', 'required': False},
            {'name': '断电状态', 'type': 'string', 'required': False},
            {'name': '运行角度', 'type': 'string', 'required': False},
            {'name': '防护等级', 'type': 'string', 'required': False},
            {'name': '适配阀门', 'type': 'string', 'required': False},
        ]
    }
}

# 添加到配置中
print('添加设备类型配置：\n')
for device_type, config in new_device_types.items():
    if device_type in device_params['device_types']:
        print(f'⚠️  {device_type} - 已存在，跳过')
    else:
        device_params['device_types'][device_type] = config
        print(f'✅ {device_type} - 参数数量: {len(config["params"])}')

# 保存到数据库
print('\n保存配置到数据库...')
success = db_loader.update_config('device_params', device_params)

if success:
    print('✅ 配置更新成功')
    print(f'\n更新后设备类型数量: {len(device_params["device_types"])}')
    print('\n' + '=' * 80)
    print('步骤1完成！现在可以执行步骤2：导入设备数据')
    print('=' * 80)
else:
    print('❌ 配置更新失败')
    sys.exit(1)
