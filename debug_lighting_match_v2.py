#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""调试智能照明设备匹配问题 v2"""

import sys
sys.path.insert(0, 'backend')
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("🔍 调试智能照明设备匹配问题 v2...")

try:
    # 1. 检查智能照明设备数量
    with db_manager.session_scope() as session:
        lighting_devices = session.query(Device).filter(
            Device.device_type == "智能照明设备"
        ).all()
        
        print(f"数据库中智能照明设备数量: {len(lighting_devices)}")
        
        if lighting_devices:
            sample_device = lighting_devices[0]
            print(f"示例设备: {sample_device.device_name}")
            print(f"设备ID: {sample_device.device_id}")
            print(f"规格型号: {sample_device.spec_model}")
            print(f"设备类型: {sample_device.device_type}")
            
            # 检查规则
            rule = session.query(RuleModel).filter(
                RuleModel.target_device_id == sample_device.device_id
            ).first()
            
            if rule:
                print(f"规则存在: ✅")
                print(f"规则ID: {rule.rule_id}")
                print(f"特征数量: {len(rule.auto_extracted_features) if rule.auto_extracted_features else 0}")
                print(f"匹配阈值: {rule.match_threshold}")
                
                # 显示前几个特征
                if rule.auto_extracted_features:
                    print(f"前5个特征:")
                    for i, feature in enumerate(rule.auto_extracted_features[:5]):
                        if isinstance(feature, dict):
                            print(f"  {i+1}. {feature.get('feature', 'N/A')} (权重: {feature.get('weight', 0)})")
                        else:
                            print(f"  {i+1}. {feature}")
            else:
                print(f"规则存在: ❌")
        else:
            print("❌ 没有找到智能照明设备")
            sys.exit(1)
    
    # 2. 检查所有设备数量
    with db_manager.session_scope() as session:
        all_devices = session.query(Device).all()
        print(f"\n数据库中总设备数量: {len(all_devices)}")
        
        # 按设备类型统计
        device_types = {}
        for device in all_devices:
            device_type = device.device_type or "未知"
            device_types[device_type] = device_types.get(device_type, 0) + 1
        
        print(f"设备类型统计:")
        for device_type, count in sorted(device_types.items()):
            print(f"  {device_type}: {count} 个")
    
    # 3. 检查规则数量
    with db_manager.session_scope() as session:
        all_rules = session.query(RuleModel).all()
        print(f"\n数据库中总规则数量: {len(all_rules)}")
        
        # 检查智能照明设备的规则
        lighting_rules = session.query(RuleModel).join(Device).filter(
            Device.device_type == "智能照明设备"
        ).all()
        print(f"智能照明设备规则数量: {len(lighting_rules)}")

except Exception as e:
    print(f"❌ 调试过程中出错: {e}")
    import traceback
    traceback.print_exc()