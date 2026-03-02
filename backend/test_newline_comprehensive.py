"""
综合测试：换行符和"水"特征提取问题的完整修复验证

测试场景：
1. 真实换行符处理
2. 字符串字面量 \n 处理
3. "水"特征提取
4. 完整的预处理流程
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

print("=" * 80)
print("综合测试：换行符和特征提取问题修复验证")
print("=" * 80)

# 测试用例1：真实换行符
print("\n【测试用例1：真实换行符】")
print("-" * 80)
test_text_1 = """型号：V5011N1040/U
 通径：1/2"(DN15)
 阀体类型：二通座阀 
 适用介质：水"""

print(f"输入文本: {repr(test_text_1)}")
result_1 = preprocessor.preprocess(test_text_1, mode='matching')

print(f"\n原始文本: {repr(result_1.original)}")
print(f"归一化后: {repr(result_1.normalized)}")
print(f"提取特征: {result_1.features}")

# 验证
assert '\n' not in result_1.normalized, "❌ 归一化后的文本不应包含换行符"
assert '\\n' not in result_1.normalized, "❌ 归一化后的文本不应包含字符串字面量\\n"
assert 'v5011n1040/u' in result_1.features, "❌ 应该提取型号特征"
assert '1/2"' in result_1.features, "❌ 应该提取通径特征"
assert 'dn15' in result_1.features, "❌ 应该提取DN15特征"
assert '二通座阀' in result_1.features, "❌ 应该提取阀体类型特征"
assert '水' in result_1.features, "❌ 应该提取介质特征'水'"

print("\n✓ 测试用例1通过：真实换行符被正确处理，所有特征正确提取")

# 测试用例2：字符串字面量 \n
print("\n【测试用例2：字符串字面量 \\n】")
print("-" * 80)
test_text_2 = r'型号：V5011N1040/U\n 通径：1/2"(DN15)\n 阀体类型：二通座阀 \n 适用介质：水'

print(f"输入文本: {repr(test_text_2)}")
result_2 = preprocessor.preprocess(test_text_2, mode='matching')

print(f"\n原始文本: {repr(result_2.original)}")
print(f"归一化后: {repr(result_2.normalized)}")
print(f"提取特征: {result_2.features}")

# 验证
assert '\n' not in result_2.normalized, "❌ 归一化后的文本不应包含换行符"
assert '\\n' not in result_2.normalized, "❌ 归一化后的文本不应包含字符串字面量\\n"
assert 'v5011n1040/u' in result_2.features, "❌ 应该提取型号特征"
assert '1/2"' in result_2.features, "❌ 应该提取通径特征"
assert 'dn15' in result_2.features, "❌ 应该提取DN15特征"
assert '二通座阀' in result_2.features, "❌ 应该提取阀体类型特征"
assert '水' in result_2.features, "❌ 应该提取介质特征'水'"

print("\n✓ 测试用例2通过：字符串字面量\\n被正确处理，所有特征正确提取")

# 测试用例3：其他介质
print("\n【测试用例3：其他介质特征】")
print("-" * 80)
test_cases = [
    ("适用介质：气", "气"),
    ("适用介质：油", "油"),
    ("适用介质：蒸汽", "蒸汽"),
    ("适用介质：空气", "空气"),
    ("适用介质：冷媒", "冷媒"),
]

for test_text, expected_medium in test_cases:
    result = preprocessor.preprocess(test_text, mode='matching')
    assert expected_medium in result.features, f"❌ 应该提取介质特征'{expected_medium}'"
    print(f"✓ '{test_text}' → 特征: {result.features}")

print("\n✓ 测试用例3通过：所有介质特征正确提取")

# 测试用例4：用户原始问题的完整测试
print("\n【测试用例4：用户原始问题】")
print("-" * 80)
# 这是用户报告的原始问题
test_text_4 = r'型号：V5011N1040/U\n 通径：1/2"(DN15)\n 阀体类型：二通座阀 \n 适用介质：水'

print(f"输入文本（字符串字面量\\n）: {repr(test_text_4)}")
result_4 = preprocessor.preprocess(test_text_4, mode='matching')

print(f"\n原始文本: {repr(result_4.original)}")
print(f"归一化后: {repr(result_4.normalized)}")
print(f"提取特征: {result_4.features}")

# 验证核心问题
print("\n核心验证：")
print(f"1. 归一化后是否包含\\n: {'\\n' in result_4.normalized}")
print(f"2. 归一化后是否包含真实换行符: {chr(10) in result_4.normalized}")
print(f"3. 是否提取了'水'特征: {'水' in result_4.features}")
print(f"4. 特征中是否包含\\n: {any('\\n' in f for f in result_4.features)}")

# 断言
assert '\\n' not in result_4.normalized, "❌ 归一化后不应包含字符串字面量\\n"
assert chr(10) not in result_4.normalized, "❌ 归一化后不应包含真实换行符"
assert '水' in result_4.features, f"❌ 应该提取'水'特征，实际特征: {result_4.features}"
assert not any('\\n' in f for f in result_4.features), f"❌ 特征中不应包含\\n，实际特征: {result_4.features}"

print("\n✓ 测试用例4通过：用户原始问题已完全修复")

# 测试用例5：特征质量评分
print("\n【测试用例5：特征质量评分】")
print("-" * 80)
test_text_5 = "水"

print(f"输入文本: '{test_text_5}'")
quality_score = preprocessor._calculate_feature_quality(test_text_5)

print(f"质量评分: {quality_score}")
print(f"最小要求: 50")

assert quality_score >= 50, f"❌ '水'的质量评分应该 >= 50，实际: {quality_score}"

print(f"\n✓ 测试用例5通过：'水'的质量评分为 {quality_score}，满足最小要求")

# 总结
print("\n" + "=" * 80)
print("【测试总结】")
print("=" * 80)
print("✓ 所有测试用例通过！")
print("\n修复内容：")
print("1. 在归一化阶段添加了字符串字面量\\n到真实换行符的转换")
print("2. 在智能清理阶段删除所有换行符（真实的和转换后的）")
print("3. 添加了介质关键词配置（medium_keywords）")
print("4. 修改了特征质量评分，对介质关键词给予加分")
print("5. 对在设备关键词中的单字特征不扣'太短'的分")
print("\n结果：")
print("- 真实换行符被正确删除 ✓")
print("- 字符串字面量\\n被正确处理 ✓")
print("- '水'等介质特征被正确提取 ✓")
print("- 所有其他特征正常提取 ✓")
print("=" * 80)
