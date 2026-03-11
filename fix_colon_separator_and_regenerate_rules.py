#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复冒号分隔符问题并重新生成所有规则
支持英文冒号":"和中文冒号"："
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel
from modules.rule_generator import RuleGenerator
from datetime import datetime

print('=' * 80)
print('修复冒号分隔符问题并重新生成所有规则')
print('=' * 80)

# 初始化
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 加载配置
print('\n加载配置...')
config = db_loader.load_config()
rule_generator = RuleGenerator(config)
print('✅ 配置加载成功')

# 统计信息
stats = {
    'total_devices': 0,
    'fixed_devices': 0,
    'unchanged_devices': 0,
    'total_rules_deleted': 0,
    'total_rules_generated': 0,
    'failed': 0
}

print('\n' + '=' * 80)
print('步骤1：修复设备的key_params（支持英文冒号）')
print('=' * 80)

with db_manager.session_scope() as session:
    # 获取所有设备
    devices = session.query(Device).all()
    stats['total_devices'] = len(devices)
    
    print(f'\n找到 {len(devices)} 个设备')
    
    for device in devices:
        try:
            # 检查是否有detailed_params
            if not device.detailed_params:
                stats['unchanged_devices'] += 1
                continue
            
            # 重新解析key_params，同时支持中文和英文冒号
            new_key_params = {}
            description = device.detailed_params
            
            # 先按中文逗号分割
            params = description.split('，')
            
            for param in params:
                # 同时检查中文冒号和英文冒号
                if '：' in param:
                    key, value = param.split('：', 1)
                    new_key_params[key.strip()] = {"value": value.strip()}
                elif ':' in param:
                    key, value = param.split(':', 1)
                    new_key_params[key.strip()] = {"value": value.strip()}
            
            # 检查是否有变化
            if new_key_params != device.key_params:
                old_count = len(device.key_params) if device.key_params else 0
                new_count = len(new_key_params)
                
                if new_count > old_count:
                    print(f'  ✅ {device.device_id}: 参数数量 {old_count} -> {new_count}')
                    device.key_params = new_key_params
                    device.updated_at = datetime.now()
                    stats['fixed_devices'] += 1
                else:
                    stats['unchanged_devices'] += 1
            else:
                stats['unchanged_devices'] += 1
        
        except Exception as e:
            print(f'  ❌ {device.device_id}: 修复失败 - {str(e)}')
            stats['failed'] += 1

print(f'\n修复统计:')
print(f'  总设备数: {stats["total_devices"]}')
print(f'  已修复: {stats["fixed_devices"]}')
print(f'  未变化: {stats["unchanged_devices"]}')
print(f'  失败: {stats["failed"]}')

print('\n' + '=' * 80)
print('步骤2：删除所有现有规则')
print('=' * 80)

with db_manager.session_scope() as session:
    # 删除所有规则
    deleted_count = session.query(RuleModel).delete()
    stats['total_rules_deleted'] = deleted_count
    print(f'\n✅ 已删除 {deleted_count} 条规则')

print('\n' + '=' * 80)
print('步骤3：重新生成所有设备的规则')
print('=' * 80)

with db_manager.session_scope() as session:
    devices = session.query(Device).all()
    
    print(f'\n开始为 {len(devices)} 个设备生成规则...')
    
    for idx, device in enumerate(devices, 1):
        try:
            # 生成规则
            rule_data = rule_generator.generate_rule(device)
            
            if not rule_data:
                print(f'  ❌ {device.device_id}: 规则生成失败')
                stats['failed'] += 1
                continue
            
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
            stats['total_rules_generated'] += 1
            
            if idx % 50 == 0:
                print(f'  已生成 {idx}/{len(devices)} 条规则...')
        
        except Exception as e:
            print(f'  ❌ {device.device_id}: {str(e)}')
            stats['failed'] += 1

print(f'\n✅ 规则生成完成: {stats["total_rules_generated"]}/{stats["total_devices"]}')

# 验证结果
print('\n' + '=' * 80)
print('验证结果')
print('=' * 80)

with db_manager.session_scope() as session:
    device_count = session.query(Device).count()
    rule_count = session.query(RuleModel).count()
    
    print(f'\n设备总数: {device_count}')
    print(f'规则总数: {rule_count}')
    
    if device_count == rule_count:
        print('\n✅ 所有设备都有规则')
    else:
        print(f'\n⚠️  缺少 {device_count - rule_count} 条规则')
    
    # 检查修复效果（随机抽查几个设备）
    print('\n' + '=' * 80)
    print('抽查修复效果')
    print('=' * 80)
    
    # 查找包含英文冒号的设备
    devices_with_colon = session.query(Device).filter(
        Device.detailed_params.like('%:%')
    ).limit(5).all()
    
    if devices_with_colon:
        print(f'\n找到 {len(devices_with_colon)} 个包含英文冒号的设备（抽查）:')
        for device in devices_with_colon:
            print(f'\n设备: {device.device_id}')
            print(f'  设备类型: {device.device_type}')
            print(f'  详细参数: {device.detailed_params[:100]}...')
            print(f'  key_params数量: {len(device.key_params) if device.key_params else 0}')
            
            if device.key_params:
                print(f'  参数列表:')
                for key in list(device.key_params.keys())[:5]:
                    print(f'    - {key}: {device.key_params[key].get("value", "")}')

print('\n' + '=' * 80)
print('总结')
print('=' * 80)
print(f'\n修复的设备数: {stats["fixed_devices"]}')
print(f'删除的规则数: {stats["total_rules_deleted"]}')
print(f'生成的规则数: {stats["total_rules_generated"]}')
print(f'失败次数: {stats["failed"]}')

if stats["total_rules_generated"] == stats["total_devices"]:
    print('\n🎉 所有操作成功完成！')
else:
    print(f'\n⚠️  部分操作未完成，请检查错误信息')
