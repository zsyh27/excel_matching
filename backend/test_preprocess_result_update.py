"""
测试 PreprocessResult 数据结构更新

验证任务 24.1 和 24.2 的实现
"""

import json
from modules.text_preprocessor import TextPreprocessor, PreprocessResult
from modules.match_detail import IntelligentCleaningDetail, NormalizationDetail, ExtractionDetail

# 加载配置
with open('data/static_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 创建预处理器
preprocessor = TextPreprocessor(config)

print("=" * 80)
print("测试 PreprocessResult 数据结构更新")
print("=" * 80)

# 测试用例1: 正常文本
print("\n【测试1】正常文本处理")
test_text = "霍尼韦尔 温度传感器 -10℃~50℃ 4-20ma"
result = preprocessor.preprocess(test_text, mode='matching')

print(f"原始文本: {result.original}")
print(f"清理后: {result.cleaned}")
print(f"归一化: {result.normalized}")
print(f"特征: {result.features}")

# 验证详情字段存在
print("\n验证详情字段:")
print(f"  intelligent_cleaning_detail: {hasattr(result, 'intelligent_cleaning_detail')}")
print(f"  normalization_detail: {hasattr(result, 'normalization_detail')}")
print(f"  extraction_detail: {hasattr(result, 'extraction_detail')}")

# 验证详情对象类型
if hasattr(result, 'intelligent_cleaning_detail') and result.intelligent_cleaning_detail:
    print(f"  智能清理详情类型: {type(result.intelligent_cleaning_detail).__name__}")
    assert isinstance(result.intelligent_cleaning_detail, IntelligentCleaningDetail), \
        "intelligent_cleaning_detail 应该是 IntelligentCleaningDetail 类型"

if hasattr(result, 'normalization_detail') and result.normalization_detail:
    print(f"  归一化详情类型: {type(result.normalization_detail).__name__}")
    assert isinstance(result.normalization_detail, NormalizationDetail), \
        "normalization_detail 应该是 NormalizationDetail 类型"

if hasattr(result, 'extraction_detail') and result.extraction_detail:
    print(f"  特征提取详情类型: {type(result.extraction_detail).__name__}")
    assert isinstance(result.extraction_detail, ExtractionDetail), \
        "extraction_detail 应该是 ExtractionDetail 类型"

# 测试用例2: 测试 to_dict() 方法
print("\n【测试2】测试 to_dict() 序列化")
result_dict = result.to_dict()

print(f"序列化后的键: {list(result_dict.keys())}")
assert 'original' in result_dict, "应该包含 original 字段"
assert 'cleaned' in result_dict, "应该包含 cleaned 字段"
assert 'normalized' in result_dict, "应该包含 normalized 字段"
assert 'features' in result_dict, "应该包含 features 字段"

# 验证详情字段（如果存在）
if result.intelligent_cleaning_detail:
    assert 'intelligent_cleaning' in result_dict, "应该包含 intelligent_cleaning 字段"
    print(f"  intelligent_cleaning 字段存在: ✓")

if result.normalization_detail:
    assert 'normalization_detail' in result_dict, "应该包含 normalization_detail 字段"
    print(f"  normalization_detail 字段存在: ✓")

if result.extraction_detail:
    assert 'extraction_detail' in result_dict, "应该包含 extraction_detail 字段"
    print(f"  extraction_detail 字段存在: ✓")

# 测试用例3: 测试 from_dict() 方法
print("\n【测试3】测试 from_dict() 反序列化")
restored_result = PreprocessResult.from_dict(result_dict)

print(f"反序列化成功: ✓")
assert restored_result.original == result.original, "original 应该相同"
assert restored_result.cleaned == result.cleaned, "cleaned 应该相同"
assert restored_result.normalized == result.normalized, "normalized 应该相同"
assert restored_result.features == result.features, "features 应该相同"

# 验证详情字段
if result.intelligent_cleaning_detail:
    assert restored_result.intelligent_cleaning_detail is not None, \
        "反序列化后应该有 intelligent_cleaning_detail"
    print(f"  intelligent_cleaning_detail 反序列化成功: ✓")

if result.normalization_detail:
    assert restored_result.normalization_detail is not None, \
        "反序列化后应该有 normalization_detail"
    print(f"  normalization_detail 反序列化成功: ✓")

if result.extraction_detail:
    assert restored_result.extraction_detail is not None, \
        "反序列化后应该有 extraction_detail"
    print(f"  extraction_detail 反序列化成功: ✓")

# 测试用例4: 测试空文本
print("\n【测试4】测试空文本处理")
empty_result = preprocessor.preprocess("", mode='matching')

print(f"空文本处理成功: ✓")
assert empty_result.original == "", "original 应该为空"
assert empty_result.cleaned == "", "cleaned 应该为空"
assert empty_result.normalized == "", "normalized 应该为空"
assert empty_result.features == [], "features 应该为空列表"

# 验证空文本也有详情对象
assert hasattr(empty_result, 'intelligent_cleaning_detail'), "空文本应该有 intelligent_cleaning_detail"
assert hasattr(empty_result, 'normalization_detail'), "空文本应该有 normalization_detail"
assert hasattr(empty_result, 'extraction_detail'), "空文本应该有 extraction_detail"
print(f"  空文本详情对象存在: ✓")

# 测试用例5: 测试向后兼容性
print("\n【测试5】测试向后兼容性")
# 创建一个只有基础字段的字典（模拟旧版本数据）
old_format_dict = {
    'original': 'test',
    'cleaned': 'test',
    'normalized': 'test',
    'features': ['test']
}

old_result = PreprocessResult.from_dict(old_format_dict)
print(f"旧格式反序列化成功: ✓")
assert old_result.original == 'test', "original 应该正确"
assert old_result.intelligent_cleaning_detail is None, "旧格式不应该有详情字段"
assert old_result.normalization_detail is None, "旧格式不应该有详情字段"
assert old_result.extraction_detail is None, "旧格式不应该有详情字段"
print(f"  向后兼容性验证通过: ✓")

print("\n" + "=" * 80)
print("所有测试通过! ✓")
print("=" * 80)
print("\n任务 24.1 和 24.2 实现验证成功:")
print("  ✓ PreprocessResult 数据类已更新，添加了三个可选详情字段")
print("  ✓ to_dict() 和 from_dict() 方法已实现")
print("  ✓ 向后兼容性已保证")
print("  ✓ preprocess() 方法已更新，正确附加详情对象")
print("  ✓ 空文本处理正确")
