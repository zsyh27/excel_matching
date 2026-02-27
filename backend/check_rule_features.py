# -*- coding: utf-8 -*-
import sqlite3
import json
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查找温度传感器的规则
cursor.execute("SELECT rule_id, target_device_id, auto_extracted_features, feature_weights FROM rules WHERE target_device_id LIKE 'HST-RA%' LIMIT 1")
row = cursor.fetchone()

if row:
    print("规则详情:")
    print(f"Rule ID: {row[0]}")
    print(f"Device ID: {row[1]}")
    print(f"\n自动提取的特征 (auto_extracted_features):")
    features = json.loads(row[2])
    print(json.dumps(features, ensure_ascii=False, indent=2))
    print(f"\n特征权重 (feature_weights):")
    weights = json.loads(row[3])
    print(json.dumps(weights, ensure_ascii=False, indent=2))

conn.close()
