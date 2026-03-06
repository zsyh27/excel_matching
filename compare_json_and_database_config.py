#!/usr/bin/env python3
"""比较JSON文件和数据库中的配置,确认数据库是最新的"""

import sqlite3
import json
from datetime import datetime

print("=" * 80)
print("配置数据对比检查")
print("=" * 80)

# 1. 读取JSON配置
print("\n【步骤1】读取JSON配置文件...")
try:
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        json_config = json.load(f)
    print(f"✅ JSON配置加载成功,共 {len(json_config)} 个配置项")
except Exception as e:
    print(f"❌ JSON配置加载失败: {e}")
    exit(1)

# 2. 读取数据库配置
print("\n【步骤2】读取数据库配置...")
try:
    conn = sqlite3.connect('data/devices.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT config_key, config_value FROM configs")
    rows = cursor.fetchall()
    
    db_config = {}
    for key, value in rows:
        db_config[key] = json.loads(value)
    
    print(f"✅ 数据库配置加载成功,共 {len(db_config)} 个配置项")
except Exception as e:
    print(f"❌ 数据库配置加载失败: {e}")
    conn.close()
    exit(1)

# 3. 对比配置键
print("\n【步骤3】对比配置键...")
json_keys = set(json_config.keys())
db_keys = set(db_config.keys())

only_in_json = json_keys - db_keys
only_in_db = db_keys - json_keys
common_keys = json_keys & db_keys

print(f"  JSON独有: {len(only_in_json)} 个")
if only_in_json:
    for key in sorted(only_in_json):
        print(f"    - {key}")

print(f"  数据库独有: {len(only_in_db)} 个")
if only_in_db:
    for key in sorted(only_in_db):
        print(f"    - {key}")

print(f"  共同拥有: {len(common_keys)} 个")

# 4. 对比共同键的值
print("\n【步骤4】对比共同键的值...")
differences = []

for key in sorted(common_keys):
    json_value = json_config[key]
    db_value = db_config[key]
    
    # 比较值
    if json_value != db_value:
        differences.append({
            'key': key,
            'json_value': json_value,
            'db_value': db_value
        })

if differences:
    print(f"⚠️  发现 {len(differences)} 个配置值不同:")
    for diff in differences[:5]:  # 只显示前5个
        print(f"\n  配置键: {diff['key']}")
        print(f"    JSON: {str(diff['json_value'])[:100]}...")
        print(f"    数据库: {str(diff['db_value'])[:100]}...")
else:
    print(f"✅ 所有共同配置的值都相同")

# 5. 检查关键配置
print("\n【步骤5】检查关键配置...")
critical_keys = [
    'intelligent_extraction',
    'synonym_map',
    'device_type_keywords',
    'brand_keywords',
    'metadata_keywords'
]

for key in critical_keys:
    json_has = key in json_config
    db_has = key in db_config
    
    status = "✅" if (json_has and db_has) else "⚠️"
    print(f"  {status} {key}: JSON={json_has}, DB={db_has}")
    
    if json_has and db_has:
        # 检查值是否相同
        if json_config[key] == db_config[key]:
            print(f"      值相同 ✅")
        else:
            print(f"      值不同 ⚠️")

# 6. 检查传感器白名单
print("\n【步骤6】检查传感器白名单...")
sensor_features = ['co', 'co2', 'pm10', 'pm2.5', '温度', '湿度', '霍尼韦尔']

# 检查数据库中的白名单
if 'intelligent_extraction' in db_config:
    ie_config = db_config['intelligent_extraction']
    if 'feature_quality_scoring' in ie_config:
        fqs = ie_config['feature_quality_scoring']
        if 'whitelist_features' in fqs:
            whitelist = fqs['whitelist_features']
            print(f"  数据库白名单: {len(whitelist)} 个特征")
            
            found = 0
            for feature in sensor_features:
                if feature in whitelist:
                    found += 1
                    print(f"    ✅ {feature}")
                else:
                    print(f"    ❌ {feature} (缺失)")
            
            print(f"\n  传感器特征: {found}/{len(sensor_features)} 个")
        else:
            print("  ❌ 数据库中没有whitelist_features")
    else:
        print("  ❌ 数据库中没有feature_quality_scoring")
else:
    print("  ❌ 数据库中没有intelligent_extraction")

# 7. 生成结论
print("\n" + "=" * 80)
print("对比结论")
print("=" * 80)

# 计算数据新旧程度
json_only_count = len(only_in_json)
db_only_count = len(only_in_db)
diff_count = len(differences)

if db_only_count > json_only_count:
    print("\n✅ 数据库包含更多配置项,数据库更新")
    print(f"   数据库独有: {db_only_count} 个")
    print(f"   JSON独有: {json_only_count} 个")
elif json_only_count > db_only_count:
    print("\n⚠️  JSON包含更多配置项,JSON可能更新")
    print(f"   JSON独有: {json_only_count} 个")
    print(f"   数据库独有: {db_only_count} 个")
else:
    print("\n✅ JSON和数据库包含相同数量的配置项")

if diff_count > 0:
    print(f"\n⚠️  有 {diff_count} 个配置值不同,需要检查")
else:
    print(f"\n✅ 所有共同配置的值都相同")

# 最终建议
print("\n" + "=" * 80)
print("迁移建议")
print("=" * 80)

if db_only_count >= json_only_count and diff_count == 0:
    print("\n✅ 数据库配置是最新的,可以安全迁移")
    print("   建议: 立即执行迁移")
elif db_only_count > 0 and diff_count == 0:
    print("\n✅ 数据库包含额外配置(如传感器配置),可以迁移")
    print("   建议: 立即执行迁移")
else:
    print("\n⚠️  建议先同步配置再迁移")
    if json_only_count > 0:
        print(f"   需要将JSON独有的 {json_only_count} 个配置导入数据库")
    if diff_count > 0:
        print(f"   需要解决 {diff_count} 个配置值差异")

conn.close()

print("\n" + "=" * 80)
print(f"检查完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
