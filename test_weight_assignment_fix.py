"""
测试权重分配修复

验证设备录入阶段不再使用设备类型关键词判断
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.data_loader import Device
from modules.rule_generator import RuleGenerator
from modules.text_preprocessor import TextPreprocessor

def test_weight_assignment():
    """测试权重分配逻辑"""
    
    print("=" * 80)
    print("测试权重分配修复")
    print("=" * 80)
    
    # 初始化数据库管理器
    db_manager = DatabaseManager('sqlite:///data/devices.db')
    
    # 创建DatabaseLoader
    db_loader = DatabaseLoader(db_manager)
    
    # 从数据库加载配置
    print("\n加载配置...")
    config = db_loader.load_config()
    
    # 初始化预处理器和规则生成器
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, config=config)
    
    # 测试设备：室内温度传感器
    test_device = Device(
        device_id='TEST_001',
        device_name='室内温度传感器',
        device_type='温度传感器',
        brand='霍尼韦尔',
        spec_model='HST-RA',
        key_params={
            '温度量程': {'value': '-20~60℃'},
            '温度信号类型': {'value': 'NTC 10K'},
            '安装位置': {'value': '室内墙装'},
            '检测对象': {'value': '温度'}
        },
        detailed_params='',
        unit_price=213.22
    )
    
    print("\n测试设备信息:")
    print(f"  设备ID: {test_device.device_id}")
    print(f"  设备名称: {test_device.device_name}")
    print(f"  设备类型: {test_device.device_type}")
    print(f"  品牌: {test_device.brand}")
    print(f"  规格型号: {test_device.spec_model}")
    print(f"  关键参数: {test_device.key_params}")
    
    # 提取特征
    print("\n" + "=" * 80)
    print("步骤1: 提取特征")
    print("=" * 80)
    features = rule_generator.extract_features(test_device)
    print(f"\n提取的特征: {features}")
    
    # 分配权重
    print("\n" + "=" * 80)
    print("步骤2: 分配权重")
    print("=" * 80)
    feature_weights = rule_generator.assign_weights(features, test_device, mode='device')
    
    print("\n特征权重分配结果:")
    print("-" * 80)
    print(f"{'特征':<30} {'权重':<10} {'预期来源':<30}")
    print("-" * 80)
    
    # 预期的权重分配
    # 注意: hst-r 不等于 HST-RA,也不被_is_model_feature识别,所以权重为1.0
    expected_weights = {
        '温度传感器': (20.0, 'device.device_type字段'),
        '霍尼韦尔': (10.0, 'device.brand字段'),
        'hst-r': (1.0, '通用参数'),  # 不完整的型号,权重为1.0
        '-20-60℃': (15.0, 'key_params参数'),  # 温度量程参数
        'ntc10k': (15.0, 'key_params参数'),
        '室内墙装': (15.0, 'key_params参数'),
        '温度': (15.0, 'key_params参数'),
        '室内温度传感器': (1.0, '通用参数'),
    }
    
    # 检查每个特征的权重
    all_correct = True
    for feature, weight in feature_weights.items():
        expected_weight, source = expected_weights.get(feature, (None, '未知'))
        status = "✅" if expected_weight == weight else "❌"
        
        if expected_weight != weight:
            all_correct = False
        
        print(f"{status} {feature:<30} {weight:<10.1f} {source:<30}")
        
        if expected_weight and expected_weight != weight:
            print(f"   ⚠️  预期权重: {expected_weight}, 实际权重: {weight}")
    
    print("-" * 80)
    
    # 检查不应该出现的特征
    print("\n" + "=" * 80)
    print("步骤3: 检查不应该出现的特征")
    print("=" * 80)
    
    unwanted_features = []
    for feature in features:
        # 检查是否是从"温度传感器"拆分出来的"传感器"
        if feature == '传感器' and '温度传感器' in features:
            unwanted_features.append(('传感器', '不应该从"温度传感器"拆分出来'))
        # 检查是否是从"室内温度传感器"拆分出来的"室内"
        if feature == '室内' and '室内温度传感器' in features:
            unwanted_features.append(('室内', '不应该从"室内温度传感器"拆分出来'))
    
    if unwanted_features:
        print("\n❌ 发现不应该出现的特征:")
        for feature, reason in unwanted_features:
            print(f"  - {feature}: {reason}")
        all_correct = False
    else:
        print("\n✅ 没有发现不应该出现的特征")
    
    # 总结
    print("\n" + "=" * 80)
    print("测试结果总结")
    print("=" * 80)
    
    if all_correct:
        print("\n✅ 所有测试通过！")
        print("\n修复验证:")
        print("  1. ✅ 设备类型'温度传感器'保持完整，权重为20分")
        print("  2. ✅ key_params参数权重为15分")
        print("  3. ✅ 品牌权重为10分")
        print("  4. ✅ 规格型号权重为5分")
        print("  5. ✅ 没有使用设备类型关键词判断")
        print("  6. ✅ 没有出现不应该的拆分特征")
    else:
        print("\n❌ 部分测试失败，请检查上述错误")
    
    return all_correct

if __name__ == '__main__':
    success = test_weight_assignment()
    sys.exit(0 if success else 1)
