"""
重新生成所有设备的规则
修复：
1. spec_model权重错误（应该是5，不是15）
2. "水"特征未被识别
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
from modules.data_loader import DataLoader
from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator

print("=" * 80)
print("重新生成所有设备规则")
print("=" * 80)

# 加载配置
with open('../data/static_config.json', 'r', encoding='utf-8') as f:
    config_dict = json.load(f)

# 导入配置类
from config import Config
config = Config()

# 创建数据加载器
data_loader = DataLoader(config=config)

# 创建预处理器和规则生成器
preprocessor = TextPreprocessor(config_dict)
rule_generator = RuleGenerator(preprocessor, config=config_dict)

# 获取所有设备
devices_dict = data_loader.load_devices()
devices = list(devices_dict.values())
print(f"\n找到 {len(devices)} 个设备")

# 统计信息
success_count = 0
error_count = 0
updated_devices = []

print("\n开始重新生成规则...")
print("-" * 80)

for i, device in enumerate(devices, 1):
    try:
        # 生成新规则
        new_rule = rule_generator.generate_rule(device)
        
        if new_rule:
            # 保存规则（会覆盖旧规则）
            data_loader.loader.save_rule(new_rule)
            success_count += 1
            
            # 检查是否包含"水"特征
            has_water = '水' in new_rule.auto_extracted_features
            
            # 检查spec_model权重
            spec_model_lower = device.spec_model.lower() if device.spec_model else None
            spec_model_weight = new_rule.feature_weights.get(spec_model_lower) if spec_model_lower else None
            
            print(f"[{i}/{len(devices)}] ✓ {device.device_id}")
            print(f"  特征数: {len(new_rule.auto_extracted_features)}")
            print(f"  包含'水': {'是' if has_water else '否'}")
            if spec_model_lower and spec_model_weight:
                print(f"  spec_model权重: {spec_model_weight}")
            
            updated_devices.append({
                'device_id': device.device_id,
                'device_name': device.device_name,
                'features_count': len(new_rule.auto_extracted_features),
                'has_water': has_water,
                'spec_model_weight': spec_model_weight
            })
        else:
            error_count += 1
            print(f"[{i}/{len(devices)}] ✗ {device.device_id} - 规则生成失败")
    
    except Exception as e:
        error_count += 1
        print(f"[{i}/{len(devices)}] ✗ {device.device_id} - 错误: {e}")

print("\n" + "=" * 80)
print("规则重新生成完成")
print("=" * 80)
print(f"成功: {success_count}")
print(f"失败: {error_count}")
print(f"总计: {len(devices)}")

# 保存报告
report = {
    'total': len(devices),
    'success': success_count,
    'error': error_count,
    'updated_devices': updated_devices
}

report_file = 'regenerate_rules_report.json'
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n详细报告已保存到: {report_file}")

# 显示一些统计信息
water_count = sum(1 for d in updated_devices if d['has_water'])
print(f"\n包含'水'特征的设备数: {water_count}/{len(updated_devices)}")

spec_model_devices = [d for d in updated_devices if d['spec_model_weight'] is not None]
if spec_model_devices:
    print(f"\n有spec_model的设备数: {len(spec_model_devices)}")
    correct_weight_count = sum(1 for d in spec_model_devices if d['spec_model_weight'] == 5.0)
    print(f"spec_model权重正确(5.0)的设备数: {correct_weight_count}/{len(spec_model_devices)}")
