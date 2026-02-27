#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试新增配置项是否正确加载
"""

import json
import sys

def test_config():
    """测试配置加载"""
    try:
        # 加载配置文件
        with open('data/static_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("=" * 80)
        print("配置加载测试")
        print("=" * 80)
        
        # 测试 feature_weight_config
        print("\n1. 特征权重配置 (feature_weight_config):")
        feature_weight_config = config.get('feature_weight_config')
        if feature_weight_config:
            print(f"   ✓ 已找到")
            print(f"   - brand_weight: {feature_weight_config.get('brand_weight')}")
            print(f"   - model_weight: {feature_weight_config.get('model_weight')}")
            print(f"   - device_type_weight: {feature_weight_config.get('device_type_weight')}")
            print(f"   - parameter_weight: {feature_weight_config.get('parameter_weight')}")
        else:
            print("   ✗ 未找到")
            return False
        
        # 测试 metadata_keywords
        print("\n2. 元数据关键词 (metadata_keywords):")
        metadata_keywords = config.get('metadata_keywords')
        if metadata_keywords:
            print(f"   ✓ 已找到，共 {len(metadata_keywords)} 个关键词")
            print(f"   - 示例: {metadata_keywords[:5]}")
        else:
            print("   ✗ 未找到")
            return False
        
        # 测试 global_config 扩展
        print("\n3. 全局配置扩展 (global_config):")
        global_config = config.get('global_config')
        if global_config:
            print(f"   ✓ 已找到")
            print(f"   - min_feature_length: {global_config.get('min_feature_length')}")
            print(f"   - min_feature_length_chinese: {global_config.get('min_feature_length_chinese')}")
        else:
            print("   ✗ 未找到")
            return False
        
        # 测试 device_row_recognition
        print("\n4. 设备行识别配置 (device_row_recognition):")
        device_row_recognition = config.get('device_row_recognition')
        if device_row_recognition:
            print(f"   ✓ 已找到")
            print(f"   - probability_thresholds: {device_row_recognition.get('probability_thresholds')}")
            print(f"   - scoring_weights: {device_row_recognition.get('scoring_weights')}")
        else:
            print("   ✗ 未找到")
            return False
        
        print("\n" + "=" * 80)
        print("✓ 所有配置项测试通过")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ 配置加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_config()
    sys.exit(0 if success else 1)
