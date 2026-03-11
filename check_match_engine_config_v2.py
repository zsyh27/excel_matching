#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查匹配引擎配置 v2"""

import sys
sys.path.insert(0, 'backend')
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
import json

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("🔍 检查匹配引擎配置 v2...")

try:
    # 加载配置
    config = db_loader.load_config()
    
    print(f"配置加载成功，共 {len(config)} 项配置")
    
    # 列出所有配置键
    print(f"\n所有配置键:")
    for key in sorted(config.keys()):
        print(f"  {key}")
    
    # 检查特征权重配置
    feature_weight_config = config.get('feature_weight_config', {})
    print(f"\n特征权重配置:")
    for key, value in feature_weight_config.items():
        print(f"  {key}: {value}")
    
    # 检查设备类型关键词
    device_type_keywords = config.get('device_type_keywords', {})
    print(f"\n设备类型关键词配置:")
    print(f"  类型: {type(device_type_keywords)}")
    
    if isinstance(device_type_keywords, dict):
        print(f"  配置项数量: {len(device_type_keywords)}")
        # 检查智能照明设备相关配置
        lighting_keywords = device_type_keywords.get('智能照明设备', [])
        print(f"  智能照明设备关键词: {lighting_keywords}")
    elif isinstance(device_type_keywords, list):
        print(f"  配置项数量: {len(device_type_keywords)}")
        print(f"  前5项: {device_type_keywords[:5]}")
    
    # 检查品牌关键词
    brand_keywords = config.get('brand_keywords', {})
    print(f"\n品牌关键词配置:")
    print(f"  类型: {type(brand_keywords)}")
    
    if isinstance(brand_keywords, dict):
        print(f"  配置项数量: {len(brand_keywords)}")
        honeywell_keywords = brand_keywords.get('霍尼韦尔', [])
        print(f"  霍尼韦尔关键词: {honeywell_keywords}")
    
    # 检查设备参数配置
    device_params = config.get('device_params', {})
    if device_params and 'device_types' in device_params:
        lighting_params = device_params['device_types'].get('智能照明设备', {})
        print(f"\n智能照明设备参数配置:")
        print(f"  关键词: {lighting_params.get('keywords', [])}")
        print(f"  参数数量: {len(lighting_params.get('params', []))}")
    
    # 检查匹配阈值设置
    print(f"\n查找匹配阈值设置...")
    
    # 可能的阈值配置键
    threshold_keys = ['threshold', 'match_threshold', 'matching_threshold', 'default_threshold']
    
    for key in threshold_keys:
        if key in config:
            print(f"  找到阈值配置 {key}: {config[key]}")
    
    # 检查是否有匹配相关的配置
    matching_keys = [key for key in config.keys() if 'match' in key.lower() or 'threshold' in key.lower()]
    print(f"\n匹配相关配置键: {matching_keys}")
    
    for key in matching_keys:
        print(f"  {key}: {config[key]}")

except Exception as e:
    print(f"❌ 检查配置时出错: {e}")
    import traceback
    traceback.print_exc()