#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""调试参数提取过程"""

import sys
import re
sys.path.insert(0, 'backend')

from modules.database_loader import DatabaseLoader
from modules.database import DatabaseManager
from modules.intelligent_extraction.parameter_extractor import ParameterExtractor

def debug_parameter_extraction():
    # 初始化
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    config = db_loader.load_config()
    
    # 获取参数提取配置
    ie_config = config.get('intelligent_extraction', {})
    parameter_config = ie_config.get('parameter_extraction', {})
    
    print("=" * 80)
    print("参数提取配置分析")
    print("=" * 80)
    
    print("参数提取配置内容:")
    for key, value in parameter_config.items():
        print(f"  {key}: {value}")
    print()
    
    # 创建参数提取器
    extractor = ParameterExtractor(parameter_config)
    
    # 测试文本
    test_text = "1.名称:CO浓度探测器 2.规格参数：工作原理：电化学式； 0-250ppm ；4-20mA / 2~10VDC；精度±5%  @25C. 50% RH（0~100  ppm） 3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。"
    
    print(f"测试文本: {test_text}")
    print()
    
    # 详细分析每个参数的提取过程
    print("=" * 80)
    print("量程参数提取分析")
    print("=" * 80)
    
    range_config = extractor.range_config
    print(f"量程配置: {range_config}")
    
    # 量程提取逻辑
    labels = range_config.get('labels', ['量程', '范围'])
    pattern = r'(\d+(?:\.\d+)?)\s*[~\-]\s*(\d+(?:\.\d+)?)\s*([a-zA-Z%℃°]+)'
    
    print(f"查找标签: {labels}")
    print(f"正则模式: {pattern}")
    
    # 检查标签附近
    for label in labels:
        if label in test_text:
            print(f"✅ 找到标签 '{label}' 在位置: {test_text.index(label)}")
            label_pos = test_text.index(label)
            search_text = test_text[label_pos:label_pos+100]
            print(f"搜索文本: {search_text}")
            match = re.search(pattern, search_text)
            if match:
                print(f"✅ 标签附近匹配成功: {match.group(0)}")
                print(f"   最小值: {match.group(1)}")
                print(f"   最大值: {match.group(2)}")
                print(f"   单位: {match.group(3)}")
                print(f"   置信度: 0.95")
            else:
                print(f"❌ 标签附近未匹配")
        else:
            print(f"❌ 未找到标签 '{label}'")
    
    # 全文搜索
    print(f"\n全文搜索:")
    match = re.search(pattern, test_text)
    if match:
        print(f"✅ 全文匹配成功: {match.group(0)}")
        print(f"   最小值: {match.group(1)}")
        print(f"   最大值: {match.group(2)}")
        print(f"   单位: {match.group(3)}")
        print(f"   置信度: 0.80")
    else:
        print(f"❌ 全文未匹配")
    
    print("\n" + "=" * 80)
    print("输出信号提取分析")
    print("=" * 80)
    
    output_config = extractor.output_config
    print(f"输出配置: {output_config}")
    
    # 输出信号提取逻辑
    labels = output_config.get('labels', ['输出', '输出信号'])
    pattern = r'(\d+)\s*[~\-]\s*(\d+)\s*(mA|V|VDC)'
    
    print(f"查找标签: {labels}")
    print(f"正则模式: {pattern}")
    
    # 检查标签附近
    for label in labels:
        if label in test_text:
            print(f"✅ 找到标签 '{label}' 在位置: {test_text.index(label)}")
            label_pos = test_text.index(label)
            search_text = test_text[label_pos:label_pos+50]
            print(f"搜索文本: {search_text}")
            match = re.search(pattern, search_text)
            if match:
                print(f"✅ 标签附近匹配成功: {match.group(0)}")
                print(f"   最小值: {match.group(1)}")
                print(f"   最大值: {match.group(2)}")
                print(f"   单位: {match.group(3)}")
                print(f"   置信度: 0.90")
            else:
                print(f"❌ 标签附近未匹配")
        else:
            print(f"❌ 未找到标签 '{label}'")
    
    # 全文搜索
    print(f"\n全文搜索:")
    match = re.search(pattern, test_text)
    if match:
        print(f"✅ 全文匹配成功: {match.group(0)}")
        print(f"   最小值: {match.group(1)}")
        print(f"   最大值: {match.group(2)}")
        print(f"   单位: {match.group(3)}")
        print(f"   置信度: 0.75")
    else:
        print(f"❌ 全文未匹配")
    
    print("\n" + "=" * 80)
    print("精度参数提取分析")
    print("=" * 80)
    
    accuracy_config = extractor.accuracy_config
    print(f"精度配置: {accuracy_config}")
    
    # 精度提取逻辑
    labels = accuracy_config.get('labels', ['精度'])
    pattern = r'±\s*(\d+(?:\.\d+)?)\s*(%|℃|°C)'
    
    print(f"查找标签: {labels}")
    print(f"正则模式: {pattern}")
    
    # 检查标签附近
    for label in labels:
        if label in test_text:
            print(f"✅ 找到标签 '{label}' 在位置: {test_text.index(label)}")
            label_pos = test_text.index(label)
            search_text = test_text[label_pos:label_pos+50]
            print(f"搜索文本: {search_text}")
            match = re.search(pattern, search_text)
            if match:
                print(f"✅ 标签附近匹配成功: {match.group(0)}")
                print(f"   数值: {match.group(1)}")
                print(f"   单位: {match.group(2)}")
                print(f"   置信度: 0.90")
            else:
                print(f"❌ 标签附近未匹配")
        else:
            print(f"❌ 未找到标签 '{label}'")
    
    # 全文搜索
    print(f"\n全文搜索:")
    match = re.search(pattern, test_text)
    if match:
        print(f"✅ 全文匹配成功: {match.group(0)}")
        print(f"   数值: {match.group(1)}")
        print(f"   单位: {match.group(2)}")
        print(f"   置信度: 0.75")
    else:
        print(f"❌ 全文未匹配")
    
    print("\n" + "=" * 80)
    print("实际提取结果")
    print("=" * 80)
    
    # 实际提取
    result = extractor.extract(test_text)
    
    if result.range:
        print(f"量程参数: {result.range.value} (置信度: {result.range.confidence})")
        print(f"  归一化: {result.range.normalized}")
    else:
        print("量程参数: 未提取")
    
    if result.output:
        print(f"输出信号: {result.output.value} (置信度: {result.output.confidence})")
        print(f"  归一化: {result.output.normalized}")
    else:
        print("输出信号: 未提取")
    
    if result.accuracy:
        print(f"精度参数: {result.accuracy.value} (置信度: {result.accuracy.confidence})")
        print(f"  归一化: {result.accuracy.normalized}")
    else:
        print("精度参数: 未提取")
    
    if result.specs:
        print(f"规格参数: {result.specs}")
    else:
        print("规格参数: 未提取")

if __name__ == "__main__":
    debug_parameter_extraction()