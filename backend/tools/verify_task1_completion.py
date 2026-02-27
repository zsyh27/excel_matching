"""
任务1完成验证脚本

验证以下内容:
1. data/static_config.json 包含设备行识别配置
2. backend/modules/device_row_classifier.py 文件存在
3. 数据模型类正确定义: RowAnalysisResult, AnalysisContext, ProbabilityLevel
4. 配置包含所有必需字段
"""

import sys
import json
import os

sys.path.insert(0, 'backend')

def verify_config_file():
    """验证配置文件"""
    print("1. 验证配置文件...")
    
    config_path = 'data/static_config.json'
    assert os.path.exists(config_path), "配置文件不存在"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    assert 'device_row_recognition' in config, "缺少device_row_recognition配置"
    
    dr_config = config['device_row_recognition']
    
    # 验证评分权重
    assert 'scoring_weights' in dr_config, "缺少scoring_weights"
    weights = dr_config['scoring_weights']
    assert 'data_type' in weights, "缺少data_type权重"
    assert 'structure' in weights, "缺少structure权重"
    assert 'industry' in weights, "缺少industry权重"
    assert weights['data_type'] == 0.30, "data_type权重不正确"
    assert weights['structure'] == 0.35, "structure权重不正确"
    assert weights['industry'] == 0.35, "industry权重不正确"
    
    # 验证概率阈值
    assert 'probability_thresholds' in dr_config, "缺少probability_thresholds"
    thresholds = dr_config['probability_thresholds']
    assert 'high' in thresholds, "缺少high阈值"
    assert 'medium' in thresholds, "缺少medium阈值"
    assert thresholds['high'] == 70.0, "high阈值不正确"
    assert thresholds['medium'] == 40.0, "medium阈值不正确"
    
    # 验证行业词库
    assert 'industry_keywords' in dr_config, "缺少industry_keywords"
    keywords = dr_config['industry_keywords']
    assert 'device_types' in keywords, "缺少device_types词库"
    assert 'parameters' in keywords, "缺少parameters词库"
    assert 'brands' in keywords, "缺少brands词库"
    assert 'model_patterns' in keywords, "缺少model_patterns词库"
    
    assert len(keywords['device_types']) > 0, "device_types词库为空"
    assert len(keywords['parameters']) > 0, "parameters词库为空"
    assert len(keywords['brands']) > 0, "brands词库为空"
    assert len(keywords['model_patterns']) > 0, "model_patterns词库为空"
    
    print("   ✓ 配置文件验证通过")
    print(f"   - 设备类型词库: {len(keywords['device_types'])} 个")
    print(f"   - 参数词库: {len(keywords['parameters'])} 个")
    print(f"   - 品牌词库: {len(keywords['brands'])} 个")
    print(f"   - 型号模式: {len(keywords['model_patterns'])} 个")
    
    return config


def verify_classifier_file():
    """验证分类器文件"""
    print("\n2. 验证分类器文件...")
    
    classifier_path = 'backend/modules/device_row_classifier.py'
    assert os.path.exists(classifier_path), "分类器文件不存在"
    
    print("   ✓ 分类器文件存在")


def verify_data_models():
    """验证数据模型"""
    print("\n3. 验证数据模型...")
    
    from modules.device_row_classifier import (
        DeviceRowClassifier,
        RowAnalysisResult,
        AnalysisContext,
        ProbabilityLevel
    )
    
    # 验证ProbabilityLevel枚举
    assert hasattr(ProbabilityLevel, 'HIGH'), "缺少HIGH枚举值"
    assert hasattr(ProbabilityLevel, 'MEDIUM'), "缺少MEDIUM枚举值"
    assert hasattr(ProbabilityLevel, 'LOW'), "缺少LOW枚举值"
    assert ProbabilityLevel.HIGH.value == 'high', "HIGH值不正确"
    assert ProbabilityLevel.MEDIUM.value == 'medium', "MEDIUM值不正确"
    assert ProbabilityLevel.LOW.value == 'low', "LOW值不正确"
    print("   ✓ ProbabilityLevel枚举定义正确")
    
    # 验证RowAnalysisResult
    result = RowAnalysisResult(
        row_number=1,
        probability_level=ProbabilityLevel.HIGH,
        total_score=85.0,
        dimension_scores={'data_type': 90.0, 'structure': 80.0, 'industry': 85.0},
        reasoning="测试"
    )
    assert hasattr(result, 'row_number'), "RowAnalysisResult缺少row_number"
    assert hasattr(result, 'probability_level'), "RowAnalysisResult缺少probability_level"
    assert hasattr(result, 'total_score'), "RowAnalysisResult缺少total_score"
    assert hasattr(result, 'dimension_scores'), "RowAnalysisResult缺少dimension_scores"
    assert hasattr(result, 'reasoning'), "RowAnalysisResult缺少reasoning"
    assert hasattr(result, 'is_manually_adjusted'), "RowAnalysisResult缺少is_manually_adjusted"
    assert hasattr(result, 'manual_decision'), "RowAnalysisResult缺少manual_decision"
    assert hasattr(result, 'to_dict'), "RowAnalysisResult缺少to_dict方法"
    print("   ✓ RowAnalysisResult数据模型定义正确")
    
    # 验证AnalysisContext
    context = AnalysisContext(all_rows=[])
    assert hasattr(context, 'all_rows'), "AnalysisContext缺少all_rows"
    assert hasattr(context, 'header_row_index'), "AnalysisContext缺少header_row_index"
    assert hasattr(context, 'column_headers'), "AnalysisContext缺少column_headers"
    assert hasattr(context, 'device_row_indices'), "AnalysisContext缺少device_row_indices"
    print("   ✓ AnalysisContext数据模型定义正确")


def verify_classifier_class(config):
    """验证分类器类"""
    print("\n4. 验证DeviceRowClassifier类...")
    
    from modules.device_row_classifier import DeviceRowClassifier
    
    classifier = DeviceRowClassifier(config)
    
    # 验证必需的方法
    assert hasattr(classifier, 'analyze_row'), "缺少analyze_row方法"
    assert hasattr(classifier, 'calculate_data_type_score'), "缺少calculate_data_type_score方法"
    assert hasattr(classifier, 'calculate_structure_score'), "缺少calculate_structure_score方法"
    assert hasattr(classifier, 'calculate_industry_score'), "缺少calculate_industry_score方法"
    assert hasattr(classifier, 'get_probability_level'), "缺少get_probability_level方法"
    assert hasattr(classifier, 'is_header_row'), "缺少is_header_row方法"
    
    # 验证配置加载
    assert hasattr(classifier, 'weights'), "缺少weights属性"
    assert hasattr(classifier, 'thresholds'), "缺少thresholds属性"
    assert hasattr(classifier, 'device_types'), "缺少device_types属性"
    assert hasattr(classifier, 'parameters'), "缺少parameters属性"
    assert hasattr(classifier, 'brands'), "缺少brands属性"
    assert hasattr(classifier, 'model_patterns'), "缺少model_patterns属性"
    
    print("   ✓ DeviceRowClassifier类定义正确")
    print("   ✓ 所有必需方法已实现")


def main():
    print("=" * 60)
    print("任务1完成验证")
    print("=" * 60)
    
    try:
        config = verify_config_file()
        verify_classifier_file()
        verify_data_models()
        verify_classifier_class(config)
        
        print("\n" + "=" * 60)
        print("✅ 任务1验证通过！")
        print("=" * 60)
        print("\n已完成:")
        print("  ✓ 在 data/static_config.json 中添加设备行识别配置")
        print("  ✓ 创建 backend/modules/device_row_classifier.py 文件")
        print("  ✓ 定义数据模型类: RowAnalysisResult, AnalysisContext, ProbabilityLevel")
        print("  ✓ 实现DeviceRowClassifier核心类")
        print("\n需求覆盖:")
        print("  ✓ 需求 1.1, 1.4, 1.5 - 三维度评分模型")
        print("  ✓ 需求 4.1, 4.2, 4.3, 4.4 - 行业词库")
        print("  ✓ 需求 5.1, 5.2, 5.3 - 概率等级划分")
        print("  ✓ 需求 13.1, 13.2, 13.3 - 配置文件管理")
        
    except AssertionError as e:
        print(f"\n❌ 验证失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
