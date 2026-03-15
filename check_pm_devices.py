import sqlite3
import json

conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 查找包含PM的设备
cursor.execute("""
SELECT device_id, device_name, key_params 
FROM devices 
WHERE key_params LIKE '%pm%' OR key_params LIKE '%PM%'
LIMIT 5
""")

print("包含PM的设备:")
for row in cursor.fetchall():
    print(f"\n设备: {row[1]}")
    key_params = json.loads(row[2]) if row[2] else {}
    for k, v in key_params.items():
        if 'pm' in str(v).lower() or 'pm' in k.lower():
            print(f"  {k}: {v}")

conn.close()
