#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查所有执行器相关设备的特征提取"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule
from modules.device_feature_extractor import DeviceFeatureExtractor
import json

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 加载配置
config = db_loader.load_config()

# 初始化特征提取器
feature_extractor = DeviceFeatureExtractor(config)

# 要检查的设备类型
device_types = [
    '开关型执行器',
    '调节型执行器',
    '蝶阀+开关型执行器',
    '蝶阀+调节型执行器'
]

print("=" * 80)
print("检查执行器相关设备的特征提取")
print("=" * 80)

with db_manager.session_scope() as session:
    for device_type in device_types:
        print(f"\n{'=' * 80}")
        print(f"设备类型: {device_type}")
        print("=" * 80)
        
        # 查询该类型的第一个设备
        device = session.query(Device).filter(
            Device.device_type == device_type
        ).first()
        
        if not device:
            print(f"❌ 未找到 {device_type} 类型的设备")
            continue
        
        print(f"\n设备ID: {device.device_id}")
        print(f"设备名称: {device.device_name}")
        print(f"规格型号: {device.spec_model}")
        
        # 检查 key_params
        print(f"\n关键参数 (key_params):")
        if device.key_params:
            if isinstance(device.key_params, str):
                key_params = json.loads(device.key_params)
            else:
                key_params = device.key_params
            
            print(f"参数数量: {len(key_params)}")
            for param_name, param_data in key_params.items():
                value = param_data.get('value', '') if isinstance(param_data, dict) else param_data
                print(f"  - {param_name}: {value}")
        else:
            print("  ❌ key_params 为空")
        
        # 提取特征
        features = feature_extractor.extract_features(device)
        
        print(f"\n提取的特征:")
        print(f"特征数量: {len(features)}")
        for i, feature in enumerate(features, 1):
            print(f"  {i}. {feature.feature} (类型: {feature.type}, 权重: {feature.weight})")
        
        # 查询规则
        rule = session.query(Rule).filter(
            Rule.target_device_id == device.device_id
        ).first()
        
        if rule:
            if isinstance(rule.feature_weights, str):
                weights = json.loads(rule.feature_weights)
            else:
                weights = rule.feature_weights
            
            print(f"\n规则中的特征权重:")
            print(f"特征数量: {len(weights)}")
            for feature, weight in weights.items():
                print(f"  {feature}: {weight}")
        else:
            print("\n❌ 未找到规则")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)
