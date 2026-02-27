# -*- coding: utf-8 -*-
"""
同步JSON配置文件到数据库

将static_config.json中的配置同步到数据库的configs表
"""

import sqlite3
import json
import os
import sys

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'static_config.json')
DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')

def sync_config_to_database():
    """同步配置到数据库"""
    
    # 1. 读取JSON配置文件
    print(f"读取配置文件: {CONFIG_FILE}")
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print(f"配置项数量: {len(config)}")
    
    # 2. 连接数据库
    print(f"\n连接数据库: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 3. 同步每个配置项
    print("\n同步配置项:")
    synced_count = 0
    updated_count = 0
    
    for config_key, config_value in config.items():
        # 检查配置项是否已存在
        cursor.execute("SELECT config_key FROM configs WHERE config_key = ?", (config_key,))
        exists = cursor.fetchone() is not None
        
        # 转换为JSON字符串
        config_value_json = json.dumps(config_value, ensure_ascii=False)
        
        if exists:
            # 更新现有配置
            cursor.execute(
                "UPDATE configs SET config_value = ? WHERE config_key = ?",
                (config_value_json, config_key)
            )
            print(f"  ✓ 更新: {config_key}")
            updated_count += 1
        else:
            # 插入新配置
            cursor.execute(
                "INSERT INTO configs (config_key, config_value) VALUES (?, ?)",
                (config_key, config_value_json)
            )
            print(f"  + 新增: {config_key}")
            synced_count += 1
    
    # 4. 提交更改
    conn.commit()
    conn.close()
    
    print(f"\n同步完成:")
    print(f"  - 新增配置项: {synced_count}")
    print(f"  - 更新配置项: {updated_count}")
    print(f"  - 总计: {synced_count + updated_count}")
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("配置同步工具：JSON → 数据库")
    print("=" * 60)
    
    if not os.path.exists(CONFIG_FILE):
        print(f"✗ 配置文件不存在: {CONFIG_FILE}")
        sys.exit(1)
    
    if not os.path.exists(DB_FILE):
        print(f"✗ 数据库文件不存在: {DB_FILE}")
        sys.exit(1)
    
    try:
        sync_config_to_database()
        print("\n" + "=" * 60)
        print("同步成功！")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ 同步失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
