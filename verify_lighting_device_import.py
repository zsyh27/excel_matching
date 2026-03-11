#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证智能照明设备导入结果"""

import sys
sys.path.insert(0, 'backend')
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("🔍 验证智能照明设备导入结果...")

try:
    with db_manager.session_scope() as session:
        # 1. 查询智能照明设备
        lighting_devices = session.query(Device).filter(
            Device.device_type == "智能照明设备"
        ).all()
        
        print(f"\n📊 设备导入统计:")
        print(f"   智能照明设备总数: {len(lighting_devices)}")
        
        if not lighting_devices:
            print("❌ 没有找到智能照明设备")
            sys.exit(1)
        
        # 2. 验证设备数据完整性
        print(f"\n📋 设备数据验证:")
        
        devices_with_key_params = 0
        devices_without_key_params = 0
        total_params = 0
        
        for device in lighting_devices:
            if device.key_params and len(device.key_params) > 0:
                devices_with_key_params += 1
                total_params += len(device.key_params)
            else:
                devices_without_key_params += 1
        
        print(f"   有key_params的设备: {devices_with_key_params} 个")
        print(f"   无key_params的设备: {devices_without_key_params} 个")
        print(f"   平均参数数量: {total_params / len(lighting_devices):.1f} 个/设备")
        
        # 3. 验证规则生成
        print(f"\n🔧 规则生成验证:")
        
        devices_with_rules = 0
        devices_without_rules = 0
        total_features = 0
        
        for device in lighting_devices:
            rule = session.query(RuleModel).filter(
                RuleModel.target_device_id == device.device_id
            ).first()
            
            if rule:
                devices_with_rules += 1
                if rule.auto_extracted_features:
                    total_features += len(rule.auto_extracted_features)
            else:
                devices_without_rules += 1
        
        print(f"   有规则的设备: {devices_with_rules} 个")
        print(f"   无规则的设备: {devices_without_rules} 个")
        if devices_with_rules > 0:
            print(f"   平均特征数量: {total_features / devices_with_rules:.1f} 个/规则")
        
        # 4. 显示设备详情示例
        print(f"\n📝 设备详情示例（前3个）:")
        
        for i, device in enumerate(lighting_devices[:3]):
            print(f"\n设备 {i+1}: {device.device_id}")
            print(f"   品牌: {device.brand}")
            print(f"   设备名称: {device.device_name}")
            print(f"   规格型号: {device.spec_model}")
            print(f"   设备类型: {device.device_type}")
            print(f"   单价: ¥{device.unit_price / 100:.2f}")
            
            if device.key_params:
                print(f"   参数数量: {len(device.key_params)}")
                # 显示前5个参数
                param_names = list(device.key_params.keys())[:5]
                print(f"   前5个参数: {param_names}")
            else:
                print(f"   参数数量: 0")
            
            # 检查规则
            rule = session.query(RuleModel).filter(
                RuleModel.target_device_id == device.device_id
            ).first()
            
            if rule:
                print(f"   规则ID: {rule.rule_id}")
                print(f"   特征数量: {len(rule.auto_extracted_features) if rule.auto_extracted_features else 0}")
                print(f"   匹配阈值: {rule.match_threshold}")
            else:
                print(f"   规则: 未生成")
        
        # 5. 配置验证
        print(f"\n⚙️ 配置验证:")
        
        device_params = db_loader.get_config_by_key('device_params')
        if device_params and 'device_types' in device_params:
            lighting_config = device_params['device_types'].get('智能照明设备', {})
            if lighting_config:
                print(f"   智能照明设备配置: ✅ 存在")
                print(f"   配置参数数量: {len(lighting_config.get('params', []))}")
                print(f"   关键词数量: {len(lighting_config.get('keywords', []))}")
            else:
                print(f"   智能照明设备配置: ❌ 不存在")
        else:
            print(f"   device_params配置: ❌ 不存在")
        
        # 6. 总体评估
        print(f"\n🎯 总体评估:")
        
        success_rate = (devices_with_key_params / len(lighting_devices)) * 100
        rule_rate = (devices_with_rules / len(lighting_devices)) * 100
        
        print(f"   数据完整性: {success_rate:.1f}% ({devices_with_key_params}/{len(lighting_devices)})")
        print(f"   规则覆盖率: {rule_rate:.1f}% ({devices_with_rules}/{len(lighting_devices)})")
        
        if success_rate >= 90 and rule_rate >= 90:
            print(f"   状态: ✅ 导入成功")
        elif success_rate >= 70 and rule_rate >= 70:
            print(f"   状态: ⚠️ 基本成功，有少量问题")
        else:
            print(f"   状态: ❌ 导入有问题，需要检查")
        
        print(f"\n🎉 智能照明设备导入验证完成！")

except Exception as e:
    print(f"❌ 验证过程中出错: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)