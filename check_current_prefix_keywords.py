#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查当前前缀关键词配置"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("=" * 80)
print("检查当前前缀关键词配置")
print("=" * 80)

# 获取配置
config = db_loader.load_config()
ie_config = config.get('intelligent_extraction', {})
device_type_config = ie_config.get('device_type_recognition', {})

prefix_keywords = device_type_config.get('prefix_keywords', {})

print(f"\n前缀关键词数量: {len(prefix_keywords)}")
print("\n当前前缀关键词:")
for prefix, types in prefix_keywords.items():
    print(f"  {prefix} → {types}")

print("\n" + "=" * 80)
