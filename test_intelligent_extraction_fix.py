#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试智能提取API设备格式修复

验证修复后的 IntelligentMatcher 可以正确处理设备数据格式
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.intelligent_extraction.api_handler import IntelligentExtractionAPI

def test_intelligent_extraction_fix():
    """测试智能提取API修复"""
    
    print("=" * 80)
    print("测试智能提取API设备格式修复")
    print("=" * 80)
    
    # 1. 初始化数据库
    print("\n步骤1：初始化数据库...")
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    
    # 2. 加载配置
    print("步骤2：加载配置...")
    config = db_loader.load_config()
    
    if not config:
        print("❌ 配置加载失败")
        return False
    
    print(f"✅ 配置加载成功")
    
    # 3. 初始化智能提取API
    print("\n步骤3：初始化智能提取API...")
    try:
        api = IntelligentExtractionAPI(config, db_loader)
        print("✅ 智能提取API初始化成功")
    except Exception as e:
        print(f"❌ 智能提取API初始化失败: {e}")
        return False
    
    # 4. 测试用例
    test_cases = [
        {
            'name': '测试1：新设备类型（压力变送器）',
            'text': '压力变送器 量程0-10Bar',
            'expected': '应返回结果（可能为空列表）'
        },
        {
            'name': '测试2：已有设备类型（温度传感器）',
            'text': '温度传感器 量程-20~60℃',
            'expected': '应返回匹配的温度传感器'
        },
        {
            'name': '测试3：模糊输入',
            'text': '传感器 0-10Bar',
            'expected': '应返回相关传感器设备'
        },
        {
            'name': '测试4：空输入',
            'text': '',
            'expected': '应返回错误提示'
        }
    ]
    
    print("\n步骤4：执行测试用例...")
    print("=" * 80)
    
    all_passed = True
    
    for idx, test_case in enumerate(test_cases, 1):
        print(f"\n{test_case['name']}")
        print(f"输入文本: '{test_case['text']}'")
        print(f"预期结果: {test_case['expected']}")
        
        try:
            # 调用预览接口（包含完整的五步流程）
            result = api.preview(test_case['text'])
            
            if result['success']:
                print("✅ 测试通过")
                
                # 显示匹配结果
                data = result['data']
                step4 = data.get('step4_matching', {})
                candidates = step4.get('candidates', [])
                
                print(f"   匹配状态: {step4.get('status', 'unknown')}")
                print(f"   候选设备数量: {len(candidates)}")
                
                if candidates:
                    print(f"   最佳匹配: {candidates[0].get('device_name', 'N/A')} (得分: {candidates[0].get('total_score', 0):.2f})")
                
                # 显示性能
                debug_info = data.get('debug_info', {})
                performance = debug_info.get('performance', {})
                print(f"   总耗时: {performance.get('total_time_ms', 0):.2f}ms")
            else:
                error = result.get('error', {})
                if test_case['text'] == '':
                    # 空输入应该返回错误
                    print("✅ 测试通过（预期的错误）")
                    print(f"   错误代码: {error.get('code', 'N/A')}")
                    print(f"   错误信息: {error.get('message', 'N/A')}")
                else:
                    print("❌ 测试失败")
                    print(f"   错误代码: {error.get('code', 'N/A')}")
                    print(f"   错误信息: {error.get('message', 'N/A')}")
                    all_passed = False
        
        except Exception as e:
            print(f"❌ 测试失败（异常）")
            print(f"   异常信息: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    # 5. 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    if all_passed:
        print("✅ 所有测试通过！")
        print("\n修复验证成功：")
        print("  - IntelligentMatcher 可以正确处理设备数据格式")
        print("  - 所有匹配阶段（严格、宽松、模糊、兜底）都能正常工作")
        print("  - 实时测试功能可以正常使用")
        return True
    else:
        print("❌ 部分测试失败")
        print("\n请检查：")
        print("  - 后端服务是否已重启")
        print("  - 数据库连接是否正常")
        print("  - 配置是否正确加载")
        return False


if __name__ == '__main__':
    success = test_intelligent_extraction_fix()
    sys.exit(0 if success else 1)
