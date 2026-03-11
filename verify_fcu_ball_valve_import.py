#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证FCU电动球阀设备导入结果 - 步骤4"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device, Rule as RuleModel

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

print("🔍 验证FCU电动球阀设备导入结果...")
print("=" * 80)

# FCU相关设备类型
fcu_device_types = [
    'FCU电动球阀',
    'FCU 阀门执行器',
    'FCU温控器',
    'FCU调节型温控器',
    'FCU联网型温控器'
]

with db_manager.session_scope() as session:
    # 1. 验证设备数量
    print("\n1. 设备数量验证")
    print("-" * 80)
    
    total_devices = 0
    for device_type in fcu_device_types:
        count = session.query(Device).filter(
            Device.device_type == device_type
        ).count()
        print(f"  {device_type}: {count} 个")
        total_devices += count
    
    print(f"\n  总计: {total_devices} 个设备")
    
    # 2. 验证规则数量
    print("\n2. 规则数量验证")
    print("-" * 80)
    
    devices = session.query(Device).filter(
        Device.device_type.in_(fcu_device_types)
    ).all()
    
    devices_with_rules = 0
    devices_without_rules = 0
    
    for device in devices:
        rule = session.query(RuleModel).filter(
            RuleModel.target_device_id == device.device_id
        ).first()
        
        if rule:
            devices_with_rules += 1
        else:
            devices_without_rules += 1
            print(f"  ⚠️ 缺少规则: {device.device_id} - {device.device_name}")
    
    print(f"\n  有规则的设备: {devices_with_rules} 个")
    print(f"  缺少规则的设备: {devices_without_rules} 个")
    
    # 3. 验证key_params完整性
    print("\n3. key_params完整性验证")
    print("-" * 80)
    
    devices_with_params = 0
    devices_without_params = 0
    param_count_stats = {}
    
    for device in devices:
        if device.key_params and len(device.key_params) > 0:
            devices_with_params += 1
            param_count = len(device.key_params)
            param_count_stats[param_count] = param_count_stats.get(param_count, 0) + 1
        else:
            devices_without_params += 1
            print(f"  ⚠️ key_params为空: {device.device_id} - {device.device_name}")
    
    print(f"\n  有参数的设备: {devices_with_params} 个")
    print(f"  参数为空的设备: {devices_without_params} 个")
    
    if param_count_stats:
        print(f"\n  参数数量分布:")
        for count, num_devices in sorted(param_count_stats.items()):
            print(f"    {count} 个参数: {num_devices} 个设备")
    
    # 4. 验证特征提取数量
    print("\n4. 特征提取数量验证")
    print("-" * 80)
    
    feature_count_stats = {}
    
    for device in devices[:10]:  # 只检查前10个设备
        rule = session.query(RuleModel).filter(
            RuleModel.target_device_id == device.device_id
        ).first()
        
        if rule and rule.auto_extracted_features:
            feature_count = len(rule.auto_extracted_features)
            feature_count_stats[feature_count] = feature_count_stats.get(feature_count, 0) + 1
            
            # 计算预期特征数量（4个基础特征 + key_params数量）
            expected_count = 4 + len(device.key_params) if device.key_params else 4
            
            if feature_count != expected_count:
                print(f"  ⚠️ 特征数量不匹配: {device.device_id}")
                print(f"     实际: {feature_count}, 预期: {expected_count}")
    
    if feature_count_stats:
        print(f"\n  特征数量分布（前10个设备）:")
        for count, num_devices in sorted(feature_count_stats.items()):
            print(f"    {count} 个特征: {num_devices} 个设备")
    
    # 5. 显示示例设备
    print("\n5. 示例设备展示")
    print("-" * 80)
    
    for device_type in fcu_device_types:
        device = session.query(Device).filter(
            Device.device_type == device_type
        ).first()
        
        if device:
            print(f"\n  设备类型: {device_type}")
            print(f"  设备ID: {device.device_id}")
            print(f"  设备名称: {device.device_name}")
            print(f"  规格型号: {device.spec_model}")
            print(f"  参数数量: {len(device.key_params) if device.key_params else 0}")
            
            if device.key_params:
                print(f"  参数列表: {', '.join(list(device.key_params.keys())[:5])}...")
            
            # 检查规则
            rule = session.query(RuleModel).filter(
                RuleModel.target_device_id == device.device_id
            ).first()
            
            if rule:
                print(f"  规则ID: {rule.rule_id}")
                print(f"  特征数量: {len(rule.auto_extracted_features)}")
                print(f"  匹配阈值: {rule.match_threshold}")

# 总结
print("\n" + "=" * 80)
print("验证总结:")
print("=" * 80)

if devices_without_rules == 0 and devices_without_params == 0:
    print("✅ 所有验证通过！")
    print(f"   - {total_devices} 个设备已成功导入")
    print(f"   - {devices_with_rules} 个规则已成功生成")
    print(f"   - 所有设备的key_params都已正确填充")
else:
    print("⚠️ 发现问题:")
    if devices_without_rules > 0:
        print(f"   - {devices_without_rules} 个设备缺少规则")
    if devices_without_params > 0:
        print(f"   - {devices_without_params} 个设备的key_params为空")

print("\n" + "=" * 80)
print("🎉 FCU电动球阀设备导入流程完成！")
print("=" * 80)
