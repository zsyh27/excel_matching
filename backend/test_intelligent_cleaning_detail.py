"""
测试智能清理详情记录功能

验证 TextPreprocessor 的 _intelligent_clean_with_detail() 方法
能够正确记录智能清理过程的详细信息
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.text_preprocessor import TextPreprocessor
from modules.match_detail import IntelligentCleaningDetail, TruncationMatch, NoiseMatch, MetadataMatch
import json


def test_intelligent_cleaning_detail_basic():
    """测试基本的智能清理详情记录"""
    print("\n=== 测试1: 基本智能清理详情记录 ===")
    
    # 创建配置
    config = {
        'intelligent_extraction': {
            'enabled': True,
            'text_cleaning': {
                'enabled': True,
                'truncate_delimiters': [
                    {'name': '备注分隔符', 'pattern': r'备注[:：]'}
                ],
                'noise_section_patterns': [
                    {'name': '序号模式', 'pattern': r'^\d+[\.\、]'}
                ]
            }
        },
        'metadata_label_patterns': [r'名称[:：]', r'型号[:：]'],
        'normalization_map': {},
        'feature_split_chars': ['+'],
        'ignore_keywords': [],
        'global_config': {},
        'synonym_map': {},
        'brand_keywords': [],
        'device_type_keywords': []
    }
    
    preprocessor = TextPreprocessor(config)
    
    # 测试文本
    test_text = "名称:温度传感器+型号:T100+量程0-100℃备注:这是备注内容"
    
    # 执行智能清理
    cleaned_text, detail = preprocessor._intelligent_clean_with_detail(test_text)
    
    print(f"原始文本: {test_text}")
    print(f"清理后文本: {cleaned_text}")
    print(f"\n详情信息:")
    print(f"  应用的规则: {detail.applied_rules}")
    print(f"  原始长度: {detail.original_length}")
    print(f"  清理后长度: {detail.cleaned_length}")
    print(f"  删除长度: {detail.deleted_length}")
    print(f"  截断匹配数: {len(detail.truncation_matches)}")
    print(f"  噪音匹配数: {len(detail.noise_pattern_matches)}")
    print(f"  元数据匹配数: {len(detail.metadata_tag_matches)}")
    
    # 验证
    assert detail.original_length == len(test_text)
    assert detail.cleaned_length == len(cleaned_text)
    assert detail.deleted_length == detail.original_length - detail.cleaned_length
    assert detail.before_text == test_text
    assert detail.after_text == cleaned_text
    
    # 验证截断匹配
    if detail.truncation_matches:
        print(f"\n截断匹配详情:")
        for match in detail.truncation_matches:
            print(f"  分隔符: {match.delimiter}")
            print(f"  位置: {match.position}")
            print(f"  删除的文本: {match.deleted_text}")
    
    # 验证元数据匹配
    if detail.metadata_tag_matches:
        print(f"\n元数据匹配详情:")
        for match in detail.metadata_tag_matches:
            print(f"  标签: {match.tag}")
            print(f"  匹配的文本: {match.matched_text}")
            print(f"  位置: {match.position}")
    
    print("\n✓ 测试1通过")


def test_intelligent_cleaning_disabled():
    """测试智能清理未启用时的行为"""
    print("\n=== 测试2: 智能清理未启用 ===")
    
    config = {
        'intelligent_extraction': {
            'enabled': False
        },
        'metadata_label_patterns': [],
        'normalization_map': {},
        'feature_split_chars': ['+'],
        'ignore_keywords': [],
        'global_config': {},
        'synonym_map': {},
        'brand_keywords': [],
        'device_type_keywords': []
    }
    
    preprocessor = TextPreprocessor(config)
    test_text = "名称:温度传感器+型号:T100"
    
    cleaned_text, detail = preprocessor._intelligent_clean_with_detail(test_text)
    
    print(f"原始文本: {test_text}")
    print(f"清理后文本: {cleaned_text}")
    print(f"应用的规则: {detail.applied_rules}")
    
    # 验证未启用时返回原文本
    assert cleaned_text == test_text
    assert detail.applied_rules == []
    assert detail.original_length == len(test_text)
    assert detail.cleaned_length == len(test_text)
    assert detail.deleted_length == 0
    
    print("✓ 测试2通过")


def test_preprocess_with_intelligent_cleaning_detail():
    """测试 preprocess() 方法集成智能清理详情"""
    print("\n=== 测试3: preprocess() 方法集成 ===")
    
    config = {
        'intelligent_extraction': {
            'enabled': True,
            'text_cleaning': {
                'enabled': True,
                'truncate_delimiters': [
                    {'name': '备注分隔符', 'pattern': r'备注[:：]'}
                ]
            }
        },
        'metadata_label_patterns': [r'名称[:：]', r'型号[:：]'],
        'normalization_map': {},
        'feature_split_chars': ['+'],
        'ignore_keywords': [],
        'global_config': {
            'fullwidth_to_halfwidth': True,
            'remove_whitespace': True,
            'unify_lowercase': True
        },
        'synonym_map': {},
        'brand_keywords': [],
        'device_type_keywords': []
    }
    
    preprocessor = TextPreprocessor(config)
    test_text = "名称:温度传感器+型号:T100备注:这是备注"
    
    result = preprocessor.preprocess(test_text)
    
    print(f"原始文本: {result.original}")
    print(f"清理后文本: {result.cleaned}")
    print(f"归一化文本: {result.normalized}")
    print(f"提取的特征: {result.features}")
    
    # 验证智能清理详情已附加
    assert hasattr(result, 'intelligent_cleaning_detail')
    detail = result.intelligent_cleaning_detail
    
    print(f"\n智能清理详情:")
    print(f"  应用的规则: {detail.applied_rules}")
    print(f"  原始长度: {detail.original_length}")
    print(f"  清理后长度: {detail.cleaned_length}")
    print(f"  删除长度: {detail.deleted_length}")
    
    # 验证详情对象可以序列化
    detail_dict = detail.to_dict()
    print(f"\n详情对象序列化:")
    print(json.dumps(detail_dict, ensure_ascii=False, indent=2))
    
    # 验证可以从字典恢复
    restored_detail = IntelligentCleaningDetail.from_dict(detail_dict)
    assert restored_detail.original_length == detail.original_length
    assert restored_detail.cleaned_length == detail.cleaned_length
    assert restored_detail.deleted_length == detail.deleted_length
    
    print("\n✓ 测试3通过")


def test_detail_serialization():
    """测试详情对象的序列化和反序列化"""
    print("\n=== 测试4: 详情对象序列化 ===")
    
    # 创建详情对象
    detail = IntelligentCleaningDetail(
        applied_rules=['truncation', 'metadata_tag'],
        truncation_matches=[
            TruncationMatch(
                delimiter='备注:',
                position=20,
                deleted_text='备注:这是备注内容'
            )
        ],
        noise_pattern_matches=[],
        metadata_tag_matches=[
            MetadataMatch(
                tag='名称:',
                matched_text='名称:',
                position=0
            )
        ],
        original_length=50,
        cleaned_length=30,
        deleted_length=20,
        before_text='名称:温度传感器备注:这是备注内容',
        after_text='温度传感器'
    )
    
    # 序列化
    detail_dict = detail.to_dict()
    print("序列化结果:")
    print(json.dumps(detail_dict, ensure_ascii=False, indent=2))
    
    # 反序列化
    restored_detail = IntelligentCleaningDetail.from_dict(detail_dict)
    
    # 验证
    assert restored_detail.applied_rules == detail.applied_rules
    assert restored_detail.original_length == detail.original_length
    assert restored_detail.cleaned_length == detail.cleaned_length
    assert restored_detail.deleted_length == detail.deleted_length
    assert len(restored_detail.truncation_matches) == len(detail.truncation_matches)
    assert len(restored_detail.metadata_tag_matches) == len(detail.metadata_tag_matches)
    
    print("\n✓ 测试4通过")


if __name__ == '__main__':
    print("开始测试智能清理详情记录功能...")
    
    try:
        test_intelligent_cleaning_detail_basic()
        test_intelligent_cleaning_disabled()
        test_preprocess_with_intelligent_cleaning_detail()
        test_detail_serialization()
        
        print("\n" + "="*50)
        print("所有测试通过! ✓")
        print("="*50)
    except AssertionError as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
