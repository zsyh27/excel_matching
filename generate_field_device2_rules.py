#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为现场设备2生成匹配规则"""

import sys
sys.path.insert(0, 'backend')
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel
from modules.device_feature_extractor import DeviceFeatureExtractor
from modules.rule_generator import RuleGenerator

print("🚀 开始为现场设备2生成匹配规则...")

# 初始化数据库和配置
try:
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    config = db_loader.load_config()
    print("✅ 数据库和配置加载成功")
except Exception as e:
    print(f"❌ 初始化失败: {str(e)}")
    sys.exit(1)

# 初始化特征提取器和规则生成器
try:
    feature_extractor = DeviceFeatureExtractor(config)
    rule_generator = RuleGenerator(config)
    print("✅ 特征提取器和规则生成器初始化成功")
except Exception as e:
    print(f"❌ 组件初始化失败: {str(e)}")
    sys.exit(1)

# 查询现场设备2的设备
with db_manager.session_scope() as session:
    # 查询所有以FIELD2_开头的设备ID（现场设备2的标识）
    devices = session.query(Device).filter(
        Device.device_id.like('FIELD2_%')
    ).all()
    
    print(f"📋 找到 {len(devices)} 个现场设备2")
    
    if not devices:
        print("❌ 没有找到现场设备2数据")
        sys.exit(1)
    
    # 按设备类型分组统计
    device_type_count = {}
    for device in devices:
        device_type = device.device_type
        device_type_count[device_type] = device_type_count.get(device_type, 0) + 1
    
    print(f"\n📊 设备类型分布:")
    for device_type, count in sorted(device_type_count.items()):
        print(f"   {device_type}: {count} 个")
    
    # 生成规则
    print(f"\n🔧 开始生成规则...")
    success_count = 0
    error_count = 0
    skip_count = 0
    
    for i, device in enumerate(devices):
        if (i + 1) % 50 == 0:
            print(f"生成进度: {i + 1}/{len(devices)}")
        
        try:
            # 检查是否已存在规则
            existing_rule = session.query(RuleModel).filter(
                RuleModel.target_device_id == device.device_id
            ).first()
            
            if existing_rule:
                skip_count += 1
                continue
            
            # 生成规则
            rule_data = rule_generator.generate_rule(device)
            
            if rule_data:
                # 转换为ORM模型并保存
                rule_orm = RuleModel(
                    rule_id=rule_data.rule_id,
                    target_device_id=rule_data.target_device_id,
                    auto_extracted_features=rule_data.auto_extracted_features,
                    feature_weights=rule_data.feature_weights,
                    match_threshold=rule_data.match_threshold,
                    remark=rule_data.remark
                )
                session.add(rule_orm)
                success_count += 1
            else:
                error_count += 1
                print(f"⚠️ 规则生成失败: {device.device_id} - {device.device_name}")
                
        except Exception as e:
            error_count += 1
            print(f"❌ 规则生成错误: {device.device_id} - {str(e)}")
    
    print(f"\n📊 规则生成统计:")
    print(f"   成功生成: {success_count} 个规则")
    print(f"   已存在跳过: {skip_count} 个规则")
    print(f"   生成失败: {error_count} 个规则")
    print(f"   总计处理: {len(devices)} 个设备")

# 验证规则生成结果
print(f"\n🔍 验证规则生成结果...")
with db_manager.session_scope() as session:
    # 统计规则数量
    total_rules = session.query(RuleModel).filter(
        RuleModel.target_device_id.like('FIELD2_%')
    ).count()
    
    print(f"现场设备2规则总数: {total_rules}")
    
    # 检查几个示例规则
    sample_rules = session.query(RuleModel).filter(
        RuleModel.target_device_id.like('FIELD2_%')
    ).limit(3).all()
    
    print(f"\n📋 规则示例:")
    for rule in sample_rules:
        device = session.query(Device).filter(
            Device.device_id == rule.target_device_id
        ).first()
        
        if device:
            feature_count = len(rule.auto_extracted_features) if rule.auto_extracted_features else 0
            param_count = len(device.key_params) if device.key_params else 0
            
            print(f"   设备: {device.device_name} ({device.device_type})")
            print(f"   规则ID: {rule.rule_id}")
            print(f"   特征数量: {feature_count}")
            print(f"   参数数量: {param_count}")
            print(f"   匹配阈值: {rule.match_threshold}")
            print()

if success_count > 0:
    print(f"✅ 规则生成完成！")
    print(f"下一步：运行 python verify_field_device2_import.py 验证导入结果")
else:
    print(f"⚠️ 没有新规则被生成")

print(f"\n🎉 规则生成脚本执行完成！")