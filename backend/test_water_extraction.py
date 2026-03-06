"""
测试"水"特征提取
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator
from modules.data_loader import Device

print("=" * 80)
print("测试'水'特征提取")
print("=" * 80)

# 加载配置
with open('../data/static_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

print("\n【配置检查】")
print("-" * 80)
print(f"metadata_keywords中是否包含'介质': {'介质' in config.get('metadata_keywords', [])}")
print(f"whitelist_features: {config.get('intelligent_extraction', {}).get('feature_quality_scoring', {}).get('whitelist_features', [])}")

# 创建预处理器
preprocessor = TextPreprocessor(config)

print("\n【测试1：直接提取'水'】")
print("-" * 80)
test_text = "水"
result = preprocessor.preprocess(test_text, mode='device')
print(f"输入: {test_text}")
print(f"清理后: {result.cleaned}")
print(f"归一化后: {result.normalized}")
print(f"提取的特征: {result.features}")
print(f"✓ 成功" if '水' in result.features else "✗ 失败")

print("\n【测试2：从'介质: 水'提取】")
print("-" * 80)
test_text = "介质: 水"
result = preprocessor.preprocess(test_text, mode='device')
print(f"输入: {test_text}")
print(f"清理后: {result.cleaned}")
print(f"归一化后: {result.normalized}")
print(f"提取的特征: {result.features}")
print(f"✓ 成功" if '水' in result.features else "✗ 失败")

print("\n【测试3：从key_params提取】")
print("-" * 80)

# 创建模拟设备
class MockDevice:
    def __init__(self):
        self.device_id = 'TEST_001'
        self.device_name = '电动调节阀'
        self.device_type = '电动调节阀'
        self.brand = '霍尼韦尔'
        self.spec_model = 'V5013P1010'
        self.key_params = {
            '介质': '水',
            '执行器品牌': '霍尼韦尔',
            '执行器型号': 'ML7420A8088',
            '通径': 'DN10',
            '通数': '二通',
            '阀体类型': '座阀'
        }
        self.detailed_params = None
        self.unit_price = None
        self.input_method = 'manual'

device = MockDevice()

# 创建规则生成器
rule_generator = RuleGenerator(preprocessor, config=config)

# 提取特征
features = rule_generator.extract_features(device)
print(f"设备key_params: {device.key_params}")
print(f"提取的特征: {features}")
print(f"✓ 成功" if '水' in features else "✗ 失败")

# 分配权重
weights = rule_generator.assign_weights(features, device)
print(f"\n特征权重:")
for feature, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
    print(f"  {feature}: {weight}")

# 检查spec_model权重
spec_model_lower = device.spec_model.lower()
if spec_model_lower in weights:
    actual_weight = weights[spec_model_lower]
    expected_weight = 5.0
    print(f"\nspec_model权重检查:")
    print(f"  特征: {spec_model_lower}")
    print(f"  实际权重: {actual_weight}")
    print(f"  期望权重: {expected_weight}")
    if actual_weight == expected_weight:
        print(f"  ✓ 权重正确")
    else:
        print(f"  ✗ 权重错误！")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
