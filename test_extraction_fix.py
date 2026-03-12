#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试智能提取修复"""

import sys
sys.path.insert(0, 'backend')

from modules.database_loader import DatabaseLoader
from modules.database import DatabaseManager
from modules.intelligent_extraction.api_handler import IntelligentExtractionAPI

def test_extraction():
    # 初始化
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    config = db_loader.load_config()
    
    # 创建API处理器
    api = IntelligentExtractionAPI(config, db_loader)
    
    # 测试文本
    test_text = "1.名称:CO浓度探测器 2.规格参数：工作原理：电化学式； 量程 0~ 250ppm ；输出信号 4~20mA / 2~10VDC；精度±5%  @25C. 50% RH（0~100  ppm） 3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。"
    
    print("=" * 80)
    print("测试智能提取修复")
    print("=" * 80)
    print(f"输入文本: {test_text}")
    print()
    
    # 测试预览功能
    result = api.preview(test_text)
    
    if result['success']:
        data = result['data']
        
        print("📋 步骤1：设备类型识别")
        step1 = data['step1_device_type']
        print(f"  识别结果: {step1['sub_type']}")
        print(f"  主类型: {step1['main_type']}")
        print(f"  置信度: {step1['confidence']}%")
        print(f"  识别模式: {step1['mode']}")
        print(f"  关键词: {step1['keywords']}")
        print()
        
        print("🔧 步骤2：技术参数提取")
        step2 = data['step2_parameters']
        print(f"  量程参数: {step2.get('range', {}).get('value', '未提取')}")
        print(f"  输出信号: {step2.get('output', {}).get('value', '未提取')}")
        print(f"  精度参数: {step2.get('accuracy', {}).get('value', '未提取')}")
        print(f"  规格参数: {step2.get('specs', '未提取')}")
        print()
        
        print("ℹ️ 步骤3：辅助信息提取")
        step3 = data['step3_auxiliary']
        print(f"  品牌信息: {step3.get('brand', '未识别')}")
        print(f"  适用介质: {step3.get('medium', '未识别')}")
        print(f"  设备型号: {step3.get('model', '未识别')}")
        print()
        
        print("🎯 步骤4：智能匹配")
        step4 = data['step4_matching']
        print(f"  匹配状态: {step4['status']}")
        print(f"  候选设备数量: {len(step4['candidates'])}")
        print()
        
        print("📊 性能统计")
        perf = data['debug_info']['performance']
        print(f"  总耗时: {perf['total_time_ms']:.2f}ms")
        print(f"  步骤1耗时: {perf['step1_time_ms']:.2f}ms")
        print(f"  步骤2耗时: {perf['step2_time_ms']:.2f}ms")
        print(f"  步骤3耗时: {perf['step3_time_ms']:.2f}ms")
        print(f"  步骤4耗时: {perf['step4_time_ms']:.2f}ms")
        
    else:
        print(f"❌ 测试失败: {result.get('error', {}).get('message', '未知错误')}")

if __name__ == "__main__":
    test_extraction()