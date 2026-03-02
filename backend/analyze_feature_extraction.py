"""
分析当前设备数据的特征提取效果
"""
import sqlite3
import json
import sys
sys.path.append('.')

from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator
from modules.data_loader import Device

# 加载配置
with open('../data/static_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 创建预处理器和规则生成器
preprocessor = TextPreprocessor(config)
rule_generator = RuleGenerator(preprocessor, config=config)

# 连接数据库
conn = sqlite3.connect('../data/devices.db')
cursor = conn.cursor()

# 随机抽取10个设备进行分析
cursor.execute("SELECT * FROM devices ORDER BY RANDOM() LIMIT 10")
rows = cursor.fetchall()

print("=" * 100)
print("特征提取分析（随机抽取10个设备）")
print("=" * 100)

for i, row in enumerate(rows, 1):
    device_id, brand, device_name, spec_model, detailed_params, unit_price = row
    
    # 创建Device对象
    device = Device(
        device_id=device_id,
        brand=brand,
        device_name=device_name,
        spec_model=spec_model,
        detailed_params=detailed_params,
        unit_price=unit_price
    )
    
    print(f"\n{'=' * 100}")
    print(f"设备 {i}: {brand} - {device_name}")
    print(f"{'=' * 100}")
    print(f"原始数据：")
    print(f"  品牌: {brand}")
    print(f"  设备名称: {device_name}")
    print(f"  规格型号: {spec_model}")
    print(f"  详细参数: {detailed_params[:100]}...")
    
    # 提取特征
    features = rule_generator.extract_features(device)
    
    print(f"\n提取的特征（共{len(features)}个）：")
    for feature in features[:20]:  # 只显示前20个
        print(f"  - {feature}")
    if len(features) > 20:
        print(f"  ... 还有 {len(features) - 20} 个特征")
    
    # 分配权重
    weights = rule_generator.assign_weights(features)
    
    print(f"\n特征权重分布：")
    # 按权重分组
    weight_groups = {}
    for feature, weight in weights.items():
        if weight not in weight_groups:
            weight_groups[weight] = []
        weight_groups[weight].append(feature)
    
    for weight in sorted(weight_groups.keys(), reverse=True):
        features_list = weight_groups[weight]
        print(f"  权重 {weight}: {len(features_list)} 个特征")
        for feature in features_list[:5]:  # 每组只显示前5个
            print(f"    - {feature}")
        if len(features_list) > 5:
            print(f"    ... 还有 {len(features_list) - 5} 个")
    
    # 分析问题
    print(f"\n问题分析：")
    
    # 检查是否提取到设备类型
    device_type_features = [f for f in features if rule_generator._is_device_type_keyword(f.lower())]
    if device_type_features:
        print(f"  [OK] 设备类型特征: {device_type_features}")
    else:
        print(f"  [NO] 未提取到设备类型特征（设备名称: {device_name}）")
    
    # 检查是否提取到品牌
    brand_features = [f for f in features if rule_generator._is_brand_keyword(f.lower())]
    if brand_features:
        print(f"  [OK] 品牌特征: {brand_features}")
    else:
        print(f"  [NO] 未提取到品牌特征（品牌: {brand}）")
    
    # 检查是否提取到型号
    model_features = [f for f in features if rule_generator._is_model_feature(f.lower())]
    if model_features:
        print(f"  [OK] 型号特征: {model_features}")
    else:
        print(f"  [NO] 未提取到型号特征（规格型号: {spec_model}）")
    
    # 检查是否提取到重要参数
    important_params = [f for f in features if rule_generator._is_important_parameter(f.lower())]
    if important_params:
        print(f"  [OK] 重要参数: {important_params[:5]}")
    else:
        print(f"  [NO] 未提取到重要参数")

conn.close()

print("\n" + "=" * 100)
print("分析完成")
print("=" * 100)
