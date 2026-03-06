#!/usr/bin/env python3
"""测试设备类型特征提取"""

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
print("✅ 配置加载成功\n")

# 初始化预处理器
preprocessor = TextPreprocessor(config=config)

# 测试不同的输入
test_cases = [
    "温度传感器",
    "室内温度传感器",
    "传感器",
    "霍尼韦尔",
    "HST-RA"
]

print("=" * 80)
print("测试设备类型特征提取")
print("=" * 80)

for test_input in test_cases:
    result = preprocessor.preprocess(test_input, mode='device')
    print(f"\n输入: '{test_input}'")
    print(f"特征: {result.features}")
    print(f"特征数量: {len(result.features)}")
