#!/usr/bin/env python3
"""
检查设备参数配置显示问题
"""

import json

# 读取配置文件
with open('data/static_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 检查 device_params
device_params = config.get('device_params', {})

print("=" * 60)
print("设备参数配置检查")
print("=" * 60)

print(f"\n设备类型总数: {len(device_params)}")
print("\n设备类型列表:")

for device_type, config_data in device_params.items():
    params = config_data.get('params', [])
    keywords = config_data.get('keywords', [])
    
    print(f"\n  {device_type}:")
    print(f"    - 关键词数量: {len(keywords)}")
    print(f"    - 参数数量: {len(params)}")
    
    if params:
        print(f"    - 参数列表:")
        for i, param in enumerate(params[:3], 1):  # 只显示前3个
            print(f"      {i}. {param.get('name', '未命名')} ({'必填' if param.get('required') else '选填'})")
        if len(params) > 3:
            print(f"      ... 还有 {len(params) - 3} 个参数")

print("\n" + "=" * 60)
print("检查完成")
print("=" * 60)

# 检查前端可能遇到的问题
print("\n可能的问题:")

# 1. 检查是否有空的设备类型
empty_types = [dt for dt, cfg in device_params.items() if not cfg.get('params')]
if empty_types:
    print(f"  ⚠️  发现 {len(empty_types)} 个没有参数的设备类型:")
    for dt in empty_types[:5]:
        print(f"    - {dt}")
else:
    print("  ✓ 所有设备类型都有参数配置")

# 2. 检查数据结构
print("\n数据结构检查:")
sample_type = list(device_params.keys())[0] if device_params else None
if sample_type:
    sample_config = device_params[sample_type]
    print(f"  示例设备类型: {sample_type}")
    print(f"  配置结构: {list(sample_config.keys())}")
    if sample_config.get('params'):
        sample_param = sample_config['params'][0]
        print(f"  参数结构: {list(sample_param.keys())}")
