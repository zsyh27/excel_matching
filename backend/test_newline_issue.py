"""
测试换行符和"水"特征提取问题

问题描述：
1. 原始文本中的换行符(\n)没有被清理
2. "水"这个重要特征没有被提取
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.text_preprocessor import TextPreprocessor
import json

# 加载配置
with open('data/static_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 创建预处理器
preprocessor = TextPreprocessor(config)

# 测试数据
test_text = """型号：V5011N1040/U
 通径：1/2"(DN15)
 阀体类型：二通座阀 
 适用介质：水"""

print("=" * 80)
print("测试：换行符和'水'特征提取问题")
print("=" * 80)

print("\n【原始文本】")
print(repr(test_text))  # 使用repr显示转义字符
print(f"长度: {len(test_text)}")

# 执行预处理
result = preprocessor.preprocess(test_text, mode='matching')

print("\n【清理后文本】")
print(repr(result.cleaned))
print(f"长度: {len(result.cleaned)}")

print("\n【归一化后文本】")
print(repr(result.normalized))
print(f"长度: {len(result.normalized)}")

print("\n【提取的特征】")
for i, feature in enumerate(result.features, 1):
    print(f"{i}. {repr(feature)} (长度: {len(feature)})")

print("\n【问题诊断】")
print("-" * 80)

# 检查换行符问题
has_newline_in_features = any('\n' in f for f in result.features)
if has_newline_in_features:
    print("❌ 问题1: 特征中包含换行符")
    for f in result.features:
        if '\n' in f:
            print(f"   - {repr(f)}")
else:
    print("✓ 问题1: 特征中没有换行符")

# 检查"水"是否被提取
has_water = any('水' in f for f in result.features)
if has_water:
    print("✓ 问题2: '水'已被提取")
else:
    print("❌ 问题2: '水'没有被提取")
    print(f"   原始文本包含'水': {'水' in test_text}")
    print(f"   清理后包含'水': {'水' in result.cleaned}")
    print(f"   归一化后包含'水': {'水' in result.normalized}")

print("\n【详细分析】")
print("-" * 80)

# 分析归一化过程
print("\n1. 归一化配置检查:")
print(f"   - remove_whitespace: {config['global_config'].get('remove_whitespace', True)}")
print(f"   - 分隔符: {config['feature_split_chars']}")

# 手动测试归一化
print("\n2. 手动测试归一化:")
normalized_manual = preprocessor.normalize_text(result.cleaned, mode='matching')
print(f"   归一化结果: {repr(normalized_manual)}")

# 手动测试特征提取
print("\n3. 手动测试特征提取:")
features_manual = preprocessor.extract_features(normalized_manual)
print(f"   提取的特征: {features_manual}")

# 检查"水；"的处理
print("\n4. 检查'水；'的处理:")
if '水；' in test_text:
    print("   原始文本包含'水；'")
    # 检查分号是否在分隔符列表中
    if '；' in config['feature_split_chars']:
        print("   ✓ 分号(；)在分隔符列表中")
    else:
        print("   ❌ 分号(；)不在分隔符列表中")

# 测试简化版本
print("\n5. 测试简化版本:")
simple_test = "水；"
simple_result = preprocessor.preprocess(simple_test, mode='matching')
print(f"   输入: {repr(simple_test)}")
print(f"   归一化: {repr(simple_result.normalized)}")
print(f"   特征: {simple_result.features}")

print("\n" + "=" * 80)
