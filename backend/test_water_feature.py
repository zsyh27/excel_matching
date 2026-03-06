"""
测试"水"特征是否被过滤
"""
import sys
sys.path.insert(0, '.')

from modules.data_loader import DataLoader, Device
from modules.rule_generator import RuleGenerator
from modules.text_preprocessor import TextPreprocessor
from config import Config
import json

print("=" * 80)
print("测试'水'特征是否被过滤")
print("=" * 80)

# 初始化
loader = DataLoader(config=Config)
config = loader.load_config()
preprocessor = TextPreprocessor(config=config)
rule_gen = RuleGenerator(config=config, preprocessor=preprocessor)

# 1. 检查预处理器配置
print("\n1. 预处理器配置:")
print(f"   最小特征长度: {preprocessor.min_feature_length}")

# 2. 测试预处理"水"
print("\n2. 测试预处理'水':")
result = preprocessor.preprocess("水", mode='device')
print(f"   输入: '水'")
print(f"   输出特征: {result.features}")
if result.features:
    print(f"   ✓ '水'没有被过滤")
else:
    print(f"   ✗ '水'被过滤了")

# 3. 创建测试设备（介质为"水"）
print("\n3. 创建测试设备（介质为'水'）:")
test_device = Device(
    device_id="TEST_WATER_001",
    brand="霍尼韦尔",
    device_type="电动调节阀",
    device_name="座阀",
    spec_model="V5011N1040",
    unit_price=4099.0,
    key_params={
        "介质": "水",  # 关键：介质为"水"
        "通径": "DN10",
        "通数": "二通"
    },
    detailed_params="",
    input_method="manual"
)

print(f"   设备ID: {test_device.device_id}")
print(f"   关键参数: {json.dumps(test_device.key_params, ensure_ascii=False)}")

# 4. 生成规则
print("\n4. 生成规则:")
rule = rule_gen.generate_rule(test_device)

if rule:
    print(f"   ✓ 规则生成成功")
    print(f"   规则ID: {rule.rule_id}")
    print(f"   特征数量: {len(rule.auto_extracted_features)}")
    print(f"   特征列表: {rule.auto_extracted_features}")
    print(f"\n   特征权重:")
    for feature, weight in sorted(rule.feature_weights.items(), key=lambda x: x[1], reverse=True):
        print(f"     {feature}: {weight}")
    
    # 5. 检查"水"是否在特征中
    print(f"\n5. 检查'水'是否在特征中:")
    if "水" in rule.auto_extracted_features:
        weight = rule.feature_weights.get("水", 0)
        print(f"   ✓ 找到特征'水'，权重: {weight}")
    else:
        print(f"   ✗ 特征'水'未找到")
        print(f"   可能的原因:")
        print(f"     1. 被预处理器过滤")
        print(f"     2. 在特征提取过程中被跳过")
        print(f"     3. key_params处理有问题")
else:
    print(f"   ✗ 规则生成失败")

# 6. 检查数据库中是否有介质为"水"的设备
print("\n" + "=" * 80)
print("6. 检查数据库中介质为'水'的设备:")
print("=" * 80)

devices = loader.load_devices()
water_devices = []

for device in devices.values():
    if hasattr(device, 'key_params') and device.key_params:
        if '介质' in device.key_params:
            medium = device.key_params['介质']
            if isinstance(medium, dict):
                medium = medium.get('value', '')
            if medium == '水':
                water_devices.append(device)

print(f"\n找到 {len(water_devices)} 个介质为'水'的设备")

if water_devices:
    # 检查第一个设备的规则
    device = water_devices[0]
    print(f"\n检查设备: {device.device_id}")
    print(f"  品牌: {device.brand}")
    print(f"  设备类型: {device.device_type}")
    print(f"  规格型号: {device.spec_model}")
    print(f"  关键参数: {json.dumps(device.key_params, ensure_ascii=False)}")
    
    # 查找规则
    rules = loader.load_rules()
    if isinstance(rules, dict):
        rule_list = list(rules.values())
    else:
        rule_list = rules
    
    device_rule = None
    for rule in rule_list:
        if rule.target_device_id == device.device_id:
            device_rule = rule
            break
    
    if device_rule:
        print(f"\n  规则ID: {device_rule.rule_id}")
        print(f"  特征: {device_rule.auto_extracted_features}")
        
        if "水" in device_rule.auto_extracted_features:
            weight = device_rule.feature_weights.get("水", 0)
            print(f"\n  ✓ 找到特征'水'，权重: {weight}")
        else:
            print(f"\n  ✗ 特征'水'未找到")
            print(f"  这可能是用旧代码生成的规则")
            print(f"  建议重新生成规则")
    else:
        print(f"\n  ✗ 没有找到规则")
else:
    print("\n没有找到介质为'水'的设备")
    print("Excel文件中的设备介质可能是'蒸汽'而不是'水'")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
