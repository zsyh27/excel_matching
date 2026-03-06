#!/usr/bin/env python3
"""检查metadata_keywords配置"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from modules.data_loader import DataLoader
from modules.text_preprocessor import TextPreprocessor

# 创建配置对象
class Config:
    STORAGE_MODE = 'database'
    DATABASE_URL = 'sqlite:///data/devices.db'
    DATABASE_TYPE = 'sqlite'
    FALLBACK_TO_JSON = False

config_obj = Config()
data_loader = DataLoader(config=config_obj)

# 加载配置
config = data_loader.load_config()

# 初始化预处理器
preprocessor = TextPreprocessor(config=config)

print("=" * 80)
print("检查metadata_keywords配置")
print("=" * 80)

print(f"\nmetadata_keywords: {preprocessor.metadata_keywords}")
print(f"\n'温度' in metadata_keywords: {'温度' in preprocessor.metadata_keywords}")
print(f"'传感器' in metadata_keywords: {'传感器' in preprocessor.metadata_keywords}")

# 测试删除前缀
test_input = "温度传感器"
print(f"\n测试输入: '{test_input}'")

# 检查是否以元数据关键词开头
sorted_metadata_keywords = sorted(preprocessor.metadata_keywords, key=len, reverse=True)
for keyword in sorted_metadata_keywords:
    keyword_lower = keyword.lower()
    text_lower = test_input.lower()
    if text_lower.startswith(keyword_lower):
        print(f"\n匹配到元数据关键词: '{keyword}'")
        print(f"  删除前缀后: '{test_input[len(keyword):]}'")
        break
