#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""调试蝶阀设备的特征提取问题"""

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

# 查询一个蝶阀设备
with db_manager.session_scope() as session:
    # 查询设备名称包含 "DN50 蝶阀 对夹式" 的设备
    device = session.query(Device).filter(
        Device.device_name.like('%DN50%蝶阀%对夹式%')
    ).first()
    
    if not device:
        print("❌ 未找到设备")
        sys.exit(1)
    
    print("=" * 80)
    print("设备信息")
    print("=" * 80)
    print(f"设备ID: {device.device_id}")
    print(f"品牌: {device.brand}")
    print(f"设备名称: {device.device_name}")
    print(f"规格型号: {device.spec_model}")
    print(f"设备类型: {device.device_type}")
    print(f"单价: {device.unit_price}")
    
    print("\n" + "=" * 80)
    print("关键参数 (key_params)")
    print("=" * 80)
    if device.key_params:
        if isinstance(device.key_params, str):
            key_params = json.loads(device.key_params)
        else:
            key_params = device.key_params
        
        print(f"类型: {type(key_params)}")
        print(f"内容: {json.dumps(key_params, ensure_ascii=False, indent=2)}")
        print(f"参数数量: {len(key_params)}")
        
        for param_name, param_data in key_params.items():
            print(f"  - {param_name}: {param_data}")
    else:
        print("❌ key_params 为空")
    
    print("\n" + "=" * 80)
    print("详细参数 (detailed_params)")
    print("=" * 80)
    if device.detailed_params:
        print(device.detailed_params)
    else:
        print("❌ detailed_params 为空")
    
    print("\n" + "=" * 80)
    print("特征提取")
    print("=" * 80)
    
    # 提取特征
    features = feature_extractor.extract_features(device)
    
    print(f"提取的特征数量: {len(features)}")
    print("\n特征列表:")
    for i, feature in enumerate(features, 1):
        print(f"{i}. 特征: {feature.feature}")
        print(f"   类型: {feature.type}")
        print(f"   权重: {feature.weight}")
        print(f"   来源: {feature.source}")
        print()
    
    # 查询该设备的规则
    print("=" * 80)
    print("规则信息")
    print("=" * 80)
    
    rule = session.query(Rule).filter(
        Rule.target_device_id == device.device_id
    ).first()
    
    if rule:
        print(f"规则ID: {rule.rule_id}")
        
        if rule.auto_extracted_features:
            if isinstance(rule.auto_extracted_features, str):
                auto_features = json.loads(rule.auto_extracted_features)
            else:
                auto_features = rule.auto_extracted_features
            
            print(f"\n自动提取的特征数量: {len(auto_features)}")
            print("特征列表:")
            for i, feature in enumerate(auto_features, 1):
                print(f"  {i}. {feature}")
        
        if rule.feature_weights:
            if isinstance(rule.feature_weights, str):
                weights = json.loads(rule.feature_weights)
            else:
                weights = rule.feature_weights
            
            print(f"\n特征权重:")
            for feature, weight in weights.items():
                print(f"  {feature}: {weight}")
    else:
        print("❌ 未找到规则")
    
    print("\n" + "=" * 80)
    print("权重配置")
    print("=" * 80)
    feature_weight_config = config.get('feature_weight_config', {})
    print(json.dumps(feature_weight_config, ensure_ascii=False, indent=2))
