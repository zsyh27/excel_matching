"""
任务2验证测试 - 三维度评分算法

验证所有三维度评分方法的正确性:
- 2.1 数据类型组合分析
- 2.2 结构关联性分析
- 2.3 行业通用特征分析
- 2.4 综合评分与概率等级划分
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
from dataclasses import dataclass
from typing import List
from modules.device_row_classifier import (
    DeviceRowClassifier, 
    AnalysisContext, 
    ProbabilityLevel
)


@dataclass
class MockParsedRow:
    """模拟ParsedRow对象用于测试"""
    row_number: int
    raw_data: List


def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'static_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_subtask_2_1_data_type_score():
    """
    测试子任务2.1: 数据类型组合分析
    
    验证:
    - calculate_data_type_score 方法存在
    - 文本/数值单元格统计逻辑
    - 文本/数值比例评分逻辑
    - 空单元格比例扣分逻辑
    """
    print("\n" + "="*60)
    print("测试子任务2.1: 数据类型组合分析")
    print("="*60)
    
    config = load_config()
    classifier = DeviceRowClassifier(config)
    
    # 测试用例1: 理想比例 (文本:数值 = 2:1)
    row1 = MockParsedRow(
        row_number=10,
        raw_data=["CO传感器", "霍尼韦尔", "2", "500", "1000"]
    )
    score1 = classifier.calculate_data_type_score(row1)
    print(f"✓ 测试用例1 - 理想比例 (3文本:2数值): {score1:.1f}分")
    assert 70 <= score1 <= 100, f"理想比例应得高分，实际: {score1}"
    
    # 测试用例2: 纯文本行
    row2 = MockParsedRow(
        row_number=2,
        raw_data=["序号", "设备名称", "品牌", "型号", "备注"]
    )
    score2 = classifier.calculate_data_type_score(row2)
    print(f"✓ 测试用例2 - 纯文本行: {score2:.1f}分")
    assert score2 < 50, f"纯文本行应得低分，实际: {score2}"
    
    # 测试用例3: 纯数值行
    row3 = MockParsedRow(
        row_number=50,
        raw_data=["1", "2", "3", "4", "5"]
    )
    score3 = classifier.calculate_data_type_score(row3)
    print(f"✓ 测试用例3 - 纯数值行: {score3:.1f}分")
    assert score3 < 50, f"纯数值行应得低分，实际: {score3}"
    
    # 测试用例4: 空单元格过多
    row4 = MockParsedRow(
        row_number=15,
        raw_data=["", "", "", "传感器", ""]
    )
    score4 = classifier.calculate_data_type_score(row4)
    print(f"✓ 测试用例4 - 空单元格过多 (80%空): {score4:.1f}分")
    assert score4 < 30, f"空单元格过多应得很低分，实际: {score4}"
    
    # 测试用例5: 全空行
    row5 = MockParsedRow(
        row_number=20,
        raw_data=["", "", "", "", ""]
    )
    score5 = classifier.calculate_data_type_score(row5)
    print(f"✓ 测试用例5 - 全空行: {score5:.1f}分")
    assert score5 == 0.0, f"全空行应得0分，实际: {score5}"
    
    print("\n✅ 子任务2.1验证通过: 数据类型组合分析正确实现")
    return True


def test_subtask_2_2_structure_score():
    """
    测试子任务2.2: 结构关联性分析
    
    验证:
    - calculate_structure_score 方法存在
    - _check_header_alignment 方法
    - _calculate_row_similarity 方法
    - _evaluate_row_position 方法
    - _extract_row_pattern 方法
    """
    print("\n" + "="*60)
    print("测试子任务2.2: 结构关联性分析")
    print("="*60)
    
    config = load_config()
    classifier = DeviceRowClassifier(config)
    
    # 创建测试上下文
    header_row = MockParsedRow(1, ["序号", "设备名称", "品牌", "数量", "单价"])
    device_row1 = MockParsedRow(5, ["1", "CO传感器", "霍尼韦尔", "2", "500"])
    device_row2 = MockParsedRow(6, ["2", "温度传感器", "西门子", "3", "600"])
    test_row = MockParsedRow(7, ["3", "压力传感器", "施耐德", "1", "800"])
    
    all_rows = [header_row, device_row1, device_row2, test_row]
    
    # 测试用例1: 有表头、有已知设备行、位置合理
    context1 = AnalysisContext(
        all_rows=all_rows,
        header_row_index=0,
        column_headers=header_row.raw_data,
        device_row_indices=[1, 2]  # device_row1 和 device_row2 的索引
    )
    score1 = classifier.calculate_structure_score(test_row, context1)
    print(f"✓ 测试用例1 - 完整上下文: {score1:.1f}分")
    assert 60 <= score1 <= 100, f"完整上下文应得高分，实际: {score1}"
    
    # 测试用例2: 无表头、无已知设备行
    context2 = AnalysisContext(
        all_rows=all_rows,
        header_row_index=None,
        column_headers=[],
        device_row_indices=[]
    )
    score2 = classifier.calculate_structure_score(test_row, context2)
    print(f"✓ 测试用例2 - 无上下文: {score2:.1f}分")
    assert 40 <= score2 <= 70, f"无上下文应得中等分，实际: {score2}"
    
    # 测试用例3: 前3行（可能是表头）
    early_row = MockParsedRow(2, ["1", "CO传感器", "霍尼韦尔", "2", "500"])
    score3 = classifier.calculate_structure_score(early_row, context2)
    print(f"✓ 测试用例3 - 前3行位置: {score3:.1f}分")
    # 位置得分会较低，但不影响整体太多
    
    # 测试用例4: 最后2行（可能是合计）
    late_row = MockParsedRow(99, ["合计", "", "", "100", "50000"])
    context4 = AnalysisContext(
        all_rows=[MockParsedRow(i, []) for i in range(100)],
        header_row_index=None,
        column_headers=[],
        device_row_indices=[]
    )
    score4 = classifier.calculate_structure_score(late_row, context4)
    print(f"✓ 测试用例4 - 最后2行位置: {score4:.1f}分")
    
    # 验证辅助方法存在
    print("\n验证辅助方法:")
    pattern = classifier._extract_row_pattern(test_row)
    print(f"✓ _extract_row_pattern: {pattern}")
    assert pattern == ["N", "T", "T", "N", "N"], f"模式提取错误: {pattern}"
    
    similarity = classifier._pattern_similarity(["N", "T", "T"], ["N", "T", "N"])
    print(f"✓ _pattern_similarity: {similarity:.2f}")
    assert 0 <= similarity <= 1, f"相似度应在0-1之间: {similarity}"
    
    pos_score = classifier._evaluate_row_position(10, 50)
    print(f"✓ _evaluate_row_position: {pos_score:.1f}")
    assert pos_score == 100.0, f"中间位置应得满分: {pos_score}"
    
    header_score = classifier._check_header_alignment(test_row, header_row.raw_data)
    print(f"✓ _check_header_alignment: {header_score:.1f}")
    assert 0 <= header_score <= 100, f"对齐得分应在0-100之间: {header_score}"
    
    print("\n✅ 子任务2.2验证通过: 结构关联性分析正确实现")
    return True


def test_subtask_2_3_industry_score():
    """
    测试子任务2.3: 行业通用特征分析
    
    验证:
    - calculate_industry_score 方法存在
    - 设备类型词库匹配逻辑
    - 参数词库匹配逻辑
    - 品牌词库匹配逻辑
    - 型号模式匹配逻辑
    """
    print("\n" + "="*60)
    print("测试子任务2.3: 行业通用特征分析")
    print("="*60)
    
    config = load_config()
    classifier = DeviceRowClassifier(config)
    
    # 测试用例1: 包含设备类型、品牌、参数
    row1 = MockParsedRow(
        row_number=10,
        raw_data=["1", "CO传感器", "霍尼韦尔", "0-2000PPM", "2", "500"]
    )
    score1 = classifier.calculate_industry_score(row1)
    print(f"✓ 测试用例1 - 包含设备类型+品牌+参数: {score1:.1f}分")
    assert score1 >= 60, f"包含多个行业特征应得高分，实际: {score1}"
    
    # 测试用例2: 仅包含设备类型
    row2 = MockParsedRow(
        row_number=11,
        raw_data=["2", "控制器", "未知品牌", "1", "300"]
    )
    score2 = classifier.calculate_industry_score(row2)
    print(f"✓ 测试用例2 - 仅包含设备类型: {score2:.1f}分")
    assert 20 <= score2 <= 50, f"仅设备类型应得中等分，实际: {score2}"
    
    # 测试用例3: 无行业特征
    row3 = MockParsedRow(
        row_number=12,
        raw_data=["备注", "这是一个备注行", "没有设备信息", "", ""]
    )
    score3 = classifier.calculate_industry_score(row3)
    print(f"✓ 测试用例3 - 无行业特征: {score3:.1f}分")
    assert score3 < 20, f"无行业特征应得低分，实际: {score3}"
    
    # 测试用例4: 包含型号模式
    row4 = MockParsedRow(
        row_number=13,
        raw_data=["3", "DDC控制器", "西门子", "PXC36-E.D", "1", "5000"]
    )
    score4 = classifier.calculate_industry_score(row4)
    print(f"✓ 测试用例4 - 包含型号模式: {score4:.1f}分")
    assert score4 >= 50, f"包含型号模式应得较高分，实际: {score4}"
    
    # 测试用例5: 多个设备类型词汇
    row5 = MockParsedRow(
        row_number=14,
        raw_data=["4", "温度传感器+控制器", "霍尼韦尔", "DC24V", "1", "800"]
    )
    score5 = classifier.calculate_industry_score(row5)
    print(f"✓ 测试用例5 - 多个设备类型词汇: {score5:.1f}分")
    assert score5 >= 60, f"多个设备类型应得高分，实际: {score5}"
    
    print("\n✅ 子任务2.3验证通过: 行业通用特征分析正确实现")
    return True


def test_subtask_2_4_comprehensive_scoring():
    """
    测试子任务2.4: 综合评分与概率等级划分
    
    验证:
    - analyze_row 方法整合三维度评分
    - 加权总分计算逻辑
    - get_probability_level 方法
    - _generate_reasoning 方法
    """
    print("\n" + "="*60)
    print("测试子任务2.4: 综合评分与概率等级划分")
    print("="*60)
    
    config = load_config()
    classifier = DeviceRowClassifier(config)
    
    # 创建测试上下文
    header_row = MockParsedRow(1, ["序号", "设备名称", "品牌", "规格", "数量", "单价"])
    all_rows = [header_row]
    
    context = AnalysisContext(
        all_rows=all_rows,
        header_row_index=0,
        column_headers=header_row.raw_data,
        device_row_indices=[]
    )
    
    # 测试用例1: 典型设备行（应为高概率）
    row1 = MockParsedRow(
        row_number=5,
        raw_data=["1", "CO传感器", "霍尼韦尔", "0-2000PPM", "2", "500"]
    )
    result1 = classifier.analyze_row(row1, context)
    print(f"\n✓ 测试用例1 - 典型设备行:")
    print(f"  - 综合得分: {result1.total_score:.1f}")
    print(f"  - 概率等级: {result1.probability_level.value}")
    print(f"  - 数据类型得分: {result1.dimension_scores['data_type']:.1f}")
    print(f"  - 结构关联得分: {result1.dimension_scores['structure']:.1f}")
    print(f"  - 行业特征得分: {result1.dimension_scores['industry']:.1f}")
    print(f"  - 判定依据: {result1.reasoning}")
    
    assert result1.probability_level == ProbabilityLevel.HIGH, \
        f"典型设备行应为高概率，实际: {result1.probability_level}"
    assert result1.total_score >= 70, \
        f"典型设备行综合得分应≥70，实际: {result1.total_score}"
    assert 'data_type' in result1.dimension_scores, "缺少数据类型得分"
    assert 'structure' in result1.dimension_scores, "缺少结构关联得分"
    assert 'industry' in result1.dimension_scores, "缺少行业特征得分"
    assert len(result1.reasoning) > 0, "判定依据不能为空"
    
    # 测试用例2: 表头行（应为低概率）
    row2 = MockParsedRow(
        row_number=2,
        raw_data=["序号", "设备名称", "品牌", "型号", "数量", "单价"]
    )
    result2 = classifier.analyze_row(row2, context)
    print(f"\n✓ 测试用例2 - 表头行:")
    print(f"  - 综合得分: {result2.total_score:.1f}")
    print(f"  - 概率等级: {result2.probability_level.value}")
    print(f"  - 判定依据: {result2.reasoning}")
    
    assert result2.probability_level in [ProbabilityLevel.LOW, ProbabilityLevel.MEDIUM], \
        f"表头行应为低或中概率，实际: {result2.probability_level}"
    
    # 测试用例3: 备注行（应为低概率）
    row3 = MockParsedRow(
        row_number=50,
        raw_data=["备注", "以上价格仅供参考", "", "", "", ""]
    )
    result3 = classifier.analyze_row(row3, context)
    print(f"\n✓ 测试用例3 - 备注行:")
    print(f"  - 综合得分: {result3.total_score:.1f}")
    print(f"  - 概率等级: {result3.probability_level.value}")
    print(f"  - 判定依据: {result3.reasoning}")
    
    assert result3.probability_level == ProbabilityLevel.LOW, \
        f"备注行应为低概率，实际: {result3.probability_level}"
    assert result3.total_score < 40, \
        f"备注行综合得分应<40，实际: {result3.total_score}"
    
    # 测试用例4: 验证加权计算
    print(f"\n✓ 测试用例4 - 验证加权计算:")
    weights = classifier.weights
    print(f"  - 配置权重: {weights}")
    
    # 手动计算加权总分
    manual_score = (
        result1.dimension_scores['data_type'] * weights['data_type'] +
        result1.dimension_scores['structure'] * weights['structure'] +
        result1.dimension_scores['industry'] * weights['industry']
    )
    print(f"  - 手动计算: {manual_score:.1f}")
    print(f"  - 系统计算: {result1.total_score:.1f}")
    
    assert abs(manual_score - result1.total_score) < 0.1, \
        f"加权计算不一致: 手动={manual_score:.1f}, 系统={result1.total_score:.1f}"
    
    # 测试用例5: 验证概率等级阈值
    print(f"\n✓ 测试用例5 - 验证概率等级阈值:")
    thresholds = classifier.thresholds
    print(f"  - 配置阈值: {thresholds}")
    
    level_high = classifier.get_probability_level(75.0)
    level_medium = classifier.get_probability_level(55.0)
    level_low = classifier.get_probability_level(30.0)
    
    assert level_high == ProbabilityLevel.HIGH, "≥70分应为高概率"
    assert level_medium == ProbabilityLevel.MEDIUM, "40-69分应为中概率"
    assert level_low == ProbabilityLevel.LOW, "<40分应为低概率"
    print(f"  - 75分 -> {level_high.value} ✓")
    print(f"  - 55分 -> {level_medium.value} ✓")
    print(f"  - 30分 -> {level_low.value} ✓")
    
    # 测试用例6: 验证to_dict方法
    print(f"\n✓ 测试用例6 - 验证to_dict方法:")
    result_dict = result1.to_dict()
    assert 'row_number' in result_dict, "缺少row_number字段"
    assert 'probability_level' in result_dict, "缺少probability_level字段"
    assert 'total_score' in result_dict, "缺少total_score字段"
    assert 'dimension_scores' in result_dict, "缺少dimension_scores字段"
    assert 'reasoning' in result_dict, "缺少reasoning字段"
    print(f"  - to_dict方法正常工作 ✓")
    
    print("\n✅ 子任务2.4验证通过: 综合评分与概率等级划分正确实现")
    return True


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("任务2完成验证 - 三维度评分算法")
    print("="*60)
    
    try:
        # 测试子任务2.1
        test_subtask_2_1_data_type_score()
        
        # 测试子任务2.2
        test_subtask_2_2_structure_score()
        
        # 测试子任务2.3
        test_subtask_2_3_industry_score()
        
        # 测试子任务2.4
        test_subtask_2_4_comprehensive_scoring()
        
        print("\n" + "="*60)
        print("✅ 任务2所有子任务验证通过！")
        print("="*60)
        print("\n已完成:")
        print("  ✓ 2.1 实现数据类型组合分析")
        print("  ✓ 2.2 实现结构关联性分析")
        print("  ✓ 2.3 实现行业通用特征分析")
        print("  ✓ 2.4 实现综合评分与概率等级划分")
        print("\n需求覆盖:")
        print("  ✓ 需求 1.1, 1.2, 1.3, 1.4, 1.5 - 三维度评分模型")
        print("  ✓ 需求 2.1-2.5 - 数据类型组合分析")
        print("  ✓ 需求 3.1-3.5 - 结构关联性分析")
        print("  ✓ 需求 4.1-4.6 - 行业通用特征分析")
        print("  ✓ 需求 5.1-5.6 - 概率等级划分")
        print("="*60)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ 验证失败: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
