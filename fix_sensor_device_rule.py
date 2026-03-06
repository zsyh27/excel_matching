#!/usr/bin/env python3
"""修复传感器设备规则生成问题"""

import sys
import os

# 添加backend目录到路径
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

import sqlite3
import json

print("=" * 80)
print("修复传感器设备规则")
print("=" * 80)

# 导入模块
try:
    from modules.data_loader import DataLoader, Device
    from modules.text_preprocessor import TextPreprocessor
    from modules.rule_generator import RuleGenerator
    print("✅ 模块导入成功")
except Exception as e:
    print(f"❌ 模块导入失败: {e}")
    exit(1)

# 初始化数据加载器
# 创建配置对象
class Config:
    STORAGE_MODE = 'database'
    DATABASE_URL = 'sqlite:///data/devices.db'
    DATABASE_TYPE = 'sqlite'
    FALLBACK_TO_JSON = False

config_obj = Config()
data_loader = DataLoader(config=config_obj)

# 加载配置
config = data_loader.load_config()
print(f"\n✅ 配置加载成功")

# 初始化预处理器和规则生成器
preprocessor = TextPreprocessor(config=config)
rule_generator = RuleGenerator(preprocessor=preprocessor, config=config)

# 目标设备ID
device_id = "霍尼韦尔_HST-RA_20260306113921944861"

print(f"\n【1. 查找设备】")
print(f"设备ID: {device_id}")

# 从数据库加载设备
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,))
row = cursor.fetchone()

if not row:
    print(f"❌ 未找到设备")
    conn.close()
    exit(1)

print(f"✅ 找到设备")
print(f"  品牌: {row[1]}")
print(f"  设备名称: {row[2]}")
print(f"  规格型号: {row[3]}")
print(f"  设备类型: {row[9]}")

# 解析key_params
key_params = json.loads(row[7]) if row[7] else {}
print(f"  关键参数: {list(key_params.keys())}")

# 创建Device对象
device = Device(
    device_id=row[0],
    brand=row[1],
    device_name=row[2],
    spec_model=row[3],
    detailed_params=row[4],
    unit_price=row[5],
    raw_description=row[6],
    key_params=key_params,
    confidence_score=row[8],
    device_type=row[9]
)

print(f"\n【2. 提取特征】")
features = rule_generator.extract_features(device)
print(f"  特征数量: {len(features)}")
print(f"  特征列表:")
for feature in features:
    print(f"    - {feature}")

print(f"\n【3. 分配权重】")
weights = rule_generator.assign_weights(features, device)
print(f"  权重数量: {len(weights)}")

# 按权重排序显示
feature_weight_pairs = sorted(weights.items(), key=lambda x: x[1], reverse=True)
print(f"  权重列表(按权重排序):")
total_weight = 0
for feature, weight in feature_weight_pairs:
    print(f"    {feature:30s} 权重: {weight}")
    total_weight += weight

print(f"\n  总权重: {total_weight}")

# 检查关键特征
print(f"\n【4. 验证关键特征】")

if '温度传感器' in features:
    print(f"  ✅ '温度传感器'在特征列表中")
    print(f"     权重: {weights.get('温度传感器', 0)}")
else:
    print(f"  ❌ '温度传感器'不在特征列表中")

if '传感器' in features:
    print(f"  ⚠️  '传感器'在特征列表中")
    print(f"     权重: {weights.get('传感器', 0)}")
    print(f"     这可能是错误拆分的结果")

# 询问是否更新规则
print(f"\n【5. 更新规则】")
response = input("是否更新该设备的规则? (y/n): ")

if response.lower() == 'y':
    # 生成新规则
    rule = rule_generator.generate_rule(device)
    
    # 更新数据库
    cursor.execute("""
        UPDATE rules 
        SET auto_extracted_features = ?, feature_weights = ?, match_threshold = ?
        WHERE target_device_id = ?
    """, (
        json.dumps(rule.auto_extracted_features, ensure_ascii=False),
        json.dumps(rule.feature_weights, ensure_ascii=False),
        rule.match_threshold,
        device_id
    ))
    
    conn.commit()
    print(f"✅ 规则已更新")
    
    # 显示更新后的规则
    print(f"\n【6. 更新后的规则】")
    print(f"  规则ID: {rule.rule_id}")
    print(f"  特征数量: {len(rule.auto_extracted_features)}")
    print(f"  匹配阈值: {rule.match_threshold}")
    
    print(f"\n  特征列表(按权重排序):")
    feature_weight_pairs = sorted(rule.feature_weights.items(), key=lambda x: x[1], reverse=True)
    for feature, weight in feature_weight_pairs:
        print(f"    {feature:30s} 权重: {weight}")
else:
    print(f"❌ 取消更新")

conn.close()

print("\n" + "=" * 80)
print("完成")
print("=" * 80)
