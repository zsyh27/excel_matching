#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复组合设备的key_params
为蝶阀+执行器组合设备补充缺失的执行器参数
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device
import json
import re

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

print("=" * 80)
print("修复组合设备的key_params - 补充执行器参数")
print("=" * 80)

# 执行器型号到参数的映射（基于已有的执行器设备数据）
ACTUATOR_PARAMS = {
    # 开关型执行器参数模板
    'switch': {
        '额定扭矩': {'value': ''},
        '供电电压': {'value': 'AC230V 50/60Hz'},
        '控制类型': {'value': '开关型'},
        '复位方式': {'value': '非弹簧复位'},
        '断电状态': {'value': '断电保位'},
        '运行角度': {'value': '90°'},
        '防护等级': {'value': 'IP54'},
        '适配阀门': {'value': '蝶阀/风阀'}
    },
    # 调节型执行器参数模板
    'modulating': {
        '额定扭矩': {'value': ''},
        '供电电压': {'value': 'AC230V 50/60Hz'},
        '控制类型': {'value': '调节型'},
        '控制信号': {'value': '0-10V/4-20mA'},
        '复位方式': {'value': '非弹簧复位'},
        '断电状态': {'value': '断电保位'},
        '运行角度': {'value': '90°'},
        '防护等级': {'value': 'IP54'},
        '适配阀门': {'value': '蝶阀/风阀'}
    }
}

# 从型号中提取扭矩值
def extract_torque_from_model(model):
    """从型号中提取扭矩值"""
    # CN4620A1001 -> 20Nm
    # CN7220A2007 -> 20Nm
    # NOM16H0050 -> 50Nm
    # NOM16H0050P -> 50Nm
    
    # 尝试从型号中提取数字
    match = re.search(r'(\d+)(?:A|H)', model)
    if match:
        torque_value = match.group(1)
        return f"{torque_value}Nm"
    
    return ''

def get_actuator_params(device_type, spec_model):
    """
    根据设备类型和型号获取执行器参数
    
    Args:
        device_type: 设备类型
        spec_model: 规格型号
        
    Returns:
        dict: 执行器参数字典
    """
    # 确定执行器类型
    if '开关型' in device_type:
        params = ACTUATOR_PARAMS['switch'].copy()
    elif '调节型' in device_type:
        params = ACTUATOR_PARAMS['modulating'].copy()
    else:
        return {}
    
    # 从型号中提取扭矩
    # 型号格式: V8BFW16-050+CN4620A1001+V8BF-CN
    parts = spec_model.split('+')
    if len(parts) >= 2:
        actuator_model = parts[1]  # CN4620A1001
        torque = extract_torque_from_model(actuator_model)
        if torque:
            params['额定扭矩']['value'] = torque
    
    return params

# 统计信息
stats = {
    'total': 0,
    'updated': 0,
    'skipped': 0,
    'failed': 0
}

print("\n开始处理组合设备...")
print("-" * 80)

with db_manager.session_scope() as session:
    # 查询所有组合设备
    combined_devices = session.query(Device).filter(
        Device.device_type.in_(['蝶阀+开关型执行器', '蝶阀+调节型执行器'])
    ).all()
    
    stats['total'] = len(combined_devices)
    print(f"找到 {stats['total']} 个组合设备")
    
    for device in combined_devices:
        try:
            # 检查当前key_params
            current_params = device.key_params or {}
            param_count_before = len(current_params)
            
            # 检查是否已经有执行器参数
            has_actuator_params = any(
                key in current_params 
                for key in ['额定扭矩', '供电电压', '控制类型', '复位方式']
            )
            
            if has_actuator_params:
                stats['skipped'] += 1
                continue
            
            # 获取执行器参数
            actuator_params = get_actuator_params(device.device_type, device.spec_model)
            
            if not actuator_params:
                stats['skipped'] += 1
                continue
            
            # 合并参数（蝶阀参数 + 执行器参数）
            updated_params = current_params.copy()
            updated_params.update(actuator_params)
            
            # 更新设备
            device.key_params = updated_params
            
            param_count_after = len(updated_params)
            stats['updated'] += 1
            
            if stats['updated'] % 100 == 0:
                print(f"  已更新 {stats['updated']} 个设备...")
            
        except Exception as e:
            stats['failed'] += 1
            print(f"  ✗ 更新设备 {device.device_id} 失败: {e}")
            continue
    
    # 提交更改
    print(f"\n提交更改到数据库...")

print("\n" + "-" * 80)
print("处理完成")
print("-" * 80)

print(f"\n统计信息:")
print(f"  总设备数: {stats['total']}")
print(f"  已更新: {stats['updated']}")
print(f"  跳过: {stats['skipped']}")
print(f"  失败: {stats['failed']}")

# 验证更新结果
print("\n" + "=" * 80)
print("验证更新结果")
print("=" * 80)

with db_manager.session_scope() as session:
    # 随机抽取几个设备验证
    sample_devices = session.query(Device).filter(
        Device.device_type.in_(['蝶阀+开关型执行器', '蝶阀+调节型执行器'])
    ).limit(3).all()
    
    for device in sample_devices:
        print(f"\n设备: {device.device_name} ({device.device_id})")
        print(f"  设备类型: {device.device_type}")
        print(f"  规格型号: {device.spec_model}")
        
        if device.key_params:
            print(f"  key_params参数数量: {len(device.key_params)}")
            print(f"  参数列表:")
            for param_name in device.key_params.keys():
                print(f"    - {param_name}")
        else:
            print(f"  ⚠️ key_params为空")

print("\n" + "=" * 80)
print("修复完成")
print("=" * 80)

print("\n下一步操作:")
print("1. 重新生成规则: python regenerate_all_butterfly_rules.py")
print("2. 验证特征提取: python analyze_combined_device_features.py")
print("3. 在前端查看设备详情，确认参数显示正确")
