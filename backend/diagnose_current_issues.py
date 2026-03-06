"""
诊断当前问题
"""
import sys
sys.path.insert(0, '.')

from modules.data_loader import DataLoader
from modules.rule_generator import RuleGenerator
from modules.text_preprocessor import TextPreprocessor
from config import Config
import json

print("=" * 80)
print("诊断当前问题")
print("=" * 80)

# 初始化
loader = DataLoader(config=Config)
config = loader.load_config()
preprocessor = TextPreprocessor(config=config)
rule_gen = RuleGenerator(config=config, preprocessor=preprocessor)

# 1. 检查最近导入的设备
print("\n" + "=" * 80)
print("1. 检查最近导入的设备")
print("=" * 80)

devices = loader.load_devices()
print(f"设备总数: {len(devices)}")

# 找到最近导入的设备（Excel导入）
excel_devices = [d for d in devices.values() if hasattr(d, 'input_method') and d.input_method == 'excel']
print(f"Excel导入的设备数: {len(excel_devices)}")

if excel_devices:
    # 取第一个设备详细检查
    device = excel_devices[0]
    print(f"\n检查设备: {device.device_id}")
    print(f"  品牌: {device.brand}")
    print(f"  设备类型: {device.device_type}")
    print(f"  设备名称: {device.device_name}")
    print(f"  规格型号: {device.spec_model}")
    print(f"  关键参数: {json.dumps(device.key_params, ensure_ascii=False) if hasattr(device, 'key_params') and device.key_params else '无'}")
    
    # 2. 检查该设备的规则
    print("\n" + "=" * 80)
    print("2. 检查该设备的规则")
    print("=" * 80)
    
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
        print(f"✓ 找到规则: {device_rule.rule_id}")
        print(f"  特征数量: {len(device_rule.auto_extracted_features)}")
        print(f"  特征: {device_rule.auto_extracted_features}")
        print(f"  特征权重:")
        print(json.dumps(device_rule.feature_weights, ensure_ascii=False, indent=2))
        
        # 检查问题
        print(f"\n问题检查:")
        
        # 问题1: 设备类型权重
        device_type_lower = device.device_type.lower() if device.device_type else ''
        if device_type_lower in device_rule.feature_weights:
            weight = device_rule.feature_weights[device_type_lower]
            if weight == 20.0:
                print(f"  ✓ 设备类型 '{device_type_lower}' 权重正确: {weight}")
            else:
                print(f"  ✗ 设备类型 '{device_type_lower}' 权重错误: {weight} (应该是20.0)")
        else:
            print(f"  ✗ 设备类型 '{device_type_lower}' 未找到")
        
        # 问题2: 规格型号权重
        spec_model_lower = device.spec_model.lower() if device.spec_model else ''
        if spec_model_lower in device_rule.feature_weights:
            weight = device_rule.feature_weights[spec_model_lower]
            if weight == 15.0:
                print(f"  ✓ 规格型号 '{spec_model_lower}' 权重正确: {weight}")
            else:
                print(f"  ✗ 规格型号 '{spec_model_lower}' 权重错误: {weight} (应该是15.0)")
        else:
            print(f"  ✗ 规格型号 '{spec_model_lower}' 未找到")
        
        # 问题3: 关键参数"水"
        if hasattr(device, 'key_params') and device.key_params:
            if '介质' in device.key_params:
                medium_value = device.key_params['介质']
                if isinstance(medium_value, dict):
                    medium_value = medium_value.get('value', '')
                
                print(f"  关键参数'介质'的值: '{medium_value}'")
                
                # 检查是否在特征中
                if medium_value.lower() in device_rule.auto_extracted_features:
                    weight = device_rule.feature_weights.get(medium_value.lower(), 0)
                    print(f"  ✓ 找到特征 '{medium_value}' 权重: {weight}")
                else:
                    print(f"  ✗ 特征 '{medium_value}' 未找到（可能被过滤）")
    else:
        print(f"✗ 没有找到规则")
    
    # 3. 测试重新生成规则
    print("\n" + "=" * 80)
    print("3. 测试重新生成规则")
    print("=" * 80)
    
    print(f"使用当前代码重新生成规则...")
    new_rule = rule_gen.generate_rule(device)
    
    if new_rule:
        print(f"✓ 规则生成成功")
        print(f"  规则ID: {new_rule.rule_id}")
        print(f"  特征数量: {len(new_rule.auto_extracted_features)}")
        print(f"  特征: {new_rule.auto_extracted_features}")
        print(f"  特征权重:")
        print(json.dumps(new_rule.feature_weights, ensure_ascii=False, indent=2))
        
        # 对比新旧规则
        if device_rule:
            print(f"\n对比新旧规则:")
            print(f"  旧规则特征数: {len(device_rule.auto_extracted_features)}")
            print(f"  新规则特征数: {len(new_rule.auto_extracted_features)}")
            
            # 检查差异
            old_features = set(device_rule.auto_extracted_features)
            new_features = set(new_rule.auto_extracted_features)
            
            added = new_features - old_features
            removed = old_features - new_features
            
            if added:
                print(f"  新增特征: {added}")
            if removed:
                print(f"  删除特征: {removed}")
            
            # 检查权重差异
            print(f"\n  权重差异:")
            for feature in new_features & old_features:
                old_weight = device_rule.feature_weights.get(feature, 0)
                new_weight = new_rule.feature_weights.get(feature, 0)
                if old_weight != new_weight:
                    print(f"    '{feature}': {old_weight} → {new_weight}")
    else:
        print(f"✗ 规则生成失败")
    
    # 4. 检查预处理器配置
    print("\n" + "=" * 80)
    print("4. 检查预处理器配置")
    print("=" * 80)
    
    print(f"最小特征长度: {preprocessor.min_feature_length}")
    print(f"最大特征长度: {preprocessor.max_feature_length}")
    
    # 测试"水"是否会被过滤
    test_text = "水"
    result = preprocessor.preprocess(test_text, mode='device')
    print(f"\n测试预处理 '{test_text}':")
    print(f"  特征: {result.features}")
    if not result.features:
        print(f"  ✗ 特征被过滤（长度太短）")
    else:
        print(f"  ✓ 特征保留")

else:
    print("\n没有找到Excel导入的设备")

print("\n" + "=" * 80)
print("诊断完成")
print("=" * 80)
