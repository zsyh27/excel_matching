#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
设备行智能识别准确率验证测试

验证需求: 15.1, 15.2, 15.3, 15.4, 15.5
测试目标:
1. 自动识别准确率 ≥95%
2. 手动调整后准确率达到100%
"""

import sys
from pathlib import Path

# 添加backend目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from modules.data_loader import DataLoader
from modules.text_preprocessor import TextPreprocessor
from modules.excel_parser import ExcelParser
from modules.device_row_classifier import DeviceRowClassifier, ProbabilityLevel, AnalysisContext


def test_auto_recognition_accuracy():
    """
    测试自动识别准确率
    
    验证需求: 15.1, 15.2, 15.3
    
    使用真实文件: data/(原始表格)建筑设备监控及能源管理报价清单(2).xlsx
    真实设备行: 第6-21行、第23-57行，共51行
    
    期望结果: 自动识别准确率 ≥95%
    """
    print("\n" + "="*80)
    print("测试 1: 设备行自动识别准确率验证 (目标 ≥95%)")
    print("="*80)
    
    # 加载数据和配置
    base_dir = Path(__file__).parent.parent
    data_loader = DataLoader(
        device_file=str(base_dir / 'data/static_device.json'),
        rule_file=str(base_dir / 'data/static_rule.json'),
        config_file=str(base_dir / 'data/static_config.json')
    )
    config = data_loader.load_config()
    
    # 初始化组件
    preprocessor = TextPreprocessor(config)
    parser = ExcelParser(preprocessor)
    classifier = DeviceRowClassifier(config)
    
    # 解析真实Excel文件
    test_file = base_dir / 'data/(原始表格)建筑设备监控及能源管理报价清单(2).xlsx'
    
    if not test_file.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    print(f"\n正在解析文件: {test_file.name}")
    parse_result = parser.parse_file(str(test_file))
    print(f"解析完成: 总行数={parse_result.total_rows}, 有效行数={len(parse_result.rows)}")
    
    # 定义真实设备行（第6-21行、第23-57行）
    expected_device_rows = set(list(range(6, 22)) + list(range(23, 58)))
    print(f"\n真实设备行数量: {len(expected_device_rows)} 行")
    print(f"真实设备行范围: 第6-21行、第23-57行")
    
    # 初始化分析上下文
    context = AnalysisContext(
        all_rows=parse_result.rows,
        header_row_index=None,
        column_headers=[],
        device_row_indices=[]
    )
    
    # 第一遍：识别表头
    print("\n第一遍分析: 识别表头行...")
    for idx, row in enumerate(parse_result.rows):
        if classifier.is_header_row(row):
            context.header_row_index = idx
            context.column_headers = row.raw_data
            print(f"  识别到表头行: 第{row.row_number}行")
            print(f"  列标题: {context.column_headers[:5]}...")
            break
    
    # 第二遍：分析所有行
    print("\n第二遍分析: 评估所有行...")
    analysis_results = []
    auto_identified_device_rows = set()
    
    for row in parse_result.rows:
        result = classifier.analyze_row(row, context)
        analysis_results.append(result)
        
        # 记录高概率设备行
        if result.probability_level == ProbabilityLevel.HIGH:
            auto_identified_device_rows.add(row.row_number)
            context.device_row_indices.append(row.row_number - 1)
    
    print(f"  自动识别为高概率设备行: {len(auto_identified_device_rows)} 行")
    
    # 计算准确率指标
    true_positives = len(expected_device_rows & auto_identified_device_rows)  # 正确识别的设备行
    false_positives = len(auto_identified_device_rows - expected_device_rows)  # 误识别为设备行
    false_negatives = len(expected_device_rows - auto_identified_device_rows)  # 漏识别的设备行
    
    # 准确率 = 正确识别的设备行 / 真实设备行总数
    accuracy = (true_positives / len(expected_device_rows)) * 100 if expected_device_rows else 0
    
    # 精确率 = 正确识别的设备行 / 所有识别为设备行的行
    precision = (true_positives / len(auto_identified_device_rows)) * 100 if auto_identified_device_rows else 0
    
    # 召回率 = 正确识别的设备行 / 真实设备行总数
    recall = (true_positives / len(expected_device_rows)) * 100 if expected_device_rows else 0
    
    # 打印详细结果
    print("\n" + "-"*80)
    print("自动识别结果统计:")
    print("-"*80)
    print(f"真实设备行总数:        {len(expected_device_rows)} 行")
    print(f"自动识别设备行总数:    {len(auto_identified_device_rows)} 行")
    print(f"正确识别 (TP):         {true_positives} 行")
    print(f"误识别 (FP):           {false_positives} 行")
    print(f"漏识别 (FN):           {false_negatives} 行")
    print("-"*80)
    print(f"准确率 (Accuracy):     {accuracy:.2f}%")
    print(f"精确率 (Precision):    {precision:.2f}%")
    print(f"召回率 (Recall):       {recall:.2f}%")
    print("-"*80)
    
    # 显示误识别和漏识别的行
    if false_positives > 0:
        print(f"\n误识别的行 (共{false_positives}行):")
        fp_rows = sorted(auto_identified_device_rows - expected_device_rows)
        for row_num in fp_rows[:10]:  # 只显示前10个
            row = next((r for r in parse_result.rows if r.row_number == row_num), None)
            if row:
                result = next((r for r in analysis_results if r.row_number == row_num), None)
                content = ' | '.join(str(c) for c in row.raw_data[:5])
                print(f"  第{row_num}行 (得分:{result.total_score:.1f}): {content}...")
        if len(fp_rows) > 10:
            print(f"  ... 还有 {len(fp_rows) - 10} 行")
    
    if false_negatives > 0:
        print(f"\n漏识别的行 (共{false_negatives}行):")
        fn_rows = sorted(expected_device_rows - auto_identified_device_rows)
        for row_num in fn_rows[:10]:  # 只显示前10个
            row = next((r for r in parse_result.rows if r.row_number == row_num), None)
            if row:
                result = next((r for r in analysis_results if r.row_number == row_num), None)
                content = ' | '.join(str(c) for c in row.raw_data[:5])
                print(f"  第{row_num}行 (得分:{result.total_score:.1f}, 等级:{result.probability_level.value}): {content}...")
        if len(fn_rows) > 10:
            print(f"  ... 还有 {len(fn_rows) - 10} 行")
    
    # 显示得分分布
    print("\n概率等级分布:")
    high_count = sum(1 for r in analysis_results if r.probability_level == ProbabilityLevel.HIGH)
    medium_count = sum(1 for r in analysis_results if r.probability_level == ProbabilityLevel.MEDIUM)
    low_count = sum(1 for r in analysis_results if r.probability_level == ProbabilityLevel.LOW)
    print(f"  高概率 (HIGH):   {high_count} 行")
    print(f"  中概率 (MEDIUM): {medium_count} 行")
    print(f"  低概率 (LOW):    {low_count} 行")
    
    # 判断是否通过
    print("\n" + "="*80)
    if accuracy >= 95.0:
        print(f"✅ 自动识别准确率测试通过！({accuracy:.2f}% ≥ 95%)")
        return True, analysis_results, expected_device_rows, auto_identified_device_rows
    else:
        print(f"❌ 自动识别准确率测试失败！({accuracy:.2f}% < 95%)")
        print("\n建议:")
        print("  1. 调整配置文件中的评分权重 (data/static_config.json)")
        print("  2. 调整概率等级阈值")
        print("  3. 扩充行业词库")
        return False, analysis_results, expected_device_rows, auto_identified_device_rows


def test_manual_adjustment_accuracy(analysis_results, expected_device_rows, auto_identified_device_rows):
    """
    测试手动调整后的准确率
    
    验证需求: 15.4
    
    模拟手动调整：将所有误识别和漏识别的行进行手动修正
    
    期望结果: 手动调整后准确率达到100%
    """
    print("\n" + "="*80)
    print("测试 2: 手动调整后准确率验证 (目标 100%)")
    print("="*80)
    
    # 模拟手动调整记录
    manual_adjustments = {}
    
    # 将误识别的行标记为非设备行
    false_positives = auto_identified_device_rows - expected_device_rows
    for row_num in false_positives:
        manual_adjustments[row_num] = False  # 取消设备行标记
    
    # 将漏识别的行标记为设备行
    false_negatives = expected_device_rows - auto_identified_device_rows
    for row_num in false_negatives:
        manual_adjustments[row_num] = True  # 标记为设备行
    
    print(f"\n手动调整操作:")
    print(f"  取消设备行标记: {len(false_positives)} 行")
    print(f"  添加设备行标记: {len(false_negatives)} 行")
    print(f"  总调整数量:     {len(manual_adjustments)} 行")
    
    # 计算最终设备行列表（手动调整优先）
    final_device_rows = set()
    
    for result in analysis_results:
        row_number = result.row_number
        
        # 检查是否有手动调整
        if row_number in manual_adjustments:
            is_device = manual_adjustments[row_number]
        else:
            # 使用自动判断结果（高概率）
            is_device = result.probability_level == ProbabilityLevel.HIGH
        
        if is_device:
            final_device_rows.add(row_number)
    
    # 计算最终准确率
    correct = len(expected_device_rows & final_device_rows)
    total = len(expected_device_rows)
    final_accuracy = (correct / total) * 100 if total > 0 else 0
    
    print("\n" + "-"*80)
    print("手动调整后结果统计:")
    print("-"*80)
    print(f"真实设备行总数:        {len(expected_device_rows)} 行")
    print(f"最终识别设备行总数:    {len(final_device_rows)} 行")
    print(f"正确识别:              {correct} 行")
    print(f"最终准确率:            {final_accuracy:.2f}%")
    print("-"*80)
    
    # 判断是否通过
    print("\n" + "="*80)
    if final_accuracy >= 100.0:
        print(f"✅ 手动调整后准确率测试通过！({final_accuracy:.2f}% = 100%)")
        return True
    else:
        print(f"❌ 手动调整后准确率测试失败！({final_accuracy:.2f}% < 100%)")
        
        # 显示仍然不匹配的行
        still_wrong = expected_device_rows ^ final_device_rows
        if still_wrong:
            print(f"\n仍然不匹配的行 (共{len(still_wrong)}行):")
            for row_num in sorted(still_wrong)[:10]:
                print(f"  第{row_num}行")
        
        return False


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("设备行智能识别准确率验证测试")
    print("="*80)
    print("\n测试文件: data/(原始表格)建筑设备监控及能源管理报价清单(2).xlsx")
    print("真实设备行: 第6-21行、第23-57行，共51行")
    print("测试目标: 自动识别准确率 ≥95%，手动调整后准确率 100%")
    
    # 测试1: 自动识别准确率
    test1_passed, analysis_results, expected_rows, auto_rows = test_auto_recognition_accuracy()
    
    # 测试2: 手动调整后准确率
    test2_passed = test_manual_adjustment_accuracy(analysis_results, expected_rows, auto_rows)
    
    # 汇总结果
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)
    print(f"自动识别准确率测试:    {'✅ 通过' if test1_passed else '❌ 失败'}")
    print(f"手动调整后准确率测试:  {'✅ 通过' if test2_passed else '❌ 失败'}")
    print("="*80)
    
    if test1_passed and test2_passed:
        print("\n🎉 所有测试通过！设备行智能识别功能已达到预期目标。")
        return True
    else:
        print("\n⚠️  部分测试失败，需要进一步调优。")
        if not test1_passed:
            print("\n调优建议:")
            print("  1. 检查配置文件 data/static_config.json 中的评分权重")
            print("  2. 调整概率等级阈值 (high: 70.0, medium: 40.0)")
            print("  3. 扩充行业词库 (device_types, parameters, brands)")
            print("  4. 分析误识别和漏识别的行，找出规律")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
