#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库状态
"""

import sqlite3
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database():
    """检查数据库状态"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')
    
    print("=" * 80)
    print("数据库状态检查")
    print("=" * 80)
    print(f"数据库路径: {db_path}")
    print(f"数据库存在: {os.path.exists(db_path)}")
    print("-" * 80)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"数据库表: {', '.join(tables)}")
        print("-" * 80)
        
        # 检查设备数量
        cursor.execute("SELECT COUNT(*) FROM devices")
        device_count = cursor.fetchone()[0]
        print(f"设备数量: {device_count}")
        
        # 检查规则数量
        cursor.execute("SELECT COUNT(*) FROM rules")
        rule_count = cursor.fetchone()[0]
        print(f"规则数量: {rule_count}")
        
        # 检查配置数量
        cursor.execute("SELECT COUNT(*) FROM configs")
        config_count = cursor.fetchone()[0]
        print(f"配置数量: {config_count}")
        
        print("-" * 80)
        
        # 如果有设备，显示前3个
        if device_count > 0:
            print("前3个设备:")
            cursor.execute("SELECT device_id, brand, device_name, device_type FROM devices LIMIT 3")
            for row in cursor.fetchall():
                device_id, brand, device_name, device_type = row
                print(f"  {device_id}: {brand} {device_name} ({device_type})")
        
        # 如果有规则，显示前3个
        if rule_count > 0:
            print("\n前3个规则:")
            cursor.execute("SELECT rule_id, target_device_id FROM rules LIMIT 3")
            for row in cursor.fetchall():
                rule_id, target_device_id = row
                print(f"  {rule_id} -> {target_device_id}")
        
        # 显示所有配置
        print("\n所有配置:")
        cursor.execute("SELECT config_key FROM configs")
        for row in cursor.fetchall():
            print(f"  - {row[0]}")
        
        conn.close()
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_database()
