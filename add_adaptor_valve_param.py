#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为组合设备类型添加"适配阀门"参数"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
import json

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("=" * 80)
print("为组合设备类型添加'适配阀门'参数")
print("=" * 80)

# 获取device_params配置
device_params = db_loader.get_config_by_key('device_params')

if not device_params or 'device_types' not in device_params:
    print("❌ device_params配置不存在")
    sys.exit(1)

device_types = device_params['device_types']

# 定义"适配阀门"参数配置
adaptor_valve_param = {
    'name': '适配阀门',
    'type': 'string',
    'required': False,  # 不是必填项
    'options': ['蝶阀/风阀', '球阀', '座阀', '其他']
}

# 需要添加参数的设备类型
device_types_to_update = [
    '蝶阀+开关型执行器',
    '蝶阀+调节型执行器'
]

print("\n开始添加参数...")
print("-" * 80)

updated_count = 0

for device_type in device_types_to_update:
    if device_type not in device_types:
        print(f"\n⚠️ 设备类型 '{device_type}' 不存在，跳过")
        continue
    
    params = device_types[device_type].get('params', [])
    param_names = [p['name'] for p in params]
    
    print(f"\n{device_type}:")
    print(f"  当前参数数量: {len(params)}")
    
    # 检查是否已经有"适配阀门"参数
    if '适配阀门' in param_names:
        print(f"  ✅ 已存在'适配阀门'参数，无需添加")
        continue
    
    # 添加"适配阀门"参数到参数列表末尾
    params.append(adaptor_valve_param)
    device_types[device_type]['params'] = params
    
    print(f"  ✅ 已添加'适配阀门'参数")
    print(f"  更新后参数数量: {len(params)}")
    updated_count += 1

if updated_count > 0:
    # 保存更新后的配置
    print("\n" + "-" * 80)
    print("保存配置到数据库...")
    
    success = db_loader.update_config('device_params', device_params)
    
    if success:
        print("✅ 配置保存成功")
        
        # 验证更新
        print("\n" + "-" * 80)
        print("验证更新结果:")
        
        # 重新加载配置
        updated_device_params = db_loader.get_config_by_key('device_params')
        updated_device_types = updated_device_params['device_types']
        
        for device_type in device_types_to_update:
            if device_type in updated_device_types:
                params = updated_device_types[device_type].get('params', [])
                param_names = [p['name'] for p in params]
                
                print(f"\n{device_type}:")
                print(f"  参数数量: {len(params)}")
                print(f"  包含'适配阀门': {'✅' if '适配阀门' in param_names else '❌'}")
    else:
        print("❌ 配置保存失败")
else:
    print("\n⚠️ 没有需要更新的设备类型")

print("\n" + "=" * 80)
print("操作完成")
print("=" * 80)
