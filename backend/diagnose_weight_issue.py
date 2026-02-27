"""
诊断权重配置问题
检查配置和规则生成逻辑
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from modules.data_loader import DataLoader, ConfigManager
from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator

print("=" * 80)
print("诊断权重配置问题")
print("=" * 80)

# 1. 检查JSON配置文件
print("\n步骤1: 检查JSON配置文件")
config_manager = ConfigManager(Config.CONFIG_FILE)
json_config = config_manager.get_config()
feature_weight_config = json_config.get('feature_weight_config', {})
print(f"JSON文件中的特征权重配置:")
print(f"  brand_weight: {feature_weight_config.get('brand_weight')}")
print(f"  model_weight: {feature_weight_config.get('model_weight')}")
print(f"  device_type_weight: {feature_weight_config.get('device_type_weight')}")
print(f"  parameter_weight: {feature_weight_config.get('parameter_weight')}")

# 2. 检查数据库配置
print("\n步骤2: 检查数据库配置")
preprocessor = TextPreprocessor(json_config)
data_loader = DataLoader(config=Config, preprocessor=preprocessor)
db_config = data_loader.load_config()
db_feature_weight_config = db_config.get('feature_weight_config', {})
print(f"数据库中的特征权重配置:")
print(f"  brand_weight: {db_feature_weight_config.get('brand_weight')}")
print(f"  model_weight: {db_feature_weight_config.get('model_weight')}")
print(f"  device_type_weight: {db_feature_weight_config.get('device_type_weight')}")
print(f"  parameter_weight: {db_feature_weight_config.get('parameter_weight')}")

# 3. 测试规则生成器
print("\n步骤3: 测试规则生成器")
rule_generator = RuleGenerator(preprocessor, default_threshold=5.0, config=db_config)
print(f"规则生成器中的权重配置:")
print(f"  brand_weight: {rule_generator.brand_weight}")
print(f"  model_weight: {rule_generator.model_weight}")
print(f"  device_type_weight: {rule_generator.device_type_weight}")
print(f"  parameter_weight: {rule_generator.parameter_weight}")

# 4. 检查特定设备的规则
print("\n步骤4: 检查设备 V5011N1040_U000000000000000001 的规则")
devices = data_loader.load_devices()
target_device_id = "V5011N1040_U000000000000000001"

if target_device_id in devices:
    device = devices[target_device_id]
    print(f"\n设备信息:")
    print(f"  device_id: {device.device_id}")
    print(f"  brand: {device.brand}")
    print(f"  device_name: {device.device_name}")
    print(f"  spec_model: {device.spec_model}")
    
    # 提取特征
    features = rule_generator.extract_features(device)
    print(f"\n提取的特征: {features}")
    
    # 分配权重
    feature_weights = rule_generator.assign_weights(features)
    print(f"\n特征权重:")
    for feature, weight in feature_weights.items():
        print(f"  {feature}: {weight}")
    
    # 检查数据库中的规则
    print(f"\n数据库中的规则:")
    rules = data_loader.load_rules()
    target_rule = None
    for rule in rules:
        if rule.target_device_id == target_device_id:
            target_rule = rule
            break
    
    if target_rule:
        print(f"  rule_id: {target_rule.rule_id}")
        print(f"  match_threshold: {target_rule.match_threshold}")
        print(f"  特征权重:")
        for feature, weight in target_rule.feature_weights.items():
            print(f"    {feature}: {weight}")
    else:
        print("  未找到规则")
else:
    print(f"未找到设备: {target_device_id}")

print("\n" + "=" * 80)
print("诊断完成")
print("=" * 80)
