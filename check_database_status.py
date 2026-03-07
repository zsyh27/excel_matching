import sqlite3
import json

def check_database_status(db_path='data/devices.db'):
    """
    检查数据库状态
    
    这个脚本会检查：
    1. 所有表及其记录数
    2. 设备类型分布
    3. 品牌分布
    4. 设备表结构
    5. 示例设备数据
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 80)
    print("数据库状态检查")
    print("=" * 80)

    # 1. 检查所有表
    print("\n【1】数据库表列表:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(f"  - {table[0]}")

    # 2. 检查设备数量
    print("\n【2】设备数量:")
    cursor.execute("SELECT COUNT(*) FROM devices")
    device_count = cursor.fetchone()[0]
    print(f"  总设备数: {device_count}")

    # 3. 检查设备类型分布
    print("\n【3】设备类型分布:")
    cursor.execute("SELECT device_type, COUNT(*) FROM devices GROUP BY device_type")
    type_distribution = cursor.fetchall()
    for device_type, count in type_distribution:
        print(f"  - {device_type}: {count}")

    # 4. 检查品牌分布
    print("\n【4】品牌分布:")
    cursor.execute("SELECT brand, COUNT(*) FROM devices GROUP BY brand")
    brand_distribution = cursor.fetchall()
    for brand, count in brand_distribution:
        print(f"  - {brand}: {count}")

    # 5. 检查规则表（如果存在）
    print("\n【5】规则表检查:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%rule%'")
    rule_tables = cursor.fetchall()
    if rule_tables:
        for table in rule_tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} 条记录")
    else:
        print("  ⚠️ 未找到规则表")

    # 6. 检查配置表
    print("\n【6】配置表检查:")
    cursor.execute("SELECT COUNT(*) FROM configs")
    config_count = cursor.fetchone()[0]
    print(f"  配置项数量: {config_count}")
    
    cursor.execute("SELECT config_key FROM configs ORDER BY config_key")
    configs = cursor.fetchall()
    print("  配置项列表:")
    for i, config in enumerate(configs, 1):
        print(f"    {i}. {config[0]}")

    # 7. 检查设备表结构
    print("\n【7】设备表结构:")
    cursor.execute("PRAGMA table_info(devices)")
    columns = cursor.fetchall()
    print("  列名及类型:")
    for col in columns:
        print(f"    - {col[1]} ({col[2]})")

    # 8. 检查示例设备
    print("\n【8】示例设备（前3个）:")
    cursor.execute("SELECT * FROM devices LIMIT 3")
    devices = cursor.fetchall()
    for i, device in enumerate(devices, 1):
        print(f"\n  设备 {i}:")
        for j, col in enumerate(columns):
            value = device[j]
            col_name = col[1]
            
            # 特殊处理JSON字段
            if col_name == 'key_params' and value:
                try:
                    params = json.loads(value)
                    print(f"    {col_name}: {json.dumps(params, ensure_ascii=False)[:100]}...")
                except:
                    print(f"    {col_name}: {str(value)[:50]}...")
            elif isinstance(value, str) and len(value) > 50:
                print(f"    {col_name}: {value[:50]}...")
            else:
                print(f"    {col_name}: {value}")

    conn.close()

    print("\n" + "=" * 80)
    print("检查完成")
    print("=" * 80)

if __name__ == '__main__':
    check_database_status()
