# -*- coding: utf-8 -*-
"""
数据库迁移脚本：添加配置历史表

用于存储配置的历史版本，支持配置回滚功能
"""

import sqlite3
import os
import sys

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')


def add_config_history_table():
    """添加配置历史表"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查表是否已存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='config_history'
        """)
        
        if cursor.fetchone():
            print("配置历史表已存在，跳过创建")
            return True
        
        # 创建配置历史表
        cursor.execute("""
            CREATE TABLE config_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version INTEGER NOT NULL UNIQUE,
                config_data TEXT NOT NULL,
                remark TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX idx_config_history_version 
            ON config_history(version)
        """)
        
        cursor.execute("""
            CREATE INDEX idx_config_history_created_at 
            ON config_history(created_at)
        """)
        
        conn.commit()
        print("✓ 配置历史表创建成功")
        
        # 验证表结构
        cursor.execute("PRAGMA table_info(config_history)")
        columns = cursor.fetchall()
        print("\n表结构:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ 创建配置历史表失败: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("数据库迁移：添加配置历史表")
    print("=" * 60)
    print(f"数据库路径: {DB_PATH}")
    print()
    
    if not os.path.exists(DB_PATH):
        print(f"✗ 数据库文件不存在: {DB_PATH}")
        sys.exit(1)
    
    success = add_config_history_table()
    
    print()
    print("=" * 60)
    if success:
        print("迁移完成！")
    else:
        print("迁移失败！")
    print("=" * 60)
