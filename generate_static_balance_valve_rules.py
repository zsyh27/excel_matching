#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
步骤3：生成静态平衡阀设备匹配规则
为导入的设备生成匹配规则
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel
from modules.rule_generator import RuleGenerator

print('=' * 80)
print('生成静态平衡阀设备匹配规则')
print('=' * 80)

# 初始化
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 加载配置
print('\n加载配置...')
config = db_loader.load_config()
print('✅ 配置加载成功')

# 初始化规则生成器
rule_generator = RuleGenerator(config)

# 设备类型列表
device_types = ['静态平衡阀', '动态压差阀', '动态压差控制阀', '动态压差控制阀专用支架']

# 统计信息
stats = {
    'total': 0,
    'success': 0,
    'skipped': 0,
    'failed': 0,
    'by_type': {}
}

# 生成规则
with db_manager.session_scope() as session:
    for device_type in device_types:
        print(f'\n处理设备类型: {device_type}')
        
        # 查询该类型的所有设备
        devices = session.query(Device).filter(
            Device.device_type == device_type,
            Device.brand == '霍尼韦尔'
        ).all()
        
        print(f'  找到 {len(devices)} 个设备')
        
        for device in devices:
            stats['total'] += 1
            
            try:
                # 检查规则是否已存在
                existing_rule = session.query(RuleModel).filter(
                    RuleModel.target_device_id == device.device_id
                ).first()
                
                if existing_rule:
                    stats['skipped'] += 1
                    continue
                
                # 生成规则
                rule_data = rule_generator.generate_rule(device)
                
                if not rule_data:
                    print(f'    ❌ {device.device_id}: 规则生成失败')
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
                stats['success'] += 1
                
                # 统计各类型数量
                if device_type not in stats['by_type']:
                    stats['by_type'][device_type] = 0
                stats['by_type'][device_type] += 1
                
            except Exception as e:
                print(f'    ❌ {device.device_id}: {str(e)}')
                stats['failed'] += 1
                continue
        
        print(f'  ✅ 完成 {device_type}')

# 显示统计结果
print('\n' + '=' * 80)
print('规则生成统计')
print('=' * 80)
print(f'总计: {stats["total"]}')
print(f'成功: {stats["success"]}')
print(f'跳过: {stats["skipped"]}')
print(f'失败: {stats["failed"]}')

print('\n按设备类型统计:')
for device_type, count in sorted(stats['by_type'].items()):
    print(f'  - {device_type}: {count}')

# 验证规则生成结果
print('\n' + '=' * 80)
print('验证规则生成结果')
print('=' * 80)

with db_manager.session_scope() as session:
    for device_type in device_types:
        # 统计设备数量
        device_count = session.query(Device).filter(
            Device.device_type == device_type,
            Device.brand == '霍尼韦尔'
        ).count()
        
        # 统计规则数量
        rule_count = session.query(RuleModel).join(
            Device, RuleModel.target_device_id == Device.device_id
        ).filter(
            Device.device_type == device_type,
            Device.brand == '霍尼韦尔'
        ).count()
        
        status = '✅' if device_count == rule_count else '❌'
        print(f'  {status} {device_type}: {rule_count}/{device_count} 规则')

success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
print(f'\n✅ 规则生成完成！成功率: {success_rate:.1f}%')

if stats['success'] > 0:
    print('\n下一步：运行 verify_static_balance_valve_import.py 验证导入结果')
