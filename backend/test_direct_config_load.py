# -*- coding: utf-8 -*-
"""
直接测试配置文件加载
"""

import json
import os

config_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'static_config.json')

print(f"配置文件路径: {config_file}")
print(f"文件存在: {os.path.exists(config_file)}")

with open(config_file, 'r', encoding='utf-8') as f:
    config = json.load(f)

print("\n配置键列表:")
for key in config.keys():
    print(f"  - {key}")

# 检查我们需要的配置项
required_keys = [
    'ignore_keywords',
    'feature_split_chars',
    'synonym_map',
    'normalization_map',
    'global_config',
    'brand_keywords',
    'device_type_keywords'
]

print("\n必需配置项检查:")
for key in required_keys:
    exists = key in config
    print(f"  - {key}: {'✓ 存在' if exists else '✗ 缺失'}")
    if exists:
        value = config[key]
        if isinstance(value, list):
            print(f"    类型: list, 长度: {len(value)}")
            if len(value) > 0:
                print(f"    示例: {value[:3]}")
        elif isinstance(value, dict):
            print(f"    类型: dict, 键数量: {len(value)}")
            if len(value) > 0:
                keys = list(value.keys())[:3]
                print(f"    示例键: {keys}")
        else:
            print(f"    类型: {type(value).__name__}, 值: {value}")
