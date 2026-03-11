#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查规则权重问题"""

import sys
sys.path.insert(0, 'backend')
from modules.database import DatabaseManager
from modules.models import Device, Rule as RuleModel
import json

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

print("🔍 检查规则权重问题...")

try:
    with db_manager.session_scope() as session:
        # 查询一个智能照明设备的规则
        lighting_device = session.query(Device).filter(
            Device.device_type == "智能照明设备"
        ).first()
        
        if lighting_device:
            print(f"检查设备: {lighting_device.device_name}")
            print(f"设备ID: {lighting_device.device_id}")
            
            rule = session.query(RuleModel).filter(
                RuleModel.target_device_id == lighting_device.device_id
            ).first()
            
            if rule:
                print(f"规则ID: {rule.rule_id}")
                print(f"匹配阈值: {rule.match_threshold}")
                
                # 检查特征数据结构
                if rule.auto_extracted_features:
                    print(f"特征数量: {len(rule.auto_extracted_features)}")
                    
                    # 显示原始特征数据
                    print(f"\n原始特征数据:")
                    for i, feature in enumerate(rule.auto_extracted_features[:5]):
                        print(f"  特征 {i+1}: {feature}")
                        print(f"    类型: {type(feature)}")
                        
                        if isinstance(feature, dict):
                            print(f"    键: {list(feature.keys())}")
                            print(f"    权重: {feature.get('weight', '未设置')}")
                        elif isinstance(feature, str):
                            print(f"    值: {feature}")
                
                # 检查权重数据
                if rule.feature_weights:
                    print(f"\n权重数据:")
                    print(f"  类型: {type(rule.feature_weights)}")
                    print(f"  内容: {rule.feature_weights}")
                else:
                    print(f"\n❌ 没有权重数据")
            else:
                print(f"❌ 没有找到规则")
        else:
            print(f"❌ 没有找到智能照明设备")

except Exception as e:
    print(f"❌ 检查过程中出错: {e}")
    import traceback
    traceback.print_exc()