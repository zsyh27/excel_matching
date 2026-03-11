#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查智能照明设备的得分情况"""

import sys
sys.path.insert(0, 'backend')
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("🔍 检查智能照明设备的得分情况...")

try:
    with db_manager.session_scope() as session:
        # 查询智能照明设备及其规则
        lighting_devices = session.query(Device).filter(
            Device.device_type == "智能照明设备"
        ).all()
        
        print(f"智能照明设备数量: {len(lighting_devices)}")
        
        if lighting_devices:
            # 检查前3个设备的规则
            for i, device in enumerate(lighting_devices[:3]):
                print(f"\n设备 {i+1}: {device.device_name}")
                print(f"  设备ID: {device.device_id}")
                print(f"  规格型号: {device.spec_model}")
                
                # 查询规则
                rule = session.query(RuleModel).filter(
                    RuleModel.target_device_id == device.device_id
                ).first()
                
                if rule and rule.auto_extracted_features:
                    print(f"  规则特征数量: {len(rule.auto_extracted_features)}")
                    print(f"  匹配阈值: {rule.match_threshold}")
                    
                    # 计算总权重
                    total_weight = 0
                    feature_details = []
                    
                    for feature in rule.auto_extracted_features:
                        if isinstance(feature, dict):
                            weight = feature.get('weight', 0)
                            total_weight += weight
                            feature_details.append({
                                'feature': feature.get('feature', 'N/A'),
                                'weight': weight,
                                'type': feature.get('type', 'unknown')
                            })
                    
                    print(f"  总权重: {total_weight}")
                    print(f"  权重分布:")
                    
                    # 按类型统计权重
                    weight_by_type = {}
                    for detail in feature_details:
                        feature_type = detail['type']
                        weight_by_type[feature_type] = weight_by_type.get(feature_type, 0) + detail['weight']
                    
                    for feature_type, weight in sorted(weight_by_type.items()):
                        print(f"    {feature_type}: {weight}")
                    
                    # 显示前5个特征
                    print(f"  前5个特征:")
                    for j, detail in enumerate(feature_details[:5]):
                        print(f"    {j+1}. {detail['feature']} (权重: {detail['weight']}, 类型: {detail['type']})")
                else:
                    print(f"  ❌ 没有规则或特征")
    
    # 检查匹配阈值配置
    config = db_loader.load_config()
    default_threshold = config.get('default_match_threshold', {}).get('value', 0.6)
    
    print(f"\n📊 阈值分析:")
    print(f"  系统默认阈值: {default_threshold} (百分比)")
    print(f"  规则中的阈值: 5.0 (绝对分数)")
    
    # 计算需要的最低得分
    if lighting_devices:
        sample_device = lighting_devices[0]
        rule = session.query(RuleModel).filter(
            RuleModel.target_device_id == sample_device.device_id
        ).first()
        
        if rule and rule.auto_extracted_features:
            total_weight = sum(f.get('weight', 0) for f in rule.auto_extracted_features if isinstance(f, dict))
            required_score = total_weight * default_threshold
            
            print(f"  示例设备总权重: {total_weight}")
            print(f"  需要的最低得分: {required_score:.2f}")
            print(f"  规则设置的阈值: {rule.match_threshold}")
            
            if rule.match_threshold > required_score:
                print(f"  ⚠️ 规则阈值过高！建议调整为: {required_score:.2f}")
            else:
                print(f"  ✅ 规则阈值合理")

except Exception as e:
    print(f"❌ 检查过程中出错: {e}")
    import traceback
    traceback.print_exc()