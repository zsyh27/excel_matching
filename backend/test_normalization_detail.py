"""
测试归一化详情记录功能

验证 TextPreprocessor 的 _normalize_with_detail() 方法是否正确记录归一化过程
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from modules.text_preprocessor import TextPreprocessor
from modules.match_detail import NormalizationDetail, MappingApplication


def test_normalize_with_detail_basic():
    """测试基本的归一化详情记录"""
    config = {
        'synonym_map': {
            '霍尼韦尔': 'honeywell',
            '西门子': 'siemens'
        },
        'normalization_map': {
            '℃': 'c',
            '°C': 'c',
            '（': '(',
            '）': ')'
        },
        'global_config': {
            'fullwidth_to_halfwidth': True,
            'remove_whitespace': True,
            'unify_lowercase': True
        },
        'feature_split_chars': ['+'],
        'ignore_keywords': [],
        'brand_keywords': [],
        'device_type_keywords': [],
        'intelligent_extraction': {'enabled': False}
    }
    
    preprocessor = TextPreprocessor(config)
    
    # 测试文本包含同义词、归一化映射和全局配置
    text = "霍尼韦尔 温度传感器 -10℃~50℃"
    normalized_text, detail = preprocessor._normalize_with_detail(text)
    
    print("原始文本:", text)
    print("归一化后:", normalized_text)
    print("\n同义词映射:")
    for mapping in detail.synonym_mappings:
        print(f"  {mapping.from_text} → {mapping.to_text} (位置: {mapping.position})")
    
    print("\n归一化映射:")
    for mapping in detail.normalization_mappings:
        print(f"  {mapping.from_text} → {mapping.to_text} (位置: {mapping.position})")
    
    print("\n应用的全局配置:")
    for config_name in detail.global_configs:
        print(f"  {config_name}")
    
    print("\n对比:")
    print(f"  归一化前: {detail.before_text}")
    print(f"  归一化后: {detail.after_text}")
    
    # 验证同义词映射被记录
    assert len(detail.synonym_mappings) > 0, "应该记录同义词映射"
    assert any(m.from_text == '霍尼韦尔' for m in detail.synonym_mappings), "应该记录'霍尼韦尔'的映射"
    
    # 验证归一化映射被记录
    assert len(detail.normalization_mappings) > 0, "应该记录归一化映射"
    assert any(m.from_text == '℃' for m in detail.normalization_mappings), "应该记录'℃'的映射"
    
    # 验证全局配置被记录
    assert len(detail.global_configs) > 0, "应该记录全局配置"
    
    # 验证对比文本
    assert detail.before_text == text, "before_text应该是原始文本"
    assert detail.after_text == normalized_text, "after_text应该是归一化后的文本"
    
    print("\n✓ 基本归一化详情记录测试通过")


def test_normalize_with_detail_multiple_occurrences():
    """测试多次出现的映射记录"""
    config = {
        'synonym_map': {
            '传感器': 'sensor'
        },
        'normalization_map': {
            '℃': 'c'
        },
        'global_config': {
            'fullwidth_to_halfwidth': True,
            'remove_whitespace': True,
            'unify_lowercase': True
        },
        'feature_split_chars': ['+'],
        'ignore_keywords': [],
        'brand_keywords': [],
        'device_type_keywords': [],
        'intelligent_extraction': {'enabled': False}
    }
    
    preprocessor = TextPreprocessor(config)
    
    # 测试文本包含多次出现的映射
    text = "温度传感器+湿度传感器+压力传感器 -10℃~50℃"
    normalized_text, detail = preprocessor._normalize_with_detail(text)
    
    print("\n原始文本:", text)
    print("归一化后:", normalized_text)
    
    # 验证多次出现的同义词映射都被记录
    sensor_mappings = [m for m in detail.synonym_mappings if m.from_text == '传感器']
    print(f"\n'传感器'出现次数: {len(sensor_mappings)}")
    for mapping in sensor_mappings:
        print(f"  位置: {mapping.position}")
    
    assert len(sensor_mappings) == 3, "应该记录3次'传感器'的映射"
    
    # 验证多次出现的归一化映射都被记录
    celsius_mappings = [m for m in detail.normalization_mappings if m.from_text == '℃']
    print(f"\n'℃'出现次数: {len(celsius_mappings)}")
    for mapping in celsius_mappings:
        print(f"  位置: {mapping.position}")
    
    assert len(celsius_mappings) == 2, "应该记录2次'℃'的映射"
    
    print("\n✓ 多次出现的映射记录测试通过")


def test_normalize_with_detail_empty_text():
    """测试空文本的归一化详情"""
    config = {
        'synonym_map': {},
        'normalization_map': {},
        'global_config': {},
        'feature_split_chars': ['+'],
        'ignore_keywords': [],
        'brand_keywords': [],
        'device_type_keywords': [],
        'intelligent_extraction': {'enabled': False}
    }
    
    preprocessor = TextPreprocessor(config)
    
    # 测试空文本
    text = ""
    normalized_text, detail = preprocessor._normalize_with_detail(text)
    
    print("\n测试空文本:")
    print(f"  归一化后: '{normalized_text}'")
    print(f"  同义词映射数: {len(detail.synonym_mappings)}")
    print(f"  归一化映射数: {len(detail.normalization_mappings)}")
    print(f"  全局配置数: {len(detail.global_configs)}")
    
    assert normalized_text == "", "空文本应该返回空字符串"
    assert len(detail.synonym_mappings) == 0, "空文本不应该有同义词映射"
    assert len(detail.normalization_mappings) == 0, "空文本不应该有归一化映射"
    assert len(detail.global_configs) == 0, "空文本不应该有全局配置"
    
    print("\n✓ 空文本归一化详情测试通过")


def test_normalize_with_detail_in_preprocess():
    """测试在preprocess方法中归一化详情的集成"""
    config = {
        'synonym_map': {
            '霍尼韦尔': 'honeywell'
        },
        'normalization_map': {
            '℃': 'c'
        },
        'global_config': {
            'fullwidth_to_halfwidth': True,
            'remove_whitespace': True,
            'unify_lowercase': True
        },
        'feature_split_chars': ['+'],
        'ignore_keywords': [],
        'brand_keywords': ['honeywell'],
        'device_type_keywords': ['传感器'],
        'intelligent_extraction': {'enabled': False}
    }
    
    preprocessor = TextPreprocessor(config)
    
    # 测试完整的预处理流程
    text = "霍尼韦尔 温度传感器 -10℃~50℃"
    result = preprocessor.preprocess(text, mode='matching')
    
    print("\n测试preprocess集成:")
    print(f"  原始文本: {result.original}")
    print(f"  归一化后: {result.normalized}")
    print(f"  特征数: {len(result.features)}")
    
    # 验证归一化详情被附加到结果
    assert hasattr(result, 'normalization_detail'), "PreprocessResult应该有normalization_detail属性"
    assert result.normalization_detail is not None, "normalization_detail不应该为None"
    
    detail = result.normalization_detail
    print(f"\n  同义词映射数: {len(detail.synonym_mappings)}")
    print(f"  归一化映射数: {len(detail.normalization_mappings)}")
    print(f"  全局配置数: {len(detail.global_configs)}")
    
    # 验证详情内容
    assert len(detail.synonym_mappings) > 0, "应该有同义词映射"
    assert len(detail.normalization_mappings) > 0, "应该有归一化映射"
    assert detail.before_text != "", "before_text不应该为空"
    assert detail.after_text != "", "after_text不应该为空"
    
    print("\n✓ preprocess集成测试通过")


def test_normalization_detail_serialization():
    """测试归一化详情的序列化和反序列化"""
    from modules.match_detail import NormalizationDetail, MappingApplication
    
    # 创建测试数据
    detail = NormalizationDetail(
        synonym_mappings=[
            MappingApplication(
                rule_name="霍尼韦尔 → honeywell",
                from_text="霍尼韦尔",
                to_text="honeywell",
                position=0,
                mapping_type="synonym"
            )
        ],
        normalization_mappings=[
            MappingApplication(
                rule_name="℃ → c",
                from_text="℃",
                to_text="c",
                position=10,
                mapping_type="normalization"
            )
        ],
        global_configs=['fullwidth_to_halfwidth', 'remove_whitespace'],
        before_text="霍尼韦尔 温度传感器 -10℃~50℃",
        after_text="honeywell温度传感器-10c~50c"
    )
    
    # 序列化
    detail_dict = detail.to_dict()
    print("\n序列化结果:")
    print(f"  同义词映射数: {len(detail_dict['synonym_mappings'])}")
    print(f"  归一化映射数: {len(detail_dict['normalization_mappings'])}")
    print(f"  全局配置数: {len(detail_dict['global_configs'])}")
    
    # 反序列化
    detail_restored = NormalizationDetail.from_dict(detail_dict)
    print("\n反序列化结果:")
    print(f"  同义词映射数: {len(detail_restored.synonym_mappings)}")
    print(f"  归一化映射数: {len(detail_restored.normalization_mappings)}")
    print(f"  全局配置数: {len(detail_restored.global_configs)}")
    
    # 验证
    assert len(detail_restored.synonym_mappings) == 1, "同义词映射数应该为1"
    assert len(detail_restored.normalization_mappings) == 1, "归一化映射数应该为1"
    assert len(detail_restored.global_configs) == 2, "全局配置数应该为2"
    assert detail_restored.before_text == detail.before_text, "before_text应该相同"
    assert detail_restored.after_text == detail.after_text, "after_text应该相同"
    
    print("\n✓ 序列化测试通过")


if __name__ == '__main__':
    print("=" * 60)
    print("测试归一化详情记录功能")
    print("=" * 60)
    
    try:
        test_normalize_with_detail_basic()
        test_normalize_with_detail_multiple_occurrences()
        test_normalize_with_detail_empty_text()
        test_normalize_with_detail_in_preprocess()
        test_normalization_detail_serialization()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
