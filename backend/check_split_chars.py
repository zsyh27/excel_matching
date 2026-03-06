#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查特征分隔符配置
"""

import sqlite3
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 读取feature_split_chars配置
cursor.execute("SELECT config_value FROM configs WHERE config_key = 'feature_split_chars'")
result = cursor.fetchone()

if result:
    split_chars = json.loads(result[0])
    print("特征分隔符配置 (feature_split_chars):")
    print("=" * 80)
    print(f"分隔符数量: {len(split_chars)}")
    print(f"分隔符列表: {split_chars}")
    print("\n详细列表:")
    for i, char in enumerate(split_chars, 1):
        print(f"  {i}. '{char}' (ASCII: {ord(char) if len(char) == 1 else 'N/A'})")
else:
    print("未找到feature_split_chars配置")

conn.close()
