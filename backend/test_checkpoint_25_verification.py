"""
任务25检查点验证测试

验证所有新的详情记录功能:
- 智能清理详情记录
- 归一化详情记录
- 特征提取详情记录
- PreprocessResult数据结构更新
"""

import json
from modules.text_preprocessor import TextPreprocessor, PreprocessResult
from modules.match_detail import (
    IntelligentCleaningDetail, 
    NormalizationDetail, 
    ExtractionDetail
)


def test_all_detail_recording():
    """测试所有详情记录功能的完整性"""
    print("\n" + "=" * 80)
    print("任务25检查点验证 - 后端详情记录增强")
    print("=" * 80)
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    # 测试文本
    test_text = "霍尼韦尔室内温度传感器 dn15 4-20ma 0-100℃"
    
    print(f"\n测试文本: {test_text}")
    print("-" * 80)
    
    # 执行预处理
    result = preprocessor.preprocess(test_text, mode='matching')
    
    # 验证基本结构
    print("\n【1】验证 PreprocessResult 基本结构")
    assert isinstance(result, PreprocessResult), "结果应该是PreprocessResult类型"
    assert hasattr(result, 'original'), "应该有original字段"
    assert hasattr(result, 'cleaned'), "应该有cleaned字段"
    assert hasattr(result, 'normalized'), "应该有normalized字段"
    assert hasattr(result, 'features'), "应该有features字段"
    print("  ✓ 基本字段完整")
    
    # 验证智能清理详情
    print("\n【2】验证智能清理详情记录 (任务21)")
    assert hasattr(result, 'intelligent_cleaning_detail'), "应该有intelligent_cleaning_detail字段"
    assert result.intelligent_cleaning_detail is not None, "intelligent_cleaning_detail不应该为None"
    assert isinstance(result.intelligent_cleaning_detail, IntelligentCleaningDetail), \
        "intelligent_cleaning_detail应该是IntelligentCleaningDetail类型"
    
    cleaning = result.intelligent_cleaning_detail
    assert hasattr(cleaning, 'applied_rules'), "应该有applied_rules字段"
    assert hasattr(cleaning, 'truncation_matches'), "应该有truncation_matches字段"
    assert hasattr(cleaning, 'noise_pattern_matches'), "应该有noise_pattern_matches字段"
    assert hasattr(cleaning, 'metadata_tag_matches'), "应该有metadata_tag_matches字段"
    assert hasattr(cleaning, 'original_length'), "应该有original_length字段"
    assert hasattr(cleaning, 'cleaned_length'), "应该有cleaned_length字段"
    assert hasattr(cleaning, 'deleted_length'), "应该有deleted_length字段"
    assert hasattr(cleaning, 'before_text'), "应该有before_text字段"
    assert hasattr(cleaning, 'after_text'), "应该有after_text字段"
    
    print(f"  ✓ 智能清理详情完整")
    print(f"    - 应用规则: {cleaning.applied_rules}")
    print(f"    - 原始长度: {cleaning.original_length}")
    print(f"    - 清理后长度: {cleaning.cleaned_length}")
    print(f"    - 删除长度: {cleaning.deleted_length}")
    
    # 验证归一化详情
    print("\n【3】验证归一化详情记录 (任务22)")
    assert hasattr(result, 'normalization_detail'), "应该有normalization_detail字段"
    assert result.normalization_detail is not None, "normalization_detail不应该为None"
    assert isinstance(result.normalization_detail, NormalizationDetail), \
        "normalization_detail应该是NormalizationDetail类型"
    
    normalization = result.normalization_detail
    assert hasattr(normalization, 'synonym_mappings'), "应该有synonym_mappings字段"
    assert hasattr(normalization, 'normalization_mappings'), "应该有normalization_mappings字段"
    assert hasattr(normalization, 'global_configs'), "应该有global_configs字段"
    assert hasattr(normalization, 'before_text'), "应该有before_text字段"
    assert hasattr(normalization, 'after_text'), "应该有after_text字段"
    
    print(f"  ✓ 归一化详情完整")
    print(f"    - 同义词映射: {len(normalization.synonym_mappings)} 个")
    print(f"    - 归一化映射: {len(normalization.normalization_mappings)} 个")
    print(f"    - 全局配置: {normalization.global_configs}")
    
    # 验证特征提取详情
    print("\n【4】验证特征提取详情记录 (任务23)")
    assert hasattr(result, 'extraction_detail'), "应该有extraction_detail字段"
    assert result.extraction_detail is not None, "extraction_detail不应该为None"
    assert isinstance(result.extraction_detail, ExtractionDetail), \
        "extraction_detail应该是ExtractionDetail类型"
    
    extraction = result.extraction_detail
    assert hasattr(extraction, 'split_chars'), "应该有split_chars字段"
    assert hasattr(extraction, 'identified_brands'), "应该有identified_brands字段"
    assert hasattr(extraction, 'identified_device_types'), "应该有identified_device_types字段"
    assert hasattr(extraction, 'quality_rules'), "应该有quality_rules字段"
    assert hasattr(extraction, 'extracted_features'), "应该有extracted_features字段"
    assert hasattr(extraction, 'filtered_features'), "应该有filtered_features字段"
    
    print(f"  ✓ 特征提取详情完整")
    print(f"    - 分隔符: {extraction.split_chars}")
    print(f"    - 识别品牌: {extraction.identified_brands}")
    print(f"    - 识别设备类型: {extraction.identified_device_types}")
    print(f"    - 提取特征: {len(extraction.extracted_features)} 个")
    print(f"    - 过滤特征: {len(extraction.filtered_features)} 个")
    
    # 验证序列化
    print("\n【5】验证数据序列化 (任务24)")
    result_dict = result.to_dict()
    
    assert 'intelligent_cleaning' in result_dict, "序列化应该包含intelligent_cleaning"
    assert 'normalization_detail' in result_dict, "序列化应该包含normalization_detail"
    assert 'extraction_detail' in result_dict, "序列化应该包含extraction_detail"
    
    print("  ✓ 序列化成功")
    print(f"    - 序列化键: {list(result_dict.keys())}")
    
    # 验证反序列化
    result_restored = PreprocessResult.from_dict(result_dict)
    
    assert result_restored.intelligent_cleaning_detail is not None, "反序列化应该恢复intelligent_cleaning_detail"
    assert result_restored.normalization_detail is not None, "反序列化应该恢复normalization_detail"
    assert result_restored.extraction_detail is not None, "反序列化应该恢复extraction_detail"
    
    print("  ✓ 反序列化成功")
    
    # 验证数据完整性
    print("\n【6】验证数据完整性")
    
    # 智能清理详情完整性
    assert cleaning.original_length >= cleaning.cleaned_length, \
        "原始长度应该大于等于清理后长度"
    assert cleaning.deleted_length == cleaning.original_length - cleaning.cleaned_length, \
        "删除长度应该等于原始长度减清理后长度"
    print("  ✓ 智能清理数据一致性验证通过")
    
    # 归一化详情完整性
    assert normalization.before_text is not None, "归一化前文本不应该为None"
    assert normalization.after_text is not None, "归一化后文本不应该为None"
    print("  ✓ 归一化数据一致性验证通过")
    
    # 特征提取详情完整性
    assert len(extraction.split_chars) > 0, "应该有分隔符"
    assert len(extraction.extracted_features) > 0, "应该有提取的特征"
    
    # 验证每个特征详情的结构
    for feat_detail in extraction.extracted_features:
        assert hasattr(feat_detail, 'feature'), "特征详情应该有feature字段"
        assert hasattr(feat_detail, 'feature_type'), "特征详情应该有feature_type字段"
        assert hasattr(feat_detail, 'source'), "特征详情应该有source字段"
        assert hasattr(feat_detail, 'quality_score'), "特征详情应该有quality_score字段"
        assert hasattr(feat_detail, 'position'), "特征详情应该有position字段"
    
    print("  ✓ 特征提取数据一致性验证通过")
    
    # 最终总结
    print("\n" + "=" * 80)
    print("✓ 任务25检查点验证通过!")
    print("=" * 80)
    print("\n验证结果:")
    print("  ✓ 任务21: 智能清理详情记录 - 完成")
    print("  ✓ 任务22: 归一化详情记录 - 完成")
    print("  ✓ 任务23: 特征提取详情记录 - 完成")
    print("  ✓ 任务24: PreprocessResult数据结构更新 - 完成")
    print("\n所有新的详情记录功能测试通过!")
    print("数据结构的完整性和正确性已验证!")
    print("=" * 80)
    
    return True


if __name__ == '__main__':
    try:
        test_all_detail_recording()
        exit(0)
    except AssertionError as e:
        print(f"\n✗ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
