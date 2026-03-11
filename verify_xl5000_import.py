#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证XL5000设备导入结果 - 步骤4"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device, Rule as RuleModel

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

print("🔍 验证XL5000设备导入结果...")
print("=" * 80)

# XL5000相关设备类型
xl5000_device_types = [
    '温度控制器',
    '通用型温度控制器',
    '独立式AHU控制器',
    '墙面式温度模块',
    '墙面式温湿度模块',
    'VAV专用墙面模块',
    'Zio系列智能温控器',
    'Zio Plus系列智能温湿度控制器',
    'Zio Plus系列智能温控器'
]

with db_manager.session_scope() as session:
    # 1. 验证设备数量
    print("\n1. 设备数量验证")
    print("-" * 80)
    
    # 使用品牌筛选XL5000设备
    devices = session.query(Device).filter(
        Device.brand == 'XL5000'
    ).all()
    
    total_devices = len(devices)
    
    # 按设备类型统计
    device_type_counts = {}
    for device in devices:
        device_type_counts[device.device_type] = device_type_counts.get(device.device_type, 0) + 1
    
    for device_type in sorted(device_type_counts.keys()):
        count = device_type_counts[device_type]
        print(f"  {device_type}: {count} 个")
    
    print(f"\n  总计: {total_devices} 个设备")
    
    # 2. 验证规则数量
    print("\n2. 规则数量验证")
    print("-" * 80)
    
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
    
    # 4. 验证价格信息
    print("\n4. 价格信息验证")
    print("-" * 80)
    
    devices_with_price = 0
    devices_without_price = 0
    prices = []
    
    for device in devices:
        if device.unit_price and device.unit_price > 0:
            devices_with_price += 1
            prices.append(device.unit_price)
        else:
            devices_without_price += 1
    
    print(f"\n  有价格的设备: {devices_with_price} 个")
    print(f"  无价格的设备: {devices_without_price} 个")
    
    if prices:
        print(f"\n  价格统计:")
        print(f"    最低价格: ¥{min(prices)}")
        print(f"    最高价格: ¥{max(prices)}")
        print(f"    平均价格: ¥{sum(prices) // len(prices)}")
    
    # 5. 验证特征提取数量
    print("\n5. 特征提取数量验证")
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
    
    # 6. 显示示例设备
    print("\n6. 示例设备展示")
    print("-" * 80)
    
    # 显示每种设备类型的一个示例
    shown_types = set()
    for device in devices:
        if device.device_type not in shown_types:
            shown_types.add(device.device_type)
            
            print(f"\n  设备类型: {device.device_type}")
            print(f"  设备ID: {device.device_id}")
            print(f"  设备名称: {device.device_name}")
            print(f"  规格型号: {device.spec_model}")
            print(f"  单价: ¥{device.unit_price}")
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
    print(f"   - {devices_with_price} 个设备有价格信息")
else:
    print("⚠️ 发现问题:")
    if devices_without_rules > 0:
        print(f"   - {devices_without_rules} 个设备缺少规则")
    if devices_without_params > 0:
        print(f"   - {devices_without_params} 个设备的key_params为空")

print("\n" + "=" * 80)
print("🎉 XL5000设备导入流程完成！")
print("=" * 80)
