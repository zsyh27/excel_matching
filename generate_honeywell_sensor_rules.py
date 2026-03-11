#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为霍尼韦尔传感器设备生成匹配规则"""

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

print("🚀 开始为霍尼韦尔传感器设备生成匹配规则...")

try:
    # 加载配置
    config = db_loader.load_config()
    
    # 初始化组件
    feature_extractor = DeviceFeatureExtractor(config)
    rule_generator = RuleGenerator(config)
    
    print("✅ 组件初始化完成")
    
    with db_manager.session_scope() as session:
        # 查询霍尼韦尔传感器设备（温度传感器和温湿度传感器）
        sensor_devices = session.query(Device).filter(
            Device.brand == '霍尼韦尔',
            Device.device_type.in_(['温度传感器', '温湿度传感器'])
        ).all()
        
        print(f"📊 找到 {len(sensor_devices)} 个霍尼韦尔传感器设备")
        
        # 统计设备类型
        device_type_counts = {}
        for device in sensor_devices:
            device_type_counts[device.device_type] = device_type_counts.get(device.device_type, 0) + 1
        
        for device_type, count in device_type_counts.items():
            print(f"   {device_type}: {count} 个设备")
        
        generated_count = 0
        updated_count = 0
        error_count = 0
        
        for i, device in enumerate(sensor_devices, 1):
            try:
                # 检查是否已存在规则
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
                    
                    # 每10个设备显示进度
                    if i % 10 == 0:
                        print(f"   已处理 {i}/{len(sensor_devices)} 个设备...")
                        
                else:
                    print(f"⚠️ 设备 {device.device_id} 规则生成失败")
                    error_count += 1
                    
            except Exception as e:
                print(f"❌ 设备 {device.device_id} 处理失败: {e}")
                error_count += 1
                continue
    
    print(f"\n✅ 霍尼韦尔传感器规则生成完成！")
    print(f"   新生成规则: {generated_count} 个")
    print(f"   更新规则: {updated_count} 个")
    print(f"   处理失败: {error_count} 个")
    
    # 验证规则生成结果
    with db_manager.session_scope() as session:
        # 检查规则示例
        sample_device = session.query(Device).filter(
            Device.brand == '霍尼韦尔',
            Device.device_type.in_(['温度传感器', '温湿度传感器'])
        ).first()
        
        if sample_device:
            sample_rule = session.query(RuleModel).filter(
                RuleModel.target_device_id == sample_device.device_id
            ).first()
            
            if sample_rule:
                print(f"\n🔍 规则生成示例 (设备: {sample_device.device_name}):")
                print(f"   设备类型: {sample_device.device_type}")
                print(f"   规格型号: {sample_device.spec_model}")
                print(f"   参数数量: {len(sample_device.key_params) if sample_device.key_params else 0}")
                print(f"   提取特征数量: {len(sample_rule.auto_extracted_features)}")
                print(f"   匹配阈值: {sample_rule.match_threshold}")
                
                # 显示前5个特征
                print(f"   特征示例:")
                for i, feature in enumerate(sample_rule.auto_extracted_features[:5]):
                    weight = sample_rule.feature_weights.get(feature, 1.0)
                    print(f"     {feature} (权重: {weight})")
                
                if len(sample_rule.auto_extracted_features) > 5:
                    print(f"     ... 还有 {len(sample_rule.auto_extracted_features) - 5} 个特征")
        
        # 统计规则数量
        total_rules = session.query(RuleModel).join(Device).filter(
            Device.brand == '霍尼韦尔',
            Device.device_type.in_(['温度传感器', '温湿度传感器'])
        ).count()
        
        print(f"\n📊 规则统计:")
        print(f"   霍尼韦尔传感器规则总数: {total_rules}")

except Exception as e:
    print(f"❌ 规则生成过程中出错: {e}")
    sys.exit(1)

print("\n🎉 霍尼韦尔传感器匹配规则生成完成！")
print("现在可以使用智能匹配功能了！")