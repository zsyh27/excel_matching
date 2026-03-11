#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证静态平衡阀设备导入结果
检查设备数据、key_params和规则生成是否正确
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel
from modules.device_feature_extractor import DeviceFeatureExtractor

print('=' * 80)
print('验证静态平衡阀设备导入结果')
print('=' * 80)

# 初始化
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 加载配置
config = db_loader.load_config()
feature_extractor = DeviceFeatureExtractor(config)

# 设备类型列表
device_types = ['静态平衡阀', '动态压差阀', '动态压差控制阀', '动态压差控制阀专用支架']

# 预期参数数量
expected_params = {
    '静态平衡阀': 9,
    '动态压差阀': 10,
    '动态压差控制阀': 10,
    '动态压差控制阀专用支架': 7
}

# 验证结果
all_passed = True

with db_manager.session_scope() as session:
    for device_type in device_types:
        print(f'\n{"=" * 80}')
        print(f'验证设备类型: {device_type}')
        print('=' * 80)
        
        # 查询设备
        devices = session.query(Device).filter(
            Device.device_type == device_type,
            Device.brand == '霍尼韦尔'
        ).all()
        
        print(f'\n设备数量: {len(devices)}')
        
        if len(devices) == 0:
            print('❌ 没有找到设备')
            all_passed = False
            continue
        
        # 检查第一个设备的详细信息
        device = devices[0]
        print(f'\n示例设备: {device.device_id}')
        print(f'  设备名称: {device.device_name}')
        print(f'  规格型号: {device.spec_model}')
        print(f'  设备类型: {device.device_type}')
        print(f'  品牌: {device.brand}')
        print(f'  单价: {device.unit_price}')
        
        # 检查 key_params
        if device.key_params:
            print(f'  key_params 参数数量: {len(device.key_params)}')
            expected = expected_params.get(device_type, 0)
            
            if len(device.key_params) == expected:
                print(f'  ✅ 参数数量正确 ({expected})')
            else:
                print(f'  ⚠️  参数数量不匹配: 实际 {len(device.key_params)}, 预期 {expected}')
                all_passed = False
            
            print(f'  参数列表:')
            for key, value in device.key_params.items():
                print(f'    - {key}: {value.get("value", "")}')
        else:
            print(f'  ❌ key_params 为空')
            all_passed = False
        
        # 检查特征提取
        features = feature_extractor.extract_features(device)
        expected_feature_count = 4 + len(device.key_params) if device.key_params else 4
        
        print(f'\n  特征提取:')
        print(f'    提取特征数量: {len(features)}')
        print(f'    预期特征数量: {expected_feature_count} (4个基础特征 + {len(device.key_params) if device.key_params else 0}个参数)')
        
        if len(features) == expected_feature_count:
            print(f'    ✅ 特征数量正确')
        else:
            print(f'    ⚠️  特征数量不匹配')
            all_passed = False
        
        # 检查规则
        rule = session.query(RuleModel).filter(
            RuleModel.target_device_id == device.device_id
        ).first()
        
        print(f'\n  规则验证:')
        if rule:
            print(f'    ✅ 规则已生成: {rule.rule_id}')
            print(f'    规则特征数量: {len(rule.auto_extracted_features)}')
            print(f'    匹配阈值: {rule.match_threshold}')
            
            if len(rule.auto_extracted_features) == len(features):
                print(f'    ✅ 规则特征数量与提取特征数量一致')
            else:
                print(f'    ⚠️  规则特征数量不一致')
                all_passed = False
        else:
            print(f'    ❌ 规则不存在')
            all_passed = False
        
        # 统计该类型的所有设备
        print(f'\n  统计信息:')
        device_count = len(devices)
        rule_count = session.query(RuleModel).join(
            Device, RuleModel.target_device_id == Device.device_id
        ).filter(
            Device.device_type == device_type,
            Device.brand == '霍尼韦尔'
        ).count()
        
        print(f'    设备总数: {device_count}')
        print(f'    规则总数: {rule_count}')
        
        if device_count == rule_count:
            print(f'    ✅ 所有设备都有规则')
        else:
            print(f'    ❌ 部分设备缺少规则')
            all_passed = False

# 总结
print('\n' + '=' * 80)
print('验证总结')
print('=' * 80)

with db_manager.session_scope() as session:
    total_devices = 0
    total_rules = 0
    
    for device_type in device_types:
        device_count = session.query(Device).filter(
            Device.device_type == device_type,
            Device.brand == '霍尼韦尔'
        ).count()
        
        rule_count = session.query(RuleModel).join(
            Device, RuleModel.target_device_id == Device.device_id
        ).filter(
            Device.device_type == device_type,
            Device.brand == '霍尼韦尔'
        ).count()
        
        total_devices += device_count
        total_rules += rule_count
        
        status = '✅' if device_count == rule_count else '❌'
        print(f'{status} {device_type}: {device_count} 设备, {rule_count} 规则')
    
    print(f'\n总计: {total_devices} 设备, {total_rules} 规则')
    
    if all_passed and total_devices == total_rules:
        print('\n🎉 所有验证通过！')
    else:
        print('\n⚠️  部分验证未通过，请检查上面的详细信息')
