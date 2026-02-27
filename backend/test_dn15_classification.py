"""
测试 dn15 的分类问题
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from modules.data_loader import ConfigManager
from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator

# 加载配置
config_manager = ConfigManager(Config.CONFIG_FILE)
config = config_manager.get_config()

# 创建预处理器和规则生成器
preprocessor = TextPreprocessor(config)
rule_generator = RuleGenerator(preprocessor, config=config)

# 测试特征分类
test_features = [
    'dn15',      # 通径参数，应该是参数
    'dn20',      # 通径参数，应该是参数
    'dn25',      # 通径参数，应该是参数
    'v5011n1040',  # 型号，应该是型号
    'qaa2061',     # 型号，应该是型号
    'ml6420a3018', # 型号，应该是型号
    '水',          # 介质参数，应该是参数
    '座阀',        # 设备类型，应该是设备类型
]

print("=" * 80)
print("特征分类测试")
print("=" * 80)

for feature in test_features:
    is_model = rule_generator._is_model_number(feature)
    weights = rule_generator.assign_weights([feature])
    weight = weights.get(feature, 0)
    
    print(f"\n特征: {feature}")
    print(f"  是否型号: {is_model}")
    print(f"  分配权重: {weight}")
    
    # 判断类型
    if any(brand in feature for brand in rule_generator.brand_keywords):
        feature_type = "品牌"
    elif is_model:
        feature_type = "型号"
    elif any(keyword in feature for keyword in rule_generator.device_type_keywords):
        feature_type = "设备类型"
    else:
        feature_type = "参数"
    
    print(f"  识别类型: {feature_type}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
