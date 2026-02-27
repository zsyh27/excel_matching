# -*- coding: utf-8 -*-
"""
测试DataLoader的load_config方法
"""

import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from modules.text_preprocessor import TextPreprocessor
from modules.data_loader import DataLoader, ConfigManager

# 初始化配置管理器
temp_config_manager = ConfigManager(Config.CONFIG_FILE)
config = temp_config_manager.get_config()

print("通过ConfigManager直接加载的配置:")
print(f"  - 配置键数量: {len(config)}")
print(f"  - 配置键列表: {list(config.keys())}")

# 初始化预处理器
preprocessor = TextPreprocessor(config)

# 初始化DataLoader
data_loader = DataLoader(
    config=Config,
    preprocessor=preprocessor
)

# 通过DataLoader加载配置
loaded_config = data_loader.load_config()

print("\n通过DataLoader加载的配置:")
print(f"  - 配置键数量: {len(loaded_config)}")
print(f"  - 配置键列表: {list(loaded_config.keys())}")

# 检查必需的配置项
required_keys = [
    'ignore_keywords',
    'feature_split_chars',
    'synonym_map',
    'normalization_map',
    'global_config',
    'brand_keywords',
    'device_type_keywords'
]

print("\n必需配置项检查:")
for key in required_keys:
    exists = key in loaded_config
    print(f"  - {key}: {'✓ 存在' if exists else '✗ 缺失'}")
    if exists:
        value = loaded_config[key]
        if isinstance(value, list):
            print(f"    类型: list, 长度: {len(value)}")
        elif isinstance(value, dict):
            print(f"    类型: dict, 键数量: {len(value)}")
