#!/usr/bin/env python3
"""检查传感器设备的规则生成问题"""

import sqlite3
import json

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

print("=" * 80)
print("检查传感器设备规则")
print("=" * 80)

# 查找这个设备
device_id = "霍尼韦尔_HST-RA_20260306113921944861"

print(f"\n【1. 查找设备】")
print(f"设备ID: {device_id}")

cursor.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,))
device = cursor.fetchone()

if device:
    print(f"✅ 找到设备")
    print(f"  品牌: {device[1]}")
    print(f"  设备名称: {device[2]}")
    print(f"  设备类型: {device[6]}")  # device_type字段
    print(f"  规格型号: {device[3]}")
else:
    print(f"❌ 未找到设备")
    conn.close()
    exit(1)

# 查找对应的规则
print(f"\n【2. 查找规则】")
cursor.execute("SELECT * FROM rules WHERE target_device_id = ?", (device_id,))
rule = cursor.fetchone()

if rule:
    print(f"✅ 找到规则")
    rule_id = rule[0]
    print(f"  规则ID: {rule_id}")
    
    # 解析特征和权重
    auto_features = json.loads(rule[2])
    feature_weights = json.loads(rule[3])
    
    print(f"\n【3. 特征分析】")
    print(f"  特征数量: {len(auto_features)}")
    print(f"  权重数量: {len(feature_weights)}")
    
    # 按权重排序显示
    feature_weight_pairs = [(f, feature_weights.get(f, 0)) for f in auto_features]
    feature_weight_pairs.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n  特征列表(按权重排序):")
    total_weight = 0
    for feature, weight in feature_weight_pairs:
        print(f"    {feature:30s} 权重: {weight}")
        total_weight += weight
    
    print(f"\n  总权重: {total_weight}")
    print(f"  匹配阈值: {rule[4]}")
    
    # 检查问题
    print(f"\n【4. 问题检查】")
    
    # 检查是否有"传感器"特征
    if '传感器' in auto_features:
        print(f"  ⚠️  发现'传感器'特征,权重: {feature_weights.get('传感器', 0)}")
        print(f"      这可能是'温度传感器'被错误拆分的结果")
    
    # 检查是否有"温度传感器"特征
    if '温度传感器' in auto_features:
        print(f"  ✅ 发现'温度传感器'特征,权重: {feature_weights.get('温度传感器', 0)}")
    else:
        print(f"  ❌ 缺少'温度传感器'特征")
    
    # 检查设备类型字段
    device_type = device[6]
    print(f"\n  设备类型字段: '{device_type}'")
    
    if device_type and device_type not in auto_features:
        print(f"  ⚠️  设备类型'{device_type}'不在特征列表中")
        print(f"      可能被拆分成了: {[f for f in auto_features if f in device_type or device_type in f]}")
    
else:
    print(f"❌ 未找到规则")

# 检查配置中的设备类型关键词
print(f"\n【5. 检查配置】")
cursor.execute("SELECT config_value FROM configs WHERE config_key = 'device_type_keywords'")
row = cursor.fetchone()

if row:
    device_type_keywords = json.loads(row[0])
    print(f"  设备类型关键词数量: {len(device_type_keywords)}")
    
    # 检查是否包含"温度传感器"
    if '温度传感器' in device_type_keywords:
        print(f"  ✅ '温度传感器'在关键词列表中")
    else:
        print(f"  ❌ '温度传感器'不在关键词列表中")
    
    # 检查是否包含"传感器"
    if '传感器' in device_type_keywords:
        print(f"  ⚠️  '传感器'在关键词列表中")
        print(f"      这可能导致拆分问题")

# 检查特征权重配置
print(f"\n【6. 检查特征权重配置】")
cursor.execute("SELECT config_value FROM configs WHERE config_key = 'feature_weights'")
row = cursor.fetchone()

if row:
    feature_weights_config = json.loads(row[0])
    
    # 检查设备类型权重
    device_type_weight = feature_weights_config.get('device_type', 0)
    print(f"  设备类型默认权重: {device_type_weight}")
    
    # 检查"传感器"的权重
    if '传感器' in feature_weights_config:
        print(f"  '传感器'权重: {feature_weights_config['传感器']}")
    
    # 检查"温度传感器"的权重
    if '温度传感器' in feature_weights_config:
        print(f"  '温度传感器'权重: {feature_weights_config['温度传感器']}")
else:
    print(f"  ℹ️  未找到feature_weights配置")

conn.close()

print("\n" + "=" * 80)
print("问题诊断")
print("=" * 80)

print("\n可能的原因:")
print("  1. 规则生成时,'温度传感器'被拆分成了'温度'和'传感器'")
print("  2. '传感器'作为独立特征,权重只有1")
print("  3. 应该保持'温度传感器'作为完整的设备类型,权重20")

print("\n建议:")
print("  1. 重新生成该设备的规则")
print("  2. 确保设备类型不被拆分")
print("  3. 检查规则生成器的分词逻辑")
