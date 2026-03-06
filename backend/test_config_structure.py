# -*- coding: utf-8 -*-
"""
测试配置结构

检查从数据库加载的配置结构
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from modules.data_loader import DataLoader
from modules.text_preprocessor import TextPreprocessor
from modules.match_engine import MatchEngine

def main():
    print("\n" + "="*60)
    print("测试配置结构")
    print("="*60)
    
    # 初始化数据加载器
    data_loader = DataLoader(config=Config, preprocessor=None)
    
    # 加载配置
    config = data_loader.load_config()
    
    print("\n检查配置结构:")
    
    # 检查 device_type_keywords
    if 'device_type_keywords' in config:
        dtk = config['device_type_keywords']
        print(f"\ndevice_type_keywords:")
        print(f"  类型: {type(dtk)}")
        if isinstance(dtk, dict):
            print(f"  键: {list(dtk.keys())}")
            if 'device_type_keywords' in dtk:
                print(f"  嵌套值类型: {type(dtk['device_type_keywords'])}")
                print(f"  嵌套值长度: {len(dtk['device_type_keywords'])}")
        elif isinstance(dtk, list):
            print(f"  长度: {len(dtk)}")
    
    # 检查 brand_keywords
    if 'brand_keywords' in config:
        bk = config['brand_keywords']
        print(f"\nbrand_keywords:")
        print(f"  类型: {type(bk)}")
        if isinstance(bk, dict):
            print(f"  键: {list(bk.keys())}")
        elif isinstance(bk, list):
            print(f"  长度: {len(bk)}")
    
    # 检查 synonym_map
    if 'synonym_map' in config:
        sm = config['synonym_map']
        print(f"\nsynonym_map:")
        print(f"  类型: {type(sm)}")
        print(f"  条目数: {len(sm)}")
        
        # 检查是否有列表类型的值
        list_values = [(k, v) for k, v in sm.items() if isinstance(v, list)]
        if list_values:
            print(f"  列表类型的值数量: {len(list_values)}")
            print(f"  示例: {list_values[0]}")
    
    # 尝试创建 TextPreprocessor
    print("\n" + "="*60)
    print("测试创建 TextPreprocessor")
    print("="*60)
    
    try:
        preprocessor = TextPreprocessor(config)
        print("✓ TextPreprocessor 创建成功")
    except Exception as e:
        print(f"✗ TextPreprocessor 创建失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 尝试创建 MatchEngine
    print("\n" + "="*60)
    print("测试创建 MatchEngine")
    print("="*60)
    
    try:
        # 加载设备和规则
        devices = data_loader.load_devices()
        rules = data_loader.load_rules()
        
        print(f"已加载 {len(devices)} 个设备，{len(rules)} 条规则")
        
        match_engine = MatchEngine(rules=rules, devices=devices, config=config)
        print("✓ MatchEngine 创建成功")
    except Exception as e:
        print(f"✗ MatchEngine 创建失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 测试预处理
    print("\n" + "="*60)
    print("测试预处理")
    print("="*60)
    
    test_text = "霍尼韦尔室内温湿度传感器"
    print(f"测试文本: {test_text}")
    
    try:
        result = preprocessor.preprocess(test_text)
        print(f"\n✓ 预处理成功")
        print(f"  原始: {result.original}")
        print(f"  清理: {result.cleaned}")
        print(f"  归一化: {result.normalized}")
        print(f"  特征: {result.features}")
    except Exception as e:
        print(f"\n✗ 预处理失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 测试匹配
    print("\n" + "="*60)
    print("测试匹配")
    print("="*60)
    
    try:
        match_result, _ = match_engine.match(result.features, test_text, record_detail=False)
        print(f"\n✓ 匹配成功")
        print(f"  状态: {match_result.match_status}")
        print(f"  设备: {match_result.matched_device_text}")
        print(f"  得分: {match_result.match_score}")
    except Exception as e:
        print(f"\n✗ 匹配失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "="*60)
    print("✓ 所有测试通过")
    print("="*60)
    
    return 0


if __name__ == '__main__':
    exit(main())
