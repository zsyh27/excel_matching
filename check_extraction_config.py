import sqlite3, json

conn = sqlite3.connect('data/devices.db')
cur = conn.cursor()
cur.execute("SELECT config_value FROM configs WHERE config_key='intelligent_extraction'")
row = cur.fetchone()
if row:
    cfg = json.loads(row[0])
    dtr = cfg.get('device_type_recognition', {})
    print('device_types 数量:', len(dtr.get('device_types', [])))
    print('prefix_keywords 数量:', len(dtr.get('prefix_keywords', {})))
    print()
    print('前5个 device_types:', dtr.get('device_types', [])[:5])
    print()
    print('prefix_keywords:')
    for k, v in dtr.get('prefix_keywords', {}).items():
        print(f'  "{k}": {v}')
else:
    print('未找到配置')
conn.close()
