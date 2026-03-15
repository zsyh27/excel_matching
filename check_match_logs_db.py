import sqlite3

conn = sqlite3.connect('data/devices.db')
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='match_logs'")
result = cur.fetchone()
print('match_logs表存在:', result is not None)

if result:
    cur.execute('SELECT COUNT(*) FROM match_logs')
    count = cur.fetchone()[0]
    print('记录数:', count)
    if count > 0:
        cur.execute('SELECT log_id, match_status, timestamp FROM match_logs LIMIT 3')
        for row in cur.fetchall():
            print(' ', row)
else:
    print('表不存在，需要创建')
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    print('现有表:', tables)

conn.close()
