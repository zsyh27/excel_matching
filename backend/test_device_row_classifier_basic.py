"""
基础测试 - 验证设备行分类器的核心数据模型和初始化
"""

import sys
import json
sys.path.insert(0, 'backend')

from modules.device_row_classifier import (
    DeviceRowClassifier, 
    RowAnalysisResult, 
    AnalysisContext, 
    ProbabilityLevel
)


def test_probability_level_enum():
    """测试概率等级枚举"""
    assert ProbabilityLevel.HIGH.value == "high"
    assert ProbabilityLevel.MEDIUM.value == "medium"
    assert ProbabilityLevel.LOW.value == "low"
    print("✓ ProbabilityLevel enum test passed")


def test_row_analysis_result_creation():
    """测试RowAnalysisResult数据模型创建"""
    result = RowAnalysisResult(
        row_number=5,
        probability_level=ProbabilityLevel.HIGH,
        total_score=85.5,
        dimension_scores={
            'data_type': 90.0,
            'structure': 82.0,
            'industry': 84.5
        },
        reasoning="测试判定依据"
    )
    
    assert result.row_number == 5
    assert result.probability_level == ProbabilityLevel.HIGH
    assert result.total_score == 85.5
    assert result.is_manually_adjusted == False
    assert result.manual_decision is None
    
    # 测试to_dict方法
    result_dict = result.to_dict()
    assert result_dict['row_number'] == 5
    assert result_dict['probability_level'] == 'high'
    assert result_dict['total_score'] == 85.5
    
    print("✓ RowAnalysisResult creation test passed")


def test_analysis_context_creation():
    """测试AnalysisContext数据模型创建"""
    context = AnalysisContext(
        all_rows=[],
        header_row_index=2,
        column_headers=['序号', '设备名称', '型号', '数量'],
        device_row_indices=[5, 6, 7]
    )
    
    assert context.header_row_index == 2
    assert len(context.column_headers) == 4
    assert len(context.device_row_indices) == 3
    
    # 测试默认值
    context2 = AnalysisContext(all_rows=[])
    assert context2.header_row_index is None
    assert context2.column_headers == []
    assert context2.device_row_indices == []
    
    print("✓ AnalysisContext creation test passed")


def test_classifier_initialization():
    """测试DeviceRowClassifier初始化"""
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    classifier = DeviceRowClassifier(config)
    
    # 验证权重加载
    assert classifier.weights['data_type'] == 0.30
    assert classifier.weights['structure'] == 0.35
    assert classifier.weights['industry'] == 0.35
    
    # 验证阈值加载
    assert classifier.thresholds['high'] == 70.0
    assert classifier.thresholds['medium'] == 40.0
    
    # 验证词库加载
    assert len(classifier.device_types) > 0
    assert len(classifier.parameters) > 0
    assert len(classifier.brands) > 0
    assert len(classifier.model_patterns) > 0
    
    assert '传感器' in classifier.device_types
    assert 'PPM' in classifier.parameters or 'ppm' in classifier.parameters
    assert '霍尼韦尔' in classifier.brands
    
    print("✓ DeviceRowClassifier initialization test passed")


def test_get_probability_level():
    """测试概率等级判定"""
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    classifier = DeviceRowClassifier(config)
    
    # 测试高概率
    assert classifier.get_probability_level(85.0) == ProbabilityLevel.HIGH
    assert classifier.get_probability_level(70.0) == ProbabilityLevel.HIGH
    
    # 测试中概率
    assert classifier.get_probability_level(69.9) == ProbabilityLevel.MEDIUM
    assert classifier.get_probability_level(50.0) == ProbabilityLevel.MEDIUM
    assert classifier.get_probability_level(40.0) == ProbabilityLevel.MEDIUM
    
    # 测试低概率
    assert classifier.get_probability_level(39.9) == ProbabilityLevel.LOW
    assert classifier.get_probability_level(20.0) == ProbabilityLevel.LOW
    assert classifier.get_probability_level(0.0) == ProbabilityLevel.LOW
    
    print("✓ get_probability_level test passed")


if __name__ == '__main__':
    print("Running basic tests for DeviceRowClassifier...\n")
    
    test_probability_level_enum()
    test_row_analysis_result_creation()
    test_analysis_context_creation()
    test_classifier_initialization()
    test_get_probability_level()
    
    print("\n✅ All basic tests passed!")
