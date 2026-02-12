"""
从数据库中删除 JSON 文件中的模拟设备数据
只保留真实的设备数据
"""

import json
import sqlite3
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def remove_json_devices():
    """从数据库中删除 JSON 文件中的设备"""
    
    # 1. 读取 JSON 文件中的设备 ID
    json_file = '../data/static_device.json'
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_devices = json.load(f)
        json_device_ids = [d['device_id'] for d in json_devices]
        print(f"📋 JSON 文件中有 {len(json_device_ids)} 个模拟设备")
        print(f"   设备ID示例: {json_device_ids[:5]}")
    except Exception as e:
        print(f"❌ 读取 JSON 文件失败: {e}")
        return
    
    # 2. 连接数据库
    db_file = '../data/devices.db'
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        print(f"\n✅ 连接数据库成功: {db_file}")
    except Exception as e:
        print(f"❌ 连接数据库失败: {e}")
        return
    
    # 3. 查询数据库中的设备总数
    cursor.execute("SELECT COUNT(*) FROM devices")
    total_before = cursor.fetchone()[0]
    print(f"\n📊 删除前数据库中有 {total_before} 个设备")
    
    # 4. 查询有多少 JSON 设备在数据库中
    placeholders = ','.join(['?' for _ in json_device_ids])
    cursor.execute(f"SELECT COUNT(*) FROM devices WHERE device_id IN ({placeholders})", json_device_ids)
    json_devices_in_db = cursor.fetchone()[0]
    print(f"   其中 {json_devices_in_db} 个是 JSON 模拟设备")
    
    # 5. 显示将要删除的设备
    cursor.execute(f"SELECT device_id, brand, device_name FROM devices WHERE device_id IN ({placeholders}) LIMIT 10", json_device_ids)
    sample_devices = cursor.fetchall()
    print(f"\n将要删除的设备示例（前10个）:")
    for device_id, brand, device_name in sample_devices:
        print(f"  - {device_id}: {brand} {device_name}")
    
    # 6. 确认删除
    print(f"\n⚠️  准备删除 {json_devices_in_db} 个 JSON 模拟设备")
    print(f"   删除后将剩余 {total_before - json_devices_in_db} 个真实设备")
    
    confirm = input("\n确认删除？(yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ 取消删除操作")
        conn.close()
        return
    
    # 7. 删除设备（会自动级联删除关联的规则）
    try:
        cursor.execute(f"DELETE FROM devices WHERE device_id IN ({placeholders})", json_device_ids)
        deleted_devices = cursor.rowcount
        
        # 提交事务
        conn.commit()
        
        print(f"\n✅ 成功删除 {deleted_devices} 个设备")
        
        # 8. 验证删除结果
        cursor.execute("SELECT COUNT(*) FROM devices")
        total_after = cursor.fetchone()[0]
        print(f"📊 删除后数据库中有 {total_after} 个设备")
        
        cursor.execute("SELECT COUNT(*) FROM rules")
        total_rules = cursor.fetchone()[0]
        print(f"📊 当前有 {total_rules} 条规则")
        
        # 9. 显示剩余设备示例
        cursor.execute("SELECT device_id, brand, device_name FROM devices LIMIT 5")
        remaining_devices = cursor.fetchall()
        print(f"\n剩余设备示例（前5个）:")
        for device_id, brand, device_name in remaining_devices:
            print(f"  - {device_id}: {brand} {device_name}")
        
        print(f"\n✅ 清理完成！数据库现在只包含 {total_after} 个真实设备")
        
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("="*60)
    print("从数据库中删除 JSON 模拟设备")
    print("="*60)
    remove_json_devices()
