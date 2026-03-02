"""
集成测试：验证智能清理详情记录与匹配引擎的集成

测试智能清理详情能够正确地通过 PreprocessResult 传递到 MatchDetail
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.text_preprocessor import TextPreprocessor
import json


def test_real_world_scenario():
    """测试真实场景：包含多种清理规则的文本"""
    print("\n=== 真实场景测试 ===")
    
    # 加载实际配置
    config_path = 'data/static_config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        preprocessor = TextPreprocessor(config)
        
        # 测试文本：包含元数据标签、备注等
        test_cases = [
            "1.名称:室内温度传感器+2.型号:T100+3.量程:0-50℃备注:用于空调系统",
            "温度传感器(T100)+湿度传感器(H200)备注:配套使用",
            "霍尼韦尔温度传感器+西门子控制器备注:进口设备"
        ]
        
        for i, test_text in enumerate(test_cases, 1):
            print(f"\n--- 测试用例 {i} ---")
            print(f"原始文本: {test_text}")
            
            result = preprocessor.preprocess(test_text)
            
            print(f"清理后文本: {result.cleaned}")
            print(f"归一化文本: {result.normalized}")
            print(f"提取的特征: {result.features}")
            
            if hasattr(result, 'intelligent_cleaning_detail'):
                detail = result.intelligent_cleaning_detail
                print(f"\n智能清理详情:")
                print(f"  应用的规则: {detail.applied_rules}")
                print(f"  删除长度: {detail.deleted_length}")
                
                if detail.truncation_matches:
                    print(f"  截断匹配:")
                    for match in detail.truncation_matches:
                        print(f"    - 分隔符: {match.delimiter}, 删除: {match.deleted_text[:20]}...")
                
                if detail.metadata_tag_matches:
                    print(f"  元数据匹配: {len(detail.metadata_tag_matches)} 个")
                
                # 验证详情对象可以序列化
                detail_dict = detail.to_dict()
                assert 'applied_rules' in detail_dict
                assert 'original_length' in detail_dict
                assert 'cleaned_length' in detail_dict
                
                print(f"  ✓ 详情对象序列化成功")
            else:
                print("  (智能清理未启用)")
        
        print("\n✓ 真实场景测试通过")
    else:
        print(f"配置文件不存在: {config_path}")
        print("跳过真实场景测试")


def test_empty_and_edge_cases():
    """测试边缘情况"""
    print("\n=== 边缘情况测试 ===")
    
    config = {
        'intelligent_extraction': {
            'enabled': True,
            'text_cleaning': {
                'enabled': True,
                'truncate_delimiters': [
                    {'name': '备注', 'pattern': r'备注[:：]'}
                ],
                'noise_section_patterns': []
            }
        },
        'metadata_label_patterns': [r'名称[:：]'],
        'normalization_map': {},
        'feature_split_chars': ['+'],
        'ignore_keywords': [],
        'global_config': {},
        'synonym_map': {},
        'brand_keywords': [],
        'device_type_keywords': []
    }
    
    preprocessor = TextPreprocessor(config)
    
    # 测试空文本
    print("\n1. 空文本")
    result = preprocessor.preprocess("")
    assert result.original == ""
    assert result.cleaned == ""
    print("  ✓ 空文本处理正确")
    
    # 测试没有任何匹配的文本
    print("\n2. 没有匹配的文本")
    result = preprocessor.preprocess("温度传感器+湿度传感器")
    if hasattr(result, 'intelligent_cleaning_detail'):
        detail = result.intelligent_cleaning_detail
        assert detail.deleted_length == 0
        assert len(detail.truncation_matches) == 0
        print(f"  应用的规则: {detail.applied_rules}")
        print("  ✓ 无匹配情况处理正确")
    
    # 测试只有截断的文本
    print("\n3. 只有截断的文本")
    result = preprocessor.preprocess("温度传感器备注:这是备注")
    if hasattr(result, 'intelligent_cleaning_detail'):
        detail = result.intelligent_cleaning_detail
        assert detail.deleted_length > 0
        assert len(detail.truncation_matches) == 1
        print(f"  删除长度: {detail.deleted_length}")
        print("  ✓ 截断处理正确")
    
    print("\n✓ 边缘情况测试通过")


def test_detail_completeness():
    """测试详情对象的完整性"""
    print("\n=== 详情完整性测试 ===")
    
    config = {
        'intelligent_extraction': {
            'enabled': True,
            'text_cleaning': {
                'enabled': True,
                'truncate_delimiters': [
                    {'name': '备注', 'pattern': r'备注[:：]'}
                ],
                'noise_section_patterns': [
                    {'name': '序号', 'pattern': r'^\d+[\.\、]'}
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
    test_text = "1.名称:温度传感器+型号:T100备注:这是备注"
    
    result = preprocessor.preprocess(test_text)
    
    # 验证 PreprocessResult 的基本字段
    assert hasattr(result, 'original')
    assert hasattr(result, 'cleaned')
    assert hasattr(result, 'normalized')
    assert hasattr(result, 'features')
    print("✓ PreprocessResult 基本字段完整")
    
    # 验证智能清理详情字段
    assert hasattr(result, 'intelligent_cleaning_detail')
    detail = result.intelligent_cleaning_detail
    print("✓ intelligent_cleaning_detail 字段存在")
    
    # 验证详情对象的所有必需字段
    required_fields = [
        'applied_rules',
        'truncation_matches',
        'noise_pattern_matches',
        'metadata_tag_matches',
        'original_length',
        'cleaned_length',
        'deleted_length',
        'before_text',
        'after_text'
    ]
    
    for field in required_fields:
        assert hasattr(detail, field), f"缺少字段: {field}"
    print(f"✓ 所有必需字段存在: {', '.join(required_fields)}")
    
    # 验证统计信息的一致性
    assert detail.original_length == len(detail.before_text)
    assert detail.cleaned_length == len(detail.after_text)
    assert detail.deleted_length == detail.original_length - detail.cleaned_length
    print("✓ 统计信息一致性验证通过")
    
    # 验证序列化和反序列化
    detail_dict = detail.to_dict()
    from modules.match_detail import IntelligentCleaningDetail
    restored_detail = IntelligentCleaningDetail.from_dict(detail_dict)
    
    assert restored_detail.original_length == detail.original_length
    assert restored_detail.cleaned_length == detail.cleaned_length
    assert restored_detail.deleted_length == detail.deleted_length
    assert len(restored_detail.applied_rules) == len(detail.applied_rules)
    print("✓ 序列化/反序列化验证通过")
    
    print("\n✓ 详情完整性测试通过")


if __name__ == '__main__':
    print("开始集成测试...")
    
    try:
        test_real_world_scenario()
        test_empty_and_edge_cases()
        test_detail_completeness()
        
        print("\n" + "="*50)
        print("所有集成测试通过! ✓")
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
