import sqlite3
import json

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 查询设备
cursor.execute("SELECT device_id, device_name, key_params FROM devices WHERE device_id = 'FIELD_0796672C'")
result = cursor.fetchone()

if result:
    print(f"设备ID: {result[0]}")
    print(f"设备名称: {result[1]}")
    print(f"\nkey_params 原始数据:")
    key_params = json.loads(result[2]) if result[2] else {}
    for name, value in key_params.items():
        print(f"  {name}: {value}")

conn.close()
