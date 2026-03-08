#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查设备类型配置结构"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
import json

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("=" * 80)
print("检查设备类型配置结构")
print("=" * 80)

# 1. 获取device_params配置
device_params = db_loader.get_config_by_key('device_params')

if not device_params:
    print("❌ device_params配置不存在")
    sys.exit(1)

print("\n✅ device_params配置存在")
print(f"配置键: {list(device_params.keys())}")

# 2. 检查是否有device_types键
if 'device_types' in device_params:
    print("\n✅ 发现device_types键")
    device_types = device_params['device_types']
    print(f"设备类型数量: {len(device_types)}")
    print(f"设备类型列表: {list(device_types.keys())[:10]}...")  # 只显示前10个
    
    # 检查一个设备类型的结构
    first_type = list(device_types.keys())[0]
    print(f"\n示例设备类型: {first_type}")
    print(f"配置结构: {list(device_types[first_type].keys())}")
    
    if 'params' in device_types[first_type]:
        params = device_types[first_type]['params']
        print(f"参数数量: {len(params)}")
        if params:
            print(f"第一个参数: {params[0]}")
else:
    print("\n⚠️ 没有device_types键，直接是设备类型字典")
    print(f"设备类型数量: {len(device_params)}")
    print(f"设备类型列表: {list(device_params.keys())[:10]}...")  # 只显示前10个
    
    # 检查一个设备类型的结构
    first_type = list(device_params.keys())[0]
    print(f"\n示例设备类型: {first_type}")
    print(f"配置结构: {list(device_params[first_type].keys())}")
    
    if 'params' in device_params[first_type]:
        params = device_params[first_type]['params']
        print(f"参数数量: {len(params)}")
        if params:
            print(f"第一个参数: {params[0]}")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)
