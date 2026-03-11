#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证涡街流量计导入结果 - 修复版"""

import sys
sys.path.insert(0, 'backend')
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("🔍 验证涡街流量计导入结果...")

with db_manager.session_scope() as session:
    # 1. 验证设备导入
    vortex_devices = session.query(Device).filter(
        Device.device_type == "涡街流量计"
    ).all()
    
    print(f"\n📊 设备导入验证:")
    print(f"   涡街流量计设备总数: {len(vortex_devices)}")
    
    if vortex_devices:
        sample_device = vortex_devices[0]
        print(f"\n📋 示例设备详情:")
        print(f"   设备ID: {sample_device.device_id}")
        print(f"   设备名称: {sample_device.device_name}")
        print(f"   规格型号: {sample_device.spec_model}")
        print(f"   设备类型: {sample_device.device_type}")
        print(f"   品牌: {sample_device.brand}")
        print(f"   单价: {sample_device.unit_price}")
        
        if sample_device.key_params:
            print(f"   关键参数数量: {len(sample_device.key_params)}")
            print("   关键参数列表:")
            for i, (param_name, param_info) in enumerate(sample_device.key_params.items(), 1):
                value = param_info.get('value', '') if isinstance(param_info, dict) else str(param_info)
                print(f"     {i:2d}. {param_name}: {value}")
        else:
            print("   ⚠️ 关键参数为空")
    
    # 2. 验证规则生成
    vortex_rules = session.query(RuleModel).join(Device).filter(
        Device.device_type == "涡街流量计"
    ).all()
    
    print(f"\n📊 规则生成验证:")
    print(f"   涡街流量计规则总数: {len(vortex_rules)}")
    
    if vortex_rules:
        # 统计特征数量
        feature_counts = []
        for rule in vortex_rules:
            if rule.auto_extracted_features:
                feature_counts.append(len(rule.auto_extracted_features))
        
        if feature_counts:
            avg_features = sum(feature_counts) / len(feature_counts)
            min_features = min(feature_counts)
            max_features = max(feature_counts)
            
            print(f"   特征数量统计:")
            print(f"     平均特征数: {avg_features:.1f}")
            print(f"     最少特征数: {min_features}")
            print(f"     最多特征数: {max_features}")
        
        # 显示示例规则
        sample_rule = vortex_rules[0]
        sample_device = session.query(Device).filter(
            Device.device_id == sample_rule.target_device_id
        ).first()
        
        print(f"\n📋 示例规则详情:")
        print(f"   规则ID: {sample_rule.rule_id}")
        print(f"   目标设备: {sample_device.spec_model if sample_device else 'Unknown'}")
        print(f"   特征数量: {len(sample_rule.auto_extracted_features) if sample_rule.auto_extracted_features else 0}")
        print(f"   匹配阈值: {sample_rule.match_threshold}")
        
        # 安全地显示特征类型分布
        if sample_rule.auto_extracted_features:
            feature_types = {}
            for feature in sample_rule.auto_extracted_features:
                if isinstance(feature, dict):
                    feature_type = feature.get('type', 'unknown')
                    feature_types[feature_type] = feature_types.get(feature_type, 0) + 1
                else:
                    feature_types['string_format'] = feature_types.get('string_format', 0) + 1
            
            print(f"   特征类型分布:")
            for feature_type, count in sorted(feature_types.items()):
                print(f"     {feature_type}: {count} 个")
            
            # 显示前5个特征
            print("   前5个特征:")
            for i, feature in enumerate(sample_rule.auto_extracted_features[:5], 1):
                if isinstance(feature, dict):
                    feature_text = feature.get('feature', 'N/A')
                    feature_type = feature.get('type', 'unknown')
                    feature_weight = feature.get('weight', 0)
                    print(f"     {i}. {feature_text} (类型: {feature_type}, 权重: {feature_weight})")
                else:
                    print(f"     {i}. {feature} (字符串格式)")
    
    # 3. 验证配置
    device_params = db_loader.get_config_by_key('device_params')
    if device_params and 'device_types' in device_params:
        vortex_config = device_params['device_types'].get('涡街流量计')
        if vortex_config:
            print(f"\n📊 配置验证:")
            print(f"   涡街流量计配置存在: ✅")
            print(f"   配置参数数量: {len(vortex_config.get('params', []))}")
            print(f"   配置关键词: {vortex_config.get('keywords', [])}")
        else:
            print(f"\n📊 配置验证:")
            print(f"   涡街流量计配置存在: ❌")
    
    # 4. 数据完整性检查
    devices_without_rules = 0
    rules_without_devices = 0
    
    # 获取所有设备ID和规则ID进行比较
    device_ids = set(device.device_id for device in vortex_devices)
    rule_device_ids = set(rule.target_device_id for rule in vortex_rules)
    
    devices_without_rules = len(device_ids - rule_device_ids)
    rules_without_devices = len(rule_device_ids - device_ids)
    
    print(f"\n📊 数据完整性检查:")
    print(f"   设备总数: {len(vortex_devices)}")
    print(f"   规则总数: {len(vortex_rules)}")
    print(f"   缺少规则的设备: {devices_without_rules} 个")
    print(f"   缺少设备的规则: {rules_without_devices} 个")
    
    if devices_without_rules == 0 and rules_without_devices == 0:
        print("   数据完整性: ✅ 完整")
    else:
        print("   数据完整性: ⚠️ 存在问题")
        if devices_without_rules > 0:
            missing_rule_devices = device_ids - rule_device_ids
            print(f"   缺少规则的设备ID: {list(missing_rule_devices)[:5]}...")
        if rules_without_devices > 0:
            orphan_rules = rule_device_ids - device_ids
            print(f"   孤立规则的设备ID: {list(orphan_rules)[:5]}...")

print("\n🎉 涡街流量计导入验证完成！")

# 5. 测试匹配功能
print("\n🧪 测试匹配功能...")
try:
    import requests
    
    # 测试匹配API
    test_text = "涡街流量计 DN25 PN16 液体介质 4-20mA输出"
    
    response = requests.post(
        'http://localhost:5000/api/match',
        json={'text': test_text, 'top_k': 3},
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        matches = result.get('matches', [])
        print(f"   测试文本: {test_text}")
        print(f"   匹配结果数量: {len(matches)}")
        
        if matches:
            best_match = matches[0]
            print(f"   最佳匹配:")
            print(f"     设备名称: {best_match.get('device_name', 'N/A')}")
            print(f"     匹配得分: {best_match.get('score', 0):.2f}")
            print(f"     设备类型: {best_match.get('device_type', 'N/A')}")
        
        print("   匹配功能: ✅ 正常")
    else:
        print(f"   匹配功能: ❌ API错误 (状态码: {response.status_code})")
        
except Exception as e:
    print(f"   匹配功能: ⚠️ 测试失败 ({str(e)})")

print("\n✅ 所有验证完成！")