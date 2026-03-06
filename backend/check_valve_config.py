#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查电动调节阀配置
"""

import sqlite3
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 读取device_params配置
cursor.execute("SELECT config_value FROM configs WHERE config_key = 'device_params'")
result = cursor.fetchone()

if result:
    config = json.loads(result[0])
    if "电动调节阀" in config:
        valve_config = config["电动调节阀"]
        print("电动调节阀配置:")
        print("=" * 80)
        print(f"关键词: {valve_config['keywords']}")
        print(f"\n参数列表 (共{len(valve_config['params'])}个):")
        print("-" * 80)
        for i, param in enumerate(valve_config['params'], 1):
            required_mark = "✓" if param['required'] else " "
            print(f"{i}. [{required_mark}] {param['name']:<15} {param['hint']}")
    else:
        print("未找到电动调节阀配置")
else:
    print("未找到device_params配置")

conn.close()
