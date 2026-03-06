"""
测试单个设备规则重新生成API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.database_loader import DatabaseLoader
from modules.database import DatabaseManager
from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator
import json

# 初始化
db = DatabaseManager('sqlite:///../data/devices.db')
data_loader = DatabaseLoader(db)
data_loader.load_from_database()

# 加载配置
with open('../data/static_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 创建预处理器和规则生成器
preprocessor = TextPreprocessor(config)
rule_gen = RuleGenerator(config=config, preprocessor=preprocessor)

# 获取所有设备
all_devices = data_loader.get_all_devices()
print(f"总设备数: {len(all_devices)}")

# 找一个没有规则的设备
device_without_rule = None
for device_id, device in all_devices.items():
    # 检查是否有规则
    all_rules = data_loader.get_all_rules()
    has_rule = False
    for rule in all_rules:
        if rule.target_device_id == device_id:
            has_rule = True
            break
    
    if not has_rule:
        device_without_rule = device
        print(f"\n找到没有规则的设备: {device_id}")
        print(f"设备名称: {device.device_name}")
        print(f"设备类型: {device.device_type}")
        print(f"品牌: {device.brand}")
        print(f"型号: {device.spec_model}")
        print(f"关键参数: {device.key_params}")
        break

if not device_without_rule:
    print("\n所有设备都有规则")
    # 使用第一个设备测试
    device_without_rule = list(all_devices.values())[0]
    print(f"\n使用第一个设备测试: {device_without_rule.device_id}")

# 测试规则生成
print("\n" + "=" * 60)
print("测试规则生成:")
print("=" * 60)

try:
    new_rule = rule_gen.generate_rule(device_without_rule)
    
    if new_rule:
        print(f"✓ 规则生成成功")
        print(f"  规则ID: {new_rule.rule_id}")
        print(f"  目标设备ID: {new_rule.target_device_id}")
        print(f"  特征数量: {len(new_rule.features)}")
        print(f"  总权重: {new_rule.total_weight}")
        print(f"  匹配阈值: {new_rule.match_threshold}")
        
        print("\n特征列表:")
        for feature in new_rule.features:
            print(f"  - {feature.feature} (类型: {feature.type}, 权重: {feature.weight})")
        
        # 保存规则
        print("\n保存规则到数据库...")
        data_loader.loader.save_rule(new_rule)
        print("✓ 规则保存成功")
        
        # 验证保存
        print("\n验证保存...")
        all_rules_after = data_loader.get_all_rules()
        found = False
        for rule in all_rules_after:
            if rule.target_device_id == device_without_rule.device_id:
                found = True
                print(f"✓ 在数据库中找到规则: {rule.rule_id}")
                break
        
        if not found:
            print("✗ 在数据库中未找到规则")
    else:
        print("✗ 规则生成失败: generate_rule返回None")
        
except Exception as e:
    print(f"✗ 规则生成失败: {e}")
    import traceback
    traceback.print_exc()
