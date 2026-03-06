#!/usr/bin/env python3
"""修复白名单配置的存储位置"""

import sqlite3
import json

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

print("=" * 80)
print("修复白名单配置位置")
print("=" * 80)

# 1. 读取当前的whitelist_features
cursor.execute("SELECT config_value FROM configs WHERE config_key = 'whitelist_features'")
row = cursor.fetchone()

if not row:
    print("❌ 未找到whitelist_features配置")
    conn.close()
    exit(1)

whitelist_features = json.loads(row[0])
print(f"\n✅ 读取到 {len(whitelist_features)} 个白名单特征")
print(f"前10项: {whitelist_features[:10]}")

# 2. 读取intelligent_extraction配置
cursor.execute("SELECT config_value FROM configs WHERE config_key = 'intelligent_extraction'")
row = cursor.fetchone()

if not row:
    print("❌ 未找到intelligent_extraction配置")
    conn.close()
    exit(1)

intelligent_extraction = json.loads(row[0])
print(f"\n✅ 读取到intelligent_extraction配置")
print(f"顶层键: {list(intelligent_extraction.keys())}")

# 3. 将whitelist_features添加到intelligent_extraction.feature_quality_scoring中
if 'feature_quality_scoring' not in intelligent_extraction:
    intelligent_extraction['feature_quality_scoring'] = {}

intelligent_extraction['feature_quality_scoring']['whitelist_features'] = whitelist_features

print(f"\n✅ 已将白名单添加到 intelligent_extraction.feature_quality_scoring.whitelist_features")
print(f"feature_quality_scoring键: {list(intelligent_extraction['feature_quality_scoring'].keys())}")

# 4. 更新数据库
cursor.execute(
    "UPDATE configs SET config_value = ? WHERE config_key = 'intelligent_extraction'",
    (json.dumps(intelligent_extraction, ensure_ascii=False),)
)

conn.commit()
print(f"\n✅ 数据库更新成功")

# 5. 验证更新
cursor.execute("SELECT config_value FROM configs WHERE config_key = 'intelligent_extraction'")
row = cursor.fetchone()
updated_config = json.loads(row[0])

if 'whitelist_features' in updated_config.get('feature_quality_scoring', {}):
    whitelist_count = len(updated_config['feature_quality_scoring']['whitelist_features'])
    print(f"✅ 验证成功: intelligent_extraction.feature_quality_scoring.whitelist_features 包含 {whitelist_count} 个特征")
    print(f"前10项: {updated_config['feature_quality_scoring']['whitelist_features'][:10]}")
else:
    print("❌ 验证失败: 白名单未正确添加")

conn.close()

print("\n" + "=" * 80)
print("修复完成！")
print("=" * 80)
print("\n请刷新配置管理页面查看效果")
