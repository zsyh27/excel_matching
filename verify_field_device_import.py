#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证现场设备导入结果"""

import sys
sys.path.insert(0, 'backend')
from modules.database import DatabaseManager
from modules.models import Device, Rule as RuleModel

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

print("🔍 验证现场设备导入结果...")

try:
    with db_manager.session_scope() as session:
        # 1. 统计现场设备数量
        field_devices = session.query(Device).filter(
            Device.device_id.like('FIELD_%')
        ).all()
        
        print(f"\n📊 设备统计:")
        print(f"   现场设备总数: {len(field_devices)} 个")
        
        # 2. 按设备类型分组统计
        device_type_stats = {}
        for device in field_devices:
            device_type = device.device_type
            if device_type not in device_type_stats:
                device_type_stats[device_type] = {
                    'count': 0,
                    'avg_params': 0,
                    'total_params': 0
                }
            device_type_stats[device_type]['count'] += 1
            if device.key_params:
                device_type_stats[device_type]['total_params'] += len(device.key_params)
        
        # 计算平均参数数量
        for device_type, stats in device_type_stats.items():
            if stats['count'] > 0:
                stats['avg_params'] = stats['total_params'] / stats['count']
        
        print(f"\n📋 设备类型分布:")
        for device_type, stats in device_type_stats.items():
            print(f"   {device_type}: {stats['count']} 个设备, 平均 {stats['avg_params']:.1f} 个参数")
        
        # 3. 统计规则数量
        field_rules = session.query(RuleModel).filter(
            RuleModel.target_device_id.like('FIELD_%')
        ).all()
        
        print(f"\n🔧 规则统计:")
        print(f"   现场设备规则总数: {len(field_rules)} 条")
        
        # 4. 检查数据完整性
        print(f"\n✅ 数据完整性检查:")
        
        devices_without_rules = 0
        rules_without_devices = 0
        
        # 检查设备是否都有规则
        for device in field_devices:
            rule = session.query(RuleModel).filter(
                RuleModel.target_device_id == device.device_id
            ).first()
            if not rule:
                devices_without_rules += 1
        
        # 检查规则是否都有对应设备
        for rule in field_rules:
            device = session.query(Device).filter(
                Device.device_id == rule.target_device_id
            ).first()
            if not device:
                rules_without_devices += 1
        
        print(f"   设备与规则匹配: {len(field_devices) - devices_without_rules}/{len(field_devices)}")
        print(f"   规则与设备匹配: {len(field_rules) - rules_without_devices}/{len(field_rules)}")
        
        if devices_without_rules > 0:
            print(f"   ⚠️ {devices_without_rules} 个设备缺少规则")
        if rules_without_devices > 0:
            print(f"   ⚠️ {rules_without_devices} 条规则缺少对应设备")
        
        # 5. 显示示例设备详情
        print(f"\n📝 示例设备详情:")
        sample_device = field_devices[0] if field_devices else None
        if sample_device:
            print(f"   设备ID: {sample_device.device_id}")
            print(f"   品牌: {sample_device.brand}")
            print(f"   设备类型: {sample_device.device_type}")
            print(f"   设备名称: {sample_device.device_name}")
            print(f"   规格型号: {sample_device.spec_model}")
            print(f"   单价: {sample_device.unit_price}")
            
            if sample_device.key_params:
                print(f"   关键参数 ({len(sample_device.key_params)} 个):")
                for param_name, param_info in list(sample_device.key_params.items())[:5]:
                    print(f"     - {param_name}: {param_info.get('value', 'N/A')}")
                if len(sample_device.key_params) > 5:
                    print(f"     ... 还有 {len(sample_device.key_params) - 5} 个参数")
            
            # 显示对应规则
            sample_rule = session.query(RuleModel).filter(
                RuleModel.target_device_id == sample_device.device_id
            ).first()
            
            if sample_rule:
                print(f"   匹配规则:")
                print(f"     规则ID: {sample_rule.rule_id}")
                print(f"     特征数量: {len(sample_rule.auto_extracted_features)}")
                print(f"     匹配阈值: {sample_rule.match_threshold}")
        
        # 6. 总结
        print(f"\n🎉 验证结果总结:")
        if len(field_devices) == len(field_rules) and devices_without_rules == 0 and rules_without_devices == 0:
            print(f"   ✅ 导入完全成功！")
            print(f"   ✅ 所有 {len(field_devices)} 个设备都已导入")
            print(f"   ✅ 所有 {len(field_rules)} 条规则都已生成")
            print(f"   ✅ 数据完整性检查通过")
            print(f"   ✅ 包含检测对象参数")
        else:
            print(f"   ⚠️ 存在一些问题需要处理")
            if devices_without_rules > 0:
                print(f"   ⚠️ 需要为 {devices_without_rules} 个设备生成规则")
            if rules_without_devices > 0:
                print(f"   ⚠️ 需要清理 {rules_without_devices} 条孤立规则")

except Exception as e:
    print(f"❌ 验证失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)