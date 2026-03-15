#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复空气质量传感器参数名称：将"co₂"改为"二氧化碳" """

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device, Rule as RuleModel
from modules.database_loader import DatabaseLoader
from modules.rule_generator import RuleGenerator
from datetime import datetime

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("=" * 80)
print("修复空气质量传感器参数名称")
print("=" * 80)

# 统计变量
total_devices = 0
updated_devices = 0
updated_params = 0
regenerated_rules = 0

with db_manager.session_scope() as session:
    # 查询所有空气质量传感器
    devices = session.query(Device).filter(
        Device.device_type == '空气质量传感器'
    ).all()
    
    total_devices = len(devices)
    print(f"\n找到 {total_devices} 个空气质量传感器设备")
    
    if total_devices == 0:
        print("没有找到空气质量传感器设备")
        sys.exit(0)
    
    # 遍历每个设备
    for device in devices:
        device_updated = False
        
        if device.key_params:
            # 检查是否包含"co₂"参数（支持多种变体）
            co2_variants = ['co₂', 'co2', 'CO₂', 'CO2', 'Co₂', 'Co2']
            found_variant = None
            
            for variant in co2_variants:
                if variant in device.key_params:
                    found_variant = variant
                    break
            
            if found_variant:
                print(f"\n处理设备: {device.device_id} - {device.device_name}")
                print(f"  找到参数: {found_variant}")
                
                # 获取参数值
                param_value = device.key_params[found_variant]
                
                # 删除旧参数名，添加新参数名
                del device.key_params[found_variant]
                device.key_params['二氧化碳'] = param_value
                
                # 标记为已修改
                device.updated_at = datetime.now()
                device_updated = True
                updated_params += 1
                
                print(f"  ✅ 已更新: {found_variant} → 二氧化碳")
                print(f"  参数值: {param_value}")
        
        if device_updated:
            updated_devices += 1

# 提交更改
print("\n" + "=" * 80)
print("数据库更新完成")
print("=" * 80)
print(f"总设备数: {total_devices}")
print(f"更新设备数: {updated_devices}")
print(f"更新参数数: {updated_params}")

# 重新生成规则
if updated_devices > 0:
    print("\n" + "=" * 80)
    print("重新生成规则")
    print("=" * 80)
    
    # 加载配置
    config = db_loader.load_config()
    rule_generator = RuleGenerator(config)
    
    with db_manager.session_scope() as session:
        # 查询所有空气质量传感器
        devices = session.query(Device).filter(
            Device.device_type == '空气质量传感器'
        ).all()
        
        for device in devices:
            # 检查是否有"二氧化碳"参数
            if device.key_params and '二氧化碳' in device.key_params:
                print(f"\n重新生成规则: {device.device_id}")
                
                # 生成规则
                rule_data = rule_generator.generate_rule(device)
                
                if rule_data:
                    # 查找现有规则
                    existing_rule = session.query(RuleModel).filter(
                        RuleModel.target_device_id == device.device_id
                    ).first()
                    
                    if existing_rule:
                        # 更新现有规则
                        existing_rule.auto_extracted_features = rule_data.auto_extracted_features
                        existing_rule.feature_weights = rule_data.feature_weights
                        existing_rule.match_threshold = rule_data.match_threshold
                        existing_rule.remark = rule_data.remark
                        print(f"  ✅ 规则已更新")
                    else:
                        # 创建新规则
                        new_rule = RuleModel(
                            rule_id=rule_data.rule_id,
                            target_device_id=rule_data.target_device_id,
                            auto_extracted_features=rule_data.auto_extracted_features,
                            feature_weights=rule_data.feature_weights,
                            match_threshold=rule_data.match_threshold,
                            remark=rule_data.remark
                        )
                        session.add(new_rule)
                        print(f"  ✅ 规则已创建")
                    
                    regenerated_rules += 1
                else:
                    print(f"  ⚠️  规则生成失败")

print("\n" + "=" * 80)
print("规则重新生成完成")
print("=" * 80)
print(f"重新生成规则数: {regenerated_rules}")

# 验证结果
print("\n" + "=" * 80)
print("验证结果")
print("=" * 80)

with db_manager.session_scope() as session:
    # 查询所有空气质量传感器
    devices = session.query(Device).filter(
        Device.device_type == '空气质量传感器'
    ).all()
    
    co2_count = 0
    eryang_count = 0
    
    for device in devices:
        if device.key_params:
            # 检查是否还有旧的参数名
            co2_variants = ['co₂', 'co2', 'CO₂', 'CO2', 'Co₂', 'Co2']
            has_old_name = any(variant in device.key_params for variant in co2_variants)
            
            if has_old_name:
                co2_count += 1
                print(f"⚠️  设备 {device.device_id} 仍包含旧参数名")
            
            # 检查是否有新的参数名
            if '二氧化碳' in device.key_params:
                eryang_count += 1
    
    print(f"\n包含旧参数名（co₂等）的设备: {co2_count}")
    print(f"包含新参数名（二氧化碳）的设备: {eryang_count}")
    
    if co2_count == 0 and eryang_count > 0:
        print("\n✅ 验证通过：所有参数名已成功更新")
    elif co2_count > 0:
        print("\n⚠️  验证警告：仍有设备包含旧参数名")
    else:
        print("\n⚠️  验证警告：没有找到包含二氧化碳参数的设备")

print("\n" + "=" * 80)
print("修复完成")
print("=" * 80)
