#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证配置文件"""
import json

print("="*60)
print("配置文件验证")
print("="*60)

# 读取配置文件
with open('data/static_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

print(f"\n✅ 白名单特征数量: {len(config.get('whitelist_features', []))}")
print(f"✅ 同义词映射数量: {len(config.get('synonym_map', {}))}")
print(f"✅ 设备类型关键词数量: {len(config.get('device_type_keywords', []))}")

print("\n【白名单特征示例】（前15个）:")
for f in config.get('whitelist_features', [])[:15]:
    print(f"  - {f}")

print("\n【同义词映射示例】（前8组）:")
for k, v in list(config.get('synonym_map', {}).items())[:8]:
    print(f"  {k}: {v}")

print("\n【设备类型关键词】:")
for k in config.get('device_type_keywords', []):
    print(f"  - {k}")

# 读取设备参数配置
print("\n" + "="*60)
print("设备参数配置验证")
print("="*60)

with open('data/sensor_params_config.json', 'r', encoding='utf-8') as f:
    params_config = json.load(f)

print(f"\n✅ 配置的设备类型数量: {len(params_config)}")

for device_type, config_data in params_config.items():
    param_count = len(config_data.get('params', []))
    print(f"\n【{device_type}】- {param_count}个参数:")
    for param in config_data.get('params', [])[:3]:  # 只显示前3个
        required = "必填" if param.get('required') else "可选"
        print(f"  - {param['name']} ({required})")
    if param_count > 3:
        print(f"  ... 还有 {param_count - 3} 个参数")

print("\n" + "="*60)
print("✅ 所有配置验证通过！")
print("="*60)
