"""
数据加载模块演示脚本

演示 DataLoader 和 ConfigManager 的功能
"""

import sys
import os

# Add modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.data_loader import DataLoader, ConfigManager
from modules.text_preprocessor import TextPreprocessor


def main():
    print("=" * 60)
    print("数据加载与校验模块演示")
    print("=" * 60)
    
    # 文件路径
    device_file = "data/static_device.json"
    rule_file = "data/static_rule.json"
    config_file = "data/static_config.json"
    
    # 检查文件是否存在
    if not all(os.path.exists(f) for f in [device_file, rule_file, config_file]):
        # 使用相对于脚本的路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        device_file = os.path.join(base_dir, "data", "static_device.json")
        rule_file = os.path.join(base_dir, "data", "static_rule.json")
        config_file = os.path.join(base_dir, "data", "static_config.json")
    
    print(f"\n1. 初始化配置管理器")
    print(f"   配置文件: {config_file}")
    config_manager = ConfigManager(config_file)
    config = config_manager.get_config()
    print(f"   ✓ 配置加载成功")
    print(f"   - 归一化映射规则: {len(config['normalization_map'])} 条")
    print(f"   - 特征拆分符号: {len(config['feature_split_chars'])} 个")
    print(f"   - 忽略关键词: {len(config['ignore_keywords'])} 个")
    print(f"   - 默认匹配阈值: {config['global_config']['default_match_threshold']}")
    
    print(f"\n2. 初始化文本预处理器")
    preprocessor = TextPreprocessor(config)
    print(f"   ✓ 预处理器初始化成功")
    
    print(f"\n3. 初始化数据加载器")
    print(f"   设备文件: {device_file}")
    print(f"   规则文件: {rule_file}")
    loader = DataLoader(device_file, rule_file, config_file, preprocessor)
    print(f"   ✓ 数据加载器初始化成功")
    
    print(f"\n4. 加载设备表")
    devices = loader.load_devices()
    print(f"   ✓ 加载成功，共 {len(devices)} 个设备")
    for device_id, device in list(devices.items())[:3]:
        print(f"   - {device_id}: {device.brand} {device.device_name} {device.spec_model}")
    
    print(f"\n5. 加载规则表")
    rules = loader.load_rules()
    print(f"   ✓ 加载成功，共 {len(rules)} 条规则")
    for rule in rules[:3]:
        print(f"   - {rule.rule_id}: 目标设备 {rule.target_device_id}, "
              f"特征数 {len(rule.auto_extracted_features)}, 阈值 {rule.match_threshold}")
    
    print(f"\n6. 验证数据完整性")
    try:
        loader.validate_data_integrity()
        print(f"   ✓ 数据完整性验证通过")
        print(f"   - 所有规则的 target_device_id 都存在于设备表")
        print(f"   - 所有规则都有有效的特征和阈值")
    except Exception as e:
        print(f"   ✗ 数据完整性验证失败: {e}")
    
    print(f"\n7. 测试自动特征生成")
    # 获取第一个设备
    first_device = list(devices.values())[0]
    print(f"   测试设备: {first_device.device_id}")
    print(f"   - 品牌: {first_device.brand}")
    print(f"   - 设备名称: {first_device.device_name}")
    print(f"   - 规格型号: {first_device.spec_model}")
    print(f"   - 详细参数: {first_device.detailed_params}")
    
    features = loader.auto_generate_features(first_device)
    print(f"   ✓ 自动生成特征 {len(features)} 个:")
    for i, feature in enumerate(features, 1):
        print(f"      {i}. {feature}")
    
    print(f"\n8. 测试设备查询")
    device = loader.get_device_by_id("SENSOR001")
    if device:
        print(f"   ✓ 查询成功: {device.get_display_text()}")
        print(f"   - 单价: ¥{device.unit_price:.2f}")
    else:
        print(f"   ✗ 设备不存在")
    
    print(f"\n9. 测试配置热加载")
    print(f"   当前默认阈值: {config['global_config']['default_match_threshold']}")
    print(f"   (配置文件修改后会自动重新加载)")
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    
    # 返回加载器供进一步测试
    return loader


if __name__ == '__main__':
    loader = main()
