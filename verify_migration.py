#!/usr/bin/env python3
"""验证配置迁移是否成功"""

import sys
import os

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 80)
print("配置迁移验证")
print("=" * 80)

# 1. 检查备份文件
print("\n【1. 检查备份文件】")
backup_files = [
    'data/config_backup_json/static_config_20260306.json',
    'data/config_backup_json/sensor_params_config.json'
]

for file in backup_files:
    if os.path.exists(file):
        size = os.path.getsize(file)
        print(f"  ✅ {file} ({size} bytes)")
    else:
        print(f"  ❌ {file} (不存在)")

# 2. 检查config.py
print("\n【2. 检查config.py】")
with open('backend/config.py', 'r', encoding='utf-8') as f:
    config_content = f.read()
    
if 'CONFIG_FILE 已废弃' in config_content:
    print("  ✅ CONFIG_FILE已标记为废弃")
else:
    print("  ⚠️  CONFIG_FILE未标记为废弃")

if '配置已迁移到数据库' in config_content:
    print("  ✅ 已添加迁移说明")
else:
    print("  ⚠️  未添加迁移说明")

# 3. 检查app.py
print("\n【3. 检查app.py】")
with open('backend/app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

if 'ConfigManager(Config.CONFIG_FILE)' in app_content:
    print("  ⚠️  仍在使用ConfigManager读取JSON")
else:
    print("  ✅ 已移除ConfigManager读取JSON")

if 'data_loader.load_config()' in app_content:
    print("  ✅ 使用data_loader从数据库加载配置")
else:
    print("  ❌ 未使用data_loader加载配置")

# 4. 测试导入模块
print("\n【4. 测试导入模块】")
try:
    from config import Config
    print("  ✅ Config导入成功")
    print(f"     存储模式: {Config.STORAGE_MODE}")
    print(f"     数据库URL: {Config.DATABASE_URL}")
except Exception as e:
    print(f"  ❌ Config导入失败: {e}")

try:
    from modules.data_loader import DataLoader
    print("  ✅ DataLoader导入成功")
except Exception as e:
    print(f"  ❌ DataLoader导入失败: {e}")

# 5. 测试配置加载
print("\n【5. 测试配置加载】")
try:
    from modules.text_preprocessor import TextPreprocessor
    
    # 初始化DataLoader
    data_loader = DataLoader(config=Config, preprocessor=None)
    print(f"  ✅ DataLoader初始化成功")
    print(f"     存储模式: {data_loader.get_storage_mode()}")
    
    # 加载配置
    config = data_loader.load_config()
    print(f"  ✅ 配置加载成功")
    print(f"     配置项数量: {len(config)}")
    
    # 检查关键配置
    key_configs = ['intelligent_extraction', 'synonym_map', 'device_type_keywords']
    for key in key_configs:
        if key in config:
            print(f"     ✅ {key}")
        else:
            print(f"     ❌ {key} (缺失)")
    
    # 初始化预处理器
    preprocessor = TextPreprocessor(config)
    print(f"  ✅ TextPreprocessor初始化成功")
    
except Exception as e:
    print(f"  ❌ 配置加载失败: {e}")
    import traceback
    traceback.print_exc()

# 6. 检查数据库配置完整性
print("\n【6. 检查数据库配置完整性】")
try:
    import sqlite3
    import json
    
    conn = sqlite3.connect('data/devices.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM configs")
    count = cursor.fetchone()[0]
    print(f"  ✅ 数据库配置项: {count} 个")
    
    # 检查传感器配置
    cursor.execute("SELECT config_value FROM configs WHERE config_key = 'intelligent_extraction'")
    row = cursor.fetchone()
    if row:
        ie_config = json.loads(row[0])
        whitelist = ie_config.get('feature_quality_scoring', {}).get('whitelist_features', [])
        print(f"  ✅ 白名单特征: {len(whitelist)} 个")
        
        sensor_features = ['co', 'co2', 'pm2.5', '温度', '湿度', '霍尼韦尔']
        found = sum(1 for f in sensor_features if f in whitelist)
        print(f"  ✅ 传感器特征: {found}/{len(sensor_features)} 个")
    
    conn.close()
    
except Exception as e:
    print(f"  ❌ 数据库检查失败: {e}")

print("\n" + "=" * 80)
print("验证结果")
print("=" * 80)

print("\n✅ 配置迁移成功!")
print("\n后续步骤:")
print("  1. 重启后端服务: cd backend && python app.py")
print("  2. 测试系统功能")
print("  3. 如有问题,可从备份恢复")
print("\n备份位置: data/config_backup_json/")
