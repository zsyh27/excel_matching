#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将JSON配置文件导入到数据库
"""
import sqlite3
import json
import os

print("="*80)
print("将配置导入到数据库")
print("="*80)

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 1. 导入主配置文件
print("\n【步骤1】导入主配置文件...")
json_config_path = 'data/static_config.json'

if os.path.exists(json_config_path):
    with open(json_config_path, 'r', encoding='utf-8') as f:
        json_config = json.load(f)
    
    # 导入白名单特征
    if 'whitelist_features' in json_config:
        config_key = 'whitelist_features'
        config_value = json.dumps({'whitelist_features': json_config['whitelist_features']}, ensure_ascii=False)
        
        # 检查是否已存在
        cursor.execute("SELECT config_key FROM configs WHERE config_key = ?", (config_key,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute("UPDATE configs SET config_value = ?, description = ? WHERE config_key = ?",
                         (config_value, '特征白名单配置', config_key))
            print(f"  ✅ 更新白名单特征: {len(json_config['whitelist_features'])}个")
        else:
            cursor.execute("INSERT INTO configs (config_key, config_value, description) VALUES (?, ?, ?)",
                         (config_key, config_value, '特征白名单配置'))
            print(f"  ✅ 添加白名单特征: {len(json_config['whitelist_features'])}个")
    
    # 导入同义词映射
    if 'synonym_map' in json_config:
        config_key = 'synonym_map'
        config_value = json.dumps({'synonym_map': json_config['synonym_map']}, ensure_ascii=False)
        
        cursor.execute("SELECT config_key FROM configs WHERE config_key = ?", (config_key,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute("UPDATE configs SET config_value = ?, description = ? WHERE config_key = ?",
                         (config_value, '同义词映射配置', config_key))
            print(f"  ✅ 更新同义词映射: {len(json_config['synonym_map'])}组")
        else:
            cursor.execute("INSERT INTO configs (config_key, config_value, description) VALUES (?, ?, ?)",
                         (config_key, config_value, '同义词映射配置'))
            print(f"  ✅ 添加同义词映射: {len(json_config['synonym_map'])}组")
    
    # 导入设备类型关键词
    if 'device_type_keywords' in json_config:
        config_key = 'device_type_keywords'
        config_value = json.dumps({'device_type_keywords': json_config['device_type_keywords']}, ensure_ascii=False)
        
        cursor.execute("SELECT config_key FROM configs WHERE config_key = ?", (config_key,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute("UPDATE configs SET config_value = ?, description = ? WHERE config_key = ?",
                         (config_value, '设备类型关键词配置', config_key))
            print(f"  ✅ 更新设备类型关键词: {len(json_config['device_type_keywords'])}个")
        else:
            cursor.execute("INSERT INTO configs (config_key, config_value, description) VALUES (?, ?, ?)",
                         (config_key, config_value, '设备类型关键词配置'))
            print(f"  ✅ 添加设备类型关键词: {len(json_config['device_type_keywords'])}个")
else:
    print("  ❌ 主配置文件不存在")

# 2. 导入设备参数配置
print("\n【步骤2】导入设备参数配置...")
params_config_path = 'data/sensor_params_config.json'

if os.path.exists(params_config_path):
    with open(params_config_path, 'r', encoding='utf-8') as f:
        params_config = json.load(f)
    
    config_key = 'device_params_config'
    config_value = json.dumps({'device_params_config': params_config}, ensure_ascii=False)
    
    cursor.execute("SELECT config_key FROM configs WHERE config_key = ?", (config_key,))
    exists = cursor.fetchone()
    
    if exists:
        cursor.execute("UPDATE configs SET config_value = ?, description = ? WHERE config_key = ?",
                     (config_value, '设备参数配置', config_key))
        print(f"  ✅ 更新设备参数配置: {len(params_config)}种设备类型")
    else:
        cursor.execute("INSERT INTO configs (config_key, config_value, description) VALUES (?, ?, ?)",
                     (config_key, config_value, '设备参数配置'))
        print(f"  ✅ 添加设备参数配置: {len(params_config)}种设备类型")
    
    for device_type in params_config.keys():
        print(f"    - {device_type}")
else:
    print("  ❌ 设备参数配置文件不存在")

# 提交更改
conn.commit()

# 3. 验证导入结果
print("\n【步骤3】验证导入结果...")
cursor.execute("SELECT config_key, description FROM configs ORDER BY config_key")
configs = cursor.fetchall()

print(f"\n数据库中的配置项（共{len(configs)}个）:")
for config in configs:
    print(f"  - {config[0]}: {config[1]}")

conn.close()

print("\n" + "="*80)
print("✅ 配置导入完成！")
print("="*80)
print("\n下一步操作：")
print("1. 刷新配置管理页面")
print("2. 检查设备参数配置、白名单、同义词映射是否已更新")
print("3. 如果需要，可以在页面上进一步调整配置")
print("\n")
