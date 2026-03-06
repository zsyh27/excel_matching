# -*- coding: utf-8 -*-
"""
调试配置数据类型
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from modules.data_loader import DataLoader

def main():
    print("\n" + "="*60)
    print("调试配置数据类型")
    print("="*60)
    
    # 初始化数据加载器
    data_loader = DataLoader(config=Config, preprocessor=None)
    
    # 加载配置
    config = data_loader.load_config()
    
    # 检查必需的配置项
    required_keys = [
        'normalization_map',
        'feature_split_chars',
        'ignore_keywords',
        'global_config',
        'synonym_map',
        'brand_keywords',
        'device_type_keywords'
    ]
    
    print("\n检查必需的配置项:")
    for key in required_keys:
        if key in config:
            value = config[key]
            print(f"  ✓ {key}: {type(value).__name__}")
            
            # 显示详细信息
            if isinstance(value, dict):
                print(f"    - 条目数: {len(value)}")
            elif isinstance(value, list):
                print(f"    - 元素数: {len(value)}")
                if len(value) > 0:
                    print(f"    - 第一个元素类型: {type(value[0]).__name__}")
            else:
                print(f"    - 值: {value}")
        else:
            print(f"  ✗ {key}: 缺失")
    
    # 特别检查 device_type_keywords
    print("\n" + "="*60)
    print("详细检查 device_type_keywords")
    print("="*60)
    
    if 'device_type_keywords' in config:
        dtk = config['device_type_keywords']
        print(f"\n类型: {type(dtk)}")
        print(f"值: {dtk}")
        
        if isinstance(dtk, dict):
            print(f"\n这是一个字典，包含 {len(dtk)} 个条目:")
            for i, (k, v) in enumerate(list(dtk.items())[:5]):
                print(f"  {i+1}. {repr(k)} -> {repr(v)} (类型: {type(v).__name__})")
        elif isinstance(dtk, list):
            print(f"\n这是一个列表，包含 {len(dtk)} 个元素:")
            for i, item in enumerate(dtk[:5]):
                print(f"  {i+1}. {repr(item)} (类型: {type(item).__name__})")
    else:
        print("\n✗ device_type_keywords 不存在")

if __name__ == '__main__':
    main()
