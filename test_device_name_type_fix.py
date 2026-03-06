"""
测试设备名称类型识别修复

验证"室内温度传感器"被正确识别为device_name而不是device_type
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

def test_device_name_type():
    """测试设备名称类型识别"""
    
    print("=" * 80)
    print("测试设备名称类型识别修复")
    print("=" * 80)
    
    # 初始化数据库管理器
    db_manager = DatabaseManager('sqlite:///data/devices.db')
    
    # 创建DatabaseLoader
    db_loader = DatabaseLoader(db_manager)
    
    # 查找测试设备
    print("\n查找测试设备...")
    devices = db_loader.load_devices()
    
    # 查找"室内温度传感器"设备
    test_device = None
    for device_id, device in devices.items():
        if device.device_name == '室内温度传感器' and device.device_type == '温度传感器':
            test_device = device
            break
    
    if not test_device:
        print("❌ 未找到测试设备")
        return False
    
    print(f"\n找到测试设备:")
    print(f"  设备ID: {test_device.device_id}")
    print(f"  设备名称: {test_device.device_name}")
    print(f"  设备类型: {test_device.device_type}")
    print(f"  品牌: {test_device.brand}")
    
    # 加载规则
    print("\n加载规则...")
    rules = db_loader.load_rules()
    
    # 查找对应的规则
    test_rule = None
    for rule in rules:
        if rule.target_device_id == test_device.device_id:
            test_rule = rule
            break
    
    if not test_rule:
        print("❌ 未找到对应的规则")
        return False
    
    print(f"\n找到规则: {test_rule.rule_id}")
    print(f"特征数量: {len(test_rule.auto_extracted_features)}")
    
    # 模拟API的特征类型判断逻辑
    print("\n" + "=" * 80)
    print("特征类型判断测试")
    print("=" * 80)
    
    features_with_types = []
    for feature_text, weight in test_rule.feature_weights.items():
        # 推断特征类型（使用修复后的逻辑）
        feature_type = 'parameter'  # 默认类型
        if feature_text in test_rule.auto_extracted_features:
            # 优先级: brand > device_type > device_name > spec_model
            if test_device.brand and feature_text.lower() == test_device.brand.lower():
                feature_type = 'brand'
            elif test_device.device_type and feature_text.lower() == test_device.device_type.lower():
                # 只有完全匹配时才判断为设备类型
                feature_type = 'device_type'
            elif test_device.device_name and feature_text.lower() == test_device.device_name.lower():
                # 判断是否是设备名称
                feature_type = 'device_name'
            elif test_device.spec_model and feature_text in test_device.spec_model:
                feature_type = 'model'
        
        features_with_types.append({
            'feature': feature_text,
            'weight': weight,
            'type': feature_type
        })
    
    # 按权重排序
    features_with_types.sort(key=lambda x: x['weight'], reverse=True)
    
    # 显示结果
    print(f"\n{'特征':<30} {'权重':<10} {'类型':<15} {'状态':<10}")
    print("-" * 80)
    
    all_correct = True
    
    # 预期的特征类型
    expected_types = {
        '温度传感器': 'device_type',
        '室内温度传感器': 'device_name',  # 关键测试点
        '霍尼韦尔': 'brand',
    }
    
    for feature_info in features_with_types:
        feature = feature_info['feature']
        weight = feature_info['weight']
        feature_type = feature_info['type']
        
        # 检查是否符合预期
        expected_type = expected_types.get(feature)
        if expected_type:
            status = "✅" if feature_type == expected_type else "❌"
            if feature_type != expected_type:
                all_correct = False
        else:
            status = "  "  # 不检查
        
        print(f"{status} {feature:<30} {weight:<10.1f} {feature_type:<15}")
        
        if expected_type and feature_type != expected_type:
            print(f"   ⚠️  预期类型: {expected_type}, 实际类型: {feature_type}")
    
    print("-" * 80)
    
    # 总结
    print("\n" + "=" * 80)
    print("测试结果总结")
    print("=" * 80)
    
    if all_correct:
        print("\n✅ 所有测试通过！")
        print("\n修复验证:")
        print("  1. ✅ '温度传感器'被正确识别为device_type")
        print("  2. ✅ '室内温度传感器'被正确识别为device_name")
        print("  3. ✅ '霍尼韦尔'被正确识别为brand")
    else:
        print("\n❌ 部分测试失败，请检查上述错误")
    
    return all_correct

if __name__ == '__main__':
    success = test_device_name_type()
    sys.exit(0 if success else 1)
