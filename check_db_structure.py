import sqlite3

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 获取所有表名
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("数据库中的表:")
for table in tables:
    print(f"  - {table[0]}")

conn.close()
