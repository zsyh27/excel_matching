#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库中的特征权重配置
"""

import sqlite3
import json
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_weight_config():
    """检查数据库中的权重配置"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')
    
    print(f"数据库路径: {db_path}")
    print(f"数据库存在: {os.path.exists(db_path)}")
    print("-" * 80)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询 feature_weight_config
        cursor.execute("SELECT config_key, config_value FROM configs WHERE config_key = 'feature_weight_config'")
        result = cursor.fetchone()
        
        if result:
            config_key, config_value = result
            print(f"配置键: {config_key}")
            print(f"配置值（原始）: {config_value}")
            print("-" * 80)
            
            # 解析JSON
            try:
                config_data = json.loads(config_value)
                print("配置值（解析后）:")
                print(json.dumps(config_data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
        else:
            print("未找到 feature_weight_config 配置")
            print("查询所有配置键:")
            cursor.execute("SELECT config_key FROM configs")
            all_keys = cursor.fetchall()
            for key in all_keys:
                print(f"  - {key[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_weight_config()
