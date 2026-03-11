#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证流量计能量表导入结果 - 步骤4"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel
from modules.device_feature_extractor import DeviceFeatureExtractor

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("🔍 开始验证流量计能量计导入结果...")
print("=" * 80)

try:
    # 加载配置
    config = db_loader.load_config()
    feature_extractor = DeviceFeatureExtractor(config)
    
    with db_manager.session_scope() as session:
        # 验证设备数量
        print("\n步骤1：验证设备数量")
        print("-" * 80)
        
        flowmeter_count = session.query(Device).filter(
            Device.device_type == '流量计'
        ).count()
        
        energymeter_count = session.query(Device).filter(
            Device.device_type == '能量表'
        ).count()
        
        print(f"流量计设备数量: {flowmeter_count} 个")
        print(f"能量表设备数量: {energymeter_count} 个")
        print(f"总计: {flowmeter_count + energymeter_count} 个")
        
        # 验证规则数量
        print("\n步骤2：验证规则数量")
        print("-" * 80)
        
        flowmeter_rule_count = session.query(RuleModel).join(
            Device, RuleModel.target_device_id == Device.device_id
        ).filter(Device.device_type == '流量计').count()
        
        energymeter_rule_count = session.query(RuleModel).join(
            Device, RuleModel.target_device_id == Device.device_id
        ).filter(Device.device_type == '能量表').count()
        
        print(f"流量计规则数量: {flowmeter_rule_count} 个")
        print(f"能量表规则数量: {energymeter_rule_count} 个")
        print(f"总计: {flowmeter_rule_count + energymeter_rule_count} 个")
        
        # 验证示例设备
        print("\n步骤3：验证示例设备")
        print("-" * 80)
        
        for device_type in ['流量计', '能量表']:
            device = session.query(Device).filter(
                Device.device_type == device_type
            ).first()
            
            if device:
                print(f"\n{device_type}示例:")
                print(f"  设备ID: {device.device_id}")
                print(f"  设备名称: {device.device_name}")
                print(f"  规格型号: {device.spec_model}")
                print(f"  单价: {device.unit_price}")
                
                # 检查 key_params
                if device.key_params:
                    print(f"  参数数量: {len(device.key_params)} 个")
                    print(f"  参数列表: {list(device.key_params.keys())}")
                else:
                    print(f"  ⚠️  key_params 为空！")
                
                # 检查特征提取
                features = feature_extractor.extract_features(device)
                expected_count = 3 + len(device.key_params) if device.key_params else 3
                
                print(f"  提取特征数量: {len(features)}")
                print(f"  预期特征数量: {expected_count}")
                
                if len(features) != expected_count:
                    print(f"  ⚠️  特征数量不匹配！")
                
                # 检查规则
                rule = session.query(RuleModel).filter(
                    RuleModel.target_device_id == device.device_id
                ).first()
                
                if rule:
                    print(f"  规则特征数量: {len(rule.auto_extracted_features)}")
                    print(f"  匹配阈值: {rule.match_threshold}")
                else:
                    print(f"  ⚠️  规则不存在！")
        
        # 验证参数完整性
        print("\n步骤4：验证参数完整性")
        print("-" * 80)
        
        expected_params = ['测量方式', '管体承压', '安装方式', '口径', '衬里材料', '输入电压', '协议', '表体形式']
        
        for device_type in ['流量计', '能量表']:
            devices = session.query(Device).filter(
                Device.device_type == device_type
            ).limit(10).all()
            
            param_coverage = {param: 0 for param in expected_params}
            
            for device in devices:
                if device.key_params:
                    for param in expected_params:
                        if param in device.key_params:
                            param_coverage[param] += 1
            
            print(f"\n{device_type}参数覆盖率（前10个设备）:")
            for param, count in param_coverage.items():
                coverage = (count / len(devices)) * 100 if devices else 0
                print(f"  {param}: {count}/{len(devices)} ({coverage:.1f}%)")
    
    print("\n" + "=" * 80)
    print("✅ 验证完成！")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ 验证失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
