#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试配置路径问题

检查智能提取API使用的配置路径
"""

import sys
sys.path.insert(0, 'backend')

import json
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

def debug_config_path():
    """调试配置路径"""
    
    print("=" * 80)
    print("调试配置路径问题")
    print("=" * 80)
    
    # 初始化数据库
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    
    # 加载配置
    config = db_loader.load_config()
    
    print("\n1. 检查 extraction_rules 路径:")
    extraction_rules = config.get('extraction_rules', {})
    print(f"   extraction_rules 存在: {bool(extraction_rules)}")
    if extraction_rules:
        print(f"   extraction_rules 的键: {list(extraction_rules.keys())}")
        device_type_config = extraction_rules.get('device_type', {})
        print(f"   extraction_rules.device_type 存在: {bool(device_type_config)}")
        if device_type_config:
            print(f"   extraction_rules.device_type 的键: {list(device_type_config.keys())}")
    else:
        print("   ❌ extraction_rules 不存在！")
    
    print("\n2. 检查 intelligent_extraction 路径:")
    ie_config = config.get('intelligent_extraction', {})
    print(f"   intelligent_extraction 存在: {bool(ie_config)}")
    if ie_config:
        print(f"   intelligent_extraction 的键: {list(ie_config.keys())}")
        device_type_recognition = ie_config.get('device_type_recognition', {})
        print(f"   intelligent_extraction.device_type_recognition 存在: {bool(device_type_recognition)}")
        if device_type_recognition:
            print(f"   intelligent_extraction.device_type_recognition 的键: {list(device_type_recognition.keys())}")
            print(f"   设备类型数量: {len(device_type_recognition.get('device_types', []))}")
            print(f"   前缀关键词数量: {len(device_type_recognition.get('prefix_keywords', {}))}")
            print(f"   主类型数量: {len(device_type_recognition.get('main_types', {}))}")
    
    print("\n3. 问题分析:")
    print("   IntelligentExtractionAPI 使用的路径:")
    print("   - extraction_config = config.get('extraction_rules', {})")
    print("   - device_type_config = extraction_config.get('device_type', {})")
    print("   - 完整路径: config['extraction_rules']['device_type']")
    
    print("\n   实际配置存储的路径:")
    print("   - config['intelligent_extraction']['device_type_recognition']")
    
    print("\n   ❌ 路径不匹配！这就是为什么无法识别设备类型的原因！")
    
    print("\n4. 解决方案:")
    print("   需要修改 IntelligentExtractionAPI 的初始化代码，使用正确的配置路径")
    
    # 检查是否有 extraction_rules 配置
    print("\n5. 检查数据库中的配置键:")
    with db_manager.session_scope() as session:
        from modules.models import Config as ConfigModel
        
        all_configs = session.query(ConfigModel).all()
        config_keys = [c.config_key for c in all_configs]
        
        print(f"   数据库中的配置键数量: {len(config_keys)}")
        print(f"   是否有 extraction_rules: {'extraction_rules' in config_keys}")
        print(f"   是否有 intelligent_extraction: {'intelligent_extraction' in config_keys}")
        
        if 'extraction_rules' in config_keys:
            extraction_rules_config = session.query(ConfigModel).filter_by(
                config_key='extraction_rules'
            ).first()
            print(f"\n   extraction_rules 配置内容:")
            print(json.dumps(extraction_rules_config.config_value, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        debug_config_path()
    except Exception as e:
        print(f"\n❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
