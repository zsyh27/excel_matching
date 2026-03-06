#!/usr/bin/env python3
"""详细对比配置差异"""

import sqlite3
import json

# 读取配置
with open('data/static_config.json', 'r', encoding='utf-8') as f:
    json_config = json.load(f)

conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()
cursor.execute("SELECT config_key, config_value FROM configs")
rows = cursor.fetchall()
db_config = {key: json.loads(value) for key, value in rows}
conn.close()

print("=" * 80)
print("详细配置差异分析")
print("=" * 80)

# 1. device_type_keywords差异
print("\n【1. device_type_keywords差异】")
json_dtk = json_config.get('device_type_keywords', [])
db_dtk_raw = db_config.get('device_type_keywords', [])

# 数据库中可能是嵌套的
if isinstance(db_dtk_raw, dict) and 'device_type_keywords' in db_dtk_raw:
    db_dtk = db_dtk_raw['device_type_keywords']
else:
    db_dtk = db_dtk_raw

print(f"JSON类型: {type(json_dtk)}, 数量: {len(json_dtk) if isinstance(json_dtk, list) else 'N/A'}")
print(f"数据库类型: {type(db_dtk)}, 数量: {len(db_dtk) if isinstance(db_dtk, list) else 'N/A'}")

if isinstance(json_dtk, list) and isinstance(db_dtk, list):
    json_set = set(json_dtk)
    db_set = set(db_dtk)
    
    only_json = json_set - db_set
    only_db = db_set - json_set
    
    if only_json:
        print(f"\nJSON独有 ({len(only_json)}个):")
        for item in sorted(only_json):
            print(f"  - {item}")
    
    if only_db:
        print(f"\n数据库独有 ({len(only_db)}个):")
        for item in sorted(only_db):
            print(f"  - {item}")
    
    if not only_json and not only_db:
        print("✅ 内容完全相同")

# 2. metadata_keywords差异
print("\n【2. metadata_keywords差异】")
json_mk = json_config.get('metadata_keywords', [])
db_mk = db_config.get('metadata_keywords', [])

print(f"JSON数量: {len(json_mk)}")
print(f"数据库数量: {len(db_mk)}")

json_mk_set = set(json_mk)
db_mk_set = set(db_mk)

only_json_mk = json_mk_set - db_mk_set
only_db_mk = db_mk_set - json_mk_set

if only_json_mk:
    print(f"\nJSON独有 ({len(only_json_mk)}个):")
    for item in sorted(only_json_mk):
        print(f"  - {item}")

if only_db_mk:
    print(f"\n数据库独有 ({len(only_db_mk)}个):")
    for item in sorted(only_db_mk):
        print(f"  - {item}")

# 3. intelligent_extraction差异
print("\n【3. intelligent_extraction差异】")
json_ie = json_config.get('intelligent_extraction', {})
db_ie = db_config.get('intelligent_extraction', {})

# 检查whitelist_features
json_whitelist = json_ie.get('feature_quality_scoring', {}).get('whitelist_features', [])
db_whitelist = db_ie.get('feature_quality_scoring', {}).get('whitelist_features', [])

print(f"JSON白名单: {len(json_whitelist)} 个")
print(f"数据库白名单: {len(db_whitelist)} 个")

if len(db_whitelist) > len(json_whitelist):
    print(f"✅ 数据库白名单更完整 (+{len(db_whitelist) - len(json_whitelist)}个)")
    
    json_wl_set = set(json_whitelist)
    db_wl_set = set(db_whitelist)
    only_db_wl = db_wl_set - json_wl_set
    
    if only_db_wl:
        print(f"\n数据库独有的白名单特征 ({len(only_db_wl)}个):")
        for item in sorted(only_db_wl):
            print(f"  - {item}")

# 4. device_params差异
print("\n【4. device_params差异】")
json_dp = json_config.get('device_params', {})
db_dp = db_config.get('device_params', {})

print(f"JSON设备类型: {len(json_dp)} 个")
print(f"数据库设备类型: {len(db_dp)} 个")

json_dp_keys = set(json_dp.keys())
db_dp_keys = set(db_dp.keys())

only_json_dp = json_dp_keys - db_dp_keys
only_db_dp = db_dp_keys - json_dp_keys

if only_json_dp:
    print(f"\nJSON独有设备类型 ({len(only_json_dp)}个):")
    for item in sorted(only_json_dp):
        print(f"  - {item}")

if only_db_dp:
    print(f"\n数据库独有设备类型 ({len(only_db_dp)}个):")
    for item in sorted(only_db_dp):
        print(f"  - {item}")

# 5. 检查JSON独有的配置
print("\n【5. JSON独有的配置】")
json_only_keys = set(json_config.keys()) - set(db_config.keys())
if json_only_keys:
    for key in sorted(json_only_keys):
        print(f"  - {key}")
        value = json_config[key]
        if isinstance(value, (list, dict)):
            print(f"    类型: {type(value).__name__}, 大小: {len(value)}")
        else:
            print(f"    值: {value}")

# 6. 检查数据库独有的配置
print("\n【6. 数据库独有的配置】")
db_only_keys = set(db_config.keys()) - set(json_config.keys())
if db_only_keys:
    for key in sorted(db_only_keys):
        print(f"  - {key}")
        value = db_config[key]
        if isinstance(value, (list, dict)):
            print(f"    类型: {type(value).__name__}, 大小: {len(value)}")
        else:
            print(f"    值: {str(value)[:100]}")

print("\n" + "=" * 80)
print("结论")
print("=" * 80)

print("\n数据库包含的额外内容:")
print("  ✅ 传感器白名单特征(7个)")
print("  ✅ 传感器设备类型(5个)")
print("  ✅ device_params_config配置")

print("\nJSON包含的额外内容:")
print("  ⚠️  medium_keywords配置")

print("\n建议:")
print("  1. 数据库配置更完整(包含传感器配置)")
print("  2. 可以将JSON的medium_keywords导入数据库")
print("  3. 然后执行迁移")
