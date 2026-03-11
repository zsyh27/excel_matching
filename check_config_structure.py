#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查配置结构

查看 intelligent_extraction 配置的实际结构
"""

import sys
sys.path.insert(0, 'backend')

import json
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

def check_config_structure():
    """检查配置结构"""
    
    print("=" * 80)
    print("检查配置结构")
    print("=" * 80)
    
    # 初始化数据库
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    
    # 加载配置
    config = db_loader.load_config()
    
    if not config:
        print("❌ 配置加载失败")
        return
    
    print(f"\n✅ 配置加载成功，共 {len(config)} 个配置项")
    
    # 检查 intelligent_extraction 配置
    ie_config = config.get('intelligent_extraction')
    
    if not ie_config:
        print("\n❌ intelligent_extraction 配置不存在")
        return
    
    print(f"\n✅ intelligent_extraction 配置存在")
    print(f"\nintelligent_extraction 配置的键:")
    for key in ie_config.keys():
        print(f"  - {key}")
    
    # 详细打印配置结构
    print(f"\nintelligent_extraction 完整配置:")
    print(json.dumps(ie_config, ensure_ascii=False, indent=2))
    
    # 检查数据库中的原始配置
    print("\n" + "=" * 80)
    print("检查数据库中的原始配置")
    print("=" * 80)
    
    with db_manager.session_scope() as session:
        from modules.models import Config as ConfigModel
        
        ie_config_db = session.query(ConfigModel).filter_by(
            config_key='intelligent_extraction'
        ).first()
        
        if ie_config_db:
            print(f"\n✅ 数据库中存在 intelligent_extraction 配置")
            print(f"\n配置值类型: {type(ie_config_db.config_value)}")
            
            config_value = ie_config_db.config_value
            
            if isinstance(config_value, str):
                config_value = json.loads(config_value)
            
            print(f"\n数据库中的配置键:")
            for key in config_value.keys():
                print(f"  - {key}")
            
            print(f"\n数据库中的完整配置:")
            print(json.dumps(config_value, ensure_ascii=False, indent=2))
        else:
            print("\n❌ 数据库中没有 intelligent_extraction 配置")


if __name__ == '__main__':
    try:
        check_config_structure()
    except Exception as e:
        print(f"\n❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
