#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""清理动态压差平衡阀设备数据和规则，准备重新导入"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device, Rule as RuleModel

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

def cleanup_dynamic_balance_valve_data():
    """删除所有动态压差平衡阀相关的设备和规则"""
    
    print("开始清理动态压差平衡阀设备数据和规则...")
    
    deleted_devices = 0
    deleted_rules = 0
    
    with db_manager.session_scope() as session:
        # 1. 查找所有动态压差平衡阀设备
        dynamic_devices = session.query(Device).filter(
            Device.device_type.like('%动态压差平衡%')
        ).all()
        
        print(f"找到 {len(dynamic_devices)} 个动态压差平衡阀设备")
        
        # 2. 删除相关规则
        for device in dynamic_devices:
            # 删除设备对应的规则
            rules = session.query(RuleModel).filter(
                RuleModel.target_device_id == device.device_id
            ).all()
            
            for rule in rules:
                session.delete(rule)
                deleted_rules += 1
                print(f"删除规则: {rule.rule_id}")
        
        # 3. 删除设备
        for device in dynamic_devices:
            print(f"删除设备: {device.device_id} - {device.spec_model}")
            session.delete(device)
            deleted_devices += 1
    
    print("\n" + "="*60)
    print("动态压差平衡阀数据清理完成")
    print("="*60)
    print(f"删除设备: {deleted_devices} 个")
    print(f"删除规则: {deleted_rules} 个")
    
    return deleted_devices, deleted_rules

def verify_cleanup():
    """验证清理结果"""
    print("\n验证清理结果...")
    
    with db_manager.session_scope() as session:
        # 检查是否还有动态压差平衡阀设备
        remaining_devices = session.query(Device).filter(
            Device.device_type.like('%动态压差平衡%')
        ).count()
        
        # 检查是否还有动态压差平衡阀相关的规则
        # 由于我们已经删除了所有动态压差平衡阀设备，相关规则应该也被删除了
        # 这里检查是否有孤立的规则（target_device_id不存在对应设备）
        all_device_ids = {device.device_id for device in session.query(Device).all()}
        orphan_rules = session.query(RuleModel).filter(
            ~RuleModel.target_device_id.in_(all_device_ids)
        ).all()
        
        # 删除孤立规则
        for rule in orphan_rules:
            session.delete(rule)
        
        remaining_rules = len(orphan_rules)
        
        print(f"剩余动态压差平衡阀设备: {remaining_devices} 个")
        print(f"清理的孤立规则: {remaining_rules} 个")
        
        if remaining_devices == 0:
            print("✅ 清理完成，可以重新导入")
            return True
        else:
            print("⚠️ 清理不完整，请检查")
            return False

if __name__ == "__main__":
    # 执行清理
    deleted_devices, deleted_rules = cleanup_dynamic_balance_valve_data()
    
    # 验证清理结果
    if verify_cleanup():
        print("\n🎉 数据清理成功！现在可以重新执行导入流程：")
        print("1. python analyze_dynamic_balance_valve_excel.py")
        print("2. python import_dynamic_balance_valve_devices.py")
        print("3. python generate_dynamic_balance_valve_rules.py")
        print("4. python verify_dynamic_balance_valve_import.py")
    else:
        print("\n❌ 数据清理失败，请检查数据库状态")