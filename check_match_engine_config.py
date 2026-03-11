#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查匹配引擎配置"""

import sys
sys.path.insert(0, 'backend')
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("🔍 检查匹配引擎配置...")

try:
    # 加载配置
    config = db_loader.load_config()
    
    print(f"配置加载成功，共 {len(config)} 项配置")
    
    # 检查匹配相关配置
    matching_config = config.get('matching', {})
    print(f"\n匹配配置:")
    print(f"  threshold: {matching_config.get('threshold', '未设置')}")
    print(f"  weights: {matching_config.get('weights', '未设置')}")
    
    # 检查特征权重配置
    feature_weight_config = config.get('feature_weight_config', {})
    print(f"\n特征权重配置:")
    for key, value in feature_weight_config.items():
        print(f"  {key}: {value}")
    
    # 检查设备类型关键词
    device_type_keywords = config.get('device_type_keywords', {})
    print(f"\n设备类型关键词配置:")
    print(f"  配置项数量: {len(device_type_keywords)}")
    
    # 检查智能照明设备相关配置
    lighting_keywords = device_type_keywords.get('智能照明设备', [])
    print(f"  智能照明设备关键词: {lighting_keywords}")
    
    # 检查品牌关键词
    brand_keywords = config.get('brand_keywords', {})
    print(f"\n品牌关键词配置:")
    print(f"  配置项数量: {len(brand_keywords)}")
    
    honeywell_keywords = brand_keywords.get('霍尼韦尔', [])
    print(f"  霍尼韦尔关键词: {honeywell_keywords}")
    
    # 检查同义词映射
    synonym_map = config.get('synonym_map', {})
    print(f"\n同义词映射配置:")
    print(f"  配置项数量: {len(synonym_map)}")
    
    # 检查设备参数配置
    device_params = config.get('device_params', {})
    if device_params and 'device_types' in device_params:
        lighting_params = device_params['device_types'].get('智能照明设备', {})
        print(f"\n智能照明设备参数配置:")
        print(f"  关键词: {lighting_params.get('keywords', [])}")
        print(f"  参数数量: {len(lighting_params.get('params', []))}")
    
    # 检查全局配置
    global_config = config.get('global_config', {})
    print(f"\n全局配置:")
    for key, value in global_config.items():
        print(f"  {key}: {value}")

except Exception as e:
    print(f"❌ 检查配置时出错: {e}")
    import traceback
    traceback.print_exc()