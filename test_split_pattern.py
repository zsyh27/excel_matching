#!/usr/bin/env python3
"""测试分隔符拆分"""

import sys
import os
import re
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
print("测试分隔符拆分")
print("=" * 80)

print(f"\n输入: '{test_input}'")
print(f"分隔符配置: {preprocessor.feature_split_chars}")
print(f"分隔符模式: {preprocessor.split_pattern.pattern if preprocessor.split_pattern else 'None'}")

# 测试拆分
if preprocessor.split_pattern:
    segments = preprocessor.split_pattern.split(test_input)
    print(f"\n拆分结果: {segments}")
    print(f"片段数量: {len(segments)}")
    
    for i, segment in enumerate(segments):
        print(f"  片段{i}: '{segment}'")
else:
    print(f"\n未配置分隔符模式")

# 检查是否有隐藏字符
print(f"\n字符分析:")
for i, char in enumerate(test_input):
    print(f"  位置{i}: '{char}' (Unicode: U+{ord(char):04X})")
