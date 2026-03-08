#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""分析组合设备的特征提取情况"""

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
print("分析组合设备的特征提取情况")
print("=" * 80)

# 查询组合设备
device_types_to_check = [
    '蝶阀+开关型执行器',
    '蝶阀+调节型执行器'
]

with db_manager.session_scope() as session:
    for device_type in device_types_to_check:
        print(f"\n{'='*80}")
        print(f"设备类型: {device_type}")
        print(f"{'='*80}")
        
        # 查询该类型的第一个设备
        device = session.query(Device).filter(
            Device.device_type == device_type
        ).first()
        
        if not device:
            print(f"⚠️ 没有找到类型为 '{device_type}' 的设备")
            continue
        
        print(f"\n设备: {device.device_name} ({device.device_id})")
        print(f"  品牌: {device.brand}")
        print(f"  规格型号: {device.spec_model}")
        
        # 检查key_params
        if device.key_params:
            print(f"\n  key_params参数数量: {len(device.key_params)}")
            print(f"  key_params参数列表:")
            for param_name, param_value in device.key_params.items():
                if isinstance(param_value, dict):
                    value = param_value.get('value', '')
                else:
                    value = param_value
                print(f"    - {param_name}: {value}")
        else:
            print(f"\n  ⚠️ key_params为空")
        
        # 检查规则
        rule = session.query(RuleModel).filter(
            RuleModel.target_device_id == device.device_id
        ).first()
        
        if rule:
            print(f"\n  规则ID: {rule.rule_id}")
            
            # 检查auto_extracted_features
            if rule.auto_extracted_features:
                features = rule.auto_extracted_features
                print(f"\n  提取的特征数量: {len(features)}")
                print(f"  提取的特征列表:")
                for i, feature in enumerate(features, 1):
                    print(f"    {i}. {feature}")
            else:
                print(f"\n  ⚠️ auto_extracted_features为空")
            
            # 检查feature_weights
            if rule.feature_weights:
                weights = rule.feature_weights
                print(f"\n  特征权重数量: {len(weights)}")
                print(f"  特征权重详情:")
                
                # 按权重分组
                weight_groups = {}
                for feature, weight in weights.items():
                    if weight not in weight_groups:
                        weight_groups[weight] = []
                    weight_groups[weight].append(feature)
                
                # 按权重从高到低排序
                for weight in sorted(weight_groups.keys(), reverse=True):
                    features_list = weight_groups[weight]
                    print(f"\n    权重 {weight}:")
                    for feature in features_list:
                        print(f"      - {feature}")
            else:
                print(f"\n  ⚠️ feature_weights为空")
        else:
            print(f"\n  ⚠️ 没有找到规则")

# 分析期望的特征数量
print("\n" + "=" * 80)
print("期望特征数量分析")
print("=" * 80)

print("\n基础特征（所有设备都有）:")
print("  1. 品牌 (权重10)")
print("  2. 设备类型 (权重20)")
print("  3. 设备名称 (权重1)")
print("  4. 规格型号 (权重5)")

print("\n蝶阀+开关型执行器 应该有的特征:")
print("  基础特征: 4个")
print("  蝶阀参数: 7个 (公称通径、公称压力、连接方式、阀体材质、密封材质、适用介质、介质温度)")
print("  执行器参数: 8个 (额定扭矩、供电电压、控制类型、复位方式、断电状态、运行角度、防护等级、适配阀门)")
print("  总计: 4 + 7 + 8 = 19个特征")

print("\n蝶阀+调节型执行器 应该有的特征:")
print("  基础特征: 4个")
print("  蝶阀参数: 7个")
print("  执行器参数: 9个 (额定扭矩、供电电压、控制类型、控制信号、复位方式、断电状态、运行角度、防护等级、适配阀门)")
print("  总计: 4 + 7 + 9 = 20个特征")

print("\n" + "=" * 80)
print("分析完成")
print("=" * 80)
