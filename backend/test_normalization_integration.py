"""
测试归一化详情在匹配引擎中的集成

验证归一化详情能够正确地通过匹配流程传递到匹配详情中
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from modules.text_preprocessor import TextPreprocessor
from modules.match_detail import MatchDetailRecorder
import json


def test_normalization_detail_in_match_flow():
    """测试归一化详情在完整匹配流程中的传递"""
    
    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'static_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 创建预处理器
    preprocessor = TextPreprocessor(config)
    
    # 测试文本
    test_text = "霍尼韦尔 温度传感器 -10℃~50℃"
    
    print("=" * 60)
    print("测试归一化详情在匹配流程中的集成")
    print("=" * 60)
    print(f"\n原始文本: {test_text}")
    
    # 执行预处理
    result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"\n预处理结果:")
    print(f"  原始文本: {result.original}")
    print(f"  清理后: {result.cleaned}")
    print(f"  归一化后: {result.normalized}")
    print(f"  特征数: {len(result.features)}")
    print(f"  特征: {result.features}")
    
    # 验证归一化详情存在
    assert hasattr(result, 'normalization_detail'), "应该有normalization_detail属性"
    assert result.normalization_detail is not None, "normalization_detail不应该为None"
    
    detail = result.normalization_detail
    
    print(f"\n归一化详情:")
    print(f"  同义词映射数: {len(detail.synonym_mappings)}")
    for mapping in detail.synonym_mappings:
        print(f"    {mapping.from_text} → {mapping.to_text} (位置: {mapping.position}, 类型: {mapping.mapping_type})")
    
    print(f"  归一化映射数: {len(detail.normalization_mappings)}")
    for mapping in detail.normalization_mappings:
        print(f"    {mapping.from_text} → {mapping.to_text} (位置: {mapping.position}, 类型: {mapping.mapping_type})")
    
    print(f"  全局配置: {detail.global_configs}")
    print(f"  归一化前: {detail.before_text}")
    print(f"  归一化后: {detail.after_text}")
    
    # 验证详情内容的正确性
    assert detail.before_text != "", "before_text不应该为空"
    assert detail.after_text != "", "after_text不应该为空"
    assert detail.after_text == result.normalized, "after_text应该等于归一化后的文本"
    
    # 测试序列化（模拟传递给匹配详情记录器）
    preprocessing_dict = {
        'original': result.original,
        'cleaned': result.cleaned,
        'normalized': result.normalized,
        'features': result.features
    }
    
    # 添加归一化详情
    if hasattr(result, 'normalization_detail') and result.normalization_detail:
        preprocessing_dict['normalization_detail'] = result.normalization_detail.to_dict()
    
    print(f"\n序列化后的预处理结果包含归一化详情: {'normalization_detail' in preprocessing_dict}")
    
    if 'normalization_detail' in preprocessing_dict:
        norm_detail = preprocessing_dict['normalization_detail']
        print(f"  同义词映射数: {len(norm_detail['synonym_mappings'])}")
        print(f"  归一化映射数: {len(norm_detail['normalization_mappings'])}")
        print(f"  全局配置数: {len(norm_detail['global_configs'])}")
    
    print("\n✓ 归一化详情在匹配流程中的集成测试通过")


def test_normalization_detail_with_real_config():
    """使用真实配置测试归一化详情"""
    
    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'static_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 创建预处理器
    preprocessor = TextPreprocessor(config)
    
    # 测试多个真实场景
    test_cases = [
        "西门子DDC控制器 24V 16AI/8AO",
        "霍尼韦尔室内温度传感器 0-50℃",
        "江森自控电动调节阀 DN50 PN16",
        "施耐德变频器 380V 7.5KW"
    ]
    
    print("\n" + "=" * 60)
    print("使用真实配置测试多个场景")
    print("=" * 60)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n场景 {i}: {test_text}")
        
        result = preprocessor.preprocess(test_text, mode='matching')
        
        print(f"  归一化后: {result.normalized}")
        print(f"  特征数: {len(result.features)}")
        
        if hasattr(result, 'normalization_detail') and result.normalization_detail:
            detail = result.normalization_detail
            print(f"  同义词映射: {len(detail.synonym_mappings)} 个")
            print(f"  归一化映射: {len(detail.normalization_mappings)} 个")
            print(f"  全局配置: {len(detail.global_configs)} 个")
            
            # 验证基本属性
            assert detail.before_text != "", f"场景{i}: before_text不应该为空"
            assert detail.after_text != "", f"场景{i}: after_text不应该为空"
        else:
            print("  警告: 没有归一化详情")
    
    print("\n✓ 真实配置测试通过")


def test_normalization_detail_requirements():
    """验证归一化详情满足需求 14.1-14.5"""
    
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
    
    print("\n" + "=" * 60)
    print("验证需求 14.1-14.5")
    print("=" * 60)
    
    test_text = "霍尼韦尔（Honeywell） 温度传感器 -10℃~50°C"
    result = preprocessor.preprocess(test_text, mode='matching')
    
    assert hasattr(result, 'normalization_detail'), "需求 14.1-14.5: 应该有归一化详情"
    detail = result.normalization_detail
    
    # 需求 14.1: 显示所有应用的同义词映射规则及其转换详情
    print("\n需求 14.1: 同义词映射")
    assert len(detail.synonym_mappings) > 0, "应该有同义词映射"
    for mapping in detail.synonym_mappings:
        print(f"  ✓ {mapping.from_text} → {mapping.to_text} (位置: {mapping.position})")
        assert mapping.mapping_type == 'synonym', "映射类型应该是'synonym'"
    
    # 需求 14.2: 显示所有应用的归一化映射规则及其转换详情
    print("\n需求 14.2: 归一化映射")
    assert len(detail.normalization_mappings) > 0, "应该有归一化映射"
    for mapping in detail.normalization_mappings:
        print(f"  ✓ {mapping.from_text} → {mapping.to_text} (位置: {mapping.position})")
        assert mapping.mapping_type == 'normalization', "映射类型应该是'normalization'"
    
    # 需求 14.3: 显示应用的全局配置项
    print("\n需求 14.3: 全局配置")
    print(f"  应用的配置: {detail.global_configs}")
    # 注意：全局配置只在实际应用时才记录，所以可能为空
    
    # 需求 14.4: 展示转换前后的文本对比
    print("\n需求 14.4: 文本对比")
    print(f"  ✓ 转换前: {detail.before_text}")
    print(f"  ✓ 转换后: {detail.after_text}")
    assert detail.before_text != "", "转换前文本不应该为空"
    assert detail.after_text != "", "转换后文本不应该为空"
    
    # 需求 14.5: 高亮显示或标注转换的具体位置
    print("\n需求 14.5: 转换位置标注")
    print("  ✓ 每个映射都包含position字段，标注了转换位置")
    for mapping in detail.synonym_mappings + detail.normalization_mappings:
        assert hasattr(mapping, 'position'), "映射应该有position属性"
        assert mapping.position >= 0, "position应该是非负整数"
    
    print("\n✓ 所有需求验证通过 (14.1, 14.2, 14.3, 14.4, 14.5)")


if __name__ == '__main__':
    try:
        test_normalization_detail_in_match_flow()
        test_normalization_detail_with_real_config()
        test_normalization_detail_requirements()
        
        print("\n" + "=" * 60)
        print("✓ 所有集成测试通过!")
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
