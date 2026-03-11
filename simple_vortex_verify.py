#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""简单验证涡街流量计导入结果"""

import sys
sys.path.insert(0, 'backend')
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("🔍 验证涡街流量计导入结果...")

# 1. 验证设备导入
with db_manager.session_scope() as session:
    vortex_devices_count = session.query(Device).filter(
        Device.device_type == "涡街流量计"
    ).count()
    
    print(f"\n📊 设备导入验证:")
    print(f"   涡街流量计设备总数: {vortex_devices_count}")
    
    if vortex_devices_count > 0:
        sample_device = session.query(Device).filter(
            Device.device_type == "涡街流量计"
        ).first()
        
        print(f"\n📋 示例设备详情:")
        print(f"   设备ID: {sample_device.device_id}")
        print(f"   设备名称: {sample_device.device_name}")
        print(f"   规格型号: {sample_device.spec_model}")
        print(f"   设备类型: {sample_device.device_type}")
        print(f"   品牌: {sample_device.brand}")
        print(f"   单价: {sample_device.unit_price}")
        
        if sample_device.key_params:
            print(f"   关键参数数量: {len(sample_device.key_params)}")
        else:
            print("   ⚠️ 关键参数为空")

# 2. 验证规则生成
with db_manager.session_scope() as session:
    vortex_rules_count = session.query(RuleModel).join(Device).filter(
        Device.device_type == "涡街流量计"
    ).count()
    
    print(f"\n📊 规则生成验证:")
    print(f"   涡街流量计规则总数: {vortex_rules_count}")
    
    if vortex_rules_count > 0:
        sample_rule = session.query(RuleModel).join(Device).filter(
            Device.device_type == "涡街流量计"
        ).first()
        
        print(f"\n📋 示例规则详情:")
        print(f"   规则ID: {sample_rule.rule_id}")
        print(f"   特征数量: {len(sample_rule.auto_extracted_features) if sample_rule.auto_extracted_features else 0}")
        print(f"   匹配阈值: {sample_rule.match_threshold}")

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
print(f"\n📊 数据完整性检查:")
print(f"   设备总数: {vortex_devices_count}")
print(f"   规则总数: {vortex_rules_count}")

if vortex_devices_count == vortex_rules_count:
    print("   数据完整性: ✅ 完整")
else:
    print("   数据完整性: ⚠️ 设备和规则数量不匹配")

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
            
            # 检查是否匹配到涡街流量计
            if best_match.get('device_type') == '涡街流量计':
                print("   涡街流量计匹配: ✅ 成功")
            else:
                print("   涡街流量计匹配: ⚠️ 未匹配到涡街流量计")
        
        print("   匹配功能: ✅ 正常")
    else:
        print(f"   匹配功能: ❌ API错误 (状态码: {response.status_code})")
        
except Exception as e:
    print(f"   匹配功能: ⚠️ 测试失败 ({str(e)})")

print("\n✅ 所有验证完成！")