# -*- coding: utf-8 -*-
"""
调试 synonym_map 配置格式
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from modules.data_loader import DataLoader

def main():
    print("\n" + "="*60)
    print("调试 synonym_map 配置格式")
    print("="*60)
    
    # 初始化数据加载器
    data_loader = DataLoader(config=Config, preprocessor=None)
    
    # 加载配置
    config = data_loader.load_config()
    
    # 检查 synonym_map
    if 'synonym_map' in config:
        synonym_map = config['synonym_map']
        print(f"\nsynonym_map 类型: {type(synonym_map)}")
        print(f"synonym_map 条目数: {len(synonym_map)}")
        
        # 检查前几个条目
        print("\n前10个条目:")
        for i, (key, value) in enumerate(list(synonym_map.items())[:10]):
            print(f"  {i+1}. {repr(key)} -> {repr(value)} (类型: {type(value).__name__})")
        
        # 检查是否有列表类型的值
        list_values = [(k, v) for k, v in synonym_map.items() if isinstance(v, list)]
        if list_values:
            print(f"\n⚠ 发现 {len(list_values)} 个列表类型的值:")
            for k, v in list_values[:5]:
                print(f"  - {repr(k)} -> {repr(v)}")
        else:
            print("\n✓ 所有值都是字符串类型")
    else:
        print("\n✗ 配置中没有 synonym_map")
    
    # 检查 JSON 文件
    print("\n" + "="*60)
    print("检查 JSON 文件中的 synonym_map")
    print("="*60)
    
    if os.path.exists(Config.CONFIG_FILE):
        with open(Config.CONFIG_FILE, 'r', encoding='utf-8') as f:
            json_config = json.load(f)
        
        if 'synonym_map' in json_config:
            json_synonym_map = json_config['synonym_map']
            print(f"\nJSON synonym_map 类型: {type(json_synonym_map)}")
            print(f"JSON synonym_map 条目数: {len(json_synonym_map)}")
            
            # 检查前几个条目
            print("\n前10个条目:")
            for i, (key, value) in enumerate(list(json_synonym_map.items())[:10]):
                print(f"  {i+1}. {repr(key)} -> {repr(value)} (类型: {type(value).__name__})")
            
            # 检查是否有列表类型的值
            list_values = [(k, v) for k, v in json_synonym_map.items() if isinstance(v, list)]
            if list_values:
                print(f"\n⚠ JSON中发现 {len(list_values)} 个列表类型的值:")
                for k, v in list_values[:5]:
                    print(f"  - {repr(k)} -> {repr(v)}")
            else:
                print("\n✓ JSON中所有值都是字符串类型")
        else:
            print("\n✗ JSON配置中没有 synonym_map")
    else:
        print(f"\n✗ JSON文件不存在: {Config.CONFIG_FILE}")

if __name__ == '__main__':
    main()
