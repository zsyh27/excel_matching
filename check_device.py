import sqlite3

conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 查找包含"室内空气质量传感器"的设备
cursor.execute("SELECT device_id, spec_model, device_name FROM devices WHERE device_name LIKE '%空气质量%' LIMIT 10")
rows = cursor.fetchall()
print(f"Found {len(rows)} devices with 空气质量:")
for row in rows:
    print(f'  {row[0]} | {row[1]} | {row[2]}')

# 查找包含"二氧化碳"的设备
cursor.execute("SELECT device_id, spec_model, device_name FROM devices WHERE device_name LIKE '%二氧化碳%' LIMIT 10")
rows = cursor.fetchall()
print(f"\nFound {len(rows)} devices with 二氧化碳:")
for row in rows:
    print(f'  {row[0]} | {row[1]} | {row[2]}')

# 查看device_id包含FIELD的设备
cursor.execute("SELECT device_id, spec_model, device_name FROM devices WHERE device_id LIKE 'FIELD%' LIMIT 10")
rows = cursor.fetchall()
print(f"\nFound {len(rows)} devices with FIELD:")
for row in rows:
    print(f'  {row[0]} | {row[1]} | {row[2]}')

conn.close()
