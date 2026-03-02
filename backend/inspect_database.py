"""
检查 devices.db 数据库的结构和数据
"""

import sqlite3
import os

def inspect_database():
    """检查数据库结构和数据"""
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')
    
    print("=" * 80)
    print("数据库检查")
    print("=" * 80)
    print(f"\n数据库路径: {db_path}")
    print(f"数据库存在: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("\n✗ 数据库文件不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 查看所有表
        print("\n" + "=" * 80)
        print("1. 数据库表列表")
        print("=" * 80)
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print(f"\n共有 {len(tables)} 个表:")
        for i, (table_name,) in enumerate(tables, 1):
            print(f"  {i}. {table_name}")
        
        # 2. 查看每个表的结构和数据统计
        for (table_name,) in tables:
            print("\n" + "=" * 80)
            print(f"表: {table_name}")
            print("=" * 80)
            
            # 表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("\n字段列表:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, is_pk = col
                pk_marker = " [主键]" if is_pk else ""
                null_marker = " [NOT NULL]" if not_null else ""
                default_marker = f" [默认值: {default_val}]" if default_val is not None else ""
                print(f"  - {col_name}: {col_type}{pk_marker}{null_marker}{default_marker}")
            
            # 数据统计
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\n数据行数: {count}")
            
            # 显示前5条数据
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()
                
                print(f"\n前 {min(5, count)} 条数据:")
                col_names = [col[1] for col in columns]
                
                # 打印表头
                print("\n  " + " | ".join(col_names))
                print("  " + "-" * (len(" | ".join(col_names))))
                
                # 打印数据行
                for row in rows:
                    # 截断过长的字段
                    truncated_row = []
                    for val in row:
                        if val is None:
                            truncated_row.append("NULL")
                        elif isinstance(val, str) and len(val) > 50:
                            truncated_row.append(val[:47] + "...")
                        else:
                            truncated_row.append(str(val))
                    print("  " + " | ".join(truncated_row))
        
        # 3. 特别关注 devices 表
        if any(t[0] == 'devices' for t in tables):
            print("\n" + "=" * 80)
            print("3. devices 表详细信息")
            print("=" * 80)
            
            # 统计品牌分布
            cursor.execute("SELECT brand, COUNT(*) as count FROM devices GROUP BY brand ORDER BY count DESC LIMIT 10")
            brands = cursor.fetchall()
            
            print("\n品牌分布（前10）:")
            for brand, count in brands:
                print(f"  - {brand}: {count} 个设备")
            
            # 统计设备名称分布
            cursor.execute("SELECT device_name, COUNT(*) as count FROM devices GROUP BY device_name ORDER BY count DESC LIMIT 10")
            device_names = cursor.fetchall()
            
            print("\n设备名称分布（前10）:")
            for device_name, count in device_names:
                print(f"  - {device_name}: {count} 个设备")
            
            # 查看最近添加的设备（前5）
            cursor.execute("SELECT device_id, device_name, brand, spec_model FROM devices LIMIT 5")
            recent_devices = cursor.fetchall()
            
            print("\n设备示例（前5）:")
            for device_id, device_name, brand, spec_model in recent_devices:
                print(f"  - ID: {device_id}")
                print(f"    名称: {device_name}")
                print(f"    品牌: {brand}")
                print(f"    规格型号: {spec_model}")
                print()
        
        # 4. 特别关注 rules 表
        if any(t[0] == 'rules' for t in tables):
            print("\n" + "=" * 80)
            print("4. rules 表详细信息")
            print("=" * 80)
            
            # 统计规则数量
            cursor.execute("SELECT COUNT(*) FROM rules")
            rule_count = cursor.fetchone()[0]
            print(f"\n规则总数: {rule_count}")
            
            # 查看最近添加的规则
            cursor.execute("SELECT rule_id, target_device_id, auto_extracted_features, match_threshold FROM rules LIMIT 5")
            recent_rules = cursor.fetchall()
            
            print("\n规则示例（前5）:")
            for rule_id, device_id, features, threshold in recent_rules:
                print(f"  - 规则ID: {rule_id}")
                print(f"    设备ID: {device_id}")
                print(f"    特征: {features[:100]}..." if len(features) > 100 else f"    特征: {features}")
                print(f"    匹配阈值: {threshold}")
                print()
        
        # 5. 特别关注 configs 表（不是 config）
        if any(t[0] == 'configs' for t in tables):
            print("\n" + "=" * 80)
            print("5. configs 表详细信息")
            print("=" * 80)
            
            # 查看所有配置项
            cursor.execute("SELECT config_key, config_value, description FROM configs ORDER BY config_key")
            configs = cursor.fetchall()
            
            print(f"\n配置项总数: {len(configs)}")
            print("\n配置项列表:")
            for key, value, description in configs:
                # 截断过长的值
                if len(value) > 100:
                    value_display = value[:97] + "..."
                else:
                    value_display = value
                print(f"  - {key}:")
                print(f"    描述: {description}")
                print(f"    值: {value_display}")
                print()
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("数据库检查完成")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    inspect_database()
