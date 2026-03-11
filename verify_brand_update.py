#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证品牌更新结果"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device, Rule as RuleModel

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

print("🔍 验证品牌更新结果...")
print("=" * 80)

with db_manager.session_scope() as session:
    # 1. 验证品牌统一性
    print("\n1. 品牌统一性验证")
    print("-" * 80)
    
    all_devices = session.query(Device).all()
    total_devices = len(all_devices)
    
    brand_counts = {}
    for device in all_devices:
        brand = device.brand if device.brand else '未知品牌'
        brand_counts[brand] = brand_counts.get(brand, 0) + 1
    
    print(f"总设备数: {total_devices} 个")
    print(f"\n品牌分布:")
    for brand, count in sorted(brand_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {brand}: {count} 个")
    
    honeywell_count = brand_counts.get('霍尼韦尔', 0)
    
    if honeywell_count == total_devices:
        print(f"\n✅ 所有 {total_devices} 个设备的品牌都是霍尼韦尔")
    else:
        print(f"\n⚠️ 还有 {total_devices - honeywell_count} 个设备的品牌不是霍尼韦尔")
        
        # 显示非霍尼韦尔品牌的设备
        non_honeywell = session.query(Device).filter(
            Device.brand != '霍尼韦尔'
        ).limit(10).all()
        
        if non_honeywell:
            print(f"\n非霍尼韦尔品牌的设备示例:")
            for device in non_honeywell:
                print(f"  - {device.device_id}: {device.brand} - {device.device_name}")
    
    # 2. 按设备类型统计
    print("\n2. 按设备类型统计（前10种）")
    print("-" * 80)
    
    device_type_counts = {}
    for device in all_devices:
        device_type = device.device_type if device.device_type else '未知类型'
        device_type_counts[device_type] = device_type_counts.get(device_type, 0) + 1
    
    sorted_types = sorted(device_type_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for device_type, count in sorted_types:
        print(f"  - {device_type}: {count} 个")
    
    # 3. 验证规则完整性
    print("\n3. 规则完整性验证")
    print("-" * 80)
    
    devices_with_rules = 0
    devices_without_rules = 0
    
    for device in all_devices:
        rule = session.query(RuleModel).filter(
            RuleModel.target_device_id == device.device_id
        ).first()
        
        if rule:
            devices_with_rules += 1
        else:
            devices_without_rules += 1
    
    print(f"有规则的设备: {devices_with_rules} 个")
    print(f"缺少规则的设备: {devices_without_rules} 个")
    
    if devices_without_rules > 0:
        print(f"\n⚠️ 有 {devices_without_rules} 个设备缺少规则")
        print("建议运行规则重新生成脚本")
    else:
        print(f"\n✅ 所有设备都有匹配规则")
    
    # 4. 显示示例设备
    print("\n4. 示例设备展示（前5个）")
    print("-" * 80)
    
    sample_devices = all_devices[:5]
    for device in sample_devices:
        print(f"\n  设备ID: {device.device_id}")
        print(f"  品牌: {device.brand}")
        print(f"  设备名称: {device.device_name}")
        print(f"  设备类型: {device.device_type}")
        print(f"  规格型号: {device.spec_model}")

print("\n" + "=" * 80)
print("验证总结:")
print("=" * 80)

if honeywell_count == total_devices:
    print("✅ 品牌更新成功！所有设备的品牌都已设置为霍尼韦尔")
else:
    print("⚠️ 品牌更新未完全成功，请检查")

print("\n" + "=" * 80)
print("🎉 验证完成！")
print("=" * 80)
