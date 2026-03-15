#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""直接修复CO₂ - 使用原始SQL"""

import sys
import sqlite3
import json

print("=" * 80)
print("直接修复CO₂（使用SQL）")
print("=" * 80)

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# CO₂的各种变体
co2_variants = ['CO₂', 'Co₂', 'co₂', 'CO2', 'Co2', 'co2']

# 查询所有空气质量传感器
cursor.execute("SELECT device_id, key_params FROM devices WHERE device_type = '空气质量传感器'")
devices = cursor.fetchall()

print(f"找到 {len(devices)} 个设备\n")

updated_count = 0

for device_id, key_params_json in devices:
    if key_params_json:
        key_params = json.loads(key_params_json)
        updated = False
        
        for param_name, param_data in key_params.items():
            if isinstance(param_data, dict) and 'value' in param_data:
                original = param_data['value']
                if isinstance(original, str):
                    new_value = original
                    for variant in co2_variants:
                        new_value = new_value.replace(variant, '二氧化碳')
                    
                    if new_value != original:
                        key_params[param_name]['value'] = new_value
                        updated = True
                        print(f"更新: {device_id} - {param_name}")
        
        if updated:
            # 更新数据库
            new_json = json.dumps(key_params, ensure_ascii=False)
            cursor.execute(
                "UPDATE devices SET key_params = ?, updated_at = datetime('now') WHERE device_id = ?",
                (new_json, device_id)
            )
            updated_count += 1

# 提交更改
conn.commit()
print(f"\n✅ 提交成功，更新了 {updated_count} 个设备")

# 验证
cursor.execute("SELECT device_id, key_params FROM devices WHERE device_type = '空气质量传感器'")
devices = cursor.fetchall()

co2_count = 0
for device_id, key_params_json in devices:
    if key_params_json:
        key_params = json.loads(key_params_json)
        for param_data in key_params.values():
            if isinstance(param_data, dict) and 'value' in param_data:
                value_str = str(param_data['value'])
                if any(variant in value_str for variant in co2_variants):
                    co2_count += 1

print(f"\n验证：仍包含CO₂的参数数: {co2_count}")

if co2_count == 0:
    print("✅ 所有CO₂已成功替换为二氧化碳")
else:
    print("⚠️  仍有CO₂未替换")

conn.close()

print("=" * 80)
print("修复完成")
print("=" * 80)
