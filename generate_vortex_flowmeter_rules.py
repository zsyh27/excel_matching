#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为涡街流量计设备生成匹配规则"""

import sys
sys.path.insert(0, 'backend')
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel
from modules.device_feature_extractor import DeviceFeatureExtractor
from modules.rule_generator import RuleGenerator

# 初始化数据库和组件
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("🚀 开始为涡街流量计设备生成匹配规则...")

# 加载配置
config = db_loader.load_config()
feature_extractor = DeviceFeatureExtractor(config)
rule_generator = RuleGenerator(config)

generated_count = 0
updated_count = 0
error_count = 0

with db_manager.session_scope() as session:
    # 获取所有涡街流量计设备
    vortex_devices = session.query(Device).filter(
        Device.device_type == "涡街流量计"
    ).all()
    
    print(f"找到 {len(vortex_devices)} 个涡街流量计设备")
    
    for i, device in enumerate(vortex_devices, 1):
        try:
            # 检查是否已有规则
            existing_rule = session.query(RuleModel).filter(
                RuleModel.target_device_id == device.device_id
            ).first()
            
            # 生成规则数据
            rule_data = rule_generator.generate_rule(device)
            
            if rule_data:
                if existing_rule:
                    # 更新现有规则
                    existing_rule.auto_extracted_features = rule_data.auto_extracted_features
                    existing_rule.feature_weights = rule_data.feature_weights
                    existing_rule.match_threshold = rule_data.match_threshold
                    existing_rule.remark = rule_data.remark
                    updated_count += 1
                    action = "更新"
                else:
                    # 创建新规则
                    rule_orm = RuleModel(
                        rule_id=rule_data.rule_id,
                        target_device_id=rule_data.target_device_id,
                        auto_extracted_features=rule_data.auto_extracted_features,
                        feature_weights=rule_data.feature_weights,
                        match_threshold=rule_data.match_threshold,
                        remark=rule_data.remark
                    )
                    session.add(rule_orm)
                    generated_count += 1
                    action = "生成"
                
                # 显示进度和规则详情
                if i <= 3 or i % 20 == 0:  # 显示前3个和每20个的详情
                    features = rule_data.auto_extracted_features
                    print(f"\n{action}规则 {i}/{len(vortex_devices)}: {device.spec_model}")
                    print(f"   设备ID: {device.device_id}")
                    print(f"   特征数量: {len(features)}")
                    print(f"   匹配阈值: {rule_data.match_threshold}")
                    
                    # 显示特征详情（前5个）
                    print("   主要特征:")
                    for j, feature in enumerate(features[:5], 1):
                        print(f"     {j}. {feature['feature']} (类型: {feature['type']}, 权重: {feature['weight']})")
                    if len(features) > 5:
                        print(f"     ... 还有 {len(features) - 5} 个特征")
                elif i % 10 == 0:
                    print(f"已处理 {i}/{len(vortex_devices)} 个设备...")
                    
            else:
                print(f"❌ 规则生成失败: {device.spec_model}")
                error_count += 1
                
        except Exception as e:
            print(f"❌ 处理设备 {device.spec_model} 时出错: {str(e)}")
            error_count += 1

print(f"\n✅ 规则生成完成！")
print(f"   新生成规则: {generated_count} 条")
print(f"   更新规则: {updated_count} 条")
print(f"   错误数量: {error_count} 个")
print(f"   总计处理: {len(vortex_devices)} 个设备")

# 验证规则生成结果
with db_manager.session_scope() as session:
    # 统计涡街流量计规则
    vortex_rules = session.query(RuleModel).join(Device).filter(
        Device.device_type == "涡街流量计"
    ).all()
    
    print(f"\n📊 验证结果:")
    print(f"   涡街流量计规则总数: {len(vortex_rules)}")
    
    if vortex_rules:
        # 分析规则特征统计
        feature_counts = [len(rule.auto_extracted_features) for rule in vortex_rules]
        avg_features = sum(feature_counts) / len(feature_counts)
        min_features = min(feature_counts)
        max_features = max(feature_counts)
        
        print(f"   特征数量统计:")
        print(f"     平均特征数: {avg_features:.1f}")
        print(f"     最少特征数: {min_features}")
        print(f"     最多特征数: {max_features}")
        
        # 显示一个示例规则
        sample_rule = vortex_rules[0]
        sample_device = session.query(Device).filter(
            Device.device_id == sample_rule.target_device_id
        ).first()
        
        print(f"\n📋 示例规则详情:")
        print(f"   规则ID: {sample_rule.rule_id}")
        print(f"   目标设备: {sample_device.spec_model if sample_device else 'Unknown'}")
        print(f"   特征数量: {len(sample_rule.auto_extracted_features)}")
        print(f"   匹配阈值: {sample_rule.match_threshold}")
        
        # 按特征类型统计
        feature_types = {}
        for feature in sample_rule.auto_extracted_features:
            feature_type = feature.get('type', 'unknown')
            feature_types[feature_type] = feature_types.get(feature_type, 0) + 1
        
        print(f"   特征类型分布:")
        for feature_type, count in sorted(feature_types.items()):
            print(f"     {feature_type}: {count} 个")

print("\n🎉 涡街流量计规则生成完成！")