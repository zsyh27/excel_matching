#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查数据库中的配置"""
import sys
import os
import json
import sqlite3

print("="*80)
print("检查数据库中的配置")
print("="*80)

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 查询配置表
print("\n【配置表内容】")
cursor.execute("SELECT key, value FROM config ORDER BY key")
configs = cursor.fetchall()

if configs:
    print(f"找到 {len(configs)} 条配置记录:\n")
    for config in configs:
        key = config[0]
        value_str = config[1]
        
        # 尝试解析JSON
        try:
            value = json.loads(value_str)
            if isinstance(value, dict):
                print(f"【{key}】")
                if key == 'whitelist_features':
                    print(f"  类型: 列表")
                    print(f"  数量: {len(value.get('whitelist_features', []))}")
                    print(f"  示例: {value.get('whitelist_features', [])[:5]}")
                elif key == 'synonym_map':
                    print(f"  类型: 字典")
                    print(f"  数量: {len(value.get('synonym_map', {}))}")
                    print(f"  示例: {list(value.get('synonym_map', {}).items())[:3]}")
                elif key == 'device_type_keywords':
                    print(f"  类型: 列表")
                    print(f"  数量: {len(value.get('device_type_keywords', []))}")
                    print(f"  示例: {value.get('device_type_keywords', [])[:5]}")
                elif key == 'device_params_config':
                    print(f"  类型: 字典")
                    print(f"  设备类型数量: {len(value.get('device_params_config', {}))}")
                    print(f"  设备类型: {list(value.get('device_params_config', {}).keys())}")
                else:
                    print(f"  内容: {str(value)[:100]}...")
                print()
        except:
            print(f"【{key}】")
            print(f"  值: {value_str[:100]}...")
            print()
else:
    print("❌ 配置表为空！")

# 检查是否需要从JSON文件导入配置
print("\n" + "="*80)
print("检查JSON配置文件")
print("="*80)

json_config_path = 'data/static_config.json'
if os.path.exists(json_config_path):
    with open(json_config_path, 'r', encoding='utf-8') as f:
        json_config = json.load(f)
    
    print(f"\n✅ JSON配置文件存在")
    print(f"  白名单特征: {len(json_config.get('whitelist_features', []))}")
    print(f"  同义词映射: {len(json_config.get('synonym_map', {}))}")
    print(f"  设备类型关键词: {len(json_config.get('device_type_keywords', []))}")
else:
    print("\n❌ JSON配置文件不存在")

# 检查设备参数配置文件
params_config_path = 'data/sensor_params_config.json'
if os.path.exists(params_config_path):
    with open(params_config_path, 'r', encoding='utf-8') as f:
        params_config = json.load(f)
    
    print(f"\n✅ 设备参数配置文件存在")
    print(f"  设备类型数量: {len(params_config)}")
    print(f"  设备类型: {list(params_config.keys())}")
else:
    print("\n❌ 设备参数配置文件不存在")

print("\n" + "="*80)
print("结论")
print("="*80)
print("\n配置脚本只更新了JSON文件，但系统从数据库读取配置。")
print("需要将JSON文件中的配置导入到数据库中。")
print("\n")

conn.close()
