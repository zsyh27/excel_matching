#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""将数据库中所有设备的品牌统一设置为霍尼韦尔"""

import sys
sys.path.insert(0, 'backend')

from datetime import datetime
from modules.database import DatabaseManager
from modules.models import Device

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

print("🚀 开始更新所有设备品牌为霍尼韦尔...")
print("=" * 80)

with db_manager.session_scope() as session:
    # 1. 统计当前品牌分布
    print("\n步骤1：统计当前品牌分布")
    print("-" * 80)
    
    all_devices = session.query(Device).all()
    total_devices = len(all_devices)
    
    brand_counts = {}
    for device in all_devices:
        brand = device.brand if device.brand else '未知品牌'
        brand_counts[brand] = brand_counts.get(brand, 0) + 1
    
    print(f"总设备数: {total_devices} 个")
    print(f"\n当前品牌分布:")
    for brand, count in sorted(brand_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {brand}: {count} 个")
    
    # 2. 更新所有设备品牌
    print("\n步骤2：更新所有设备品牌为霍尼韦尔")
    print("-" * 80)
    
    update_count = 0
    skip_count = 0
    
    for device in all_devices:
        if device.brand != '霍尼韦尔':
            old_brand = device.brand if device.brand else '未知品牌'
            device.brand = '霍尼韦尔'
            device.updated_at = datetime.now()
            update_count += 1
            
            if update_count <= 10:  # 只显示前10个更新
                print(f"  更新: {device.device_id} - {old_brand} → 霍尼韦尔")
        else:
            skip_count += 1
    
    if update_count > 10:
        print(f"  ... (还有 {update_count - 10} 个设备已更新)")
    
    print(f"\n更新结果:")
    print(f"  已更新: {update_count} 个设备")
    print(f"  已跳过: {skip_count} 个设备（已经是霍尼韦尔）")
    
    # 3. 验证更新结果
    print("\n步骤3：验证更新结果")
    print("-" * 80)
    
    # 重新统计品牌分布
    brand_counts_after = {}
    for device in all_devices:
        brand = device.brand if device.brand else '未知品牌'
        brand_counts_after[brand] = brand_counts_after.get(brand, 0) + 1
    
    print(f"更新后品牌分布:")
    for brand, count in sorted(brand_counts_after.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {brand}: {count} 个")
    
    # 检查是否所有设备都是霍尼韦尔
    honeywell_count = brand_counts_after.get('霍尼韦尔', 0)
    
    if honeywell_count == total_devices:
        print(f"\n✅ 验证通过：所有 {total_devices} 个设备的品牌都已设置为霍尼韦尔")
    else:
        print(f"\n⚠️ 验证失败：还有 {total_devices - honeywell_count} 个设备的品牌不是霍尼韦尔")

print("\n" + "=" * 80)
print("🎉 品牌更新完成！")
print("=" * 80)
