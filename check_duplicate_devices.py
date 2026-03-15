import sqlite3

conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 查找重复的设备
cursor.execute("""
SELECT device_id, device_name, spec_model, COUNT(*) as cnt 
FROM devices
GROUP BY device_id, device_name, spec_model
HAVING cnt > 1
ORDER BY cnt DESC
LIMIT 5
""")

for row in cursor.fetchall():
    print(f"设备ID: {row[0]}, 名称: {row[1]}, 型号: {row[2]}, 重复次数: {row[3]}")
