#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试配置结构
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Config
import json

def debug_config():
    db = DatabaseManager('sqlite:///data/devices.db')
    
    with db.session_scope() as session:
        # 查询所有配置
        configs = session.query(Config).all()
        
        print("="*60)
        print("数据库中的所有配置")
        print("="*60)
        print(f"\n总配置数: {len(configs)}\n")
        
        for config in configs:
            print(f"配置键: {config.config_key}")
            print(f"描述: {config.description}")
            
            # 检查config_value的类型
            value = config.config_value
            print(f"值类型: {type(value)}")
            
            if isinstance(value, dict):
                print(f"字典键: {list(value.keys())}")
                
                # 如果是device_params，详细显示
                if config.config_key == 'device_params':
                    print("\n--- device_params 详细结构 ---")
                    for key, val in value.items():
                        if isinstance(val, dict):
                            print(f"  {key}: {len(val)} 项")
                            if key == 'device_types':
                                print(f"    设备类型: {list(val.keys())}")
                        elif isinstance(val, list):
                            print(f"  {key}: {len(val)} 项")
                        else:
                            print(f"  {key}: {val}")
            elif isinstance(value, str):
                print(f"字符串长度: {len(value)}")
                try:
                    parsed = json.loads(value)
                    print(f"解析后类型: {type(parsed)}")
                    print(f"解析后键: {list(parsed.keys()) if isinstance(parsed, dict) else 'N/A'}")
                except:
                    print("无法解析为JSON")
            
            print("-"*60)
            print()

if __name__ == '__main__':
    debug_config()
