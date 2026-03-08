#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""重新生成组合设备的规则"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel
from modules.rule_generator import RuleGenerator
from datetime import datetime

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 加载配置
config = db_loader.load_config()

# 初始化规则生成器
rule_generator = RuleGenerator(config)

print("=" * 80)
print("重新生成组合设备的规则")
print("=" * 80)

device_types = [
    '蝶阀+开关型执行器',
    '蝶阀+调节型执行器'
]

success_count = 0
failed_count = 0

with db_manager.session_scope() as session:
    for device_type in device_types:
        print(f"\n{'='*80}")
        print(f"处理设备类型: {device_type}")
        print(f"{'='*80}")
        
        devices = session.query(Device).filter(
            Device.device_type == device_type
        ).all()
        
        print(f"找到 {len(devices)} 个设备")
        
        for i, device in enumerate(devices, 1):
            try:
                # 生成新规则
                rule_data = rule_generator.generate_rule(device)
                
                if not rule_data:
                    print(f"⚠️ [{i}/{len(devices)}] {device.device_id}: 规则生成失败")
                    failed_count += 1
                    continue
                
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
                
                success_count += 1
                
                if i % 50 == 0:
                    print(f"进度: {i}/{len(devices)}")
                
            except Exception as e:
                print(f"❌ [{i}/{len(devices)}] {device.device_id}: {e}")
                failed_count += 1

print("\n" + "=" * 80)
print("处理完成")
print("=" * 80)
print(f"成功: {success_count}")
print(f"失败: {failed_count}")
print(f"总计: {success_count + failed_count}")
