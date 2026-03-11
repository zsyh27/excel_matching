#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为智能照明设备生成匹配规则（修复版）"""

import sys
sys.path.insert(0, 'backend')
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel
from modules.device_feature_extractor import DeviceFeatureExtractor
from modules.rule_generator import RuleGenerator

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("🚀 开始为智能照明设备生成匹配规则（修复版）...")

try:
    # 1. 加载配置
    config = db_loader.load_config()
    
    # 2. 初始化组件
    feature_extractor = DeviceFeatureExtractor(config)
    rule_generator = RuleGenerator(config)
    
    # 3. 查询智能照明设备
    with db_manager.session_scope() as session:
        lighting_devices = session.query(Device).filter(
            Device.device_type == "智能照明设备"
        ).all()
        
        print(f"找到 {len(lighting_devices)} 个智能照明设备")
        
        if not lighting_devices:
            print("❌ 没有找到智能照明设备")
            sys.exit(1)
        
        # 4. 为每个设备生成规则
        success_count = 0
        error_count = 0
        
        for device in lighting_devices:
            try:
                print(f"\n处理设备: {device.device_id} - {device.device_name}")
                
                # 检查是否已有规则
                existing_rule = session.query(RuleModel).filter(
                    RuleModel.target_device_id == device.device_id
                ).first()
                
                if existing_rule:
                    print(f"  ⚠️ 规则已存在，删除旧规则")
                    session.delete(existing_rule)
                
                # 生成新规则
                rule_data = rule_generator.generate_rule(device)
                
                if rule_data:
                    # 转换为ORM模型
                    rule_orm = RuleModel(
                        rule_id=rule_data.rule_id,
                        target_device_id=rule_data.target_device_id,
                        auto_extracted_features=rule_data.auto_extracted_features,
                        feature_weights=rule_data.feature_weights,
                        match_threshold=rule_data.match_threshold,
                        remark=rule_data.remark
                    )
                    session.add(rule_orm)
                    
                    print(f"  ✅ 规则生成成功")
                    print(f"     规则ID: {rule_data.rule_id}")
                    print(f"     特征数量: {len(rule_data.auto_extracted_features)}")
                    print(f"     匹配阈值: {rule_data.match_threshold}")
                    
                    # 显示前几个特征（安全地访问）
                    if rule_data.auto_extracted_features:
                        features_preview = []
                        for i, feature in enumerate(rule_data.auto_extracted_features[:5]):
                            if isinstance(feature, dict) and 'feature' in feature:
                                features_preview.append(feature['feature'])
                            elif isinstance(feature, str):
                                features_preview.append(feature)
                            else:
                                features_preview.append(f"特征{i+1}")
                        print(f"     前5个特征: {features_preview}")
                    
                    success_count += 1
                else:
                    print(f"  ❌ 规则生成失败")
                    error_count += 1
                    
            except Exception as e:
                print(f"  ❌ 处理设备时出错: {e}")
                import traceback
                traceback.print_exc()
                error_count += 1
                continue
    
    print(f"\n📊 规则生成统计:")
    print(f"   成功生成: {success_count} 条规则")
    print(f"   生成失败: {error_count} 条规则")
    print(f"   总计处理: {success_count + error_count} 个设备")
    
    if success_count > 0:
        print(f"\n✅ 智能照明设备规则生成完成！")
        print(f"现在可以使用匹配功能测试这些设备")
    else:
        print(f"\n⚠️ 没有成功生成任何规则")

except Exception as e:
    print(f"❌ 规则生成过程中出错: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)