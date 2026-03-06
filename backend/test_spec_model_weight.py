"""
测试规格型号权重分配
"""
import sys
sys.path.insert(0, '.')

from modules.data_loader import DataLoader, Device
from modules.rule_generator import RuleGenerator
from modules.text_preprocessor import TextPreprocessor
from config import Config

# 加载配置
loader = DataLoader(config=Config)
config = loader.load_config()

# 初始化预处理器和规则生成器
preprocessor = TextPreprocessor(config=config)
rule_gen = RuleGenerator(config=config, preprocessor=preprocessor)

# 创建测试设备
test_device = Device(
    device_id="TEST_001",
    brand="霍尼韦尔",
    device_type="电动调节阀",
    device_name="座阀",
    spec_model="V5011P2010",
    unit_price=4579.0,
    key_params={
        "介质": "蒸汽",
        "通径": "DN40",
        "通数": "二通"
    },
    detailed_params="",
    input_method="manual"
)

print("=" * 80)
print("测试设备信息")
print("=" * 80)
print(f"设备ID: {test_device.device_id}")
print(f"品牌: {test_device.brand}")
print(f"设备类型: {test_device.device_type}")
print(f"设备名称: {test_device.device_name}")
print(f"规格型号: {test_device.spec_model}")
print(f"规格型号(小写): {test_device.spec_model.lower()}")

print("\n" + "=" * 80)
print("提取特征")
print("=" * 80)
features = rule_gen.extract_features(test_device)
print(f"特征列表: {features}")

print("\n" + "=" * 80)
print("分配权重")
print("=" * 80)
weights = rule_gen.assign_weights(features, test_device)

for feature, weight in weights.items():
    print(f"特征: {feature:20s} 权重: {weight}")
    
    # 检查规格型号
    if feature.lower() == test_device.spec_model.lower():
        if weight == 15.0:
            print(f"  ✓ 规格型号权重正确")
        else:
            print(f"  ✗ 规格型号权重错误，应该是15.0，实际是{weight}")

print("\n" + "=" * 80)
print("生成规则")
print("=" * 80)
rule = rule_gen.generate_rule(test_device)
if rule:
    print(f"规则ID: {rule.rule_id}")
    print(f"特征数量: {len(rule.auto_extracted_features)}")
    print(f"特征权重:")
    import json
    print(json.dumps(rule.feature_weights, ensure_ascii=False, indent=2))
else:
    print("规则生成失败")
