"""
测试同义词映射在匹配阶段的使用

验证：
1. 预处理阶段不再应用同义词映射
2. 匹配阶段使用同义词扩展进行模糊匹配
3. 保留原始词汇，提高召回率
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from modules.text_preprocessor import TextPreprocessor
from modules.match_engine import MatchEngine
from modules.data_loader import Device, Rule

def test_synonym_in_matching():
    """测试同义词在匹配阶段的使用"""
    
    print("=" * 80)
    print("同义词映射在匹配阶段的测试")
    print("=" * 80)
    
    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'static_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 检查同义词映射配置
    synonym_map = config.get('synonym_map', {})
    print(f"\n同义词映射配置（共{len(synonym_map)}对）:")
    for i, (old_word, new_word) in enumerate(list(synonym_map.items())[:5], 1):
        print(f"  {i}. {old_word} → {new_word}")
    if len(synonym_map) > 5:
        print(f"  ...")
    
    # 创建预处理器
    preprocessor = TextPreprocessor(config)
    
    # 测试1: 验证预处理阶段不再应用同义词映射
    print("\n" + "=" * 80)
    print("测试1: 预处理阶段不应用同义词映射")
    print("=" * 80)
    
    # 假设配置中有 "阀" → "阀门" 的映射
    test_text1 = "霍尼韦尔+阀+二通+dn15"
    result1 = preprocessor.preprocess(test_text1, mode='matching')
    
    print(f"\n输入文本: {test_text1}")
    print(f"提取特征: {result1.features}")
    
    # 检查是否保留了原始词汇
    if "阀" in result1.features:
        print("  ✓ 原始词汇 '阀' 被保留（正确）")
    else:
        print("  ✗ 原始词汇 '阀' 未被保留（错误）")
    
    if "阀门" in result1.features:
        print("  ✗ 同义词 '阀门' 出现在特征中（错误，不应该在预处理阶段替换）")
    else:
        print("  ✓ 同义词 '阀门' 未出现在特征中（正确）")
    
    # 测试2: 验证匹配阶段使用同义词扩展
    print("\n" + "=" * 80)
    print("测试2: 匹配阶段使用同义词扩展")
    print("=" * 80)
    
    # 创建测试规则和设备
    # 规则使用 "阀门"
    test_rule = Rule(
        rule_id="TEST_RULE_001",
        target_device_id="TEST_DEVICE_001",
        auto_extracted_features=["霍尼韦尔", "阀门", "二通", "dn15"],
        feature_weights={"霍尼韦尔": 3.0, "阀门": 5.0, "二通": 5.0, "dn15": 1.0},
        match_threshold=5.0,
        remark="测试规则"
    )
    
    test_device = Device(
        device_id="TEST_DEVICE_001",
        brand="霍尼韦尔",
        device_name="阀门",
        spec_model="二通+DN15",
        detailed_params="",
        unit_price=1000.0
    )
    
    # 创建匹配引擎
    rules = [test_rule]
    devices = {test_device.device_id: test_device}
    match_engine = MatchEngine(rules, devices, config)
    
    # Excel输入使用 "阀"（同义词）
    excel_features = ["霍尼韦尔", "阀", "二通", "dn15"]
    
    print(f"\nExcel特征: {excel_features}")
    print(f"规则特征: {test_rule.auto_extracted_features}")
    
    # 计算权重得分
    weight_score, matched_features = match_engine.calculate_weight_score(excel_features, test_rule)
    
    print(f"\n匹配结果:")
    print(f"  权重得分: {weight_score}")
    print(f"  匹配特征: {matched_features}")
    print(f"  匹配阈值: {test_rule.match_threshold}")
    
    # 验证同义词扩展是否工作
    if "阀门" in matched_features:
        print(f"\n  ✓ 同义词扩展成功：'阀' 匹配到规则中的 '阀门'")
        print(f"  ✓ 权重得分包含了 '阀门' 的权重: {test_rule.feature_weights.get('阀门', 0)}")
    else:
        print(f"\n  ✗ 同义词扩展失败：'阀' 未能匹配到规则中的 '阀门'")
    
    if weight_score >= test_rule.match_threshold:
        print(f"  ✓ 匹配成功（得分 {weight_score} >= 阈值 {test_rule.match_threshold}）")
    else:
        print(f"  ✗ 匹配失败（得分 {weight_score} < 阈值 {test_rule.match_threshold}）")
    
    # 测试3: 反向同义词匹配
    print("\n" + "=" * 80)
    print("测试3: 反向同义词匹配")
    print("=" * 80)
    
    # 规则使用 "阀"
    test_rule2 = Rule(
        rule_id="TEST_RULE_002",
        target_device_id="TEST_DEVICE_002",
        auto_extracted_features=["霍尼韦尔", "阀", "二通", "dn15"],
        feature_weights={"霍尼韦尔": 3.0, "阀": 5.0, "二通": 5.0, "dn15": 1.0},
        match_threshold=5.0,
        remark="测试规则2"
    )
    
    # Excel输入使用 "阀门"（目标词）
    excel_features2 = ["霍尼韦尔", "阀门", "二通", "dn15"]
    
    print(f"\nExcel特征: {excel_features2}")
    print(f"规则特征: {test_rule2.auto_extracted_features}")
    
    # 计算权重得分
    weight_score2, matched_features2 = match_engine.calculate_weight_score(excel_features2, test_rule2)
    
    print(f"\n匹配结果:")
    print(f"  权重得分: {weight_score2}")
    print(f"  匹配特征: {matched_features2}")
    
    # 验证反向同义词扩展是否工作
    if "阀" in matched_features2:
        print(f"\n  ✓ 反向同义词扩展成功：'阀门' 匹配到规则中的 '阀'")
    else:
        print(f"\n  ✗ 反向同义词扩展失败：'阀门' 未能匹配到规则中的 '阀'")
    
    # 总结
    print("\n" + "=" * 80)
    print("总结")
    print("=" * 80)
    print("""
同义词映射的新工作方式：

1. 预处理阶段：
   - 不再应用同义词映射
   - 保留原始词汇
   - 特征提取保持原样

2. 匹配阶段：
   - 使用同义词扩展进行模糊匹配
   - 支持双向匹配（原词→目标词，目标词→原词）
   - 提高召回率，不丢失信息

3. 优势：
   - 保留原始信息
   - 灵活的匹配策略
   - 更好的可维护性
    """)


if __name__ == '__main__':
    test_synonym_in_matching()
