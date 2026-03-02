"""
测试智能权重分配功能
"""

import json
from modules.rule_generator import RuleGenerator
from modules.text_preprocessor import TextPreprocessor
from modules.data_loader import Device

# 加载配置
with open('../data/static_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 创建预处理器和规则生成器
preprocessor = TextPreprocessor(config)
rule_generator = RuleGenerator(preprocessor, config=config)

# 测试案例1: CO2传感器
print("=" * 80)
print("测试案例1: CO2传感器")
print("=" * 80)

device1 = Device(
    device_id="TEST_001",
    brand="霍尼韦尔",
    device_name="室内CO2传感器",
    spec_model="QAA2061",
    detailed_params="485传输方式+量程0-2000ppm+输出信号4-20mA+精度±5%",
    unit_price=1000.0
)

features1 = rule_generator.extract_features(device1)
weights1 = rule_generator.assign_weights(features1)

print(f"\n提取的特征: {features1}")
print(f"\n特征权重:")
for feature, weight in sorted(weights1.items(), key=lambda x: x[1], reverse=True):
    print(f"  {feature}: {weight}")

# 测试案例2: 温湿度传感器
print("\n" + "=" * 80)
print("测试案例2: 温湿度传感器")
print("=" * 80)

device2 = Device(
    device_id="TEST_002",
    brand="霍尼韦尔",
    device_name="室内温湿度传感器",
    spec_model="QAA2061",
    detailed_params="485传输方式+温度范围0-50℃+湿度范围0-100%RH+输出信号4-20mA+精度±2%",
    unit_price=800.0
)

features2 = rule_generator.extract_features(device2)
weights2 = rule_generator.assign_weights(features2)

print(f"\n提取的特征: {features2}")
print(f"\n特征权重:")
for feature, weight in sorted(weights2.items(), key=lambda x: x[1], reverse=True):
    print(f"  {feature}: {weight}")

# 测试案例3: PM传感器
print("\n" + "=" * 80)
print("测试案例3: PM传感器")
print("=" * 80)

device3 = Device(
    device_id="TEST_003",
    brand="霍尼韦尔",
    device_name="室内PM传感器",
    spec_model="QAA2061",
    detailed_params="485传输方式+量程0-1000ug/m3+输出信号4-20mA+精度±10%+分辨率1ug/m3",
    unit_price=1200.0
)

features3 = rule_generator.extract_features(device3)
weights3 = rule_generator.assign_weights(features3)

print(f"\n提取的特征: {features3}")
print(f"\n特征权重:")
for feature, weight in sorted(weights3.items(), key=lambda x: x[1], reverse=True):
    print(f"  {feature}: {weight}")

# 分析权重分配策略
print("\n" + "=" * 80)
print("权重分配策略分析")
print("=" * 80)

weight_strategy = config.get('feature_weight_strategy', {})
print(f"\n配置的权重策略:")
print(f"  设备类型关键词: {weight_strategy.get('device_type_weight', 15.0)}")
print(f"  品牌关键词: {weight_strategy.get('brand_weight', 10.0)}")
print(f"  型号特征: {weight_strategy.get('model_weight', 6.0)}")
print(f"  重要参数: {weight_strategy.get('important_param_weight', 3.0)}")
print(f"  通用参数: {weight_strategy.get('common_param_weight', 1.0)}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
