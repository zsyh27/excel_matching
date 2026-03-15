import sqlite3

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 获取 configs 表的结构
cursor.execute("PRAGMA table_info(configs)")
columns = cursor.fetchall()

print("configs 表结构:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# 获取前3条记录
cursor.execute("SELECT * FROM configs LIMIT 3")
rows = cursor.fetchall()

print("\n前3条记录:")
for row in rows:
    print(f"  {row}")

conn.close()
