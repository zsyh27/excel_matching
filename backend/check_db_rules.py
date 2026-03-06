"""
检查数据库中的规则数据
"""
import sqlite3
import json

conn = sqlite3.connect('../data/devices.db')
cursor = conn.cursor()

# 获取最后一条规则
cursor.execute('SELECT rule_id, target_device_id, feature_weights FROM rules LIMIT 1')
row = cursor.fetchone()

if row:
    print("=" * 80)
    print("数据库中的规则数据")
    print("=" * 80)
    print(f"规则ID: {row[0]}")
    print(f"目标设备ID: {row[1]}")
    print(f"特征权重(原始): {row[2]}")
    print(f"特征权重(类型): {type(row[2])}")
    
    # 尝试解析JSON
    try:
        weights = json.loads(row[2])
        print(f"\n解析后的特征权重:")
        print(json.dumps(weights, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"\n解析失败: {e}")

conn.close()
