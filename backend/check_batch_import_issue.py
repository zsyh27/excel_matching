"""
检查批量导入问题
"""
import sys
import json
sys.path.insert(0, '.')

from modules.data_loader import DataLoader
from config import Config

# 初始化数据加载器
loader = DataLoader(config=Config)

# 1. 检查最近导入的设备
print("=" * 80)
print("检查最近导入的设备")
print("=" * 80)

devices = loader.load_devices()
print(f"\n设备总数: {len(devices)}")

# 获取最后5个设备
device_list = list(devices.values())
recent_devices = device_list[-5:] if len(device_list) >= 5 else device_list

for device in recent_devices:
    print(f"\n设备ID: {device.device_id}")
    print(f"品牌: {device.brand}")
    print(f"设备类型: {device.device_type}")
    print(f"设备名称: {device.device_name}")
    print(f"规格型号: {device.spec_model}")
    
    # 检查关键参数
    if hasattr(device, 'key_params') and device.key_params:
        print(f"关键参数: {json.dumps(device.key_params, ensure_ascii=False, indent=2)}")
    else:
        print("关键参数: 无")

# 2. 检查规则
print("\n" + "=" * 80)
print("检查规则")
print("=" * 80)

rules = loader.load_rules()
print(f"\n规则总数: {len(rules)}")

# 获取最后5个规则
if isinstance(rules, dict):
    rule_list = list(rules.values())
else:
    rule_list = rules
recent_rules = rule_list[-5:] if len(rule_list) >= 5 else rule_list

for rule in recent_rules:
    print(f"\n规则ID: {rule.rule_id}")
    print(f"目标设备ID: {rule.target_device_id}")
    print(f"特征数量: {len(rule.auto_extracted_features)}")
    print(f"特征: {rule.auto_extracted_features}")
    print(f"特征权重: {json.dumps(rule.feature_weights, ensure_ascii=False, indent=2)}")
    
    # 检查设备类型权重
    if hasattr(rule, 'feature_weights'):
        for feature, weight in rule.feature_weights.items():
            if '电动调节阀' in feature:
                print(f"  ⚠️ 发现设备类型特征 '{feature}' 权重为: {weight}")

# 3. 检查最近导入的设备是否有对应的规则
print("\n" + "=" * 80)
print("检查设备与规则的对应关系")
print("=" * 80)

for device in recent_devices:
    rule_id = f"R_{device.device_id}"
    # 检查规则是否存在
    rule_exists = False
    if isinstance(rules, dict):
        rule_exists = rule_id in rules
    else:
        rule_exists = any(r.rule_id == rule_id for r in rules)
    
    if rule_exists:
        print(f"\n✓ 设备 {device.device_id} 有对应规则 {rule_id}")
    else:
        print(f"\n✗ 设备 {device.device_id} 没有对应规则")
