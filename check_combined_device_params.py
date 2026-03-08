#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查组合设备类型的参数配置"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
import json

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("=" * 80)
print("检查组合设备类型的参数配置")
print("=" * 80)

# 获取device_params配置
device_params = db_loader.get_config_by_key('device_params')

if not device_params or 'device_types' not in device_params:
    print("❌ device_params配置不存在")
    sys.exit(1)

device_types = device_params['device_types']

# 检查各个设备类型的参数数量
device_type_names = [
    '蝶阀',
    '开关型执行器',
    '调节型执行器',
    '蝶阀+开关型执行器',
    '蝶阀+调节型执行器'
]

print("\n设备类型参数统计:")
print("-" * 80)

for device_type in device_type_names:
    if device_type in device_types:
        params = device_types[device_type].get('params', [])
        param_names = [p['name'] for p in params]
        
        print(f"\n{device_type}:")
        print(f"  参数数量: {len(params)}")
        print(f"  参数列表: {param_names}")
        
        # 检查是否有"适配阀门"参数
        if '适配阀门' in param_names:
            print(f"  ✅ 包含'适配阀门'参数")
        else:
            print(f"  ❌ 缺少'适配阀门'参数")
    else:
        print(f"\n{device_type}: ⚠️ 配置不存在")

# 分析组合设备应该有的参数
print("\n" + "=" * 80)
print("参数数量分析:")
print("-" * 80)

butterfly_params = len(device_types.get('蝶阀', {}).get('params', []))
switch_actuator_params = len(device_types.get('开关型执行器', {}).get('params', []))
modulating_actuator_params = len(device_types.get('调节型执行器', {}).get('params', []))

print(f"\n蝶阀参数数量: {butterfly_params}")
print(f"开关型执行器参数数量: {switch_actuator_params}")
print(f"调节型执行器参数数量: {modulating_actuator_params}")

print(f"\n蝶阀+开关型执行器:")
print(f"  期望参数数量: {butterfly_params} + {switch_actuator_params} = {butterfly_params + switch_actuator_params}")
current_combined_switch = len(device_types.get('蝶阀+开关型执行器', {}).get('params', []))
print(f"  实际参数数量: {current_combined_switch}")
if current_combined_switch < butterfly_params + switch_actuator_params:
    print(f"  ❌ 缺少 {butterfly_params + switch_actuator_params - current_combined_switch} 个参数")

print(f"\n蝶阀+调节型执行器:")
print(f"  期望参数数量: {butterfly_params} + {modulating_actuator_params} = {butterfly_params + modulating_actuator_params}")
current_combined_modulating = len(device_types.get('蝶阀+调节型执行器', {}).get('params', []))
print(f"  实际参数数量: {current_combined_modulating}")
if current_combined_modulating < butterfly_params + modulating_actuator_params:
    print(f"  ❌ 缺少 {butterfly_params + modulating_actuator_params - current_combined_modulating} 个参数")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)
