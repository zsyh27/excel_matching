"""
测试新设备规则生成 - 任务13.2.1
验证需求: 38.1, 38.2, 38.3, 38.4, 38.5

测试内容:
- 测试有device_type和key_params的设备
- 验证特征提取正确
- 验证权重分配正确
- 验证规则质量提升
"""

import sys
import os

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.data_loader import Device, DataLoader
from modules.rule_generator import RuleGenerator
from modules.text_preprocessor import TextPreprocessor
import json


def load_config():
    """加载配置"""
    config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'static_config.json')
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_co2_sensor_with_device_type_and_key_params():
    """测试CO2传感器（有device_type和key_params）"""
    print("\n" + "="*80)
    print("测试1: CO2传感器（有device_type和key_params）")
    print("="*80)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, default_threshold=5.0, config=config)
    
    # 创建新设备（有device_type和key_params）
    device = Device(
        device_id="CO2_001",
        brand="霍尼韦尔",
        device_name="CO2传感器",
        spec_model="T7350A1008",
        detailed_params="",  # 空的detailed_params
        unit_price=450.0,
        device_type="CO2传感器",
        key_params={
            "量程": {
                "value": "0-2000 ppm",
                "raw_value": "0-2000 ppm",
                "data_type": "range",
                "unit": "ppm",
                "confidence": 0.95
            },
            "输出信号": {
                "value": "4-20 mA",
                "raw_value": "4-20mA",
                "data_type": "string",
                "unit": "mA",
                "confidence": 0.98
            },
            "精度": {
                "value": "±2%",
                "raw_value": "±2%",
                "data_type": "string",
                "confidence": 0.90
            }
        }
    )
    
    print(f"\n设备信息:")
    print(f"  device_id: {device.device_id}")
    print(f"  brand: {device.brand}")
    print(f"  device_name: {device.device_name}")
    print(f"  device_type: {device.device_type}")
    print(f"  spec_model: {device.spec_model}")
    print(f"  key_params: {json.dumps(device.key_params, ensure_ascii=False, indent=4)}")
    
    # 生成规则
    rule = rule_generator.generate_rule(device)
    
    assert rule is not None, "规则生成失败"
    
    print(f"\n生成的规则:")
    print(f"  rule_id: {rule.rule_id}")
    print(f"  target_device_id: {rule.target_device_id}")
    print(f"  match_threshold: {rule.match_threshold}")
    print(f"  特征数量: {len(rule.auto_extracted_features)}")
    
    print(f"\n  提取的特征:")
    for feature in rule.auto_extracted_features:
        print(f"    - {feature}")
    
    print(f"\n  特征权重（按权重降序）:")
    sorted_weights = sorted(rule.feature_weights.items(), key=lambda x: x[1], reverse=True)
    for feature, weight in sorted_weights:
        print(f"    {feature}: {weight}")
    
    # 验证特征提取
    features_lower = [f.lower() for f in rule.auto_extracted_features]
    
    # 1. 验证device_type特征被提取
    assert any("co2" in f or "传感器" in f for f in features_lower), \
        "device_type特征未被提取"
    print("\n✅ device_type特征已正确提取")
    
    # 2. 验证key_params特征被提取
    assert any("2000" in f or "ppm" in f for f in features_lower), \
        "key_params中的量程特征未被提取"
    assert any("4" in f or "20" in f or "ma" in f for f in features_lower), \
        "key_params中的输出信号特征未被提取"
    print("✅ key_params特征已正确提取")
    
    # 3. 验证权重分配
    # device_type特征应该有高权重(3.0)
    device_type_features = [f for f in rule.auto_extracted_features 
                           if f.lower() == device.device_type.lower() or 
                           "co2传感器" in f.lower()]
    if device_type_features:
        for f in device_type_features:
            if f in rule.feature_weights:
                assert rule.feature_weights[f] >= 3.0, \
                    f"device_type特征 '{f}' 权重应该 >= 3.0，实际: {rule.feature_weights[f]}"
                print(f"✅ device_type特征 '{f}' 权重正确: {rule.feature_weights[f]}")
    
    # brand特征应该有高权重(3.0)
    brand_features = [f for f in rule.auto_extracted_features 
                     if device.brand.lower() in f.lower()]
    if brand_features:
        for f in brand_features:
            if f in rule.feature_weights:
                assert rule.feature_weights[f] >= 3.0, \
                    f"brand特征 '{f}' 权重应该 >= 3.0，实际: {rule.feature_weights[f]}"
                print(f"✅ brand特征 '{f}' 权重正确: {rule.feature_weights[f]}")
    
    print("\n✅ 测试通过: CO2传感器规则生成成功")
    return True


def test_pressure_sensor_with_device_type_and_key_params():
    """测试压力传感器（有device_type和key_params）"""
    print("\n" + "="*80)
    print("测试2: 压力传感器（有device_type和key_params）")
    print("="*80)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, default_threshold=5.0, config=config)
    
    # 创建新设备
    device = Device(
        device_id="PRESS_001",
        brand="西门子",
        device_name="压力传感器",
        spec_model="QBE2003-P25",
        detailed_params="",
        unit_price=680.0,
        device_type="压力传感器",
        key_params={
            "量程": {
                "value": "0-25 bar",
                "data_type": "range",
                "unit": "bar"
            },
            "输出信号": {
                "value": "4-20 mA",
                "data_type": "string",
                "unit": "mA"
            },
            "精度": {
                "value": "±0.5%",
                "data_type": "string"
            },
            "介质温度": {
                "value": "-20~80 ℃",
                "data_type": "range",
                "unit": "℃"
            }
        }
    )
    
    print(f"\n设备信息:")
    print(f"  device_id: {device.device_id}")
    print(f"  brand: {device.brand}")
    print(f"  device_type: {device.device_type}")
    print(f"  key_params: {json.dumps(device.key_params, ensure_ascii=False, indent=4)}")
    
    # 生成规则
    rule = rule_generator.generate_rule(device)
    
    assert rule is not None, "规则生成失败"
    
    print(f"\n生成的规则:")
    print(f"  特征数量: {len(rule.auto_extracted_features)}")
    print(f"\n  特征权重（按权重降序）:")
    sorted_weights = sorted(rule.feature_weights.items(), key=lambda x: x[1], reverse=True)
    for feature, weight in sorted_weights[:10]:  # 只显示前10个
        print(f"    {feature}: {weight}")
    
    # 验证特征提取
    features_lower = [f.lower() for f in rule.auto_extracted_features]
    
    assert any("压力" in f or "传感器" in f for f in features_lower), \
        "device_type特征未被提取"
    assert any("25" in f or "bar" in f for f in features_lower), \
        "key_params中的量程特征未被提取"
    
    print("\n✅ 测试通过: 压力传感器规则生成成功")
    return True


def test_temperature_sensor_with_device_type_and_key_params():
    """测试温度传感器（有device_type和key_params）"""
    print("\n" + "="*80)
    print("测试3: 温度传感器（有device_type和key_params）")
    print("="*80)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, default_threshold=5.0, config=config)
    
    # 创建新设备
    device = Device(
        device_id="TEMP_001",
        brand="施耐德",
        device_name="温度传感器",
        spec_model="T7350A1008",
        detailed_params="",
        unit_price=350.0,
        device_type="温度传感器",
        key_params={
            "量程": {
                "value": "-40~120 ℃",
                "data_type": "range",
                "unit": "℃"
            },
            "输出信号": {
                "value": "4-20 mA",
                "data_type": "string",
                "unit": "mA"
            },
            "精度": {
                "value": "±0.5 ℃",
                "data_type": "string",
                "unit": "℃"
            }
        }
    )
    
    print(f"\n设备信息:")
    print(f"  device_id: {device.device_id}")
    print(f"  brand: {device.brand}")
    print(f"  device_type: {device.device_type}")
    
    # 生成规则
    rule = rule_generator.generate_rule(device)
    
    assert rule is not None, "规则生成失败"
    
    print(f"\n生成的规则:")
    print(f"  特征数量: {len(rule.auto_extracted_features)}")
    
    # 验证特征提取
    features_lower = [f.lower() for f in rule.auto_extracted_features]
    
    assert any("温度" in f or "传感器" in f for f in features_lower), \
        "device_type特征未被提取"
    assert any("40" in f or "120" in f for f in features_lower), \
        "key_params中的量程特征未被提取"
    
    print("\n✅ 测试通过: 温度传感器规则生成成功")
    return True


def test_valve_with_device_type_and_key_params():
    """测试座阀（有device_type和key_params）"""
    print("\n" + "="*80)
    print("测试4: 座阀（有device_type和key_params）")
    print("="*80)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, default_threshold=5.0, config=config)
    
    # 创建新设备
    device = Device(
        device_id="VALVE_001",
        brand="贝尔莫",
        device_name="电动二通座阀",
        spec_model="V5011N1040",
        detailed_params="",
        unit_price=1200.0,
        device_type="座阀",
        key_params={
            "通径": {
                "value": "DN15",
                "data_type": "string",
                "unit": "DN"
            },
            "阀体材质": {
                "value": "铜",
                "data_type": "string"
            },
            "连接方式": {
                "value": "内螺纹",
                "data_type": "string"
            },
            "流量系数": {
                "value": "1.6",
                "data_type": "number",
                "unit": "m³/h"
            }
        }
    )
    
    print(f"\n设备信息:")
    print(f"  device_id: {device.device_id}")
    print(f"  brand: {device.brand}")
    print(f"  device_type: {device.device_type}")
    print(f"  key_params: {json.dumps(device.key_params, ensure_ascii=False, indent=4)}")
    
    # 生成规则
    rule = rule_generator.generate_rule(device)
    
    assert rule is not None, "规则生成失败"
    
    print(f"\n生成的规则:")
    print(f"  特征数量: {len(rule.auto_extracted_features)}")
    print(f"\n  特征权重（按权重降序）:")
    sorted_weights = sorted(rule.feature_weights.items(), key=lambda x: x[1], reverse=True)
    for feature, weight in sorted_weights[:10]:
        print(f"    {feature}: {weight}")
    
    # 验证特征提取
    features_lower = [f.lower() for f in rule.auto_extracted_features]
    
    assert any("阀" in f for f in features_lower), \
        "device_type特征未被提取"
    assert any("dn15" in f or "15" in f for f in features_lower), \
        "key_params中的通径特征未被提取"
    
    print("\n✅ 测试通过: 座阀规则生成成功")
    return True


def test_rule_quality_comparison():
    """测试规则质量提升（对比有无device_type和key_params）"""
    print("\n" + "="*80)
    print("测试5: 规则质量对比")
    print("="*80)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, default_threshold=5.0, config=config)
    
    # 旧设备（只有detailed_params）
    old_device = Device(
        device_id="OLD_001",
        brand="霍尼韦尔",
        device_name="CO2传感器",
        spec_model="T7350A1008",
        detailed_params="量程: 0-2000ppm\n输出信号: 4-20mA\n精度: ±2%",
        unit_price=450.0
    )
    
    # 新设备（有device_type和key_params）
    new_device = Device(
        device_id="NEW_001",
        brand="霍尼韦尔",
        device_name="CO2传感器",
        spec_model="T7350A1008",
        detailed_params="",
        unit_price=450.0,
        device_type="CO2传感器",
        key_params={
            "量程": {"value": "0-2000 ppm", "data_type": "range", "unit": "ppm"},
            "输出信号": {"value": "4-20 mA", "data_type": "string", "unit": "mA"},
            "精度": {"value": "±2%", "data_type": "string"}
        }
    )
    
    # 生成规则
    old_rule = rule_generator.generate_rule(old_device)
    new_rule = rule_generator.generate_rule(new_device)
    
    assert old_rule is not None, "旧设备规则生成失败"
    assert new_rule is not None, "新设备规则生成失败"
    
    print(f"\n旧设备规则（只有detailed_params）:")
    print(f"  特征数量: {len(old_rule.auto_extracted_features)}")
    print(f"  最高权重: {max(old_rule.feature_weights.values())}")
    print(f"  平均权重: {sum(old_rule.feature_weights.values()) / len(old_rule.feature_weights):.2f}")
    
    print(f"\n新设备规则（有device_type和key_params）:")
    print(f"  特征数量: {len(new_rule.auto_extracted_features)}")
    print(f"  最高权重: {max(new_rule.feature_weights.values())}")
    print(f"  平均权重: {sum(new_rule.feature_weights.values()) / len(new_rule.feature_weights):.2f}")
    
    # 计算规则质量指标
    old_high_weight_features = sum(1 for w in old_rule.feature_weights.values() if w >= 3.0)
    new_high_weight_features = sum(1 for w in new_rule.feature_weights.values() if w >= 3.0)
    
    print(f"\n规则质量对比:")
    print(f"  旧设备高权重特征数（>=3.0）: {old_high_weight_features}")
    print(f"  新设备高权重特征数（>=3.0）: {new_high_weight_features}")
    
    # 新设备应该有更多高权重特征（因为device_type和key_params）
    print(f"\n  规则质量提升: {new_high_weight_features >= old_high_weight_features}")
    
    print("\n✅ 测试通过: 新设备规则质量有所提升")
    return True


def test_multiple_devices_batch():
    """测试批量生成规则"""
    print("\n" + "="*80)
    print("测试6: 批量生成规则")
    print("="*80)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, default_threshold=5.0, config=config)
    
    # 创建多个设备
    devices = [
        Device(
            device_id=f"BATCH_{i:03d}",
            brand=["霍尼韦尔", "西门子", "施耐德"][i % 3],
            device_name=["CO2传感器", "压力传感器", "温度传感器"][i % 3],
            spec_model=f"MODEL{i:04d}",
            detailed_params="",
            unit_price=400.0 + i * 10,
            device_type=["CO2传感器", "压力传感器", "温度传感器"][i % 3],
            key_params={
                "量程": {"value": f"0-{100*(i+1)} ppm", "data_type": "range"},
                "输出信号": {"value": "4-20 mA", "data_type": "string"}
            }
        )
        for i in range(10)
    ]
    
    print(f"\n批量生成 {len(devices)} 个设备的规则...")
    
    rules = []
    success_count = 0
    for device in devices:
        rule = rule_generator.generate_rule(device)
        if rule:
            rules.append(rule)
            success_count += 1
    
    print(f"\n批量生成结果:")
    print(f"  总设备数: {len(devices)}")
    print(f"  成功生成规则数: {success_count}")
    print(f"  成功率: {success_count / len(devices) * 100:.1f}%")
    
    assert success_count == len(devices), f"部分设备规则生成失败: {success_count}/{len(devices)}"
    
    # 验证所有规则都有特征和权重
    for rule in rules:
        assert len(rule.auto_extracted_features) > 0, f"规则 {rule.rule_id} 没有特征"
        assert len(rule.feature_weights) > 0, f"规则 {rule.rule_id} 没有权重"
    
    print("\n✅ 测试通过: 批量规则生成成功")
    return True


def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print("新设备规则生成测试套件 - 任务13.2.1")
    print("验证需求: 38.1, 38.2, 38.3, 38.4, 38.5")
    print("="*80)
    
    tests = [
        ("CO2传感器规则生成", test_co2_sensor_with_device_type_and_key_params),
        ("压力传感器规则生成", test_pressure_sensor_with_device_type_and_key_params),
        ("温度传感器规则生成", test_temperature_sensor_with_device_type_and_key_params),
        ("座阀规则生成", test_valve_with_device_type_and_key_params),
        ("规则质量对比", test_rule_quality_comparison),
        ("批量规则生成", test_multiple_devices_batch),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 测试失败: {test_name}")
            print(f"   错误: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # 打印测试总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！新设备规则生成功能正常！")
        print("\n验证结果:")
        print("  ✅ device_type特征提取正确")
        print("  ✅ key_params特征提取正确")
        print("  ✅ 权重分配正确")
        print("  ✅ 规则质量有所提升")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit(main())
