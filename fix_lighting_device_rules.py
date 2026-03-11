#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复智能照明设备规则格式"""

import sys
sys.path.insert(0, 'backend')
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("🔧 修复智能照明设备规则格式...")

try:
    with db_manager.session_scope() as session:
        # 查询所有智能照明设备的规则
        lighting_rules = session.query(RuleModel).join(Device).filter(
            Device.device_type == "智能照明设备"
        ).all()
        
        print(f"找到 {len(lighting_rules)} 个智能照明设备规则")
        
        fixed_count = 0
        
        for rule in lighting_rules:
            try:
                # 检查规则格式
                if (rule.auto_extracted_features and 
                    rule.feature_weights and 
                    isinstance(rule.auto_extracted_features, list) and
                    isinstance(rule.feature_weights, dict)):
                    
                    # 转换特征格式
                    new_features = []
                    
                    for feature_text in rule.auto_extracted_features:
                        if isinstance(feature_text, str):
                            weight = rule.feature_weights.get(feature_text, 1.0)
                            
                            # 创建新的特征字典格式
                            new_feature = {
                                'feature': feature_text,
                                'weight': weight,
                                'type': 'unknown'  # 可以根据需要设置类型
                            }
                            new_features.append(new_feature)
                        elif isinstance(feature_text, dict):
                            # 如果已经是字典格式，保持不变
                            new_features.append(feature_text)
                    
                    # 更新规则
                    rule.auto_extracted_features = new_features
                    
                    print(f"✅ 修复规则: {rule.rule_id}")
                    print(f"   特征数量: {len(new_features)}")
                    
                    # 计算总权重
                    total_weight = sum(f['weight'] for f in new_features)
                    print(f"   总权重: {total_weight}")
                    
                    # 调整匹配阈值为合理值（总权重的30%）
                    new_threshold = total_weight * 0.3
                    rule.match_threshold = new_threshold
                    print(f"   新阈值: {new_threshold:.2f}")
                    
                    fixed_count += 1
                    
            except Exception as e:
                print(f"❌ 修复规则 {rule.rule_id} 时出错: {e}")
                continue
        
        print(f"\n📊 修复统计:")
        print(f"   成功修复: {fixed_count} 个规则")
        print(f"   总规则数: {len(lighting_rules)}")
        
        if fixed_count > 0:
            print(f"\n✅ 智能照明设备规则格式修复完成！")
        else:
            print(f"\n⚠️ 没有修复任何规则")

except Exception as e:
    print(f"❌ 修复过程中出错: {e}")
    import traceback
    traceback.print_exc()