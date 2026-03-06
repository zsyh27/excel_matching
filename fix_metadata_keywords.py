#!/usr/bin/env python3
"""修复metadata_keywords配置,删除可能是设备类型一部分的词"""

import sqlite3
import json

print("=" * 80)
print("修复metadata_keywords配置")
print("=" * 80)

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 读取当前配置
cursor.execute("SELECT config_value FROM configs WHERE config_key = 'metadata_keywords'")
row = cursor.fetchone()

if not row:
    print("❌ 未找到metadata_keywords配置")
    conn.close()
    exit(1)

current_keywords = json.loads(row[0])
print(f"\n当前metadata_keywords ({len(current_keywords)}个):")
print(json.dumps(current_keywords, ensure_ascii=False, indent=2))

# 需要删除的关键词(这些词可能是设备类型的一部分)
keywords_to_remove = [
    '温度',  # "温度传感器"
    '压力',  # "压力传感器"
    '湿度',  # "湿度传感器"
    '功率',  # 可能是参数,但也可能是设备类型的一部分
]

# 过滤关键词
new_keywords = [kw for kw in current_keywords if kw not in keywords_to_remove]

print(f"\n删除的关键词:")
for kw in keywords_to_remove:
    if kw in current_keywords:
        print(f"  - {kw}")

print(f"\n新的metadata_keywords ({len(new_keywords)}个):")
print(json.dumps(new_keywords, ensure_ascii=False, indent=2))

# 询问是否更新
response = input("\n是否更新配置? (y/n): ")

if response.lower() == 'y':
    # 更新数据库
    cursor.execute("""
        UPDATE configs 
        SET config_value = ?
        WHERE config_key = 'metadata_keywords'
    """, (json.dumps(new_keywords, ensure_ascii=False),))
    
    conn.commit()
    print("\n✅ 配置已更新")
    
    # 验证更新
    cursor.execute("SELECT config_value FROM configs WHERE config_key = 'metadata_keywords'")
    row = cursor.fetchone()
    updated_keywords = json.loads(row[0])
    
    print(f"\n验证: 更新后的配置包含 {len(updated_keywords)} 个关键词")
    print(f"'温度' in metadata_keywords: {'温度' in updated_keywords}")
    print(f"'压力' in metadata_keywords: {'压力' in updated_keywords}")
else:
    print("\n❌ 取消更新")

conn.close()

print("\n" + "=" * 80)
print("完成")
print("=" * 80)
print("\n提示: 更新配置后,需要重新生成受影响设备的规则")
