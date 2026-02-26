# -*- coding: utf-8 -*-
"""
测试 DataLoader 初始化
"""
import sys
sys.path.insert(0, '.')

from config import Config
from modules.text_preprocessor import TextPreprocessor
from modules.data_loader import DataLoader, ConfigManager

print("步骤 1: 初始化文本预处理器...")
try:
    temp_config_manager = ConfigManager(Config.CONFIG_FILE)
    config = temp_config_manager.get_config()
    preprocessor = TextPreprocessor(config)
    print("✓ 文本预处理器初始化成功")
except Exception as e:
    print(f"✗ 文本预处理器初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n步骤 2: 初始化 DataLoader...")
try:
    data_loader = DataLoader(
        config=Config,
        preprocessor=preprocessor
    )
    print(f"✓ DataLoader 初始化成功")
    print(f"  存储模式: {data_loader.get_storage_mode()}")
except Exception as e:
    print(f"✗ DataLoader 初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n步骤 3: 加载设备...")
try:
    devices = data_loader.load_devices()
    print(f"✓ 设备加载成功: {len(devices)} 个设备")
except Exception as e:
    print(f"✗ 设备加载失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n步骤 4: 加载规则...")
try:
    rules = data_loader.load_rules()
    print(f"✓ 规则加载成功: {len(rules)} 条规则")
except Exception as e:
    print(f"✗ 规则加载失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ 所有测试通过！")
