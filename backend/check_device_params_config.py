#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查看设备参数配置
"""

import sqlite3
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_device_params_config():
    """查看设备参数配置"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询 device_params
        cursor.execute("SELECT config_value FROM configs WHERE config_key = 'device_params'")
        result = cursor.fetchone()
        
        if result:
            config_data = json.loads(result[0])
            print("设备参数配置 (device_params):")
            print("=" * 80)
            print(f"数据类型: {type(config_data)}")
            print(f"设备类型数量: {len(config_data)}")
            print("\n设备类型列表:")
            print("-" * 80)
            
            for device_type, config in config_data.items():
                print(f"\n设备类型: {device_type}")
                print(f"  配置: {json.dumps(config, indent=2, ensure_ascii=False)}")
        else:
            print("未找到 device_params 配置")
        
        conn.close()
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_device_params_config()
