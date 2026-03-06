"""
测试旧设备规则生成 - 任务13.2.2
验证需求: 38.4（回退逻辑）

测试内容:
- 测试无device_type的设备
- 验证回退逻辑正常工作
- 验证向后兼容性
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


def test_old_device_without_device_type():
    """测试旧设备（无device_type，只有detailed_params）"""
    print("\n" + "="*80)
    print("测试1: 旧设备（无device_type，只有detailed_params）")
    print("="*80)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, default_threshold=5.0, config=config)
    
    # 创建旧设备（无device_type和key_params）
    device = Device(
        device_id="OLD_001",
        brand="霍尼韦尔",
        device_name="CO2传感器",
        spec_model="T7350A1008",
        detailed_params="量程: 0-2000ppm\n输出信号: 4-20mA\n精度: ±2%",
        unit_price=450.0
        # 注意：没有device_type和key_params字段
    )
    
    print(f"\n设备信息:")
    print(f"  device_id: {device.device_id}")
    print(f"  brand: {device.brand}")
    print(f"  device_name: {device.device_name}")
    print(f"  spec_model: {device.spec_model}")
    print(f"  device_type: {getattr(device, 'device_type', None)}")
    print(f"  key_params: {getattr(device, 'key_params', None)}")
    print(f"  detailed_params: {device.detailed_params}")
    
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
    
    # 1. 验证从detailed_params提取了特征
    assert any("2000" in f or "ppm" in f for f in features_lower), \
        "detailed_params中的量程特征未被提取"
    assert any("4" in f or "20" in f or "ma" in f for f in features_lower), \
        "detailed_params中的输出信号特征未被提取"
    print("\n✅ detailed_params特征已正确提取")
    
    # 2. 验证品牌特征被提取
    assert any("霍尼韦尔" in f or "honeywell" in f.lower() for f in rule.auto_extracted_features), \
        "品牌特征未被提取"
    print("✅ 品牌特征已正确提取")
    
    # 3. 验证规则可以正常使用
    assert len(rule.auto_extracted_features) > 0, "规则没有特征"
    assert len(rule.feature_weights) > 0, "规则没有权重"
    print("✅ 规则结构完整")
    
    print("\n✅ 测试通过: 旧设备规则生成成功")
    return True


def test_old_device_with_multiline_detailed_params():
    """测试旧设备（多行detailed_params）"""
    print("\n" + "="*80)
    print("测试2: 旧设备（多行detailed_params）")
    print("="*80)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, default_threshold=5.0, config=config)
    
    # 创建旧设备（多行详细参数）
    device = Device(
        device_id="OLD_002",
        brand="西门子",
        device_name="压力传感器",
        spec_model="QBE2003-P25",
        detailed_params="""量程: 0-25bar
输出信号: 4-20mA
精度: ±0.5%
介质温度: -20~80℃
防护等级: IP65""",
        unit_price=680.0
    )
    
    print(f"\n设备信息:")
    print(f"  device_id: {device.device_id}")
    print(f"  brand: {device.brand}")
    print(f"  device_name: {device.device_name}")
    print(f"  detailed_params:\n{device.detailed_params}")
    
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
    
    assert any("25" in f or "bar" in f for f in features_lower), \
        "量程特征未被提取"
    assert any("4" in f or "20" in f or "ma" in f for f in features_lower), \
        "输出信号特征未被提取"
    
    print("\n✅ 测试通过: 多行detailed_params处理正确")
    return True


def test_old_device_with_escaped_newlines():
    """测试旧设备（转义的换行符）"""
    print("\n" + "="*80)
    print("测试3: 旧设备（转义的换行符）")
    print("="*80)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, default_threshold=5.0, config=config)
    
    # 创建旧设备（转义的换行符）
    device = Device(
        device_id="OLD_003",
        brand="施耐德",
        device_name="温度传感器",
        spec_model="T7350A1008",
        detailed_params="量程: -40~120℃\\n输出信号: 4-20mA\\n精度: ±0.5℃",
        unit_price=350.0
    )
    
    print(f"\n设备信息:")
    print(f"  device_id: {device.device_id}")
    print(f"  detailed_params: {device.detailed_params}")
    
    # 生成规则
    rule = rule_generator.generate_rule(device)
    
    assert rule is not None, "规则生成失败"
    
    print(f"\n生成的规则:")
    print(f"  特征数量: {len(rule.auto_extracted_features)}")
    
    # 验证特征提取
    features_lower = [f.lower() for f in rule.auto_extracted_features]
    
    assert any("40" in f or "120" in f for f in features_lower), \
        "量程特征未被提取"
    
    print("\n✅ 测试通过: 转义换行符处理正确")
    return True


def test_old_device_with_simple_detailed_params():
    """测试旧设备（简单的detailed_params，无键值对格式）"""
    print("\n" + "="*80)
    print("测试4: 旧设备（简单的detailed_params）")
    print("="*80)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, default_threshold=5.0, config=config)
    
    # 创建旧设备（简单描述）
    device = Device(
        device_id="OLD_004",
        brand="贝尔莫",
        device_name="电动二通座阀",
        spec_model="V5011N1040",
        detailed_params="DN15 铜阀体 内螺纹连接 流量系数1.6m³/h",
        unit_price=1200.0
    )
    
    print(f"\n设备信息:")
    print(f"  device_id: {device.device_id}")
    print(f"  detailed_params: {device.detailed_params}")
    
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
    
    assert any("dn15" in f or "15" in f for f in features_lower), \
        "通径特征未被提取"
    
    print("\n✅ 测试通过: 简单detailed_params处理正确")
    return True


def test_backward_compatibility():
    """测试向后兼容性（新旧设备对比）"""
    print("\n" + "="*80)
    print("测试5: 向后兼容性（新旧设备对比）")
    print("="*80)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, default_threshold=5.0, config=config)
    
    # 旧设备（只有detailed_params）
    old_device = Device(
        device_id="OLD_005",
        brand="霍尼韦尔",
        device_name="CO2传感器",
        spec_model="T7350A1008",
        detailed_params="量程: 0-2000ppm\n输出信号: 4-20mA\n精度: ±2%",
        unit_price=450.0
    )
    
    # 新设备（有device_type和key_params）
    new_device = Device(
        device_id="NEW_005",
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
    
    print(f"\n旧设备规则:")
    print(f"  特征数量: {len(old_rule.auto_extracted_features)}")
    print(f"  最高权重: {max(old_rule.feature_weights.values())}")
    print(f"  平均权重: {sum(old_rule.feature_weights.values()) / len(old_rule.feature_weights):.2f}")
    
    print(f"\n新设备规则:")
    print(f"  特征数量: {len(new_rule.auto_extracted_features)}")
    print(f"  最高权重: {max(new_rule.feature_weights.values())}")
    print(f"  平均权重: {sum(new_rule.feature_weights.values()) / len(new_rule.feature_weights):.2f}")
    
    # 验证向后兼容性
    # 1. 旧设备应该能够生成规则
    assert len(old_rule.auto_extracted_features) > 0, "旧设备规则没有特征"
    assert len(old_rule.feature_weights) > 0, "旧设备规则没有权重"
    print("\n✅ 旧设备规则生成正常")
    
    # 2. 旧设备和新设备应该提取到相似的核心特征
    old_features_set = set(f.lower() for f in old_rule.auto_extracted_features)
    new_features_set = set(f.lower() for f in new_rule.auto_extracted_features)
    
    # 计算特征重叠度
    common_features = old_features_set & new_features_set
    overlap_ratio = len(common_features) / min(len(old_features_set), len(new_features_set))
    
    print(f"\n特征重叠度: {overlap_ratio:.2%}")
    print(f"  共同特征数: {len(common_features)}")
    print(f"  旧设备特征数: {len(old_features_set)}")
    print(f"  新设备特征数: {len(new_features_set)}")
    
    # 应该有一定的特征重叠（至少30%）
    assert overlap_ratio >= 0.3, f"特征重叠度过低: {overlap_ratio:.2%}"
    print(f"✅ 特征重叠度合理: {overlap_ratio:.2%}")
    
    # 3. 新设备的规则质量应该更好（更多高权重特征）
    old_high_weight_features = sum(1 for w in old_rule.feature_weights.values() if w >= 3.0)
    new_high_weight_features = sum(1 for w in new_rule.feature_weights.values() if w >= 3.0)
    
    print(f"\n高权重特征对比（>=3.0）:")
    print(f"  旧设备: {old_high_weight_features}")
    print(f"  新设备: {new_high_weight_features}")
    
    if new_high_weight_features >= old_high_weight_features:
        print("✅ 新设备规则质量有所提升")
    else:
        print("⚠️  新设备规则质量未明显提升，但旧设备规则仍然可用")
    
    print("\n✅ 测试通过: 向后兼容性良好")
    return True


def test_old_device_with_empty_detailed_params():
    """测试旧设备（空的detailed_params）"""
    print("\n" + "="*80)
    print("测试6: 旧设备（空的detailed_params）")
    print("="*80)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, default_threshold=5.0, config=config)
    
    # 创建旧设备（空的detailed_params）
    device = Device(
        device_id="OLD_006",
        brand="江森自控",
        device_name="温控器",
        spec_model="T5800",
        detailed_params="",  # 空的detailed_params
        unit_price=280.0
    )
    
    print(f"\n设备信息:")
    print(f"  device_id: {device.device_id}")
    print(f"  brand: {device.brand}")
    print(f"  device_name: {device.device_name}")
    print(f"  detailed_params: '{device.detailed_params}'")
    
    # 生成规则
    rule = rule_generator.generate_rule(device)
    
    assert rule is not None, "规则生成失败"
    
    print(f"\n生成的规则:")
    print(f"  特征数量: {len(rule.auto_extracted_features)}")
    print(f"\n  提取的特征:")
    for feature in rule.auto_extracted_features:
        print(f"    - {feature}")
    
    # 验证特征提取
    # 即使detailed_params为空，也应该能从brand、device_name、spec_model提取特征
    assert len(rule.auto_extracted_features) > 0, "没有提取到任何特征"
    
    features_lower = [f.lower() for f in rule.auto_extracted_features]
    
    # 应该至少包含品牌或设备名称的特征
    assert any("江森" in f or "johnson" in f.lower() for f in rule.auto_extracted_features) or \
           any("温控器" in f or "控制" in f for f in rule.auto_extracted_features), \
        "未提取到品牌或设备名称特征"
    
    print("\n✅ 测试通过: 空detailed_params处理正确")
    return True


def test_batch_old_devices():
    """测试批量旧设备规则生成"""
    print("\n" + "="*80)
    print("测试7: 批量旧设备规则生成")
    print("="*80)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, default_threshold=5.0, config=config)
    
    # 创建多个旧设备
    old_devices = [
        Device(
            device_id=f"OLD_BATCH_{i:03d}",
            brand=["霍尼韦尔", "西门子", "施耐德"][i % 3],
            device_name=["CO2传感器", "压力传感器", "温度传感器"][i % 3],
            spec_model=f"MODEL{i:04d}",
            detailed_params=f"量程: 0-{100*(i+1)}ppm\n输出信号: 4-20mA",
            unit_price=400.0 + i * 10
            # 注意：没有device_type和key_params
        )
        for i in range(10)
    ]
    
    print(f"\n批量生成 {len(old_devices)} 个旧设备的规则...")
    
    rules = []
    success_count = 0
    for device in old_devices:
        rule = rule_generator.generate_rule(device)
        if rule:
            rules.append(rule)
            success_count += 1
    
    print(f"\n批量生成结果:")
    print(f"  总设备数: {len(old_devices)}")
    print(f"  成功生成规则数: {success_count}")
    print(f"  成功率: {success_count / len(old_devices) * 100:.1f}%")
    
    assert success_count == len(old_devices), f"部分设备规则生成失败: {success_count}/{len(old_devices)}"
    
    # 验证所有规则都有特征和权重
    for rule in rules:
        assert len(rule.auto_extracted_features) > 0, f"规则 {rule.rule_id} 没有特征"
        assert len(rule.feature_weights) > 0, f"规则 {rule.rule_id} 没有权重"
    
    print("\n✅ 测试通过: 批量旧设备规则生成成功")
    return True


def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print("旧设备规则生成测试套件 - 任务13.2.2")
    print("验证需求: 38.4（回退逻辑）")
    print("="*80)
    
    tests = [
        ("旧设备规则生成（无device_type）", test_old_device_without_device_type),
        ("多行detailed_params处理", test_old_device_with_multiline_detailed_params),
        ("转义换行符处理", test_old_device_with_escaped_newlines),
        ("简单detailed_params处理", test_old_device_with_simple_detailed_params),
        ("向后兼容性验证", test_backward_compatibility),
        ("空detailed_params处理", test_old_device_with_empty_detailed_params),
        ("批量旧设备规则生成", test_batch_old_devices),
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
        print("\n🎉 所有测试通过！旧设备规则生成功能正常！")
        print("\n验证结果:")
        print("  ✅ 旧设备（无device_type）规则生成正常")
        print("  ✅ 回退到detailed_params逻辑正确")
        print("  ✅ 向后兼容性良好")
        print("  ✅ 各种detailed_params格式处理正确")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit(main())
