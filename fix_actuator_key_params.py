#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复执行器设备的 key_params"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device
import re
import json

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

print("=" * 80)
print("修复执行器设备的 key_params")
print("=" * 80)

# 参数提取函数
def extract_params_from_detailed(detailed_params, device_type):
    """从 detailed_params 中提取参数"""
    if not detailed_params:
        return {}
    
    params = {}
    
    # 定义参数模式
    if device_type in ['开关型执行器', '调节型执行器']:
        # 执行器参数
        patterns = {
            '额定扭矩': r'额定扭矩[：:]\s*([^，,。\n]+)',
            '供电电压': r'供电电压[：:]\s*([^，,。\n]+)',
            '控制类型': r'控制类型[：:]\s*([^，,。\n]+)',
            '控制信号': r'控制信号[：:]\s*([^，,。\n]+)',
            '复位方式': r'复位方式[：:]\s*([^，,。\n]+)',
            '断电状态': r'断电状态[：:]\s*([^，,。\n]+)',
            '运行角度': r'运行角度[：:]\s*([^，,。\n]+)',
            '防护等级': r'防护等级[：:]\s*([^，,。\n]+)',
            '适配阀门': r'适配阀门[：:]\s*([^，,。\n]+)',
        }
    elif device_type in ['蝶阀+开关型执行器', '蝶阀+调节型执行器']:
        # 组合设备参数（蝶阀 + 执行器）
        patterns = {
            '公称通径': r'公称通径[：:]\s*([^，,。\n]+)',
            '公称压力': r'公称压力[：:]\s*([^，,。\n]+)',
            '连接方式': r'连接方式[：:]\s*([^，,。\n]+)',
            '阀体材质': r'阀体材质[：:]\s*([^，,。\n]+)',
            '密封材质': r'密封材质[：:]\s*([^，,。\n]+)',
            '适用介质': r'适用介质[：:]\s*([^，,。\n]+)',
            '介质温度': r'介质温度[：:]\s*([^，,。\n]+)',
            '额定扭矩': r'额定扭矩[：:]\s*([^，,。\n]+)',
            '供电电压': r'供电电压[：:]\s*([^，,。\n]+)',
            '控制类型': r'控制类型[：:]\s*([^，,。\n]+)',
            '控制信号': r'控制信号[：:]\s*([^，,。\n]+)',
            '复位方式': r'复位方式[：:]\s*([^，,。\n]+)',
            '断电状态': r'断电状态[：:]\s*([^，,。\n]+)',
            '运行角度': r'运行角度[：:]\s*([^，,。\n]+)',
            '防护等级': r'防护等级[：:]\s*([^，,。\n]+)',
        }
    else:
        return {}
    
    # 提取参数
    for param_name, pattern in patterns.items():
        match = re.search(pattern, detailed_params)
        if match:
            value = match.group(1).strip()
            # 移除末尾的逗号、句号等
            value = re.sub(r'[，,。]+$', '', value)
            params[param_name] = {"value": value}
    
    return params

# 查询需要修复的设备
device_types = [
    '开关型执行器',
    '调节型执行器',
    '蝶阀+开关型执行器',
    '蝶阀+调节型执行器'
]

with db_manager.session_scope() as session:
    for device_type in device_types:
        print(f"\n{'=' * 80}")
        print(f"处理设备类型: {device_type}")
        print("=" * 80)
        
        # 查询该类型的所有设备
        devices = session.query(Device).filter(
            Device.device_type == device_type
        ).all()
        
        print(f"找到 {len(devices)} 个设备")
        
        updated_count = 0
        for device in devices:
            # 检查是否需要更新
            if device.key_params:
                # 已有 key_params，跳过
                continue
            
            if not device.detailed_params:
                # 没有 detailed_params，无法提取
                continue
            
            # 从 detailed_params 提取参数
            params = extract_params_from_detailed(device.detailed_params, device_type)
            
            if params:
                device.key_params = params
                updated_count += 1
                
                if updated_count <= 3:  # 只打印前3个示例
                    print(f"\n设备 {device.device_id}:")
                    print(f"  提取了 {len(params)} 个参数")
                    for param_name, param_data in params.items():
                        print(f"    - {param_name}: {param_data['value']}")
        
        session.commit()
        
        print(f"\n✅ 更新了 {updated_count} 个设备的 key_params")

print("\n" + "=" * 80)
print("修复完成")
print("=" * 80)
print("\n下一步：重新生成规则")
print("python regenerate_all_butterfly_rules.py")
