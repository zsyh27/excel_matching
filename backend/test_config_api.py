# -*- coding: utf-8 -*-
"""
测试配置API
"""

import requests
import json

# 测试获取配置
response = requests.get('http://localhost:5000/api/config')
print("状态码:", response.status_code)
print("\n响应数据:")

if response.status_code == 200:
    data = response.json()
    print("success:", data.get('success'))
    
    if 'config' in data:
        config = data['config']
        print("\n配置键列表:")
        for key in config.keys():
            print(f"  - {key}")
        
        print("\n各配置项的类型:")
        for key, value in config.items():
            print(f"  - {key}: {type(value).__name__}")
        
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
                elif isinstance(value, dict):
                    print(f"    类型: dict, 键数量: {len(value)}")
                else:
                    print(f"    类型: {type(value).__name__}")
    else:
        print("响应中没有 'config' 字段")
        print("完整响应:", json.dumps(data, indent=2, ensure_ascii=False))
else:
    print("请求失败")
    print("响应内容:", response.text)
