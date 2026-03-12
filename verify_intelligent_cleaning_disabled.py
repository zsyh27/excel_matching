#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证智能清理功能已禁用

测试内容：
1. 验证配置中 intelligent_extraction.enabled = False
2. 测试文本预处理，确认智能清理不再执行
3. 测试六步流程预览，确认步骤0不包含智能清理详情
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.text_preprocessor import TextPreprocessor
from modules.intelligent_extraction.api_handler import IntelligentExtractionAPI

def test_config():
    """测试1：验证配置"""
    print("\n" + "=" * 80)
    print("测试1：验证配置")
    print("=" * 80)
    
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    
    intelligent_extraction = db_loader.get_config_by_key('intelligent_extraction')
    
    if not intelligent_extraction:
        print("❌ 错误：intelligent_extraction 配置不存在")
        return False
    
    enabled = intelligent_extraction.get('enabled', False)
    print(f"   intelligent_extraction.enabled = {enabled}")
    
    if not enabled:
        print("✅ 测试通过：智能清理已禁用")
        return True
    else:
        print("❌ 测试失败：智能清理仍然启用")
        return False

def test_text_preprocessing():
    """测试2：测试文本预处理"""
    print("\n" + "=" * 80)
    print("测试2：测试文本预处理")
    print("=" * 80)
    
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    config = db_loader.load_config()
    
    # 创建文本预处理器
    preprocessor = TextPreprocessor(config)
    
    # 测试文本（包含噪音段落）
    test_text = "1.名称:CO浓度探测器 2.规格参数：工作原理：电化学式； 量程 0~ 250ppm ；输出信号 4~20mA / 2~10VDC；精度±5% @25C. 50% RH（0~100 ppm） 3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。"
    
    print(f"\n原始文本:\n{test_text}\n")
    
    # 执行预处理
    result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"清理后文本:\n{result.cleaned}\n")
    print(f"归一化文本:\n{result.normalized}\n")
    print(f"提取特征: {len(result.features)} 个")
    print(f"特征列表: {result.features[:10]}...")  # 只显示前10个
    
    # 验证：智能清理已被删除，不再有intelligent_cleaning_detail字段
    # 由于智能清理已禁用并删除，清理后文本应该等于原始文本
    if result.cleaned == test_text:
        print("\n✅ 测试通过：智能清理已跳过（清理后文本 = 原始文本）")
        return True
    else:
        print("\n❌ 测试失败：智能清理仍在运行（清理后文本 ≠ 原始文本）")
        print(f"   原始长度: {len(test_text)}")
        print(f"   清理后长度: {len(result.cleaned)}")
        return False

def test_six_step_preview():
    """测试3：测试六步流程预览"""
    print("\n" + "=" * 80)
    print("测试3：测试六步流程预览")
    print("=" * 80)
    
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    config = db_loader.load_config()
    
    # 创建API处理器
    api = IntelligentExtractionAPI(config, db_loader)
    
    # 测试文本
    test_text = "CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%"
    
    print(f"\n测试文本: {test_text}\n")
    
    # 执行预览
    result = api.preview(test_text)
    
    if not result['success']:
        print(f"❌ 预览失败: {result.get('error', {}).get('message', '未知错误')}")
        return False
    
    data = result['data']
    
    # 检查步骤0
    if 'step0_preprocessing' in data:
        step0 = data['step0_preprocessing']
        print("步骤0：文本预处理")
        print(f"   原始文本: {step0.get('original', '')[:50]}...")
        print(f"   清理后文本: {step0.get('cleaned', '')[:50]}...")
        print(f"   归一化文本: {step0.get('normalized', '')[:50]}...")
        print(f"   提取特征: {len(step0.get('features', []))} 个")
        
        # 检查智能清理详情
        if 'intelligent_cleaning' in step0:
            ic = step0['intelligent_cleaning']
            applied_rules = ic.get('applied_rules', [])
            deleted_length = ic.get('deleted_length', 0)
            
            print(f"\n   智能清理详情:")
            print(f"      应用规则: {applied_rules}")
            print(f"      删除长度: {deleted_length} 字符")
            
            # 如果智能清理已禁用，应该没有应用任何规则
            if not applied_rules or len(applied_rules) == 0:
                print("✅ 测试通过：智能清理未执行（无应用规则）")
                return True
            else:
                print("❌ 测试失败：智能清理仍在执行")
                return False
        else:
            print("\n   ⚠️  警告：步骤0中没有智能清理详情")
            # 检查原始文本和清理后文本是否相同
            if step0.get('original') == step0.get('cleaned'):
                print("✅ 测试通过：原始文本和清理后文本相同（智能清理未执行）")
                return True
            else:
                print("❌ 测试失败：原始文本和清理后文本不同（智能清理可能仍在执行）")
                return False
    else:
        print("❌ 错误：预览结果中没有步骤0")
        return False

def main():
    print("=" * 80)
    print("验证智能清理功能已禁用")
    print("=" * 80)
    
    results = []
    
    # 测试1：验证配置
    results.append(("配置验证", test_config()))
    
    # 测试2：测试文本预处理
    results.append(("文本预处理", test_text_preprocessing()))
    
    # 测试3：测试六步流程预览
    results.append(("六步流程预览", test_six_step_preview()))
    
    # 汇总结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"总计: {passed}/{len(results)} 通过")
    print("=" * 80)
    
    if failed == 0:
        print("\n🎉 所有测试通过！智能清理功能已成功禁用。")
        print("\n下一步：")
        print("1. 在前端测试六步流程预览，确认智能清理不再显示")
        print("2. 如果一切正常，可以开始 Phase 2：删除智能清理代码")
        return True
    else:
        print(f"\n⚠️  有 {failed} 个测试失败，请检查配置和代码。")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
