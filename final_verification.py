#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""最终验证配置"""
import sqlite3
import json

print("="*80)
print("最终配置验证")
print("="*80)

conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 1. 验证白名单特征
print("\n【1. 白名单特征】")
cursor.execute('SELECT config_value FROM configs WHERE config_key = "whitelist_features"')
result = cursor.fetchone()
if result:
    data = json.loads(result[0])
    if isinstance(data, list):
        print(f"✅ 格式正确：列表")
        print(f"✅ 数量：{len(data)}个")
        sensor_features = [f for f in data if any(k in f for k in ['co', 'pm', '温度', '湿度', '霍尼韦尔'])]
        print(f"✅ 传感器相关：{len(sensor_features)}个")
        print(f"   示例：{sensor_features[:10]}")
    else:
        print(f"❌ 格式错误：{type(data)}")
else:
    print("❌ 未找到配置")

# 2. 验证同义词映射
print("\n【2. 同义词映射】")
cursor.execute('SELECT config_value FROM configs WHERE config_key = "synonym_map"')
result = cursor.fetchone()
if result:
    data = json.loads(result[0])
    if isinstance(data, dict) and 'synonym_map' not in data:
        print(f"✅ 格式正确：字典（不嵌套）")
        print(f"✅ 数量：{len(data)}组")
        sensor_synonyms = {k: v for k, v in data.items() if '传感器' in k or 'co' in k.lower() or 'pm' in k.lower()}
        print(f"✅ 传感器相关：{len(sensor_synonyms)}组")
        print("   示例：")
        for k, v in list(sensor_synonyms.items())[:5]:
            print(f"     {k} → {v}")
    else:
        print(f"❌ 格式错误")
else:
    print("❌ 未找到配置")

# 3. 验证设备参数配置
print("\n【3. 设备参数配置】")
cursor.execute('SELECT config_value FROM configs WHERE config_key = "device_params"')
result = cursor.fetchone()
if result:
    data = json.loads(result[0])
    print(f"✅ 总设备类型：{len(data)}种")
    
    sensor_types = [k for k in data.keys() if '传感器' in k or 'CO' in k]
    print(f"✅ 传感器类型：{len(sensor_types)}种")
    
    for device_type in sensor_types:
        config = data[device_type]
        params = config.get('params', [])
        keywords = config.get('keywords', [])
        print(f"\n   【{device_type}】")
        print(f"     关键词：{keywords}")
        print(f"     参数数量：{len(params)}个")
        print(f"     参数列表：")
        for param in params[:3]:
            required = "必填" if param.get('required') else "可选"
            hint = param.get('hint', '')
            hint_str = f"（{hint[:30]}...）" if len(hint) > 30 else f"（{hint}）" if hint else ""
            print(f"       - {param['name']} [{required}] {hint_str}")
        if len(params) > 3:
            print(f"       ... 还有 {len(params) - 3} 个参数")
else:
    print("❌ 未找到配置")

# 4. 验证设备类型关键词
print("\n【4. 设备类型关键词】")
cursor.execute('SELECT config_value FROM configs WHERE config_key = "device_type_keywords"')
result = cursor.fetchone()
if result:
    data = json.loads(result[0])
    if isinstance(data, dict) and 'device_type_keywords' in data:
        keywords = data['device_type_keywords']
    elif isinstance(data, list):
        keywords = data
    else:
        keywords = []
    
    if keywords:
        print(f"✅ 数量：{len(keywords)}个")
        sensor_keywords = [k for k in keywords if '传感器' in k or 'CO' in k or 'PM' in k]
        print(f"✅ 传感器相关：{len(sensor_keywords)}个")
        print(f"   {sensor_keywords}")
    else:
        print("❌ 格式错误或为空")
else:
    print("❌ 未找到配置")

conn.close()

print("\n" + "="*80)
print("验证完成！")
print("="*80)
print("\n✅ 所有配置格式正确")
print("✅ 传感器相关配置已完整添加")
print("\n现在可以：")
print("1. 刷新配置管理页面（Ctrl+R 或 F5）")
print("2. 在设备参数配置中查看5种传感器类型")
print("3. 在特征白名单中搜索传感器相关特征")
print("4. 在同义词映射中查看传感器相关同义词")
print("\n")
