import sqlite3

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 查询符合条件的设备数量
cursor.execute("SELECT COUNT(*) FROM devices WHERE device_type LIKE '%空气质量%' OR device_type LIKE '%PM%'")
count = cursor.fetchone()[0]
print(f"符合条件的设备数量: {count}")

# 查询前20个设备
cursor.execute("SELECT device_id, device_name, device_type FROM devices WHERE device_type LIKE '%空气质量%' OR device_type LIKE '%PM%' LIMIT 20")
devices = cursor.fetchall()

print(f"\n设备列表:")
for i, d in enumerate(devices):
    print(f"  #{i+1} {d[1]} ({d[2]})")

conn.close()
