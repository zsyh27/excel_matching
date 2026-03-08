#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查组合设备的特征提取情况"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel
from modules.device_feature_extractor import DeviceFeatureExtractor
import json

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 加载配置
config = db_loader.load_config()

# 初始化特征提取器
feature_extractor = DeviceFeatureExtractor(config)

print("=" * 80)
print("检查组合设备的特征提取情况")
print("=" * 80)

device_types = [
    '蝶阀+开关型执行器',
    '蝶阀+调节型执行器'
]

with db_manager.session_scope() as session:
    for device_type in device_types:
        print(f"\n{'='*80}")
        print(f"设备类型: {device_type}")
        print(f"{'='*80}")
        
        # 获取一个示例设备
        device = session.query(Device).filter(
            Device.device_type == device_type
        ).first()
        
        if not device:
            print(f"⚠️ 没有找到该类型的设备")
            continue
        
        print(f"\n示例设备: {device.device_id}")
        print(f"设备名称: {device.device_name}")
        print(f"规格型号: {device.spec_model}")
        
        # 检查key_params
        if device.key_params:
            print(f"\nkey_params参数数量: {len(device.key_params)}")
            print("参数列表:")
            for param_name, param_value in device.key_params.items():
                if isinstance(param_value, dict):
                    value = param_value.get('value', '')
                else:
                    value = param_value
                print(f"  - {param_name}: {value}")
        else:
            print("\n⚠️ key_params为空")
        
        # 提取特征
        features = feature_extractor.extract_features(device)
        
        print(f"\n提取的特征数量: {len(features)}")
        print("特征详情:")
        
        # 按类型分组统计
        feature_by_type = {}
        for feature in features:
            if feature.type not in feature_by_type:
                feature_by_type[feature.type] = []
            feature_by_type[feature.type].append(feature)
        
        for feature_type, type_features in feature_by_type.items():
            print(f"\n  {feature_type} ({len(type_features)}个):")
            for f in type_features:
                print(f"    - {f.feature} (权重: {f.weight}, 来源: {f.source})")
        
        # 检查规则
        rule = session.query(RuleModel).filter(
            RuleModel.target_device_id == device.device_id
        ).first()
        
        if rule:
            print(f"\n规则ID: {rule.rule_id}")
            print(f"规则特征数量: {len(rule.auto_extracted_features)}")
            print(f"规则权重数量: {len(rule.feature_weights)}")
        else:
            print("\n⚠️ 该设备没有规则")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)
