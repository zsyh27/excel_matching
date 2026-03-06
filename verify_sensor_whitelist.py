#!/usr/bin/env python3
"""验证传感器相关特征是否在白名单中"""

import sqlite3
import json

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

print("=" * 80)
print("验证传感器白名单特征")
print("=" * 80)

# 读取intelligent_extraction配置
cursor.execute("SELECT config_value FROM configs WHERE config_key = 'intelligent_extraction'")
row = cursor.fetchone()

if not row:
    print("❌ 未找到intelligent_extraction配置")
    conn.close()
    exit(1)

intelligent_extraction = json.loads(row[0])
whitelist_features = intelligent_extraction.get('feature_quality_scoring', {}).get('whitelist_features', [])

print(f"\n✅ 白名单特征总数: {len(whitelist_features)}")

# 期望的传感器相关特征
expected_sensor_features = [
    'co',
    'co2', 
    'pm10',
    'pm2.5',
    '温度',
    '湿度',
    '霍尼韦尔'
]

print(f"\n检查传感器相关特征:")
print("-" * 80)

found_count = 0
missing_features = []

for feature in expected_sensor_features:
    if feature in whitelist_features:
        print(f"  ✅ {feature}")
        found_count += 1
    else:
        print(f"  ❌ {feature} (缺失)")
        missing_features.append(feature)

print("-" * 80)
print(f"\n找到: {found_count}/{len(expected_sensor_features)} 个传感器特征")

if missing_features:
    print(f"\n⚠️  缺失的特征: {missing_features}")
else:
    print(f"\n✅ 所有传感器特征都已添加到白名单！")

# 显示所有白名单特征
print(f"\n完整白名单特征列表:")
print("-" * 80)
for i, feature in enumerate(sorted(whitelist_features), 1):
    print(f"  {i:2d}. {feature}")

conn.close()

print("\n" + "=" * 80)
print("验证完成")
print("=" * 80)
