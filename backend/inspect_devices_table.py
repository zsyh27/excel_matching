"""
检查devices表结构和数据
"""
import sqlite3
import json

# 连接数据库
conn = sqlite3.connect('../data/devices.db')
cursor = conn.cursor()

# 获取表结构
print("=" * 80)
print("devices表结构：")
print("=" * 80)
cursor.execute("PRAGMA table_info(devices)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]:20s} {col[2]:15s} {'NOT NULL' if col[3] else 'NULL':10s} {'PRIMARY KEY' if col[5] else ''}")

# 获取数据样本
print("\n" + "=" * 80)
print("数据样本（前5条）：")
print("=" * 80)
cursor.execute("SELECT * FROM devices LIMIT 5")
rows = cursor.fetchall()

# 获取列名
column_names = [description[0] for description in cursor.description]

for i, row in enumerate(rows, 1):
    print(f"\n设备 {i}:")
    for col_name, value in zip(column_names, row):
        if col_name == 'detailed_params' and value:
            print(f"  {col_name}:")
            # 尝试解析详细参数
            if value.startswith('{'):
                try:
                    params = json.loads(value)
                    for k, v in params.items():
                        print(f"    {k}: {v}")
                except:
                    print(f"    {value[:100]}...")
            else:
                print(f"    {value[:100]}...")
        else:
            print(f"  {col_name}: {value}")

# 统计信息
print("\n" + "=" * 80)
print("统计信息：")
print("=" * 80)
cursor.execute("SELECT COUNT(*) FROM devices")
total = cursor.fetchone()[0]
print(f"总设备数: {total}")

cursor.execute("SELECT COUNT(DISTINCT brand) FROM devices")
brands = cursor.fetchone()[0]
print(f"品牌数: {brands}")

cursor.execute("SELECT COUNT(DISTINCT device_name) FROM devices")
device_types = cursor.fetchone()[0]
print(f"设备类型数: {device_types}")

# 检查字段填充情况
print("\n字段填充率：")
for col in columns:
    col_name = col[1]
    cursor.execute(f"SELECT COUNT(*) FROM devices WHERE {col_name} IS NOT NULL AND {col_name} != ''")
    filled = cursor.fetchone()[0]
    rate = (filled / total * 100) if total > 0 else 0
    print(f"  {col_name:20s}: {filled:4d}/{total:4d} ({rate:5.1f}%)")

conn.close()
