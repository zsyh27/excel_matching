"""
合并设备库：将提取的能源管理系统设备合并到现有设备库中
同时生成对应的匹配规则
"""

import json

print("=" * 80)
print("合并设备库")
print("=" * 80)
print()

# 1. 读取现有设备库
print("1. 读取现有设备库...")
with open('../data/static_device.json', 'r', encoding='utf-8') as f:
    existing_devices = json.load(f)
print(f"   现有设备数: {len(existing_devices)}")

# 2. 读取提取的设备
print("2. 读取提取的设备...")
with open('../data/extracted_devices.json', 'r', encoding='utf-8') as f:
    new_devices = json.load(f)
print(f"   新设备数: {len(new_devices)}")
print()

# 3. 合并设备库
print("3. 合并设备库...")
merged_devices = existing_devices + new_devices
print(f"   合并后总设备数: {len(merged_devices)}")
print()

# 4. 保存合并后的设备库
print("4. 保存合并后的设备库...")
with open('../data/static_device.json', 'w', encoding='utf-8') as f:
    json.dump(merged_devices, f, ensure_ascii=False, indent=2)
print(f"   已保存到: data/static_device.json")
print()

# 5. 生成匹配规则
print("5. 生成匹配规则...")
print()

# 读取现有规则
with open('../data/static_rule.json', 'r', encoding='utf-8') as f:
    existing_rules = json.load(f)
print(f"   现有规则数: {len(existing_rules)}")

# 为新设备生成规则
new_rules = []
rule_id_counter = len(existing_rules) + 1

for device in new_devices:
    device_id = device['device_id']
    device_name = device['device_name']
    brand = device['brand']
    spec_model = device['spec_model']
    detailed_params = device['detailed_params']
    
    # 提取关键词
    keywords = [device_name]
    
    # 从设备名称中提取关键词
    if "采集器" in device_name:
        keywords.append("采集器")
    if "服务器" in device_name:
        keywords.append("服务器")
    if "电脑" in device_name:
        keywords.append("电脑")
    if "软件" in device_name or "系统" in device_name:
        keywords.append("软件")
        keywords.append("系统")
    if "配线" in device_name or "线" in device_name:
        keywords.append("线")
        keywords.append("配线")
    if "网线" in device_name:
        keywords.append("网线")
    if "配管" in device_name or "管" in device_name:
        keywords.append("管")
        keywords.append("配管")
    if "接线盒" in device_name:
        keywords.append("接线盒")
    if "控制器" in device_name:
        keywords.append("控制器")
    if "网关" in device_name:
        keywords.append("网关")
    if "接口" in device_name:
        keywords.append("接口")
    if "控制箱" in device_name or "箱" in device_name:
        keywords.append("箱")
        keywords.append("控制箱")
    if "传感器" in device_name or "探测器" in device_name:
        keywords.append("传感器")
    if "开关" in device_name:
        keywords.append("开关")
    if "光缆" in device_name:
        keywords.append("光缆")
    
    # 从规格参数中提取关键词
    if "能耗" in device_name or "能源" in device_name:
        keywords.append("能耗")
        keywords.append("能源")
    if "多联机" in device_name:
        keywords.append("多联机")
    if "监控" in device_name:
        keywords.append("监控")
    if "CO" in device_name or "CO2" in device_name:
        keywords.append("CO")
    if "PM" in device_name:
        keywords.append("PM")
    if "液位" in device_name:
        keywords.append("液位")
    
    # 去重
    keywords = list(set(keywords))
    
    # 创建规则
    rule = {
        "rule_id": f"RULE{rule_id_counter:03d}",
        "target_device_id": device_id,
        "auto_extracted_features": keywords,
        "feature_weights": {kw: 3.0 for kw in keywords},
        "match_threshold": 2,
        "remark": f"自动生成的规则 - {device_name}"
    }
    
    new_rules.append(rule)
    rule_id_counter += 1

print(f"   生成了 {len(new_rules)} 条新规则")
print()

# 显示部分新规则
print("6. 新规则示例（前5条）:")
print()
for rule in new_rules[:5]:
    device = next(d for d in new_devices if d['device_id'] == rule['target_device_id'])
    print(f"规则ID: {rule['rule_id']}")
    print(f"设备: {device['device_name']}")
    print(f"关键词: {', '.join(rule['auto_extracted_features'])}")
    print(f"匹配阈值: {rule['match_threshold']}")
    print()

# 7. 合并规则
print("7. 合并规则...")
merged_rules = existing_rules + new_rules
print(f"   合并后总规则数: {len(merged_rules)}")
print()

# 8. 保存合并后的规则
print("8. 保存合并后的规则...")
with open('../data/static_rule.json', 'w', encoding='utf-8') as f:
    json.dump(merged_rules, f, ensure_ascii=False, indent=2)
print(f"   已保存到: data/static_rule.json")
print()

print("=" * 80)
print("合并完成！")
print()
print("统计:")
print(f"  设备总数: {len(existing_devices)} → {len(merged_devices)} (+{len(new_devices)})")
print(f"  规则总数: {len(existing_rules)} → {len(merged_rules)} (+{len(new_rules)})")
print()
print("下一步:")
print("  运行测试脚本验证匹配效果")
print("  python backend/test_real_excel_matching.py")
print("=" * 80)
