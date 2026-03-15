import sqlite3

conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 检查devices表的结构
cursor.execute("PRAGMA table_info(devices)")
columns = cursor.fetchall()
print("设备表字段:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# 检查是否有价格相关的字段
cursor.execute("SELECT device_id, device_name, brand, spec_model FROM devices LIMIT 1")
row = cursor.fetchone()
print(f"\n示例设备:")
print(f"  ID: {row[0]}")
print(f"  名称: {row[1]}")
print(f"  品牌: {row[2]}")
print(f"  型号: {row[3]}")

conn.close()
