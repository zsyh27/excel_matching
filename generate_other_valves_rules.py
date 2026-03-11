#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为其他阀门设备生成匹配规则 - 步骤3"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel
from modules.device_feature_extractor import DeviceFeatureExtractor
from modules.rule_generator import RuleGenerator

# 初始化
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 加载配置
config = db_loader.load_config()

# 初始化组件
feature_extractor = DeviceFeatureExtractor(config)
rule_generator = RuleGenerator(config)

print('=' * 80)
print('其他阀门设备规则生成')
print('=' * 80)

# 统计信息
stats = {
    'total': 0,
    'success': 0,
    'skipped': 0,
    'error': 0,
    'by_type': {}
}

with db_manager.session_scope() as session:
    # 查询所有其他阀门相关设备
    other_valve_types = [
        '减压阀',
        '截止阀',
        '手动球阀',
        '手动蝶阀',
        '手动闸阀',
        '排气阀',
        '止回阀',
        '过滤器'
    ]
    
    devices = session.query(Device).filter(
        Device.device_type.in_(other_valve_types)
    ).all()
    
    print(f'\n找到 {len(devices)} 个其他阀门设备')
    
    for device in devices:
        stats['total'] += 1
        
        # 检查是否已有规则
        existing_rule = session.query(RuleModel).filter(
            RuleModel.target_device_id == device.device_id
        ).first()
        
        if existing_rule:
            print(f"⚠️  设备 {device.device_id} ({device.spec_model}) 已有规则，跳过")
            stats['skipped'] += 1
            continue
        
        try:
            # 生成规则（返回数据类）
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
                
                stats['success'] += 1
                stats['by_type'][device.device_type] = stats['by_type'].get(device.device_type, 0) + 1
                
                if stats['success'] % 50 == 0:
                    print(f"✅ 已生成 {stats['success']} 个规则...")
            else:
                print(f"❌ 设备 {device.device_id} ({device.spec_model}) 规则生成失败")
                stats['error'] += 1
        
        except Exception as e:
            print(f"❌ 设备 {device.device_id} ({device.spec_model}) 规则生成异常: {e}")
            stats['error'] += 1

# 显示统计信息
print('\n' + '=' * 80)
print('规则生成完成统计')
print('=' * 80)
print(f"总设备数: {stats['total']}")
print(f"成功生成: {stats['success']}")
print(f"跳过: {stats['skipped']}")
print(f"错误: {stats['error']}")

print('\n按设备类型统计:')
for device_type, count in sorted(stats['by_type'].items()):
    print(f"  {device_type}: {count}")

print('\n' + '=' * 80)
print('✅ 其他阀门设备规则生成完成！')
print('=' * 80)

# 验证规则
print('\n验证规则...')
with db_manager.session_scope() as session:
    # 随机抽取几个设备验证
    sample_types = ['截止阀', '止回阀', '过滤器']
    
    for device_type in sample_types:
        sample_device = session.query(Device).filter(
            Device.device_type == device_type
        ).first()
        
        if sample_device:
            print(f'\n示例设备: {device_type}')
            print(f'  设备ID: {sample_device.device_id}')
            print(f'  型号: {sample_device.spec_model}')
            print(f'  参数数量: {len(sample_device.key_params) if sample_device.key_params else 0}')
            
            # 查询规则
            rule = session.query(RuleModel).filter(
                RuleModel.target_device_id == sample_device.device_id
            ).first()
            
            if rule:
                print(f'  规则特征数量: {len(rule.auto_extracted_features)}')
                print(f'  匹配阈值: {rule.match_threshold}')
            else:
                print('  ❌ 规则不存在！')

print('\n' + '=' * 80)
