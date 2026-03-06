"""
检查device_type_keywords配置的数据格式
"""
import sys
import os
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager

# 获取数据库URL
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f'sqlite:///{os.path.join(BASE_DIR, "data", "devices.db")}'

# 初始化数据库管理器
db_manager = DatabaseManager(DATABASE_URL)
session = db_manager.get_session()

# 从数据库加载配置
from modules.models import Config as ConfigModel
import json

config_dict = {}
configs = session.query(ConfigModel).all()
for config in configs:
    config_dict[config.config_key] = config.config_value  # 使用config_value而不是config_data

session.close()

print("=" * 80)
print("检查device_type_keywords配置格式")
print("=" * 80)

device_type_keywords = config_dict.get('device_type_keywords')

print(f"\ndevice_type_keywords类型: {type(device_type_keywords)}")
print(f"device_type_keywords内容: {device_type_keywords}")

if isinstance(device_type_keywords, dict):
    print("\n⚠️ device_type_keywords是字典类型!")
    print(f"字典的键: {list(device_type_keywords.keys())}")
    if 'device_type_keywords' in device_type_keywords:
        inner_value = device_type_keywords['device_type_keywords']
        print(f"\n嵌套的device_type_keywords类型: {type(inner_value)}")
        print(f"嵌套的device_type_keywords内容: {inner_value[:5] if isinstance(inner_value, list) else inner_value}")
elif isinstance(device_type_keywords, list):
    print("\n✅ device_type_keywords是列表类型!")
    print(f"列表长度: {len(device_type_keywords)}")
    print(f"前5个元素: {device_type_keywords[:5]}")
