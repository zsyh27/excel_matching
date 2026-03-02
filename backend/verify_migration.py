#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证数据库迁移结果"""

import sqlite3
from pathlib import Path

def verify_migration():
    """验证迁移结果"""
    db_path = Path(__file__).parent.parent / 'data' / 'devices.db'
    
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("="*60)
    print("数据库迁移验证")
    print("="*60)
    
    # 检查表结构
    cursor.execute("PRAGMA table_info(devices)")
    columns = cursor.fetchall()
    
    print("\n表结构:")
    for col in columns:
        col_id, name, col_type, not_null, default_val, pk = col
        print(f"  - {name}: {col_type} (NOT NULL: {bool(not_null)}, PK: {bool(pk)})")
    
    # 检查必需字段
    column_names = [col[1] for col in columns]
    required_columns = ['raw_description', 'key_params', 'confidence_score']
    
    print("\n必需字段检查:")
    all_present = True
    for col in required_columns:
        if col in column_names:
            print(f"  ✅ {col}")
        else:
            print(f"  ❌ {col} (缺失)")
            all_present = False
    
    # 检查索引
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='devices'")
    indexes = cursor.fetchall()
    
    print("\n索引:")
    for idx in indexes:
        print(f"  - {idx[0]}")
    
    # 检查必需索引
    index_names = [idx[0] for idx in indexes]
    required_indexes = ['idx_devices_device_type', 'idx_devices_brand', 'idx_devices_confidence_score']
    
    print("\n必需索引检查:")
    all_indexes_present = True
    for idx in required_indexes:
        if idx in index_names:
            print(f"  ✅ {idx}")
        else:
            print(f"  ❌ {idx} (缺失)")
            all_indexes_present = False
    
    # 数据统计
    cursor.execute("SELECT COUNT(*) FROM devices")
    total_count = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT 
            COUNT(raw_description) as has_raw_desc,
            COUNT(key_params) as has_key_params,
            COUNT(confidence_score) as has_confidence
        FROM devices
    """)
    stats = cursor.fetchone()
    
    print(f"\n数据统计:")
    print(f"  - 总记录数: {total_count}")
    print(f"  - 有 raw_description: {stats[0]}")
    print(f"  - 有 key_params: {stats[1]}")
    print(f"  - 有 confidence_score: {stats[2]}")
    
    conn.close()
    
    print("\n" + "="*60)
    if all_present and all_indexes_present:
        print("✅ 迁移验证成功！所有字段和索引都已正确创建。")
        return True
    else:
        print("❌ 迁移验证失败！存在缺失的字段或索引。")
        return False

if __name__ == '__main__':
    verify_migration()
