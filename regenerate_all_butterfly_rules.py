#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""重新生成所有蝶阀设备的规则"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule
from modules.rule_generator import RuleGenerator
from modules.models import Rule as RuleModel
from datetime import datetime

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 加载配置
config = db_loader.load_config()

# 初始化规则生成器
rule_generator = RuleGenerator(config)

print("=" * 80)
print("重新生成蝶阀设备规则")
print("=" * 80)

# 查询所有蝶阀相关设备
with db_manager.session_scope() as session:
    devices = session.query(Device).filter(
        Device.device_type.in_([
            '蝶阀',
            '蝶阀+开关型执行器',
            '蝶阀+调节型执行器',
            '开关型执行器',
            '调节型执行器'
        ])
    ).all()
    
    print(f"找到 {len(devices)} 个蝶阀相关设备")
    
    # 删除现有规则
    print("\n删除现有规则...")
    device_ids = [d.device_id for d in devices]
    deleted_count = session.query(Rule).filter(
        Rule.target_device_id.in_(device_ids)
    ).delete(synchronize_session=False)
    session.commit()
    print(f"删除了 {deleted_count} 条规则")
    
    # 重新生成规则
    print("\n重新生成规则...")
    success_count = 0
    error_count = 0
    
    for i, device in enumerate(devices, 1):
        try:
            # 生成规则
            rule_data = rule_generator.generate_rule(device)
            
            if rule_data:
                # 转换为ORM模型
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
                
                if i % 100 == 0:
                    print(f"  已处理 {i}/{len(devices)} 个设备...")
            else:
                print(f"  ❌ 设备 {device.device_id} 规则生成失败")
                error_count += 1
        
        except Exception as e:
            print(f"  ❌ 设备 {device.device_id} 处理出错: {e}")
            error_count += 1
    
    # 提交所有更改
    session.commit()
    
    print("\n" + "=" * 80)
    print("规则生成完成")
    print("=" * 80)
    print(f"总设备数: {len(devices)}")
    print(f"成功生成: {success_count}")
    print(f"失败: {error_count}")
    print(f"成功率: {success_count / len(devices) * 100:.1f}%")

print("\n" + "=" * 80)
print("验证规则")
print("=" * 80)

# 验证一个设备的规则
with db_manager.session_scope() as session:
    device = session.query(Device).filter(
        Device.device_name.like('%DN50%蝶阀%对夹式%')
    ).first()
    
    if device:
        rule = session.query(Rule).filter(
            Rule.target_device_id == device.device_id
        ).first()
        
        if rule:
            import json
            
            print(f"设备: {device.device_name}")
            print(f"规则ID: {rule.rule_id}")
            
            if isinstance(rule.feature_weights, str):
                weights = json.loads(rule.feature_weights)
            else:
                weights = rule.feature_weights
            
            print(f"\n特征权重:")
            for feature, weight in weights.items():
                print(f"  {feature}: {weight}")
