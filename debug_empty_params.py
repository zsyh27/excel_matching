#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""调试key_params为空的设备"""

import sys
sys.path.insert(0, 'backend')
from modules.database import DatabaseManager
from modules.models import Device

print("🔍 调试key_params为空的设备...")

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

with db_manager.session_scope() as session:
    # 查询key_params为空的设备（包括NULL和空JSON）
    empty_param_devices = session.query(Device).filter(
        Device.device_id.like('FIELD2_%')
    ).all()
    
    # 筛选出key_params为空的设备
    truly_empty = []
    for device in empty_param_devices:
        if not device.key_params or len(device.key_params) == 0:
            truly_empty.append(device)
    
    print(f"找到 {len(truly_empty)} 个key_params为空的设备")
    
    for i, device in enumerate(truly_empty[:5]):  # 只显示前5个
        print(f"\n设备 {i+1}:")
        print(f"  设备ID: {device.device_id}")
        print(f"  设备名称: {device.device_name}")
        print(f"  设备类型: {device.device_type}")
        print(f"  规格型号: {device.spec_model}")
        print(f"  详细参数: {device.detailed_params}")
        print(f"  key_params: {device.key_params}")
        
        # 分析详细参数
        if device.detailed_params:
            desc_str = str(device.detailed_params)
            print(f"  说明字段分析:")
            
            # 检查是否包含设备类型
            if '设备类型：' in desc_str:
                type_part = desc_str.split('设备类型：')[1].split('，')[0].strip()
                print(f"    提取的设备类型: {type_part}")
            else:
                print(f"    ⚠️ 没有找到'设备类型：'")
            
            # 检查参数分隔符
            if '，' in desc_str:
                params = desc_str.split('，')
                print(f"    用'，'分割得到 {len(params)} 个部分")
            elif ',' in desc_str:
                params = desc_str.split(',')
                print(f"    用','分割得到 {len(params)} 个部分")
            else:
                print(f"    ⚠️ 没有找到分隔符")
            
            # 检查参数格式
            param_count = 0
            if '，' in desc_str:
                params = desc_str.split('，')
            elif ',' in desc_str:
                params = desc_str.split(',')
            else:
                params = [desc_str]
            
            for param in params:
                param = param.strip()
                if '：' in param:
                    key, value = param.split('：', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and key != '设备类型' and value:
                        param_count += 1
                        print(f"    参数: {key} = {value}")
                elif ':' in param:
                    key, value = param.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and key != '设备类型' and value:
                        param_count += 1
                        print(f"    参数: {key} = {value}")
            
            print(f"    应该提取到 {param_count} 个参数")

print(f"\n🎉 调试完成！")