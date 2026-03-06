#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查看设备类型关键词配置
"""

import sqlite3
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_device_type_config():
    """查看设备类型关键词配置"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询 device_type_keywords
        cursor.execute("SELECT config_value FROM configs WHERE config_key = 'device_type_keywords'")
        result = cursor.fetchone()
        
        if result:
            config_data = json.loads(result[0])
            print("设备类型关键词配置:")
            print("=" * 80)
            if isinstance(config_data, list):
                print(f"总计: {len(config_data)} 个关键词")
                print(f"关键词列表: {config_data}")
            elif isinstance(config_data, dict):
                for device_type, keywords in config_data.items():
                    print(f"\n设备类型: {device_type}")
                    print(f"  关键词: {keywords}")
        else:
            print("未找到 device_type_keywords 配置")
        
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_device_type_config()
