#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为区域阀静态平衡阀设备生成匹配规则 - 步骤3"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel
from modules.rule_generator import RuleGenerator

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("🚀 开始生成区域阀静态平衡阀设备匹配规则...")
print("=" * 80)

# 加载配置
print("\n步骤1：加载配置")
print("-" * 80)
config = db_loader.load_config()
print("✅ 配置加载成功")

# 初始化规则生成器
rule_generator = RuleGenerator(config)

# 获取所有区域阀和静态平衡阀设备
print("\n步骤2：获取区域阀和静态平衡阀设备")
print("-" * 80)

zone_valve_device_types = [
    '电动静态阀',
    '电动区域阀'
]

with db_manager.session_scope() as session:
    devices = session.query(Device).filter(
        Device.device_type.in_(zone_valve_device_types)
    ).all()
    
    print(f"找到 {len(devices)} 个区域阀和静态平衡阀设备")
    
    # 按设备类型统计
    device_type_counts = {}
    for device in devices:
        device_type_counts[device.device_type] = device_type_counts.get(device.device_type, 0) + 1
    
    print("\n设备类型统计:")
    for device_type, count in sorted(device_type_counts.items()):
        print(f"  - {device_type}: {count} 个")
    
    # 生成规则
    print("\n步骤3：生成匹配规则")
    print("-" * 80)
    
    success_count = 0
    error_count = 0
    update_count = 0
    
    for device in devices:
        try:
            # 检查是否已存在规则
            existing_rule = session.query(RuleModel).filter(
                RuleModel.target_device_id == device.device_id
            ).first()
            
            # 生成规则
            rule_data = rule_generator.generate_rule(device)
            
            if rule_data:
                if existing_rule:
                    # 更新现有规则
                    existing_rule.auto_extracted_features = rule_data.auto_extracted_features
                    existing_rule.feature_weights = rule_data.feature_weights
                    existing_rule.match_threshold = rule_data.match_threshold
                    existing_rule.remark = rule_data.remark
                    update_count += 1
                else:
                    # 创建新规则
                    rule_orm = RuleModel(
                        rule_id=rule_data.rule_id,
                        target_device_id=rule_data.target_device_id,
                        auto_extracted_features=rule_data.auto_extracted_features,
                        feature_weights=rule_data.feature_weights,
                        match_threshold=rule_data.match_threshold,
                        remark=rule_data.remark
                    )
                    session.add(rule_orm)
                    success_count += 1
            else:
                error_count += 1
                print(f"⚠️ 规则生成失败: {device.device_id} - {device.device_name}")
        
        except Exception as e:
            error_count += 1
            print(f"❌ 规则生成异常: {device.device_id} - {str(e)}")
    
    print(f"\n规则生成结果:")
    print(f"  新建: {success_count} 个")
    print(f"  更新: {update_count} 个")
    print(f"  失败: {error_count} 个")

if success_count > 0 or update_count > 0:
    print("\n" + "=" * 80)
    print("✅ 规则生成完成！")
    print("下一步：运行 verify_zone_valve_static_balance_import.py 验证导入结果")
    print("=" * 80)
else:
    print("\n❌ 没有规则生成成功")
    sys.exit(1)
