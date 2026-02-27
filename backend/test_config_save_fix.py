#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试配置保存修复

验证配置保存后能正确同步到数据库
"""

import json
import sqlite3
import os
import sys

def test_config_save():
    """测试配置保存"""
    print("=" * 80)
    print("配置保存修复测试")
    print("=" * 80)
    
    # 1. 读取JSON配置
    config_file = 'data/static_config.json'
    print(f"\n1. 读取JSON配置: {config_file}")
    with open(config_file, 'r', encoding='utf-8') as f:
        json_config = json.load(f)
    
    print(f"   ✓ JSON配置项数量: {len(json_config)}")
    
    # 2. 读取数据库配置
    db_file = 'data/devices.db'
    print(f"\n2. 读取数据库配置: {db_file}")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT config_key, config_value FROM configs")
    db_rows = cursor.fetchall()
    conn.close()
    
    db_config = {}
    for config_key, config_value in db_rows:
        db_config[config_key] = json.loads(config_value)
    
    print(f"   ✓ 数据库配置项数量: {len(db_config)}")
    
    # 3. 比较配置
    print(f"\n3. 比较JSON和数据库配置:")
    
    # 检查JSON中有但数据库中没有的
    missing_in_db = []
    for key in json_config:
        if key not in db_config:
            missing_in_db.append(key)
    
    if missing_in_db:
        print(f"   ✗ 数据库中缺失的配置项: {missing_in_db}")
        return False
    else:
        print(f"   ✓ 数据库包含所有JSON配置项")
    
    # 检查关键配置项的值是否一致
    print(f"\n4. 验证关键配置项:")
    
    # 测试 feature_weight_config
    if 'feature_weight_config' in json_config:
        json_val = json_config['feature_weight_config']
        db_val = db_config.get('feature_weight_config')
        
        if json_val == db_val:
            print(f"   ✓ feature_weight_config 一致")
            print(f"     - brand_weight: {json_val.get('brand_weight')}")
            print(f"     - model_weight: {json_val.get('model_weight')}")
            print(f"     - device_type_weight: {json_val.get('device_type_weight')}")
            print(f"     - parameter_weight: {json_val.get('parameter_weight')}")
        else:
            print(f"   ✗ feature_weight_config 不一致")
            print(f"     JSON: {json_val}")
            print(f"     DB:   {db_val}")
            return False
    
    # 测试 metadata_keywords
    if 'metadata_keywords' in json_config:
        json_val = json_config['metadata_keywords']
        db_val = db_config.get('metadata_keywords')
        
        if json_val == db_val:
            print(f"   ✓ metadata_keywords 一致 (共 {len(json_val)} 个)")
        else:
            print(f"   ✗ metadata_keywords 不一致")
            print(f"     JSON长度: {len(json_val)}")
            print(f"     DB长度:   {len(db_val) if db_val else 0}")
            return False
    
    # 测试 global_config
    if 'global_config' in json_config:
        json_val = json_config['global_config']
        db_val = db_config.get('global_config')
        
        if json_val == db_val:
            print(f"   ✓ global_config 一致")
            print(f"     - min_feature_length: {json_val.get('min_feature_length')}")
            print(f"     - min_feature_length_chinese: {json_val.get('min_feature_length_chinese')}")
        else:
            print(f"   ✗ global_config 不一致")
            return False
    
    print("\n" + "=" * 80)
    print("✓ 所有测试通过！JSON和数据库配置完全一致")
    print("=" * 80)
    return True

if __name__ == '__main__':
    try:
        success = test_config_save()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
