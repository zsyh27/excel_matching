#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查执行器和阀门设备的特征显示问题"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel
import json

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("=" * 80)
print("检查执行器和阀门设备的特征显示问题")
print("=" * 80)

# 查询这些设备类型的设备
device_types_to_check = [
    '开关型执行器',
    '调节型执行器',
    '蝶阀+开关型执行器',
    '蝶阀+调节型执行器'
]

with db_manager.session_scope() as session:
    for device_type in device_types_to_check:
        print(f"\n{'='*80}")
        print(f"设备类型: {device_type}")
        print(f"{'='*80}")
        
        # 查询该类型的设备
        devices = session.query(Device).filter(
            Device.device_type == device_type
        ).limit(2).all()
        
        if not devices:
            print(f"⚠️ 没有找到类型为 '{device_type}' 的设备")
            continue
        
        print(f"找到 {len(devices)} 个设备（显示前2个）")
        
        for device in devices:
            print(f"\n设备: {device.device_name} ({device.device_id})")
            print(f"  品牌: {device.brand}")
            print(f"  规格型号: {device.spec_model}")
            
            # 检查key_params
            if device.key_params:
                print(f"  key_params: {json.dumps(device.key_params, ensure_ascii=False, indent=4)}")
            else:
                print(f"  ⚠️ key_params为空")
            
            # 检查规则
            rule = session.query(RuleModel).filter(
                RuleModel.target_device_id == device.device_id
            ).first()
            
            if rule:
                print(f"\n  规则ID: {rule.rule_id}")
                
                # 检查auto_extracted_features
                if rule.auto_extracted_features:
                    features = rule.auto_extracted_features
                    print(f"  提取的特征数量: {len(features)}")
                    print(f"  特征列表: {features}")
                else:
                    print(f"  ⚠️ auto_extracted_features为空")
                
                # 检查feature_weights
                if rule.feature_weights:
                    weights = rule.feature_weights
                    print(f"  特征权重数量: {len(weights)}")
                    print(f"  特征权重: {json.dumps(weights, ensure_ascii=False, indent=4)}")
                else:
                    print(f"  ⚠️ feature_weights为空")
            else:
                print(f"  ⚠️ 没有找到规则")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)
