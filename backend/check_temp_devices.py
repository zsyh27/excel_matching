# -*- coding: utf-8 -*-
import sqlite3
import json

import os
db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查找温度相关的设备
cursor.execute("SELECT device_id, brand, device_name, spec_model, detailed_params FROM devices WHERE device_name LIKE '%温度%' LIMIT 3")
rows = cursor.fetchall()

print("温度相关设备:")
for row in rows:
    print(json.dumps({
        'device_id': row[0],
        'brand': row[1],
        'device_name': row[2],
        'spec_model': row[3],
        'detailed_params': row[4]
    }, ensure_ascii=False, indent=2))
    print("-" * 80)

conn.close()
