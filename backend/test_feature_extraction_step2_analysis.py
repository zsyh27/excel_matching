"""
分析第二步需要解决的问题

当前问题:
1. "0-2000ppm" → 应该变成 "0-2000" (删除单位)
2. "4~20mA / 2~10VDC" → 应该变成 ["4-20", "2-10"] (拆分并删除单位)
3. "±5%@25C.50%RH(0~100ppm)" → 应该变成 ["±5", "25", "50", "0-100"] (分解复杂参数)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.text_preprocessor import TextPreprocessor
import json


def analyze_current_behavior():
    """分析当前的特征提取行为"""
    
    with open('../data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    test_cases = [
        "0-2000ppm",
        "4-20ma",
        "2-10v",
        "±5%@25c.50%rh(0-100ppm)",
        "4~20mA / 2~10VDC",
    ]
    
    print("="*60)
    print("当前特征提取行为分析")
    print("="*60)
    
    for test_text in test_cases:
        print(f"\n输入: {test_text}")
        result = preprocessor.preprocess(test_text, mode='matching')
        print(f"归一化后: {result.normalized}")
        print(f"提取的特征: {result.features}")


if __name__ == '__main__':
    analyze_current_behavior()
