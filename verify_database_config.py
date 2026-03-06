#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证数据库中的配置"""
import sqlite3
import json

print("="*80)
print("验证数据库中的传感器配置")
print("="*80)

conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 1. 检查白名单特征
print("\n【白名单特征】")
cursor.execute("SELECT config_value FROM configs WHERE config_key = 'whitelist_features'")
result = cursor.fetchone()
if result:
    config = json.loads(result[0])
    features = config.get('whitelist_features', [])
    print(f"✅ 数量: {len(features)}")
    
    # 检查传感器相关特征
    sensor_features = [f for f in features if any(k in f for k in ['co', 'pm', '温度', '湿度', '传感器', '霍尼韦尔'])]
    print(f"✅ 传感器相关特征: {len(sensor_features)}个")
    print(f"   示例: {sensor_features[:10]}")
else:
    print("❌ 未找到白名单配置")

# 2. 检查同义词映射
print("\n【同义词映射】")
cursor.execute("SELECT config_value FROM configs WHERE config_key = 'synonym_map'")
result = cursor.fetchone()
if result:
    config = json.loads(result[0])
    synonym_map = config.get('synonym_map', {})
    print(f"✅ 数量: {len(synonym_map)}组")
    
    # 检查传感器相关同义词
    sensor_synonyms = {k: v for k, v in synonym_map.items() if any(word in k for word in ['传感器', 'co', 'co2', 'pm', '温度', '温湿度'])}
    print(f"✅ 传感器相关同义词: {len(sensor_synonyms)}组")
    for k, v in list(sensor_synonyms.items())[:5]:
        print(f"   {k}: {v}")
else:
    print("❌ 未找到同义词映射配置")

# 3. 检查设备类型关键词
print("\n【设备类型关键词】")
cursor.execute("SELECT config_value FROM configs WHERE config_key = 'device_type_keywords'")
result = cursor.fetchone()
if result:
    config = json.loads(result[0])
    keywords = config.get('device_type_keywords', [])
    print(f"✅ 数量: {len(keywords)}个")
    
    # 检查传感器相关关键词
    sensor_keywords = [k for k in keywords if '传感器' in k or 'CO' in k or 'PM' in k]
    print(f"✅ 传感器相关关键词: {len(sensor_keywords)}个")
    print(f"   {sensor_keywords}")
else:
    print("❌ 未找到设备类型关键词配置")

# 4. 检查设备参数配置
print("\n【设备参数配置】")
cursor.execute("SELECT config_value FROM configs WHERE config_key = 'device_params_config'")
result = cursor.fetchone()
if result:
    config = json.loads(result[0])
    params_config = config.get('device_params_config', {})
    print(f"✅ 设备类型数量: {len(params_config)}")
    
    for device_type, type_config in params_config.items():
        param_count = len(type_config.get('params', []))
        print(f"\n   【{device_type}】- {param_count}个参数")
        for param in type_config.get('params', [])[:3]:
            required = "必填" if param.get('required') else "可选"
            options = param.get('options', [])
            options_str = f", 选项: {len(options)}个" if options else ""
            print(f"     - {param['name']} ({required}{options_str})")
else:
    print("❌ 未找到设备参数配置")

conn.close()

print("\n" + "="*80)
print("✅ 验证完成！")
print("="*80)
print("\n现在可以：")
print("1. 刷新配置管理页面（F5或Ctrl+R）")
print("2. 在设备参数配置中应该能看到5种传感器类型")
print("3. 在特征白名单中应该能看到传感器相关特征")
print("4. 在同义词映射中应该能看到传感器相关同义词")
print("\n")
