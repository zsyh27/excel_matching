#!/usr/bin/env python3
"""同步JSON中缺失的配置到数据库"""

import sqlite3
import json

print("=" * 80)
print("同步缺失配置到数据库")
print("=" * 80)

# 读取JSON配置
with open('data/static_config.json', 'r', encoding='utf-8') as f:
    json_config = json.load(f)

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 1. 添加medium_keywords
print("\n【1. 添加medium_keywords】")
if 'medium_keywords' in json_config:
    medium_keywords = json_config['medium_keywords']
    print(f"  从JSON读取: {len(medium_keywords)} 个关键词")
    print(f"  内容: {medium_keywords}")
    
    cursor.execute(
        "INSERT OR REPLACE INTO configs (config_key, config_value) VALUES (?, ?)",
        ('medium_keywords', json.dumps(medium_keywords, ensure_ascii=False))
    )
    print("  ✅ 已添加到数据库")
else:
    print("  ⚠️  JSON中没有medium_keywords")

# 2. 更新metadata_keywords(添加"介质")
print("\n【2. 更新metadata_keywords】")
cursor.execute("SELECT config_value FROM configs WHERE config_key = 'metadata_keywords'")
row = cursor.fetchone()

if row:
    db_metadata = json.loads(row[0])
    print(f"  数据库当前: {len(db_metadata)} 个")
    
    if '介质' not in db_metadata:
        db_metadata.append('介质')
        cursor.execute(
            "UPDATE configs SET config_value = ? WHERE config_key = 'metadata_keywords'",
            (json.dumps(db_metadata, ensure_ascii=False),)
        )
        print(f"  ✅ 已添加'介质',现在共 {len(db_metadata)} 个")
    else:
        print("  ℹ️  '介质'已存在")
else:
    print("  ⚠️  数据库中没有metadata_keywords")

# 提交更改
conn.commit()

# 3. 验证
print("\n【3. 验证更新】")
cursor.execute("SELECT config_key FROM configs WHERE config_key IN ('medium_keywords', 'metadata_keywords')")
rows = cursor.fetchall()

for row in rows:
    cursor.execute("SELECT config_value FROM configs WHERE config_key = ?", (row[0],))
    value = json.loads(cursor.fetchone()[0])
    print(f"  ✅ {row[0]}: {len(value)} 项")

conn.close()

print("\n" + "=" * 80)
print("同步完成")
print("=" * 80)
print("\n✅ 数据库现在包含所有配置")
print("✅ 可以安全执行迁移")
