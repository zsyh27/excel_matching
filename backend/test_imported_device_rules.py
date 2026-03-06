# -*- coding: utf-8 -*-
"""
测试导入设备的规则生成
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.data_loader import DataLoader, Device
from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator
from config import Config
import json

print("=" * 80)
print("测试导入设备的规则生成")
print("=" * 80)

# 初始化组件
from modules.data_loader import ConfigManager
config_manager = ConfigManager(Config.CONFIG_FILE)
config = config_manager.get_config()

preprocessor = TextPreprocessor(config)
rule_gen = RuleGenerator(config=config, preprocessor=preprocessor)

# 创建测试设备（模拟从Excel导入的设备）
test_device = Device(
    device_id='test_001',
    brand='霍尼韦尔',
    device_type='电动调节阀',
    device_name='座阀',
    spec_model='V5011P2036',
    unit_price=3738.0,
    key_params={
        '介质': '蒸汽',
        '执行器品牌': '霍尼韦尔',
        '执行器型号': 'ML8824A1820',
        '通径': 'DN25',
        '通数': '二通',
        '阀体类型': '座阀'
    },
    detailed_params='',
    input_method='excel'
)

print(f"\n测试设备:")
print(f"  设备ID: {test_device.device_id}")
print(f"  品牌: {test_device.brand}")
print(f"  设备类型: {test_device.device_type}")
print(f"  设备名称: {test_device.device_name}")
print(f"  规格型号: {test_device.spec_model}")
print(f"  单价: {test_device.unit_price}")
print(f"  关键参数: {json.dumps(test_device.key_params, ensure_ascii=False)}")

# 生成规则
print("\n生成规则...")
rule = rule_gen.generate_rule(test_device)

if rule:
    print(f"\n规则生成成功:")
    print(f"  规则ID: {rule.rule_id}")
    print(f"  目标设备ID: {rule.target_device_id}")
    print(f"  总权重: {rule.total_weight}")
    print(f"\n特征列表 (共 {len(rule.features)} 个):")
    
    # 按权重排序
    sorted_features = sorted(rule.features, key=lambda x: x['weight'], reverse=True)
    
    for i, feature in enumerate(sorted_features, 1):
        print(f"  {i}. {feature['feature']} - 权重: {feature['weight']}")
    
    # 检查关键特征
    print("\n关键特征检查:")
    
    # 检查device_type
    device_type_features = [f for f in rule.features if f['feature'] == test_device.device_type]
    if device_type_features:
        print(f"  ✓ device_type '{test_device.device_type}' 权重: {device_type_features[0]['weight']}")
    else:
        print(f"  ✗ device_type '{test_device.device_type}' 未找到")
    
    # 检查spec_model
    spec_model_features = [f for f in rule.features if f['feature'] == test_device.spec_model or f['feature'].lower() == test_device.spec_model.lower()]
    if spec_model_features:
        print(f"  ✓ spec_model '{test_device.spec_model}' 权重: {spec_model_features[0]['weight']}")
    else:
        print(f"  ✗ spec_model '{test_device.spec_model}' 未找到")
        # 查找可能的型号特征
        possible_model = [f for f in rule.features if test_device.spec_model.lower() in f['feature'].lower()]
        if possible_model:
            print(f"    可能的型号特征: {possible_model}")
    
    # 检查brand
    brand_features = [f for f in rule.features if f['feature'] == test_device.brand]
    if brand_features:
        print(f"  ✓ brand '{test_device.brand}' 权重: {brand_features[0]['weight']}")
    else:
        print(f"  ✗ brand '{test_device.brand}' 未找到")
    
    # 检查key_params特征
    print(f"\n  key_params特征:")
    for param_name, param_value in test_device.key_params.items():
        param_features = [f for f in rule.features if param_value in f['feature']]
        if param_features:
            for pf in param_features:
                print(f"    ✓ '{param_value}' (来自{param_name}) 权重: {pf['weight']}")
        else:
            print(f"    ✗ '{param_value}' (来自{param_name}) 未找到")
    
else:
    print("\n规则生成失败")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
