#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
步骤3：生成蝶阀设备匹配规则

为导入的设备生成匹配规则
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel
from modules.device_feature_extractor import DeviceFeatureExtractor
from modules.rule_generator import RuleGenerator

print('=' * 80)
print('步骤3：生成蝶阀设备匹配规则')
print('=' * 80)

# 初始化
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 加载配置
print('加载配置...')
config = db_loader.load_config()

# 初始化组件
feature_extractor = DeviceFeatureExtractor(config)
rule_generator = RuleGenerator(config)

# 统计信息
stats = {
    'total': 0,
    'success': 0,
    'error': 0,
    'by_type': {}
}

with db_manager.session_scope() as session:
    # 查询所有蝶阀相关设备
    devices = session.query(Device).filter(
        Device.device_type.in_([
            '蝶阀',
            '蝶阀开关型执行器',
            '蝶阀调节型执行器',
            '蝶阀+蝶阀开关型执行器',
            '蝶阀+蝶阀调节型执行器'
        ])
    ).all()
    
    print(f'找到 {len(devices)} 个蝶阀设备\n')
    
    for device in devices:
        try:
            stats['total'] += 1
            
            # 统计设备类型
            if device.device_type not in stats['by_type']:
                stats['by_type'][device.device_type] = {'success': 0, 'error': 0}
            
            # 检查规则是否已存在
            existing_rule = session.query(RuleModel).filter(
                RuleModel.target_device_id == device.device_id
            ).first()
            
            if existing_rule:
                # 删除旧规则
                session.delete(existing_rule)
            
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
                
                stats['success'] += 1
                stats['by_type'][device.device_type]['success'] += 1
                
                # 每100条打印一次进度
                if stats['success'] % 100 == 0:
                    print(f'已生成 {stats["success"]} 条规则...')
            else:
                stats['error'] += 1
                stats['by_type'][device.device_type]['error'] += 1
                print(f'❌ 设备 {device.device_id} 规则生成失败')
        
        except Exception as e:
            stats['error'] += 1
            if device.device_type in stats['by_type']:
                stats['by_type'][device.device_type]['error'] += 1
            print(f'❌ 设备 {device.device_id} 规则生成失败: {str(e)}')
            continue

# 打印统计信息
print('\n' + '=' * 80)
print('规则生成统计')
print('=' * 80)
print(f'总设备数: {stats["total"]}')
print(f'成功生成: {stats["success"]}')
print(f'失败: {stats["error"]}')

print('\n按设备类型统计:')
for device_type, counts in sorted(stats['by_type'].items()):
    print(f'  {device_type}:')
    print(f'    成功: {counts["success"]}')
    if counts['error'] > 0:
        print(f'    失败: {counts["error"]}')

print('\n' + '=' * 80)
print('✅ 步骤3完成！所有蝶阀设备已导入并生成规则')
print('=' * 80)

# 验证结果
print('\n验证导入结果...')
with db_manager.session_scope() as session:
    # 查询示例设备
    sample_device = session.query(Device).filter(
        Device.device_type == '蝶阀'
    ).first()
    
    if sample_device:
        print(f'\n示例设备:')
        print(f'  设备ID: {sample_device.device_id}')
        print(f'  设备名称: {sample_device.device_name}')
        print(f'  规格型号: {sample_device.spec_model}')
        print(f'  设备类型: {sample_device.device_type}')
        print(f'  参数数量: {len(sample_device.key_params) if sample_device.key_params else 0}')
        
        if sample_device.key_params:
            print(f'  参数列表: {list(sample_device.key_params.keys())}')
        
        # 查询规则
        rule = session.query(RuleModel).filter(
            RuleModel.target_device_id == sample_device.device_id
        ).first()
        
        if rule:
            print(f'\n规则信息:')
            print(f'  规则ID: {rule.rule_id}')
            print(f'  特征数量: {len(rule.auto_extracted_features)}')
            print(f'  匹配阈值: {rule.match_threshold}')
        else:
            print(f'\n⚠️ 规则不存在')

print('\n' + '=' * 80)
print('🎉 蝶阀设备导入完成！')
print('=' * 80)
