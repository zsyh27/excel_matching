"""
演示设备更新时重新生成规则功能

验证需求: 13.7, 18.7
"""

import os
import sys

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.data_loader import Device
from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator


def main():
    """演示设备更新时重新生成规则功能"""
    
    print("=" * 80)
    print("演示：设备更新时重新生成规则功能")
    print("=" * 80)
    print()
    
    # 1. 创建内存数据库
    print("1. 初始化数据库...")
    db_manager = DatabaseManager('sqlite:///:memory:')
    db_manager.create_tables()
    
    # 2. 创建预处理器和规则生成器
    print("2. 初始化预处理器和规则生成器...")
    config = {
        'normalization_map': {
            '（': '(',
            '）': ')',
            '，': ',',
            '：': ':',
            '；': ';'
        },
        'feature_split_chars': [',', '，', ' ', ';', '；'],
        'ignore_keywords': ['的', '和', '或', '与'],
        'global_config': {
            'default_match_threshold': 2.0
        }
    }
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, default_threshold=2.0)
    
    # 3. 创建数据库加载器
    db_loader = DatabaseLoader(
        db_manager,
        preprocessor=preprocessor,
        rule_generator=rule_generator
    )
    
    # 4. 添加测试设备
    print("3. 添加测试设备...")
    device = Device(
        device_id='DEMO001',
        brand='霍尼韦尔',
        device_name='温度传感器',
        spec_model='T7350A1008',
        detailed_params='测量范围: -40~120℃',
        unit_price=450.0
    )
    db_loader.add_device(device)
    print(f"   设备已添加: {device.device_id}")
    print(f"   品牌: {device.brand}")
    print(f"   名称: {device.device_name}")
    print(f"   型号: {device.spec_model}")
    print(f"   参数: {device.detailed_params}")
    print(f"   价格: {device.unit_price}")
    print()
    
    # 5. 查看自动生成的规则
    print("4. 查看自动生成的规则...")
    rules = db_loader.load_rules()
    if rules:
        rule = rules[0]
        print(f"   规则ID: {rule.rule_id}")
        print(f"   目标设备: {rule.target_device_id}")
        print(f"   特征: {rule.auto_extracted_features}")
        print(f"   权重: {rule.feature_weights}")
        print(f"   阈值: {rule.match_threshold}")
    print()
    
    # 6. 更新设备（不重新生成规则）
    print("5. 更新设备（不重新生成规则）...")
    device.detailed_params = '测量范围: -40~120℃, 精度: ±0.5℃'
    device.unit_price = 480.0
    db_loader.update_device(device, regenerate_rule=False)
    print(f"   设备已更新")
    print(f"   新参数: {device.detailed_params}")
    print(f"   新价格: {device.unit_price}")
    print()
    
    # 7. 查看规则（应该未改变）
    print("6. 查看规则（应该未改变）...")
    rules = db_loader.load_rules()
    if rules:
        rule = rules[0]
        print(f"   规则ID: {rule.rule_id}")
        print(f"   特征: {rule.auto_extracted_features}")
        print(f"   （规则未改变）")
    print()
    
    # 8. 再次更新设备（重新生成规则）
    print("7. 再次更新设备（重新生成规则）...")
    device.detailed_params = '测量范围: -40~120℃, 精度: ±0.5℃, 输出: 4-20mA, 防护等级: IP65'
    device.spec_model = 'T7350A1008-U'
    db_loader.update_device(device, regenerate_rule=True)
    print(f"   设备已更新")
    print(f"   新型号: {device.spec_model}")
    print(f"   新参数: {device.detailed_params}")
    print()
    
    # 9. 查看更新后的规则
    print("8. 查看更新后的规则...")
    rules = db_loader.load_rules()
    if rules:
        rule = rules[0]
        print(f"   规则ID: {rule.rule_id}")
        print(f"   特征: {rule.auto_extracted_features}")
        print(f"   权重: {rule.feature_weights}")
        print(f"   （规则已重新生成，特征可能已更新）")
    print()
    
    # 10. 清理
    print("9. 清理资源...")
    db_manager.close()
    print("   数据库连接已关闭")
    print()
    
    print("=" * 80)
    print("演示完成！")
    print("=" * 80)
    print()
    print("总结：")
    print("- update_device() 方法支持 regenerate_rule 参数")
    print("- regenerate_rule=False（默认）：只更新设备信息，不改变规则")
    print("- regenerate_rule=True：更新设备信息并重新生成匹配规则")
    print("- 如果规则不存在，regenerate_rule=True 会创建新规则")
    print("- 规则生成失败不会回滚设备更新")
    print()


if __name__ == '__main__':
    main()
