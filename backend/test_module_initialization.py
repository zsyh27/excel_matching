#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试模块初始化是否正确使用新配置
"""

import json
import sys

def test_module_initialization():
    """测试模块初始化"""
    try:
        # 加载配置文件
        with open('data/static_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("=" * 80)
        print("模块初始化测试")
        print("=" * 80)
        
        # 测试 TextPreprocessor
        print("\n1. 测试 TextPreprocessor:")
        from modules.text_preprocessor import TextPreprocessor
        preprocessor = TextPreprocessor(config)
        print(f"   ✓ TextPreprocessor 初始化成功")
        print(f"   - metadata_keywords 数量: {len(preprocessor.metadata_keywords)}")
        print(f"   - min_feature_length: {preprocessor.min_feature_length}")
        print(f"   - min_feature_length_chinese: {preprocessor.min_feature_length_chinese}")
        
        # 测试 RuleGenerator
        print("\n2. 测试 RuleGenerator:")
        from modules.rule_generator import RuleGenerator
        rule_generator = RuleGenerator(preprocessor, default_threshold=5.0, config=config)
        print(f"   ✓ RuleGenerator 初始化成功")
        print(f"   - brand_weight: {rule_generator.brand_weight}")
        print(f"   - model_weight: {rule_generator.model_weight}")
        print(f"   - device_type_weight: {rule_generator.device_type_weight}")
        print(f"   - parameter_weight: {rule_generator.parameter_weight}")
        print(f"   - device_type_keywords 数量: {len(rule_generator.device_type_keywords)}")
        print(f"   - brand_keywords 数量: {len(rule_generator.brand_keywords)}")
        
        # 测试 MatchEngine
        print("\n3. 测试 MatchEngine:")
        from modules.match_engine import MatchEngine
        match_engine = MatchEngine(rules=[], devices={}, config=config)
        print(f"   ✓ MatchEngine 初始化成功")
        print(f"   - device_type_keywords 数量: {len(match_engine.device_type_keywords)}")
        print(f"   - default_match_threshold: {match_engine.default_match_threshold}")
        
        print("\n" + "=" * 80)
        print("✓ 所有模块初始化测试通过")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\n✗ 模块初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_module_initialization()
    sys.exit(0 if success else 1)
