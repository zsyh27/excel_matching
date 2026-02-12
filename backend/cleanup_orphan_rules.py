"""
清理数据库中的孤立规则（没有对应设备的规则）
"""

import sqlite3

def cleanup_orphan_rules():
    """清理孤立规则"""
    
    db_file = '../data/devices.db'
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    print("="*60)
    print("清理孤立规则")
    print("="*60)
    
    # 1. 查询总规则数
    cursor.execute("SELECT COUNT(*) FROM rules")
    total_rules = cursor.fetchone()[0]
    print(f"\n📊 当前规则总数: {total_rules}")
    
    # 2. 查询孤立规则（target_device_id 不在 devices 表中）
    cursor.execute("""
        SELECT COUNT(*) 
        FROM rules 
        WHERE target_device_id NOT IN (SELECT device_id FROM devices)
    """)
    orphan_count = cursor.fetchone()[0]
    print(f"   其中孤立规则: {orphan_count}")
    
    if orphan_count == 0:
        print("\n✅ 没有孤立规则，数据库状态良好")
        conn.close()
        return
    
    # 3. 显示孤立规则示例
    cursor.execute("""
        SELECT rule_id, target_device_id 
        FROM rules 
        WHERE target_device_id NOT IN (SELECT device_id FROM devices)
        LIMIT 10
    """)
    orphan_rules = cursor.fetchall()
    print(f"\n孤立规则示例（前10个）:")
    for rule_id, device_id in orphan_rules:
        print(f"  - {rule_id} -> {device_id}")
    
    # 4. 确认删除
    print(f"\n⚠️  准备删除 {orphan_count} 条孤立规则")
    confirm = input("确认删除？(yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ 取消删除操作")
        conn.close()
        return
    
    # 5. 删除孤立规则
    try:
        cursor.execute("""
            DELETE FROM rules 
            WHERE target_device_id NOT IN (SELECT device_id FROM devices)
        """)
        deleted_count = cursor.rowcount
        conn.commit()
        
        print(f"\n✅ 成功删除 {deleted_count} 条孤立规则")
        
        # 6. 验证结果
        cursor.execute("SELECT COUNT(*) FROM rules")
        remaining_rules = cursor.fetchone()[0]
        print(f"📊 剩余规则数: {remaining_rules}")
        
        cursor.execute("SELECT COUNT(*) FROM devices")
        total_devices = cursor.fetchone()[0]
        print(f"📊 设备总数: {total_devices}")
        
        print(f"\n✅ 清理完成！")
        
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    cleanup_orphan_rules()
