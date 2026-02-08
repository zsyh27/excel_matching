#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终验收测试脚本
验证匹配准确率和性能指标
"""

import time
import json
from pathlib import Path
from modules.data_loader import DataLoader
from modules.text_preprocessor import TextPreprocessor
from modules.match_engine import MatchEngine
from modules.excel_parser import ExcelParser
from modules.excel_exporter import ExcelExporter

def test_matching_accuracy():
    """测试匹配准确率"""
    print("\n" + "="*60)
    print("测试 1: 匹配准确率验证 (目标 ≥85%)")
    print("="*60)
    
    # 加载数据
    data_loader = DataLoader(
        device_file="data/static_device.json",
        rule_file="data/static_rule.json",
        config_file="data/static_config.json"
    )
    devices = data_loader.load_devices()
    rules = data_loader.load_rules()
    config = data_loader.load_config()
    
    # 初始化组件
    preprocessor = TextPreprocessor(config)
    match_engine = MatchEngine(rules, devices, config)
    
    # 测试用例：基于实际设备表生成的描述
    test_cases = [
        # 标准格式
        ("CO浓度探测器，0~100PPM", "SENSOR001"),
        ("温度传感器，0-50℃，4-20mA", "SENSOR002"),
        ("湿度传感器，0-100%RH，4-20mA", "SENSOR003"),
        ("压差传感器，0-500Pa，4-20mA", "SENSOR004"),
        ("风速传感器，0-30m/s，4-20mA", "SENSOR005"),
        ("水流开关，常开触点", "SENSOR006"),
        ("压力传感器，0-1.6MPa，4-20mA", "SENSOR007"),
        ("液位传感器，0-5m，4-20mA", "SENSOR008"),
        
        # DDC控制器
        ("DDC控制器，8AI/4AO/8DI/4DO", "DDC001"),
        ("DDC控制器，16AI/8AO/16DI/8DO", "DDC002"),
        ("DDC控制器，4AI/2AO/4DI/2DO", "DDC003"),
        ("DDC控制器，12AI/6AO/12DI/6DO", "DDC004"),
        ("DDC控制器，20AI/10AO/20DI/10DO", "DDC005"),
        
        # 阀门
        ("电动调节阀，DN50，AC220V", "VALVE001"),
        ("电动调节阀，DN80，AC220V", "VALVE002"),
        ("电动蝶阀，DN100，AC220V", "VALVE003"),
        ("电动球阀，DN65，AC220V", "VALVE004"),
        ("电磁阀，DN25，AC220V", "VALVE005"),
        ("比例积分阀，DN40，DC24V", "VALVE006"),
        
        # 控制柜
        ("DDC控制柜，800x600x250mm", "CABINET001"),
        ("DDC控制柜，1000x800x300mm", "CABINET002"),
        
        # 电源
        ("开关电源，DC24V/5A", "POWER001"),
        ("开关电源，DC24V/10A", "POWER002"),
        
        # 继电器
        ("中间继电器，AC220V", "RELAY001"),
        
        # 网关
        ("BACnet网关，支持Modbus转BACnet", "GATEWAY001"),
        
        # 非标准格式（带噪音）
        ("CO浓度探测器 电化学式 0~100PPM 4~20mA", "SENSOR001"),
        ("温度传感器 PT1000 0到50摄氏度 4到20mA", "SENSOR002"),
        ("湿度传感器 0～100%RH 4～20mA输出", "SENSOR003"),
        ("DDC控制器 8路AI 4路AO 8路DI 4路DO", "DDC001"),
        ("电动调节阀 口径DN50 电压AC220V", "VALVE001"),
        
        # 带品牌的描述
        ("霍尼韦尔CO传感器，0-100PPM", "SENSOR001"),
        ("施耐德DDC控制器，8AI/4AO/8DI/4DO", "DDC001"),
        ("江森自控温度传感器，0-50℃", "SENSOR002"),
        
        # 简化描述
        ("CO传感器", "SENSOR001"),
        ("温度传感器", "SENSOR002"),
        ("DDC控制器", "DDC001"),
        ("电动调节阀DN50", "VALVE001"),
    ]
    
    # 执行匹配测试
    correct_matches = 0
    total_tests = len(test_cases)
    failed_cases = []
    
    for description, expected_device_id in test_cases:
        # 预处理
        result = preprocessor.preprocess(description)
        features = result.features
        
        # 匹配
        match_result = match_engine.match(features)
        
        # 验证
        if match_result.device_id == expected_device_id:
            correct_matches += 1
            status = "✅"
        else:
            status = "❌"
            failed_cases.append({
                "description": description,
                "expected": expected_device_id,
                "actual": match_result.device_id,
                "score": match_result.match_score
            })
        
        print(f"{status} {description[:40]:40s} -> {match_result.device_id or 'FAILED':15s} (期望: {expected_device_id})")
    
    # 计算准确率
    accuracy = (correct_matches / total_tests) * 100
    
    print("\n" + "-"*60)
    print(f"测试总数: {total_tests}")
    print(f"匹配成功: {correct_matches}")
    print(f"匹配失败: {total_tests - correct_matches}")
    print(f"准确率: {accuracy:.2f}%")
    print("-"*60)
    
    if failed_cases:
        print("\n失败案例详情:")
        for case in failed_cases:
            print(f"  描述: {case['description']}")
            print(f"  期望: {case['expected']}")
            print(f"  实际: {case['actual']}")
            print(f"  得分: {case['score']}")
            print()
    
    if accuracy >= 85:
        print(f"✅ 准确率测试通过！({accuracy:.2f}% ≥ 85%)")
        return True
    else:
        print(f"❌ 准确率测试失败！({accuracy:.2f}% < 85%)")
        return False

def test_parsing_performance():
    """测试解析性能"""
    print("\n" + "="*60)
    print("测试 2: Excel解析性能验证 (目标 ≤5秒)")
    print("="*60)
    
    # 使用示例文件
    excel_file = "data/示例设备清单.xlsx"
    
    if not Path(excel_file).exists():
        print(f"❌ 测试文件不存在: {excel_file}")
        return False
    
    # 加载配置
    data_loader = DataLoader(
        device_file="data/static_device.json",
        rule_file="data/static_rule.json",
        config_file="data/static_config.json"
    )
    config = data_loader.load_config()
    preprocessor = TextPreprocessor(config)
    
    # 初始化解析器
    parser = ExcelParser(preprocessor)
    
    # 测试解析性能
    start_time = time.time()
    result = parser.parse_file(excel_file)
    elapsed_time = time.time() - start_time
    
    print(f"文件: {excel_file}")
    print(f"解析行数: {len(result.rows)}")
    print(f"解析时间: {elapsed_time:.3f} 秒")
    
    if elapsed_time <= 5.0:
        print(f"✅ 解析性能测试通过！({elapsed_time:.3f}秒 ≤ 5秒)")
        return True
    else:
        print(f"❌ 解析性能测试失败！({elapsed_time:.3f}秒 > 5秒)")
        return False

def test_matching_performance():
    """测试匹配性能"""
    print("\n" + "="*60)
    print("测试 3: 设备匹配性能验证 (目标 ≤10秒)")
    print("="*60)
    
    # 加载数据
    data_loader = DataLoader(
        device_file="data/static_device.json",
        rule_file="data/static_rule.json",
        config_file="data/static_config.json"
    )
    devices = data_loader.load_devices()
    rules = data_loader.load_rules()
    config = data_loader.load_config()
    
    # 初始化组件
    preprocessor = TextPreprocessor(config)
    match_engine = MatchEngine(rules, devices, config)
    
    # 生成测试数据（模拟100个设备描述）
    test_descriptions = [
        "CO浓度探测器，0~100PPM",
        "温度传感器，0-50℃，4-20mA",
        "湿度传感器，0-100%RH，4-20mA",
        "压差传感器，0-500Pa，4-20mA",
        "DDC控制器，8AI/4AO/8DI/4DO",
        "电动调节阀，DN50，AC220V",
        "DDC控制柜，800x600x250mm",
        "开关电源，DC24V/5A",
    ] * 13  # 重复以达到100+个
    
    test_descriptions = test_descriptions[:100]
    
    # 测试匹配性能
    start_time = time.time()
    
    for description in test_descriptions:
        result = preprocessor.preprocess(description)
        features = result.features
        match_result = match_engine.match(features)
    
    elapsed_time = time.time() - start_time
    
    print(f"匹配数量: {len(test_descriptions)} 个设备描述")
    print(f"匹配时间: {elapsed_time:.3f} 秒")
    print(f"平均时间: {(elapsed_time/len(test_descriptions)*1000):.2f} 毫秒/个")
    
    if elapsed_time <= 10.0:
        print(f"✅ 匹配性能测试通过！({elapsed_time:.3f}秒 ≤ 10秒)")
        return True
    else:
        print(f"❌ 匹配性能测试失败！({elapsed_time:.3f}秒 > 10秒)")
        return False

def test_export_format():
    """测试导出格式完整性"""
    print("\n" + "="*60)
    print("测试 4: Excel导出格式验证")
    print("="*60)
    
    try:
        # 使用示例文件
        excel_file = "data/示例设备清单.xlsx"
        
        if not Path(excel_file).exists():
            print(f"❌ 测试文件不存在: {excel_file}")
            return False
        
        # 加载数据和初始化组件
        data_loader = DataLoader(
            device_file="data/static_device.json",
            rule_file="data/static_rule.json",
            config_file="data/static_config.json"
        )
        devices = data_loader.load_devices()
        rules = data_loader.load_rules()
        config = data_loader.load_config()
        
        preprocessor = TextPreprocessor(config)
        parser = ExcelParser(preprocessor)
        match_engine = MatchEngine(rules, devices, config)
        exporter = ExcelExporter()
        
        # 解析文件
        parse_result = parser.parse_file(excel_file)
        
        # 匹配设备
        matched_rows = []
        for row in parse_result.rows:
            if row.row_type == "device" and row.preprocessed_features:
                match_result = match_engine.match(row.preprocessed_features)
                matched_rows.append({
                    "row_number": row.row_number,
                    "row_type": row.row_type,
                    "device_description": row.device_description,
                    "match_result": match_result.to_dict()
                })
            else:
                matched_rows.append({
                    "row_number": row.row_number,
                    "row_type": row.row_type,
                    "device_description": row.device_description,
                    "match_result": None
                })
        
        # 导出文件
        output_file = "backend/temp/final_test_export.xlsx"
        Path("backend/temp").mkdir(exist_ok=True)
        
        exported_path = exporter.export(excel_file, matched_rows, output_file)
        
        # 验证导出文件
        if Path(exported_path).exists():
            file_size = Path(exported_path).stat().st_size
            print(f"✅ 导出文件创建成功: {exported_path}")
            print(f"   文件大小: {file_size} 字节")
            print(f"   匹配行数: {len([r for r in matched_rows if r['row_type'] == 'device'])}")
            return True
        else:
            print(f"❌ 导出文件创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 导出测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_documentation():
    """测试文档完整性"""
    print("\n" + "="*60)
    print("测试 5: 文档完整性验证")
    print("="*60)
    
    required_docs = {
        "README.md": "项目说明文档",
        "MAINTENANCE.md": "维护指南文档",
        "SETUP.md": "安装指南文档",
        ".kiro/specs/ddc-device-matching/requirements.md": "需求文档",
        ".kiro/specs/ddc-device-matching/design.md": "设计文档",
        ".kiro/specs/ddc-device-matching/tasks.md": "任务清单",
    }
    
    all_exist = True
    for doc_path, doc_name in required_docs.items():
        if Path(doc_path).exists():
            size = Path(doc_path).stat().st_size
            print(f"✅ {doc_name}: {doc_path} ({size} 字节)")
        else:
            print(f"❌ {doc_name}: {doc_path} (不存在)")
            all_exist = False
    
    if all_exist:
        print("\n✅ 所有文档完整")
        return True
    else:
        print("\n❌ 部分文档缺失")
        return False

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("DDC设备清单匹配报价系统 - 最终验收测试")
    print("="*60)
    
    results = {
        "匹配准确率": test_matching_accuracy(),
        "解析性能": test_parsing_performance(),
        "匹配性能": test_matching_performance(),
        "导出格式": test_export_format(),
        "文档完整性": test_documentation(),
    }
    
    # 汇总结果
    print("\n" + "="*60)
    print("最终验收测试结果汇总")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:20s}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 所有验收测试通过！系统已准备就绪。")
    else:
        print("⚠️  部分验收测试失败，请检查上述问题。")
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
