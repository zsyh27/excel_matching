#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成流量计能量计设备匹配规则 - 步骤3"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel
from modules.rule_generator import RuleGenerator

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("🚀 开始生成流量计能量计设备匹配规则...")
print("=" * 80)

try:
    # 加载配置
    print("\n步骤1：加载配置")
    print("-" * 80)
    config = db_loader.load_config()
    print("✅ 配置加载成功")
    
    # 初始化规则生成器
    print("\n步骤2：初始化规则生成器")
    print("-" * 80)
    rule_generator = RuleGenerator(config)
    print("✅ 规则生成器初始化成功")
    
    # 统计信息
    stats = {
        '流量计': {'success': 0, 'skip': 0, 'error': 0},
        '能量表': {'success': 0, 'skip': 0, 'error': 0}
    }
    
    with db_manager.session_scope() as session:
        # 查询流量计和能量表设备
        devices = session.query(Device).filter(
            Device.device_type.in_(['流量计', '能量表'])
        ).all()
        
        print(f"\n步骤3：生成规则")
        print("-" * 80)
        print(f"找到 {len(devices)} 个设备需要生成规则")
        
        for i, device in enumerate(devices, 1):
            try:
                # 检查规则是否已存在
                existing_rule = session.query(RuleModel).filter(
                    RuleModel.target_device_id == device.device_id
                ).first()
                
                if existing_rule:
                    stats[device.device_type]['skip'] += 1
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
                    stats[device.device_type]['success'] += 1
                    
                    # 每100条打印一次进度
                    if stats[device.device_type]['success'] % 100 == 0:
                        print(f"  已生成 {device.device_type} 规则: {stats[device.device_type]['success']} 个")
                else:
                    stats[device.device_type]['error'] += 1
                    print(f"  ⚠️  设备 {device.device_id} 规则生成失败")
                
            except Exception as e:
                stats[device.device_type]['error'] += 1
                print(f"  ⚠️  设备 {device.device_id} 规则生成异常: {e}")
                continue
    
    # 输出统计信息
    print("\n" + "=" * 80)
    print("规则生成统计:")
    print("-" * 80)
    
    total_success = 0
    total_skip = 0
    total_error = 0
    
    for device_type, stat in stats.items():
        print(f"\n{device_type}:")
        print(f"  ✅ 成功生成: {stat['success']} 个")
        print(f"  ⏭️  已存在跳过: {stat['skip']} 个")
        print(f"  ❌ 失败: {stat['error']} 个")
        
        total_success += stat['success']
        total_skip += stat['skip']
        total_error += stat['error']
    
    print(f"\n总计:")
    print(f"  ✅ 成功生成: {total_success} 个")
    print(f"  ⏭️  已存在跳过: {total_skip} 个")
    print(f"  ❌ 失败: {total_error} 个")
    
    print("\n" + "=" * 80)
    print("🎉 规则生成完成！")
    print("下一步：验证导入结果（步骤4）")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ 规则生成失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
