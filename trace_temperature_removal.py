#!/usr/bin/env python3
"""追踪"温度"被删除的位置"""

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

# 测试每个阶段
test_input = "温度传感器"

print("=" * 80)
print("追踪'温度'被删除的位置")
print("=" * 80)

print(f"\n原始输入: '{test_input}'")

# 步骤1: 智能清理
if preprocessor.intelligent_extraction.get('enabled', False):
    cleaned, detail = preprocessor._intelligent_clean_with_detail(test_input, mode='device')
    print(f"\n步骤1 - 智能清理:")
    print(f"  输出: '{cleaned}'")
    print(f"  应用规则: {detail.applied_rules}")
    print(f"  删除长度: {detail.deleted_length}")
    
    # 检查ignore_keywords
    if hasattr(detail, 'ignore_keyword_matches'):
        print(f"  删除的关键词: {[m.keyword for m in detail.ignore_keyword_matches]}")
else:
    cleaned = test_input
    print(f"\n步骤1 - 智能清理: 未启用")

# 步骤2: 归一化
normalized, norm_detail = preprocessor._normalize_with_detail(cleaned, mode='device')
print(f"\n步骤2 - 归一化:")
print(f"  输出: '{normalized}'")
print(f"  归一化映射: {len(norm_detail.normalization_mappings)}")
if norm_detail.normalization_mappings:
    for mapping in norm_detail.normalization_mappings:
        print(f"    - {mapping.from_text} → {mapping.to_text}")

# 步骤3: 特征提取
features, extract_detail = preprocessor._extract_features_with_detail(normalized, mode='device')
print(f"\n步骤3 - 特征提取:")
print(f"  输出: {features}")
print(f"  识别的设备类型: {extract_detail.identified_device_types}")
print(f"  提取的特征详情:")
for feature_detail in extract_detail.extracted_features:
    print(f"    - {feature_detail.feature} (类型: {feature_detail.feature_type}, 来源: {feature_detail.source})")

# 检查配置
print(f"\n配置检查:")
print(f"  ignore_keywords中是否有'温度': {'温度' in preprocessor.ignore_keywords}")
print(f"  device_type_keywords: {preprocessor.device_type_keywords}")
print(f"  智能提取启用: {preprocessor.intelligent_extraction.get('enabled', False)}")
