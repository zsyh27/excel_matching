"""
测试API返回的匹配详情数据结构

验证智能清理和归一化详情是否正确包含在响应中
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from modules.text_preprocessor import TextPreprocessor
from modules.match_engine import MatchEngine
from modules.data_loader import DataLoader
from config import Config
import json


def test_api_response_structure():
    """测试API响应的数据结构"""
    print("\n=== 测试API响应数据结构 ===\n")
    
    # 初始化组件
    from modules.data_loader import ConfigManager
    config_manager = ConfigManager(Config.CONFIG_FILE)
    config = config_manager.get_config()
    
    preprocessor = TextPreprocessor(config)
    
    data_loader = DataLoader(
        config=Config,
        preprocessor=preprocessor
    )
    
    devices = data_loader.load_devices()
    rules = data_loader.load_rules()
    
    match_engine = MatchEngine(rules=rules, devices=devices, config=config)
    
    # 测试文本
    test_text = "室内CO2传感器 485传输方式 量程0-2000ppm 施工要求：按照图纸规范施工"
    
    print(f"测试文本: {test_text}\n")
    
    # 预处理
    preprocess_result = preprocessor.preprocess(test_text, mode='matching')
    
    print("预处理结果:")
    print(f"  - 原始: {preprocess_result.original}")
    print(f"  - 清理后: {preprocess_result.cleaned}")
    print(f"  - 归一化: {preprocess_result.normalized}")
    print(f"  - 特征: {preprocess_result.features}\n")
    
    # 执行匹配
    match_result, cache_key = match_engine.match(
        features=preprocess_result.features,
        input_description=test_text,
        record_detail=True
    )
    
    print(f"匹配结果: {match_result.match_status}")
    print(f"缓存键: {cache_key}\n")
    
    # 获取详情
    if cache_key:
        match_detail = match_engine.detail_recorder.get_detail(cache_key)
        
        if match_detail:
            # 转换为字典（模拟API响应）
            detail_dict = match_detail.to_dict()
            
            print("=== API响应数据结构 ===\n")
            
            # 检查preprocessing字段
            if 'preprocessing' in detail_dict:
                preprocessing = detail_dict['preprocessing']
                print("preprocessing字段:")
                print(f"  - 包含的键: {list(preprocessing.keys())}\n")
                
                # 检查intelligent_cleaning
                if 'intelligent_cleaning' in preprocessing:
                    print("✓ intelligent_cleaning 字段存在")
                    ic = preprocessing['intelligent_cleaning']
                    print(f"  - 应用的规则: {ic.get('applied_rules', [])}")
                    print(f"  - 原始长度: {ic.get('original_length', 0)}")
                    print(f"  - 清理后长度: {ic.get('cleaned_length', 0)}")
                    print(f"  - 删除长度: {ic.get('deleted_length', 0)}")
                    print(f"  - before_text: {ic.get('before_text', '')[:50]}...")
                    print(f"  - after_text: {ic.get('after_text', '')[:50]}...\n")
                else:
                    print("✗ intelligent_cleaning 字段不存在\n")
                
                # 检查normalization_detail
                if 'normalization_detail' in preprocessing:
                    print("✓ normalization_detail 字段存在")
                    nd = preprocessing['normalization_detail']
                    print(f"  - 同义词映射: {len(nd.get('synonym_mappings', []))} 个")
                    print(f"  - 归一化映射: {len(nd.get('normalization_mappings', []))} 个")
                    print(f"  - 全局配置: {nd.get('global_configs', [])}")
                    print(f"  - before_text: {nd.get('before_text', '')[:50]}...")
                    print(f"  - after_text: {nd.get('after_text', '')[:50]}...\n")
                else:
                    print("✗ normalization_detail 字段不存在\n")
                
                # 检查extraction_detail
                if 'extraction_detail' in preprocessing:
                    print("✓ extraction_detail 字段存在")
                    ed = preprocessing['extraction_detail']
                    print(f"  - 识别的品牌: {ed.get('identified_brands', [])}")
                    print(f"  - 识别的设备类型: {ed.get('identified_device_types', [])}")
                    print(f"  - 提取的特征: {len(ed.get('extracted_features', []))} 个\n")
                else:
                    print("✗ extraction_detail 字段不存在\n")
                
                # 输出完整的preprocessing JSON（用于调试）
                print("=== 完整的 preprocessing JSON ===")
                print(json.dumps(preprocessing, ensure_ascii=False, indent=2))
            else:
                print("✗ preprocessing 字段不存在")
        else:
            print("✗ 无法从缓存获取匹配详情")
    else:
        print("✗ 没有生成缓存键")


if __name__ == '__main__':
    try:
        test_api_response_structure()
        print("\n" + "="*50)
        print("测试完成")
        print("="*50)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
