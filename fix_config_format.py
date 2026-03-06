#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修正配置格式
将嵌套的配置格式改为正确的格式
"""
import sqlite3
import json

print("="*80)
print("修正配置格式")
print("="*80)

conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 1. 修正 whitelist_features
print("\n【步骤1】修正白名单特征格式...")
cursor.execute('SELECT config_value FROM configs WHERE config_key = "whitelist_features"')
result = cursor.fetchone()

if result:
    data = json.loads(result[0])
    # 当前格式: {"whitelist_features": [...]}
    # 应该是: [...]
    if isinstance(data, dict) and 'whitelist_features' in data:
        correct_data = data['whitelist_features']
        cursor.execute('UPDATE configs SET config_value = ? WHERE config_key = "whitelist_features"',
                     (json.dumps(correct_data, ensure_ascii=False),))
        print(f"  ✅ 已修正，包含 {len(correct_data)} 个特征")
    else:
        print(f"  ℹ️  格式已正确")
else:
    print("  ❌ 未找到配置")

# 2. 修正 synonym_map
print("\n【步骤2】修正同义词映射格式...")
cursor.execute('SELECT config_value FROM configs WHERE config_key = "synonym_map"')
result = cursor.fetchone()

if result:
    data = json.loads(result[0])
    # 当前格式: {"synonym_map": {...}}
    # 应该是: {...}
    if isinstance(data, dict) and 'synonym_map' in data:
        correct_data = data['synonym_map']
        cursor.execute('UPDATE configs SET config_value = ? WHERE config_key = "synonym_map"',
                     (json.dumps(correct_data, ensure_ascii=False),))
        print(f"  ✅ 已修正，包含 {len(correct_data)} 组同义词")
    else:
        print(f"  ℹ️  格式已正确")
else:
    print("  ❌ 未找到配置")

# 3. 修正 device_params_config 并合并到 device_params
print("\n【步骤3】将传感器参数配置合并到 device_params...")

# 读取现有的 device_params
cursor.execute('SELECT config_value FROM configs WHERE config_key = "device_params"')
result = cursor.fetchone()
device_params = json.loads(result[0]) if result else {}

# 读取 device_params_config
cursor.execute('SELECT config_value FROM configs WHERE config_key = "device_params_config"')
result = cursor.fetchone()

if result:
    data = json.loads(result[0])
    # 当前格式: {"device_params_config": {...}}
    # 需要提取并转换为 device_params 格式
    if isinstance(data, dict) and 'device_params_config' in data:
        sensor_params = data['device_params_config']
        
        # 转换格式
        for device_type, config in sensor_params.items():
            params_list = config.get('params', [])
            
            # 转换参数格式
            converted_params = []
            for param in params_list:
                converted_param = {
                    "name": param['name'],
                    "data_type": param.get('type', 'string'),
                    "required": param.get('required', False),
                    "unit": param.get('unit', ''),
                    "hint": '/'.join(param.get('options', [])) if param.get('options') else param.get('default', '')
                }
                converted_params.append(converted_param)
            
            # 添加到 device_params
            device_params[device_type] = {
                "keywords": [device_type],
                "params": converted_params
            }
            print(f"  ✅ 添加 {device_type}（{len(converted_params)}个参数）")
        
        # 更新 device_params
        cursor.execute('UPDATE configs SET config_value = ? WHERE config_key = "device_params"',
                     (json.dumps(device_params, ensure_ascii=False),))
        
        print(f"\n  ✅ 已将传感器配置合并到 device_params")
        print(f"  ✅ device_params 现在包含 {len(device_params)} 种设备类型")
    else:
        print("  ℹ️  格式已正确或无需处理")
else:
    print("  ❌ 未找到 device_params_config")

# 提交更改
conn.commit()

# 4. 验证修正结果
print("\n【步骤4】验证修正结果...")

# 验证 whitelist_features
cursor.execute('SELECT config_value FROM configs WHERE config_key = "whitelist_features"')
result = cursor.fetchone()
if result:
    data = json.loads(result[0])
    if isinstance(data, list):
        print(f"  ✅ whitelist_features: 列表格式，{len(data)}项")
        print(f"     示例: {data[:5]}")
    else:
        print(f"  ❌ whitelist_features: 格式错误")

# 验证 synonym_map
cursor.execute('SELECT config_value FROM configs WHERE config_key = "synonym_map"')
result = cursor.fetchone()
if result:
    data = json.loads(result[0])
    if isinstance(data, dict) and 'synonym_map' not in data:
        print(f"  ✅ synonym_map: 字典格式，{len(data)}项")
        sensor_synonyms = {k: v for k, v in data.items() if '传感器' in k or 'co' in k.lower()}
        print(f"     传感器相关: {len(sensor_synonyms)}项")
        for k, v in list(sensor_synonyms.items())[:3]:
            print(f"       {k}: {v}")
    else:
        print(f"  ❌ synonym_map: 格式错误")

# 验证 device_params
cursor.execute('SELECT config_value FROM configs WHERE config_key = "device_params"')
result = cursor.fetchone()
if result:
    data = json.loads(result[0])
    sensor_types = [k for k in data.keys() if '传感器' in k or 'CO' in k]
    print(f"  ✅ device_params: {len(data)}种设备类型")
    print(f"     传感器类型: {sensor_types}")

conn.close()

print("\n" + "="*80)
print("✅ 配置格式修正完成！")
print("="*80)
print("\n下一步操作：")
print("1. 刷新配置管理页面")
print("2. 检查配置是否正确显示")
print("\n")
