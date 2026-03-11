#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为动态压差平衡阀设备生成匹配规则"""

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

# 加载配置
config = db_loader.load_config()

# 初始化特征提取器和规则生成器
feature_extractor = DeviceFeatureExtractor(config)
rule_generator = RuleGenerator(config)

def generate_rules_for_dynamic_balance_valves():
    """为动态压差平衡阀设备生成规则"""
    
    print("开始为动态压差平衡阀设备生成匹配规则...")
    
    generated_count = 0
    error_count = 0
    device_type_stats = {}
    
    with db_manager.session_scope() as session:
        # 查询所有动态压差平衡阀设备
        dynamic_devices = session.query(Device).filter(
            Device.device_type.like('%动态压差平衡%')
        ).all()
        
        print(f"找到 {len(dynamic_devices)} 个动态压差平衡阀设备")
        
        for device in dynamic_devices:
            try:
                # 检查是否已存在规则
                existing_rule = session.query(RuleModel).filter(
                    RuleModel.target_device_id == device.device_id
                ).first()
                
                if existing_rule:
                    print(f"设备 {device.device_id} 已存在规则，跳过")
                    continue
                
                # 生成规则
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
                    generated_count += 1
                    
                    # 统计设备类型
                    if device.device_type not in device_type_stats:
                        device_type_stats[device.device_type] = 0
                    device_type_stats[device.device_type] += 1
                    
                    if generated_count % 10 == 0:
                        print(f"已生成 {generated_count} 个规则...")
                
                else:
                    print(f"设备 {device.device_id} 规则生成失败")
                    error_count += 1
                    
            except Exception as e:
                print(f"设备 {device.device_id} 规则生成异常: {str(e)}")
                error_count += 1
                continue
    
    # 输出统计信息
    print("\n" + "="*60)
    print("动态压差平衡阀规则生成完成")
    print("="*60)
    print(f"成功生成: {generated_count} 个规则")
    print(f"生成失败: {error_count} 个规则")
    
    print("\n按设备类型统计:")
    for device_type, count in device_type_stats.items():
        print(f"  {device_type}: {count} 个规则")
    
    return generated_count > 0

def verify_rules():
    """验证规则生成结果"""
    print("\n" + "="*60)
    print("验证规则生成结果")
    print("="*60)
    
    with db_manager.session_scope() as session:
        # 查询动态压差平衡阀设备及其规则
        dynamic_devices = session.query(Device).filter(
            Device.device_type.like('%动态压差平衡%')
        ).all()
        
        devices_with_rules = 0
        devices_without_rules = 0
        feature_stats = {}
        
        for device in dynamic_devices:
            rule = session.query(RuleModel).filter(
                RuleModel.target_device_id == device.device_id
            ).first()
            
            if rule:
                devices_with_rules += 1
                
                # 统计特征数量
                feature_count = len(rule.auto_extracted_features) if rule.auto_extracted_features else 0
                key_params_count = len(device.key_params) if device.key_params else 0
                expected_count = 4 + key_params_count  # 4个基础特征 + 参数数量
                
                if device.device_type not in feature_stats:
                    feature_stats[device.device_type] = {
                        'devices': 0,
                        'avg_features': 0,
                        'avg_expected': 0,
                        'examples': []
                    }
                
                feature_stats[device.device_type]['devices'] += 1
                feature_stats[device.device_type]['avg_features'] += feature_count
                feature_stats[device.device_type]['avg_expected'] += expected_count
                
                # 保存前3个示例
                if len(feature_stats[device.device_type]['examples']) < 3:
                    feature_stats[device.device_type]['examples'].append({
                        'device_id': device.device_id,
                        'model': device.spec_model,
                        'feature_count': feature_count,
                        'expected_count': expected_count,
                        'key_params_count': key_params_count
                    })
            else:
                devices_without_rules += 1
                print(f"⚠️ 设备 {device.device_id} ({device.spec_model}) 没有规则")
        
        print(f"有规则的设备: {devices_with_rules} 个")
        print(f"无规则的设备: {devices_without_rules} 个")
        print(f"规则覆盖率: {devices_with_rules/(devices_with_rules+devices_without_rules)*100:.1f}%")
        
        # 显示特征统计
        print("\n特征提取统计:")
        for device_type, stats in feature_stats.items():
            if stats['devices'] > 0:
                avg_features = stats['avg_features'] / stats['devices']
                avg_expected = stats['avg_expected'] / stats['devices']
                
                print(f"\n{device_type}:")
                print(f"  设备数量: {stats['devices']}")
                print(f"  平均特征数: {avg_features:.1f}")
                print(f"  预期特征数: {avg_expected:.1f}")
                print(f"  特征完整度: {avg_features/avg_expected*100:.1f}%")
                
                print("  示例设备:")
                for example in stats['examples']:
                    print(f"    {example['device_id']} - {example['model']} - "
                          f"{example['feature_count']}/{example['expected_count']}特征 "
                          f"({example['key_params_count']}个参数)")

if __name__ == "__main__":
    if generate_rules_for_dynamic_balance_valves():
        verify_rules()
        print("\n✅ 动态压差平衡阀规则生成成功！")
    else:
        print("\n❌ 动态压差平衡阀规则生成失败！")