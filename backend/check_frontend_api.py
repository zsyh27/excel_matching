"""
检查前端API返回的数据
"""
import sys
sys.path.insert(0, '.')

from modules.data_loader import DataLoader
from config import Config
import json

print("=" * 80)
print("检查前端API返回的数据")
print("=" * 80)

# 初始化
loader = DataLoader(config=Config)

# 获取设备
devices = loader.load_devices()
excel_devices = [d for d in devices.values() if hasattr(d, 'input_method') and d.input_method == 'excel']

if excel_devices:
    device = excel_devices[0]
    device_id = device.device_id
    
    print(f"\n检查设备: {device_id}")
    
    # 模拟API调用
    device_data = loader.loader.get_device_by_id(device_id)
    
    if device_data:
        print(f"\n设备数据:")
        print(f"  device_id: {device_data.device_id}")
        print(f"  brand: {device_data.brand}")
        print(f"  device_type: {device_data.device_type}")
        print(f"  spec_model: {device_data.spec_model}")
        
        # 检查key_params
        if hasattr(device_data, 'key_params') and device_data.key_params:
            print(f"  key_params:")
            print(json.dumps(device_data.key_params, ensure_ascii=False, indent=4))
        
        # 获取规则
        rule_id = f"R_{device_id}"
        rule = loader.loader.get_rule_by_id(rule_id)
        
        if rule:
            print(f"\n规则数据:")
            print(f"  rule_id: {rule.rule_id}")
            print(f"  特征数量: {len(rule.auto_extracted_features)}")
            print(f"  特征: {rule.auto_extracted_features}")
            print(f"  特征权重:")
            print(json.dumps(rule.feature_weights, ensure_ascii=False, indent=4))
            
            # 构建前端需要的格式
            print(f"\n前端显示格式:")
            features_display = []
            for feature in rule.auto_extracted_features:
                weight = rule.feature_weights.get(feature, 0)
                features_display.append({
                    'feature': feature,
                    'weight': weight
                })
            
            # 按权重排序
            features_display.sort(key=lambda x: x['weight'], reverse=True)
            
            print(f"  特征列表（按权重排序）:")
            for item in features_display:
                print(f"    {item['feature']}: {item['weight']}")
        else:
            print(f"\n✗ 没有找到规则")
    else:
        print(f"\n✗ 没有找到设备")
else:
    print("\n没有Excel导入的设备")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)
