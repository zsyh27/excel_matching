#!/usr/bin/env python3
"""调试设备类型拆分问题"""

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

# 测试device模式
print("=" * 80)
print("测试device模式")
print("=" * 80)

test_input = "温度传感器"
result = preprocessor.preprocess(test_input, mode='device')

print(f"\n输入: '{test_input}'")
print(f"模式: device")
print(f"清理后: '{result.cleaned}'")
print(f"归一化后: '{result.normalized}'")
print(f"特征: {result.features}")

# 检查智能清理详情
if result.intelligent_cleaning_detail:
    print(f"\n智能清理详情:")
    print(f"  应用规则: {result.intelligent_cleaning_detail.applied_rules}")
    print(f"  删除长度: {result.intelligent_cleaning_detail.deleted_length}")

# 检查提取详情
if result.extraction_detail:
    print(f"\n提取详情:")
    print(f"  分隔符: {result.extraction_detail.split_chars}")
    print(f"  识别的品牌: {result.extraction_detail.identified_brands}")
    print(f"  识别的设备类型: {result.extraction_detail.identified_device_types}")
    print(f"  提取的特征:")
    for feature_detail in result.extraction_detail.extracted_features:
        print(f"    - {feature_detail.feature} (类型: {feature_detail.feature_type}, 来源: {feature_detail.source})")

# 测试matching模式对比
print("\n" + "=" * 80)
print("测试matching模式(对比)")
print("=" * 80)

result2 = preprocessor.preprocess(test_input, mode='matching')

print(f"\n输入: '{test_input}'")
print(f"模式: matching")
print(f"清理后: '{result2.cleaned}'")
print(f"归一化后: '{result2.normalized}'")
print(f"特征: {result2.features}")
