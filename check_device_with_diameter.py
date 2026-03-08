#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查有公称通径的组合设备"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device
from modules.device_feature_extractor import DeviceFeatureExtractor

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 加载配置
config = db_loader.load_config()

# 初始化特征提取器
feature_extractor = DeviceFeatureExtractor(config)

print("=" * 80)
print("检查有公称通径的组合设备")
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
        
        # 获取一个有公称通径的设备
        device = session.query(Device).filter(
            Device.device_type == device_type
        ).all()
        
        # 找到第一个有公称通径的设备
        device_with_diameter = None
        for d in device:
            if d.key_params and '公称通径' in d.key_params:
                device_with_diameter = d
                break
        
        if not device_with_diameter:
            print(f"⚠️ 没有找到有公称通径的设备")
            continue
        
        print(f"\n示例设备: {device_with_diameter.device_id}")
        print(f"设备名称: {device_with_diameter.device_name}")
        print(f"规格型号: {device_with_diameter.spec_model}")
        
        # 检查key_params
        if device_with_diameter.key_params:
            print(f"\nkey_params参数数量: {len(device_with_diameter.key_params)}")
            print("参数列表:")
            for param_name, param_value in device_with_diameter.key_params.items():
                if isinstance(param_value, dict):
                    value = param_value.get('value', '')
                else:
                    value = param_value
                print(f"  - {param_name}: {value}")
        
        # 提取特征
        features = feature_extractor.extract_features(device_with_diameter)
        
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

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)
