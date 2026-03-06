#!/usr/bin/env python3
"""调试括号特征提取"""

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

test_input = "温度传感器"

print("=" * 80)
print("调试括号特征提取")
print("=" * 80)

print(f"\n输入: '{test_input}'")

# 直接调用_extract_bracket_features
bracket_features = preprocessor._extract_bracket_features(test_input)
print(f"\n_extract_bracket_features输出: {bracket_features}")

# 检查_remove_metadata_prefix
for feature in bracket_features:
    cleaned = preprocessor._remove_metadata_prefix(feature)
    print(f"\n_remove_metadata_prefix:")
    print(f"  输入: '{feature}'")
    print(f"  输出: '{cleaned}'")
    
    # 检查_remove_unit_suffix
    final = preprocessor._remove_unit_suffix(cleaned)
    print(f"\n_remove_unit_suffix:")
    print(f"  输入: '{cleaned}'")
    print(f"  输出: '{final}'")
