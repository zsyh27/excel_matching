#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为现场设备生成匹配规则"""

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

print("🚀 开始生成现场设备匹配规则...")

try:
    # 1. 加载配置
    config = db_loader.load_config()
    
    # 2. 初始化组件
    feature_extractor = DeviceFeatureExtractor(config)
    rule_generator = RuleGenerator(config)
    
    # 3. 查询所有现场设备（通过device_id前缀识别）
    with db_manager.session_scope() as session:
        field_devices = session.query(Device).filter(
            Device.device_id.like('FIELD_%')
        ).all()
        
        print(f"找到 {len(field_devices)} 个现场设备")
        
        if not field_devices:
            print("❌ 没有找到现场设备")
            sys.exit(1)
        
        success_count = 0
        error_count = 0
        
        for device in field_devices:
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
                    
                    success_count += 1
                else:
                    print(f"  ❌ 规则生成失败")
                    error_count += 1
                    
            except Exception as e:
                print(f"  ❌ 处理失败: {str(e)}")
                error_count += 1
                import traceback
                traceback.print_exc()
    
    print(f"\n📊 规则生成统计:")
    print(f"   成功生成: {success_count} 条规则")
    print(f"   生成失败: {error_count} 条规则")
    print(f"   总计处理: {len(field_devices)} 个设备")
    
    if success_count > 0:
        print(f"\n✅ 规则生成完成！")
        print(f"现场设备数据导入和规则生成全部完成！")
    else:
        print(f"\n❌ 没有规则被生成")

except Exception as e:
    print(f"❌ 规则生成失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)