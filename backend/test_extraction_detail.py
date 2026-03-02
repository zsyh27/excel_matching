"""
测试特征提取详情记录功能

验证 Task 23.1 的实现
"""

import json
from modules.text_preprocessor import TextPreprocessor
from modules.match_detail import ExtractionDetail, FeatureDetail, FilteredFeature


def test_extraction_detail_basic():
    """测试基本的特征提取详情记录"""
    print("\n=== 测试1: 基本特征提取详情 ===")
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    # 测试文本
    text = "霍尼韦尔 室内温度传感器 dn15 0-100℃"
    
    # 执行预处理
    result = preprocessor.preprocess(text, mode='matching')
    
    # 验证结果
    print(f"原始文本: {result.original}")
    print(f"清理后: {result.cleaned}")
    print(f"归一化后: {result.normalized}")
    print(f"提取的特征: {result.features}")
    
    # 检查是否有提取详情
    assert hasattr(result, 'extraction_detail'), "PreprocessResult应该包含extraction_detail属性"
    
    detail = result.extraction_detail
    assert isinstance(detail, ExtractionDetail), "extraction_detail应该是ExtractionDetail类型"
    
    # 验证详情内容
    print(f"\n--- 提取详情 ---")
    print(f"使用的分隔符: {detail.split_chars}")
    print(f"识别的品牌: {detail.identified_brands}")
    print(f"识别的设备类型: {detail.identified_device_types}")
    print(f"质量评分规则: {detail.quality_rules}")
    
    print(f"\n提取的特征详情 ({len(detail.extracted_features)} 个):")
    for feat_detail in detail.extracted_features:
        print(f"  - {feat_detail.feature}")
        print(f"    类型: {feat_detail.feature_type}")
        print(f"    来源: {feat_detail.source}")
        print(f"    质量评分: {feat_detail.quality_score}")
        print(f"    位置: {feat_detail.position}")
    
    print(f"\n被过滤的特征 ({len(detail.filtered_features)} 个):")
    for filtered in detail.filtered_features:
        print(f"  - {filtered.feature}")
        print(f"    过滤原因: {filtered.filter_reason}")
        print(f"    质量评分: {filtered.quality_score}")
    
    # 验证必需字段
    assert len(detail.split_chars) > 0, "应该记录使用的分隔符"
    assert len(detail.extracted_features) > 0, "应该有提取的特征详情"
    
    # 验证品牌识别
    if '霍尼韦尔' in text:
        assert 'honeywell' in detail.identified_brands or '霍尼韦尔' in detail.identified_brands, \
            "应该识别出霍尼韦尔品牌"
    
    print("\n✓ 测试1通过")


def test_extraction_detail_with_filtering():
    """测试特征过滤的详情记录"""
    print("\n=== 测试2: 特征过滤详情 ===")
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    # 测试文本（包含一些会被过滤的特征）
    text = "西门子 DDC控制器 a b c 123"
    
    # 执行预处理
    result = preprocessor.preprocess(text, mode='matching')
    
    detail = result.extraction_detail
    
    print(f"原始文本: {text}")
    print(f"提取的特征: {result.features}")
    print(f"\n被过滤的特征 ({len(detail.filtered_features)} 个):")
    
    for filtered in detail.filtered_features:
        print(f"  - '{filtered.feature}' (原因: {filtered.filter_reason}, 质量: {filtered.quality_score})")
    
    # 验证过滤功能
    assert len(detail.filtered_features) > 0, "应该有被过滤的特征"
    
    # 验证过滤原因的有效性
    valid_reasons = ['low_quality', 'duplicate', 'invalid']
    for filtered in detail.filtered_features:
        assert filtered.filter_reason in valid_reasons, \
            f"过滤原因应该是有效值之一: {valid_reasons}"
    
    print("\n✓ 测试2通过")


def test_extraction_detail_serialization():
    """测试提取详情的序列化"""
    print("\n=== 测试3: 提取详情序列化 ===")
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    # 测试文本
    text = "霍尼韦尔温度传感器 dn20 4-20ma"
    
    # 执行预处理
    result = preprocessor.preprocess(text, mode='matching')
    detail = result.extraction_detail
    
    # 序列化为字典
    detail_dict = detail.to_dict()
    
    print(f"序列化后的详情:")
    print(json.dumps(detail_dict, ensure_ascii=False, indent=2))
    
    # 验证字典结构
    assert 'split_chars' in detail_dict, "应该包含split_chars字段"
    assert 'identified_brands' in detail_dict, "应该包含identified_brands字段"
    assert 'identified_device_types' in detail_dict, "应该包含identified_device_types字段"
    assert 'quality_rules' in detail_dict, "应该包含quality_rules字段"
    assert 'extracted_features' in detail_dict, "应该包含extracted_features字段"
    assert 'filtered_features' in detail_dict, "应该包含filtered_features字段"
    
    # 验证特征详情的结构
    if len(detail_dict['extracted_features']) > 0:
        feat = detail_dict['extracted_features'][0]
        assert 'feature' in feat, "特征详情应该包含feature字段"
        assert 'feature_type' in feat, "特征详情应该包含feature_type字段"
        assert 'source' in feat, "特征详情应该包含source字段"
        assert 'quality_score' in feat, "特征详情应该包含quality_score字段"
        assert 'position' in feat, "特征详情应该包含position字段"
    
    # 反序列化
    detail_restored = ExtractionDetail.from_dict(detail_dict)
    
    # 验证反序列化结果
    assert detail_restored.split_chars == detail.split_chars, "反序列化后split_chars应该一致"
    assert detail_restored.identified_brands == detail.identified_brands, "反序列化后identified_brands应该一致"
    assert len(detail_restored.extracted_features) == len(detail.extracted_features), \
        "反序列化后extracted_features数量应该一致"
    
    print("\n✓ 测试3通过")


def test_extraction_detail_requirements():
    """测试需求15.1-15.5的实现"""
    print("\n=== 测试4: 验证需求15.1-15.5 ===")
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    # 测试文本
    text = "西门子DDC控制器 dn15 4-20ma 0-100℃"
    
    # 执行预处理
    result = preprocessor.preprocess(text, mode='matching')
    detail = result.extraction_detail
    
    # 需求15.1: 显示使用的所有分隔符列表
    print(f"✓ 需求15.1 - 分隔符列表: {detail.split_chars}")
    assert len(detail.split_chars) > 0, "应该记录使用的分隔符"
    
    # 需求15.2: 显示识别出的品牌关键词和设备类型关键词
    print(f"✓ 需求15.2 - 品牌关键词: {detail.identified_brands}")
    print(f"✓ 需求15.2 - 设备类型关键词: {detail.identified_device_types}")
    assert isinstance(detail.identified_brands, list), "品牌关键词应该是列表"
    assert isinstance(detail.identified_device_types, list), "设备类型关键词应该是列表"
    
    # 需求15.3: 显示应用的特征质量评分规则
    print(f"✓ 需求15.3 - 质量评分规则: {detail.quality_rules}")
    assert isinstance(detail.quality_rules, dict), "质量评分规则应该是字典"
    
    # 需求15.4: 标注每个特征的来源
    print(f"✓ 需求15.4 - 特征来源标注:")
    for feat_detail in detail.extracted_features:
        print(f"  - {feat_detail.feature}: 来源={feat_detail.source}, 类型={feat_detail.feature_type}")
        assert feat_detail.source in ['brand_keywords', 'device_type_keywords', 'parameter_recognition', 
                                       'smart_split', 'complex_parameter_decomposition'], \
            f"特征来源应该是有效值: {feat_detail.source}"
    
    # 需求15.5: 显示过滤原因
    print(f"✓ 需求15.5 - 过滤原因:")
    for filtered in detail.filtered_features:
        print(f"  - {filtered.feature}: 原因={filtered.filter_reason}, 质量={filtered.quality_score}")
        assert filtered.filter_reason in ['low_quality', 'duplicate', 'invalid'], \
            f"过滤原因应该是有效值: {filtered.filter_reason}"
    
    print("\n✓ 测试4通过 - 所有需求验证通过")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("特征提取详情记录功能测试")
    print("=" * 60)
    
    try:
        test_extraction_detail_basic()
        test_extraction_detail_with_filtering()
        test_extraction_detail_serialization()
        test_extraction_detail_requirements()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
