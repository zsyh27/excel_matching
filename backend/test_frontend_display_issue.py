"""
测试前端显示的换行符问题

验证后端是否正确处理换行符，以及前端显示是否有问题
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

# 测试数据（真实的换行符）
test_text_real_newline = """型号：V5011N1040/U
 通径：1/2"(DN15)
 阀体类型：二通座阀 
 适用介质：水"""

# 测试数据（字符串字面量 \n）
test_text_literal_backslash_n = r'型号：V5011N1040/U\n 通径：1/2"(DN15)\n 阀体类型：二通座阀 \n 适用介质：水'

print("=" * 80)
print("测试：前端显示的换行符问题")
print("=" * 80)

print("\n【测试1：真实换行符】")
print("-" * 80)
print(f"输入类型: 真实换行符")
print(f"输入内容: {repr(test_text_real_newline)}")
print(f"包含真实\\n: {chr(10) in test_text_real_newline}")
print(f"包含字面量\\n: {'\\n' in test_text_real_newline}")

result1 = preprocessor.preprocess(test_text_real_newline, mode='matching')

print(f"\n归一化后: {repr(result1.normalized)}")
print(f"包含真实\\n: {chr(10) in result1.normalized}")
print(f"包含字面量\\n: {'\\n' in result1.normalized}")

print(f"\n提取特征:")
for i, feature in enumerate(result1.features, 1):
    has_real_newline = chr(10) in feature
    has_literal = '\\n' in feature
    print(f"  {i}. {repr(feature)} - 真实\\n:{has_real_newline}, 字面量\\n:{has_literal}")

print("\n" + "-" * 80)
print("\n【测试2：字符串字面量 \\n】")
print("-" * 80)
print(f"输入类型: 字符串字面量 (反斜杠+n)")
print(f"输入内容: {repr(test_text_literal_backslash_n)}")
print(f"包含真实\\n: {chr(10) in test_text_literal_backslash_n}")
print(f"包含字面量\\n: {'\\n' in test_text_literal_backslash_n}")

result2 = preprocessor.preprocess(test_text_literal_backslash_n, mode='matching')

print(f"\n归一化后: {repr(result2.normalized)}")
print(f"包含真实\\n: {chr(10) in result2.normalized}")
print(f"包含字面量\\n: {'\\n' in result2.normalized}")

print(f"\n提取特征:")
for i, feature in enumerate(result2.features, 1):
    has_real_newline = chr(10) in feature
    has_literal = '\\n' in feature
    print(f"  {i}. {repr(feature)} - 真实\\n:{has_real_newline}, 字面量\\n:{has_literal}")

print("\n" + "=" * 80)
print("【结论】")
print("=" * 80)

if chr(10) not in result1.normalized and chr(10) not in ''.join(result1.features):
    print("✓ 测试1通过: 真实换行符被正确删除")
else:
    print("❌ 测试1失败: 真实换行符未被删除")

if '\\n' in result2.normalized or any('\\n' in f for f in result2.features):
    print("❌ 测试2失败: 字符串字面量\\n未被处理")
    print("   这可能是前端发送数据时的问题")
else:
    print("✓ 测试2通过: 字符串字面量\\n被正确处理")

print("\n【建议】")
print("如果前端显示 \\n，可能的原因：")
print("1. 前端在显示时将换行符转义为 \\n（显示问题）")
print("2. 前端发送数据时将换行符转义为字符串字面量（数据问题）")
print("3. 需要检查前端的输入处理和显示逻辑")

print("\n" + "=" * 80)
