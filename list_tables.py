import sqlite3

conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print('数据库中的表:')
for t in tables:
    print(f'  - {t[0]}')
    
    # 查看表结构
    cursor.execute(f"PRAGMA table_info({t[0]})")
    columns = cursor.fetchall()
    print(f"    列: {[col[1] for col in columns]}")

conn.close()
