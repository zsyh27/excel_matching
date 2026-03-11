#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复执行器参数配置 - 添加缺失的参数"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("=" * 80)
print("修复执行器参数配置")
print("=" * 80)

# 获取当前配置
device_params = db_loader.get_config_by_key('device_params')

if not device_params or 'device_types' not in device_params:
    print("❌ device_params 配置不存在")
    sys.exit(1)

# 更新蝶阀开关型执行器配置（添加"适配阀门"参数）
print("\n更新蝶阀开关型执行器配置:")
print("-" * 80)

if '蝶阀开关型执行器' in device_params['device_types']:
    old_params = device_params['device_types']['蝶阀开关型执行器']['params']
    print(f"当前参数数量: {len(old_params)}")
    
    # 新的完整参数列表（8个参数）
    new_params = [
        {'name': '额定扭矩', 'type': 'string', 'required': False},
        {'name': '供电电压', 'type': 'string', 'required': False},
        {'name': '控制类型', 'type': 'string', 'required': False},
        {'name': '复位方式', 'type': 'string', 'required': False},
        {'name': '断电状态', 'type': 'string', 'required': False},
        {'name': '运行角度', 'type': 'string', 'required': False},
        {'name': '防护等级', 'type': 'string', 'required': False},
        {'name': '适配阀门', 'type': 'string', 'required': False}  # 新增
    ]
    
    device_params['device_types']['蝶阀开关型执行器']['params'] = new_params
    print(f"更新后参数数量: {len(new_params)}")
    print("参数列表:")
    for idx, param in enumerate(new_params, 1):
        print(f"  {idx}. {param['name']}")

# 更新蝶阀调节型执行器配置（添加"适配阀门"参数）
print("\n更新蝶阀调节型执行器配置:")
print("-" * 80)

if '蝶阀调节型执行器' in device_params['device_types']:
    old_params = device_params['device_types']['蝶阀调节型执行器']['params']
    print(f"当前参数数量: {len(old_params)}")
    
    # 新的完整参数列表（9个参数）
    new_params = [
        {'name': '额定扭矩', 'type': 'string', 'required': False},
        {'name': '供电电压', 'type': 'string', 'required': False},
        {'name': '控制类型', 'type': 'string', 'required': False},
        {'name': '控制信号', 'type': 'string', 'required': False},
        {'name': '复位方式', 'type': 'string', 'required': False},
        {'name': '断电状态', 'type': 'string', 'required': False},
        {'name': '运行角度', 'type': 'string', 'required': False},
        {'name': '防护等级', 'type': 'string', 'required': False},
        {'name': '适配阀门', 'type': 'string', 'required': False}  # 新增
    ]
    
    device_params['device_types']['蝶阀调节型执行器']['params'] = new_params
    print(f"更新后参数数量: {len(new_params)}")
    print("参数列表:")
    for idx, param in enumerate(new_params, 1):
        print(f"  {idx}. {param['name']}")

# 同时更新组合设备的配置
print("\n更新组合设备配置:")
print("-" * 80)

# 蝶阀+蝶阀开关型执行器（7个蝶阀参数 + 8个执行器参数 = 15个）
if '蝶阀+蝶阀开关型执行器' in device_params['device_types']:
    combined_params = [
        # 蝶阀参数（7个）
        {'name': '公称通径', 'type': 'string', 'required': True},
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
        {'name': '适配阀门', 'type': 'string', 'required': False}  # 新增
    ]
    
    device_params['device_types']['蝶阀+蝶阀开关型执行器']['params'] = combined_params
    print(f"蝶阀+蝶阀开关型执行器: {len(combined_params)} 个参数")

# 蝶阀+蝶阀调节型执行器（7个蝶阀参数 + 9个执行器参数 = 16个）
if '蝶阀+蝶阀调节型执行器' in device_params['device_types']:
    combined_params = [
        # 蝶阀参数（7个）
        {'name': '公称通径', 'type': 'string', 'required': True},
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
        {'name': '适配阀门', 'type': 'string', 'required': False}  # 新增
    ]
    
    device_params['device_types']['蝶阀+蝶阀调节型执行器']['params'] = combined_params
    print(f"蝶阀+蝶阀调节型执行器: {len(combined_params)} 个参数")

# 保存配置
print("\n保存配置到数据库...")
success = db_loader.update_config('device_params', device_params)

if success:
    print("✅ 配置更新成功")
    
    # 验证更新
    print("\n验证更新结果:")
    print("-" * 80)
    updated_config = db_loader.get_config_by_key('device_params')
    
    for device_type in ['蝶阀开关型执行器', '蝶阀调节型执行器', 
                        '蝶阀+蝶阀开关型执行器', '蝶阀+蝶阀调节型执行器']:
        if device_type in updated_config['device_types']:
            param_count = len(updated_config['device_types'][device_type]['params'])
            print(f"  {device_type}: {param_count} 个参数")
else:
    print("❌ 配置更新失败")
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ 修复完成！")
print("=" * 80)
print("\n提示：")
print("1. 刷新前端配置管理页面，查看更新后的参数配置")
print("2. 已导入的设备数据不需要重新导入（数据已经是完整的）")
print("3. 规则也不需要重新生成（规则是基于实际的 key_params 生成的）")
