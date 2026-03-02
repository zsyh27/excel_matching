"""
集成测试：验证特征提取详情在匹配流程中的完整性

验证 Task 23.1 与匹配引擎的集成
"""

import json
from modules.text_preprocessor import TextPreprocessor
from modules.match_detail import ExtractionDetail


def test_preprocess_result_has_extraction_detail():
    """测试PreprocessResult包含extraction_detail"""
    print("\n=== 集成测试1: PreprocessResult包含extraction_detail ===")
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    # 测试多个场景
    test_cases = [
        "霍尼韦尔温度传感器 dn15 4-20ma",
        "西门子DDC控制器 0-100℃",
        "江森自控阀门 dn20",
        "贝尔莫压力传感器 0-1000pa"
    ]
    
    for text in test_cases:
        print(f"\n测试文本: {text}")
        result = preprocessor.preprocess(text, mode='matching')
        
        # 验证extraction_detail存在
        assert hasattr(result, 'extraction_detail'), \
            f"PreprocessResult应该包含extraction_detail属性"
        
        assert isinstance(result.extraction_detail, ExtractionDetail), \
            f"extraction_detail应该是ExtractionDetail类型"
        
        detail = result.extraction_detail
        
        # 验证核心字段
        assert isinstance(detail.split_chars, list), "split_chars应该是列表"
        assert isinstance(detail.identified_brands, list), "identified_brands应该是列表"
        assert isinstance(detail.identified_device_types, list), "identified_device_types应该是列表"
        assert isinstance(detail.quality_rules, dict), "quality_rules应该是字典"
        assert isinstance(detail.extracted_features, list), "extracted_features应该是列表"
        assert isinstance(detail.filtered_features, list), "filtered_features应该是列表"
        
        print(f"  ✓ 提取了 {len(detail.extracted_features)} 个特征")
        print(f"  ✓ 过滤了 {len(detail.filtered_features)} 个特征")
        print(f"  ✓ 识别品牌: {detail.identified_brands}")
        print(f"  ✓ 识别设备类型: {detail.identified_device_types}")
    
    print("\n✓ 集成测试1通过")


def test_extraction_detail_completeness():
    """测试提取详情的完整性（Property 16）"""
    print("\n=== 集成测试2: 提取详情完整性（Property 16） ===")
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    # 测试文本
    text = "霍尼韦尔室内温度传感器 dn15 4-20ma 0-100℃"
    
    result = preprocessor.preprocess(text, mode='matching')
    detail = result.extraction_detail
    
    # Property 16: 特征提取详情数据完整性
    # 应该包含所有核心字段
    
    print("验证 Property 16: 特征提取详情数据完整性")
    
    # 需求15.1: 使用的分隔符列表
    assert hasattr(detail, 'split_chars'), "应该有split_chars字段"
    assert isinstance(detail.split_chars, list), "split_chars应该是列表"
    assert len(detail.split_chars) > 0, "split_chars不应该为空"
    print(f"  ✓ 分隔符列表: {detail.split_chars}")
    
    # 需求15.2: 识别出的品牌和设备类型关键词
    assert hasattr(detail, 'identified_brands'), "应该有identified_brands字段"
    assert hasattr(detail, 'identified_device_types'), "应该有identified_device_types字段"
    assert isinstance(detail.identified_brands, list), "identified_brands应该是列表"
    assert isinstance(detail.identified_device_types, list), "identified_device_types应该是列表"
    print(f"  ✓ 品牌关键词: {detail.identified_brands}")
    print(f"  ✓ 设备类型关键词: {detail.identified_device_types}")
    
    # 需求15.3: 质量评分规则
    assert hasattr(detail, 'quality_rules'), "应该有quality_rules字段"
    assert isinstance(detail.quality_rules, dict), "quality_rules应该是字典"
    print(f"  ✓ 质量评分规则: {len(detail.quality_rules)} 条规则")
    
    # 需求15.4: 提取的特征详情列表
    assert hasattr(detail, 'extracted_features'), "应该有extracted_features字段"
    assert isinstance(detail.extracted_features, list), "extracted_features应该是列表"
    print(f"  ✓ 提取的特征: {len(detail.extracted_features)} 个")
    
    # 验证每个特征详情的结构
    for feat_detail in detail.extracted_features:
        assert hasattr(feat_detail, 'feature'), "特征详情应该有feature字段"
        assert hasattr(feat_detail, 'feature_type'), "特征详情应该有feature_type字段"
        assert hasattr(feat_detail, 'source'), "特征详情应该有source字段"
        assert hasattr(feat_detail, 'quality_score'), "特征详情应该有quality_score字段"
        assert hasattr(feat_detail, 'position'), "特征详情应该有position字段"
        
        # 验证feature_type的有效性
        assert feat_detail.feature_type in ['brand', 'device_type', 'model', 'parameter'], \
            f"feature_type应该是有效值: {feat_detail.feature_type}"
        
        # 验证source的有效性
        valid_sources = ['brand_keywords', 'device_type_keywords', 'parameter_recognition', 
                        'smart_split', 'complex_parameter_decomposition']
        assert feat_detail.source in valid_sources, \
            f"source应该是有效值: {feat_detail.source}"
    
    # 需求15.5: 被过滤的特征列表
    assert hasattr(detail, 'filtered_features'), "应该有filtered_features字段"
    assert isinstance(detail.filtered_features, list), "filtered_features应该是列表"
    print(f"  ✓ 过滤的特征: {len(detail.filtered_features)} 个")
    
    # 验证每个过滤特征的结构
    for filtered in detail.filtered_features:
        assert hasattr(filtered, 'feature'), "过滤特征应该有feature字段"
        assert hasattr(filtered, 'filter_reason'), "过滤特征应该有filter_reason字段"
        assert hasattr(filtered, 'quality_score'), "过滤特征应该有quality_score字段"
        
        # 验证filter_reason的有效性
        assert filtered.filter_reason in ['low_quality', 'duplicate', 'invalid'], \
            f"filter_reason应该是有效值: {filtered.filter_reason}"
    
    print("\n✓ 集成测试2通过 - Property 16验证通过")


def test_extraction_detail_with_different_modes():
    """测试不同模式下的提取详情"""
    print("\n=== 集成测试3: 不同模式下的提取详情 ===")
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    # 测试文本
    text = "霍尼韦尔温度传感器 dn15 0-100℃"
    
    # 测试matching模式
    print("\n测试 matching 模式:")
    result_matching = preprocessor.preprocess(text, mode='matching')
    detail_matching = result_matching.extraction_detail
    
    print(f"  特征数量: {len(result_matching.features)}")
    print(f"  提取详情: {len(detail_matching.extracted_features)} 个特征详情")
    
    # 测试device模式
    print("\n测试 device 模式:")
    result_device = preprocessor.preprocess(text, mode='device')
    detail_device = result_device.extraction_detail
    
    print(f"  特征数量: {len(result_device.features)}")
    print(f"  提取详情: {len(detail_device.extracted_features)} 个特征详情")
    
    # 两种模式都应该有提取详情
    assert detail_matching is not None, "matching模式应该有提取详情"
    assert detail_device is not None, "device模式应该有提取详情"
    
    print("\n✓ 集成测试3通过")


def test_extraction_detail_edge_cases():
    """测试边缘情况"""
    print("\n=== 集成测试4: 边缘情况 ===")
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    # 测试空文本
    print("\n测试空文本:")
    result_empty = preprocessor.preprocess("", mode='matching')
    assert hasattr(result_empty, 'extraction_detail'), "空文本也应该有extraction_detail"
    assert len(result_empty.features) == 0, "空文本应该没有特征"
    assert len(result_empty.extraction_detail.extracted_features) == 0, "空文本应该没有特征详情"
    print("  ✓ 空文本处理正确")
    
    # 测试只有品牌的文本
    print("\n测试只有品牌:")
    result_brand = preprocessor.preprocess("霍尼韦尔", mode='matching')
    detail_brand = result_brand.extraction_detail
    print(f"  识别品牌: {detail_brand.identified_brands}")
    assert len(detail_brand.identified_brands) > 0, "应该识别出品牌"
    print("  ✓ 品牌识别正确")
    
    # 测试只有数字的文本
    print("\n测试只有数字:")
    result_number = preprocessor.preprocess("123 456", mode='matching')
    detail_number = result_number.extraction_detail
    print(f"  提取特征: {result_number.features}")
    print(f"  过滤特征: {len(detail_number.filtered_features)} 个")
    print("  ✓ 数字处理正确")
    
    # 测试特殊字符
    print("\n测试特殊字符:")
    result_special = preprocessor.preprocess("传感器@#$%", mode='matching')
    detail_special = result_special.extraction_detail
    print(f"  提取特征: {result_special.features}")
    assert len(detail_special.extracted_features) > 0, "应该提取出有效特征"
    print("  ✓ 特殊字符处理正确")
    
    print("\n✓ 集成测试4通过")


def main():
    """运行所有集成测试"""
    print("=" * 60)
    print("特征提取详情集成测试")
    print("=" * 60)
    
    try:
        test_preprocess_result_has_extraction_detail()
        test_extraction_detail_completeness()
        test_extraction_detail_with_different_modes()
        test_extraction_detail_edge_cases()
        
        print("\n" + "=" * 60)
        print("✓ 所有集成测试通过!")
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
