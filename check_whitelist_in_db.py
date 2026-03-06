#!/usr/bin/env python3
"""检查数据库中白名单配置的存储情况"""

import sqlite3
import json

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

print("=" * 80)
print("检查数据库中的白名单配置")
print("=" * 80)

# 查询所有配置键
cursor.execute("SELECT config_key, config_value FROM configs")
rows = cursor.fetchall()

print(f"\n数据库中共有 {len(rows)} 个配置项\n")

# 查找白名单相关的配置
whitelist_configs = []
for key, value in rows:
    if 'whitelist' in key.lower():
        whitelist_configs.append((key, value))
        print(f"找到白名单配置:")
        print(f"  键名: {key}")
        try:
            parsed_value = json.loads(value)
            print(f"  值类型: {type(parsed_value)}")
            if isinstance(parsed_value, list):
                print(f"  数量: {len(parsed_value)}")
                print(f"  前5项: {parsed_value[:5]}")
            elif isinstance(parsed_value, dict):
                print(f"  字典键: {list(parsed_value.keys())}")
        except:
            print(f"  值: {value[:100]}...")
        print()

if not whitelist_configs:
    print("❌ 未找到任何白名单配置！")
    print("\n所有配置键名:")
    for key, _ in rows:
        print(f"  - {key}")

# 检查是否有intelligent_extraction配置
print("\n" + "=" * 80)
print("检查intelligent_extraction配置")
print("=" * 80)

cursor.execute("SELECT config_key, config_value FROM configs WHERE config_key LIKE '%intelligent%'")
intelligent_rows = cursor.fetchall()

if intelligent_rows:
    for key, value in intelligent_rows:
        print(f"\n键名: {key}")
        try:
            parsed = json.loads(value)
            print(f"值类型: {type(parsed)}")
            if isinstance(parsed, dict):
                print(f"顶层键: {list(parsed.keys())}")
                # 检查是否有feature_quality_scoring
                if 'feature_quality_scoring' in parsed:
                    fqs = parsed['feature_quality_scoring']
                    print(f"feature_quality_scoring键: {list(fqs.keys())}")
                    if 'whitelist_features' in fqs:
                        print(f"whitelist_features: {fqs['whitelist_features'][:5]}")
        except Exception as e:
            print(f"解析失败: {e}")
else:
    print("❌ 未找到intelligent_extraction配置")

conn.close()

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)
