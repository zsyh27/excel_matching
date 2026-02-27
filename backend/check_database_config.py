# -*- coding: utf-8 -*-
"""
检查数据库中的配置
"""

import sqlite3
import json
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')

print(f"数据库路径: {db_path}")
print(f"数据库存在: {os.path.exists(db_path)}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查询所有配置
cursor.execute("SELECT config_key, config_value FROM configs")
rows = cursor.fetchall()

print(f"\n数据库中的配置项数量: {len(rows)}")
print("\n配置项列表:")
for config_key, config_value in rows:
    try:
        value = json.loads(config_value)
        if isinstance(value, list):
            print(f"  - {config_key}: list, 长度 {len(value)}")
        elif isinstance(value, dict):
            print(f"  - {config_key}: dict, 键数量 {len(value)}")
        else:
            print(f"  - {config_key}: {type(value).__name__}")
    except:
        print(f"  - {config_key}: (无法解析)")

conn.close()

# 检查缺失的配置项
required_keys = [
    'synonym_map',
    'brand_keywords',
    'device_type_keywords'
]

existing_keys = [row[0] for row in rows]

print("\n缺失的配置项:")
for key in required_keys:
    if key not in existing_keys:
        print(f"  ✗ {key}")
