#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试归一化映射格式兼容性修复
"""

import json
import sys
sys.path.insert(0, 'backend')

from modules.text_preprocessor import TextPreprocessor

def test_normalization_formats():
    """测试列表和字典两种格式的归一化映射"""
    
    print("=" * 60)
    print("测试归一化映射格式兼容性")
    print("=" * 60)
    
    # 测试1：列表格式（前端使用的格式）
    print("\n1. 测试列表格式:")
    config_list = {
        'normalization_map': [
            {'from': '温度', 'to': '温度'},
            {'from': '温湿度', 'to': '温度'},
            {'from': '测温', 'to': '温度'}
        ],
        'feature_split_chars': [],
        'ignore_keywords': []
    }
    
    try:
        preprocessor = TextPreprocessor(config_list)
        print(f"   ✓ 初始化成功")
        print(f"   normalization_map 类型: {type(preprocessor.normalization_map)}")
        print(f"   normalization_map 内容: {preprocessor.normalization_map}")
        
        # 测试预处理
        result = preprocessor.preprocess("温湿度传感器")
        print(f"   ✓ 预处理成功: '温湿度传感器' -> '{result}'")
    except Exception as e:
        print(f"   ✗ 失败: {e}")
        return False
    
    # 测试2：字典格式（旧格式）
    print("\n2. 测试字典格式:")
    config_dict = {
        'normalization_map': {
            '温度': '温度',
            '温湿度': '温度',
            '测温': '温度'
        },
        'feature_split_chars': [],
        'ignore_keywords': []
    }
    
    try:
        preprocessor = TextPreprocessor(config_dict)
        print(f"   ✓ 初始化成功")
        print(f"   normalization_map 类型: {type(preprocessor.normalization_map)}")
        print(f"   normalization_map 内容: {preprocessor.normalization_map}")
        
        # 测试预处理
        result = preprocessor.preprocess("温湿度传感器")
        print(f"   ✓ 预处理成功: '温湿度传感器' -> '{result}'")
    except Exception as e:
        print(f"   ✗ 失败: {e}")
        return False
    
    # 测试3：空配置
    print("\n3. 测试空配置:")
    config_empty = {
        'normalization_map': [],
        'feature_split_chars': [],
        'ignore_keywords': []
    }
    
    try:
        preprocessor = TextPreprocessor(config_empty)
        print(f"   ✓ 初始化成功")
        print(f"   normalization_map 类型: {type(preprocessor.normalization_map)}")
        print(f"   normalization_map 内容: {preprocessor.normalization_map}")
        
        # 测试预处理
        result = preprocessor.preprocess("温湿度传感器")
        print(f"   ✓ 预处理成功: '温湿度传感器' -> '{result}'")
    except Exception as e:
        print(f"   ✗ 失败: {e}")
        return False
    
    # 测试4：从实际配置文件加载
    print("\n4. 测试从配置文件加载:")
    try:
        with open('data/static_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        preprocessor = TextPreprocessor(config)
        print(f"   ✓ 初始化成功")
        print(f"   normalization_map 类型: {type(preprocessor.normalization_map)}")
        print(f"   normalization_map 条目数: {len(preprocessor.normalization_map)}")
        
        # 测试预处理
        result = preprocessor.preprocess("温湿度传感器")
        print(f"   ✓ 预处理成功: '温湿度传感器' -> '{result}'")
    except Exception as e:
        print(f"   ✗ 失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_normalization_formats()
    sys.exit(0 if success else 1)
