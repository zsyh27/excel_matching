#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复匹配引擎以支持新的规则格式"""

import sys
sys.path.insert(0, 'backend')

print("🔧 分析匹配引擎与新规则格式的兼容性问题...")

# 问题分析
print("\n📋 问题分析:")
print("1. 规则格式已更新为字典格式:")
print("   [{'feature': '霍尼韦尔', 'weight': 10, 'type': 'brand'}, ...]")
print()
print("2. 匹配引擎仍期望字符串列表格式:")
print("   rule_features_set = set(rule.auto_extracted_features)")
print("   # 这会导致 set() 包含字典对象，无法正确匹配")
print()
print("3. 权重获取逻辑:")
print("   weight = rule.feature_weights.get(feature, 1.0)")
print("   # feature_weights 字典仍然存在，但应该从字典格式特征中获取权重")

print("\n🔍 解决方案:")
print("需要修改匹配引擎的 calculate_weight_score 方法，使其能够:")
print("1. 正确处理字典格式的 auto_extracted_features")
print("2. 从字典中提取特征名称和权重")
print("3. 保持向后兼容性（支持旧的字符串列表格式）")

print("\n📝 具体修改建议:")
print("""
def calculate_weight_score(self, features: List[str], rule) -> Tuple[float, List[str]]:
    weight_score = 0.0
    matched_features = []
    
    # 处理新的字典格式特征
    if rule.auto_extracted_features and isinstance(rule.auto_extracted_features[0], dict):
        # 新格式：[{'feature': 'xxx', 'weight': 10, 'type': 'brand'}, ...]
        rule_features_dict = {f['feature']: f['weight'] for f in rule.auto_extracted_features}
        rule_features_set = set(rule_features_dict.keys())
        
        for feature in features:
            if feature in rule_features_set:
                weight = rule_features_dict[feature]
                weight_score += weight
                matched_features.append(feature)
            else:
                # 同义词匹配逻辑...
                
    else:
        # 旧格式：['霍尼韦尔', '智能照明设备', ...]
        rule_features_set = set(rule.auto_extracted_features)
        
        for feature in features:
            if feature in rule_features_set:
                weight = rule.feature_weights.get(feature, 1.0)
                weight_score += weight
                matched_features.append(feature)
            else:
                # 同义词匹配逻辑...
    
    return weight_score, matched_features
""")

print("\n⚠️ 重要提醒:")
print("这个修改需要在 backend/modules/match_engine.py 中进行")
print("修改后需要重启后端服务才能生效")

print("\n🎯 修改完成后的测试步骤:")
print("1. 修改 match_engine.py 中的 calculate_weight_score 方法")
print("2. 重启后端服务")
print("3. 运行匹配测试验证修复效果")

print("\n修复分析完成！")