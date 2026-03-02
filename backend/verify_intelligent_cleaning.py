"""
智能清理功能验证脚本

一键验证智能清理功能是否正常工作
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.data_loader import DataLoader
from modules.text_preprocessor import TextPreprocessor
from modules.match_engine import MatchEngine
from config import Config
import json

def print_section(title):
    """打印章节标题"""
    print(f"\n{'=' * 80}")
    print(f"{title}")
    print(f"{'=' * 80}\n")

def print_check(passed, message):
    """打印检查结果"""
    icon = "✅" if passed else "❌"
    print(f"{icon} {message}")
    return passed

def verify_intelligent_cleaning():
    """验证智能清理功能"""
    
    print_section("智能清理功能验证")
    
    all_passed = True
    
    # 检查 1: 配置文件
    print("检查 1: 配置文件")
    try:
        with open(Config.CONFIG_FILE, 'r', encoding='utf-8') as f:
            json_config = json.load(f)
        
        has_ie_config = 'intelligent_extraction' in json_config
        all_passed &= print_check(has_ie_config, "配置文件包含 intelligent_extraction")
        
        if has_ie_config:
            ie_enabled = json_config['intelligent_extraction'].get('enabled', False)
            all_passed &= print_check(ie_enabled, f"intelligent_extraction.enabled = {ie_enabled}")
        else:
            all_passed = False
    except Exception as e:
        all_passed &= print_check(False, f"读取配置文件失败: {e}")
    
    # 检查 2: 数据库配置
    print("\n检查 2: 数据库配置")
    try:
        data_loader = DataLoader(config=Config)
        db_config = data_loader.load_config()
        
        has_ie_config = 'intelligent_extraction' in db_config
        all_passed &= print_check(has_ie_config, "数据库包含 intelligent_extraction 配置")
        
        if has_ie_config:
            ie_enabled = db_config['intelligent_extraction'].get('enabled', False)
            all_passed &= print_check(ie_enabled, f"数据库中 intelligent_extraction.enabled = {ie_enabled}")
            
            # 检查配置一致性
            if has_ie_config and 'intelligent_extraction' in json_config:
                json_enabled = json_config['intelligent_extraction'].get('enabled', False)
                consistent = ie_enabled == json_enabled
                all_passed &= print_check(consistent, f"配置一致性: JSON={json_enabled}, DB={ie_enabled}")
        else:
            all_passed = False
            print("   ⚠️  需要运行: python backend/scripts/sync_config_to_database.py")
    except Exception as e:
        all_passed &= print_check(False, f"加载数据库配置失败: {e}")
    
    # 检查 3: 文本预处理器
    print("\n检查 3: 文本预处理器")
    try:
        config = data_loader.load_config()
        preprocessor = TextPreprocessor(config)
        
        # 测试文本（包含噪音）
        test_text = "室内CO2传感器 485传输方式\n施工要求：含该项施工内容所包含的全部主材"
        result = preprocessor.preprocess(test_text, mode='matching')
        
        has_info = hasattr(result, 'intelligent_cleaning_info')
        all_passed &= print_check(has_info, "PreprocessResult 包含 intelligent_cleaning_info")
        
        if has_info:
            info = result.intelligent_cleaning_info
            is_enabled = info.get('enabled', False)
            all_passed &= print_check(is_enabled, f"智能清理已启用: {is_enabled}")
            
            is_truncated = info.get('truncated', False)
            removed = info.get('removed_length', 0)
            all_passed &= print_check(is_truncated and removed > 0, 
                                     f"成功删除噪音: {removed} 字符")
    except Exception as e:
        all_passed &= print_check(False, f"文本预处理测试失败: {e}")
    
    # 检查 4: 匹配引擎
    print("\n检查 4: 匹配引擎")
    try:
        devices = data_loader.load_devices()
        rules = data_loader.load_rules()
        match_engine = MatchEngine(rules=rules, devices=devices, config=config)
        
        # 执行匹配
        test_text = "室内CO2传感器 485传输方式\n施工要求：含该项施工内容"
        preprocess_result = preprocessor.preprocess(test_text, mode='matching')
        match_result, cache_key = match_engine.match(
            features=preprocess_result.features,
            input_description=test_text,
            record_detail=True
        )
        
        has_cache_key = cache_key is not None
        all_passed &= print_check(has_cache_key, f"生成缓存键: {cache_key}")
        
        if has_cache_key:
            # 获取匹配详情
            match_detail = match_engine.detail_recorder.get_detail(cache_key)
            has_detail = match_detail is not None
            all_passed &= print_check(has_detail, "成功获取匹配详情")
            
            if has_detail:
                # 检查 preprocessing 字段
                has_preprocessing = 'intelligent_cleaning_info' in match_detail.preprocessing
                all_passed &= print_check(has_preprocessing, 
                                         "匹配详情包含 intelligent_cleaning_info")
                
                # 序列化测试
                detail_dict = match_detail.to_dict()
                has_in_dict = 'intelligent_cleaning_info' in detail_dict.get('preprocessing', {})
                all_passed &= print_check(has_in_dict, 
                                         "序列化后的字典包含 intelligent_cleaning_info")
    except Exception as e:
        all_passed &= print_check(False, f"匹配引擎测试失败: {e}")
    
    # 总结
    print_section("验证结果")
    
    if all_passed:
        print("✅ 所有检查通过！智能清理功能正常工作。")
        print("\n下一步操作:")
        print("  1. 重启后端服务（如果正在运行）")
        print("  2. 清除浏览器缓存（Ctrl+Shift+R）")
        print("  3. 重新执行匹配操作")
        print("  4. 查看匹配详情 → 特征提取标签页")
        print("  5. 应该能看到'智能清理'阶段的显示")
    else:
        print("❌ 部分检查失败，请按照以下步骤修复:")
        print("\n修复步骤:")
        print("  1. 运行配置同步脚本:")
        print("     python backend/scripts/sync_config_to_database.py")
        print("  2. 重新运行此验证脚本:")
        print("     python backend/verify_intelligent_cleaning.py")
        print("  3. 如果仍有问题，查看详细文档:")
        print("     docs/INTELLIGENT_CLEANING_DISPLAY_FIX.md")
    
    return all_passed


if __name__ == '__main__':
    try:
        success = verify_intelligent_cleaning()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 验证过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
