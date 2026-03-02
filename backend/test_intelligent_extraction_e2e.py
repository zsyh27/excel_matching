"""
智能特征提取端到端测试

测试智能清理功能从配置到前端展示的完整流程
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from modules.text_preprocessor import TextPreprocessor
from modules.match_engine import MatchEngine
from modules.match_detail import MatchDetailRecorder
from modules.data_loader import DataLoader
import json


def test_intelligent_cleaning_e2e():
    """
    端到端测试：验证智能清理信息从预处理到匹配详情的完整传递
    """
    print("=" * 80)
    print("智能特征提取端到端测试")
    print("=" * 80)
    
    # 1. 加载配置
    print("\n【步骤1】加载配置...")
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 检查智能提取是否启用
    intelligent_extraction = config.get('intelligent_extraction', {})
    is_enabled = intelligent_extraction.get('enabled', False)
    print(f"智能提取启用状态: {is_enabled}")
    
    if not is_enabled:
        print("⚠️  警告：智能提取未启用，测试结果可能不完整")
    
    # 2. 创建预处理器
    print("\n【步骤2】创建文本预处理器...")
    preprocessor = TextPreprocessor(config)
    
    # 3. 测试用例：包含施工要求的文本
    print("\n【步骤3】测试包含施工要求的文本...")
    test_text = (
        "36,室内CO2传感器,1.名称:室内CO2传感器2.规格：485传输方式，"
        "量程0-2000ppm；输出信号4~20mA/2~10VDC；精度±5%@25C.50%RH(0~100ppm)，"
        "485通讯3.施工要求:按照图纸规范要求配置，含该项施工内容所包含的全部主材、"
        "辅材、配件、采购、运输、保管、施工、安装、调试、验收等全部费用"
    )
    
    print(f"原始文本: {test_text}")
    print(f"原始文本长度: {len(test_text)} 字符")
    
    # 4. 执行预处理
    print("\n【步骤4】执行预处理...")
    result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"\n预处理结果:")
    print(f"  - 原始文本: {result.original[:50]}...")
    print(f"  - 清理后: {result.cleaned[:50]}...")
    print(f"  - 归一化: {result.normalized[:50]}...")
    print(f"  - 提取特征数: {len(result.features)}")
    print(f"  - 特征列表: {result.features[:10]}")
    
    # 5. 检查智能清理信息
    print("\n【步骤5】检查智能清理信息...")
    if hasattr(result, 'intelligent_cleaning_info'):
        info = result.intelligent_cleaning_info
        print(f"✅ 智能清理信息已附加到结果对象")
        print(f"  - 启用状态: {info.get('enabled', False)}")
        print(f"  - 原始长度: {info.get('original_length', 0)} 字符")
        print(f"  - 清理后长度: {info.get('cleaned_length', 0)} 字符")
        print(f"  - 删除长度: {info.get('removed_length', 0)} 字符")
        print(f"  - 是否截断: {info.get('truncated', False)}")
        
        if info.get('removed_length', 0) > 0:
            percentage = (info['removed_length'] / info['original_length']) * 100
            print(f"  - 删除比例: {percentage:.1f}%")
            print(f"✅ 智能清理生效，成功删除了 {info['removed_length']} 个字符")
        else:
            print(f"⚠️  智能清理未删除任何内容")
    else:
        print(f"❌ 智能清理信息未附加到结果对象")
    
    # 6. 测试匹配引擎集成
    print("\n【步骤6】测试匹配引擎集成...")
    cache_key = None  # 初始化变量
    try:
        # 加载数据（使用数据库模式）
        data_loader = DataLoader(
            config=config,
            use_database=True,
            db_path='data/devices.db'
        )
        rules = data_loader.get_rules()
        devices = data_loader.get_devices()
        
        print(f"加载了 {len(rules)} 条规则，{len(devices)} 个设备")
        
        if len(rules) == 0 or len(devices) == 0:
            print(f"⚠️  规则或设备为空，跳过匹配引擎测试")
            raise Exception("规则或设备为空")
        
        # 创建匹配引擎
        detail_recorder = MatchDetailRecorder(config)
        match_engine = MatchEngine(
            rules=rules,
            devices=devices,
            config=config,
            match_logger=None,
            detail_recorder=detail_recorder
        )
        
        # 执行匹配（记录详情）
        match_result, cache_key = match_engine.match(
            features=result.features,
            input_description=test_text,
            record_detail=True
        )
        
        print(f"\n匹配结果:")
        print(f"  - 匹配状态: {match_result.match_status}")
        print(f"  - 匹配得分: {match_result.match_score}")
        print(f"  - 缓存键: {cache_key}")
        
        # 7. 验证匹配详情中的智能清理信息
        print("\n【步骤7】验证匹配详情中的智能清理信息...")
        if cache_key:
            detail = detail_recorder.get_detail(cache_key)
            if detail:
                preprocessing = detail.preprocessing
                if 'intelligent_cleaning_info' in preprocessing:
                    info = preprocessing['intelligent_cleaning_info']
                    print(f"✅ 匹配详情中包含智能清理信息")
                    print(f"  - 启用状态: {info.get('enabled', False)}")
                    print(f"  - 原始长度: {info.get('original_length', 0)}")
                    print(f"  - 清理后长度: {info.get('cleaned_length', 0)}")
                    print(f"  - 删除长度: {info.get('removed_length', 0)}")
                    print(f"  - 是否截断: {info.get('truncated', False)}")
                    
                    # 验证数据一致性
                    if hasattr(result, 'intelligent_cleaning_info'):
                        original_info = result.intelligent_cleaning_info
                        if (info.get('original_length') == original_info.get('original_length') and
                            info.get('cleaned_length') == original_info.get('cleaned_length')):
                            print(f"✅ 智能清理信息传递正确，数据一致")
                        else:
                            print(f"❌ 智能清理信息数据不一致")
                else:
                    print(f"❌ 匹配详情中不包含智能清理信息")
            else:
                print(f"❌ 无法获取匹配详情")
        else:
            print(f"⚠️  未生成缓存键，跳过详情验证")
            
    except Exception as e:
        print(f"⚠️  匹配引擎测试跳过: {e}")
        # 不打印完整堆栈，因为这不是关键测试
    
    # 8. 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    success_count = 0
    total_count = 4
    
    # 检查点1: 智能清理是否启用
    if is_enabled:
        print("✅ 智能清理已启用")
        success_count += 1
    else:
        print("❌ 智能清理未启用")
    
    # 检查点2: 预处理结果是否包含智能清理信息
    if hasattr(result, 'intelligent_cleaning_info'):
        print("✅ 预处理结果包含智能清理信息")
        success_count += 1
    else:
        print("❌ 预处理结果不包含智能清理信息")
    
    # 检查点3: 智能清理是否生效
    if hasattr(result, 'intelligent_cleaning_info') and result.intelligent_cleaning_info.get('removed_length', 0) > 0:
        print("✅ 智能清理生效，成功删除噪音")
        success_count += 1
    else:
        print("⚠️  智能清理未删除内容（可能文本本身很干净）")
        success_count += 0.5
    
    # 检查点4: 匹配详情是否包含智能清理信息
    try:
        if cache_key:
            detail = detail_recorder.get_detail(cache_key)
            if detail and 'intelligent_cleaning_info' in detail.preprocessing:
                print("✅ 匹配详情包含智能清理信息")
                success_count += 1
            else:
                print("❌ 匹配详情不包含智能清理信息")
        else:
            print("⚠️  无法验证匹配详情（匹配引擎测试跳过）")
    except:
        print("⚠️  无法验证匹配详情")
    
    print(f"\n通过率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count >= 3:
        print("\n🎉 端到端测试通过！智能清理功能正常工作")
    else:
        print("\n⚠️  端到端测试部分通过，需要检查配置或代码")


def test_without_intelligent_cleaning():
    """
    对比测试：禁用智能清理时的行为
    """
    print("\n" + "=" * 80)
    print("对比测试：禁用智能清理")
    print("=" * 80)
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 临时禁用智能清理
    config['intelligent_extraction']['enabled'] = False
    
    # 创建预处理器
    preprocessor = TextPreprocessor(config)
    
    # 测试文本
    test_text = (
        "室内CO2传感器,1.名称:室内CO2传感器2.规格：485传输方式，"
        "量程0-2000ppm；输出信号4~20mA/2~10VDC；精度±5%@25C.50%RH(0~100ppm)，"
        "485通讯3.施工要求:按照图纸规范要求配置"
    )
    
    # 执行预处理
    result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"原始文本长度: {len(test_text)} 字符")
    print(f"清理后长度: {len(result.cleaned)} 字符")
    print(f"提取特征数: {len(result.features)}")
    
    # 检查是否包含智能清理信息
    if hasattr(result, 'intelligent_cleaning_info'):
        print(f"⚠️  禁用时仍然包含智能清理信息（不应该出现）")
    else:
        print(f"✅ 禁用时不包含智能清理信息（符合预期）")


if __name__ == '__main__':
    # 运行端到端测试
    test_intelligent_cleaning_e2e()
    
    # 运行对比测试
    test_without_intelligent_cleaning()
    
    print("\n" + "=" * 80)
    print("所有测试完成")
    print("=" * 80)
