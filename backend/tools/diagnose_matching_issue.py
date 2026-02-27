"""
诊断匹配问题的脚本
分析为什么三个不同的设备都匹配到同一个"霍尼韦尔 一氧化碳传感器"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.database_loader import DatabaseLoader
from modules.text_preprocessor import TextPreprocessor
from modules.match_engine import MatchEngine
import json

def diagnose_matching():
    """诊断匹配问题"""
    
    print("=" * 80)
    print("匹配问题诊断工具")
    print("=" * 80)
    
    # 1. 加载数据
    print("\n[步骤 1] 加载数据...")
    from modules.database import DatabaseManager
    db_manager = DatabaseManager('sqlite:///data/devices.db')
    db_loader = DatabaseLoader(db_manager)
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    preprocessor = TextPreprocessor(config)
    
    # 加载设备和规则
    devices = db_loader.get_all_devices()
    rules = db_loader.get_all_rules()
    
    print(f"✓ 加载了 {len(devices)} 个设备")
    print(f"✓ 加载了 {len(rules)} 条规则")
    
    # 2. 查找一氧化碳传感器
    print("\n[步骤 2] 查找一氧化碳传感器...")
    
    # devices 是字典，需要获取值
    device_list = list(devices.values()) if isinstance(devices, dict) else devices
    
    co_devices = [d for d in device_list if '一氧化碳' in d.device_name or 'CO' in d.device_name or 'co' in d.device_name.lower()]
    print(f"✓ 找到 {len(co_devices)} 个一氧化碳相关设备")
    
    if co_devices:
        print("\n一氧化碳传感器列表:")
        for i, device in enumerate(co_devices[:5], 1):
            print(f"  {i}. {device.device_id}")
            print(f"     品牌: {device.brand}")
            print(f"     名称: {device.device_name}")
            print(f"     型号: {device.spec_model}")
            print(f"     参数: {device.detailed_params}")
            print(f"     价格: ¥{device.unit_price}")
            
            # 查找对应的规则
            device_rules = [r for r in rules if r.target_device_id == device.device_id]
            if device_rules:
                rule = device_rules[0]
                print(f"     规则特征: {rule.auto_extracted_features[:5]}...")
                print(f"     匹配阈值: {rule.match_threshold}")
            print()
    
    # 3. 模拟测试设备描述
    print("\n[步骤 3] 测试三个不同的设备描述...")
    
    test_descriptions = [
        "温度传感器，0-50℃，4-20mA",
        "压力传感器，0-1.6MPa，4-20mA",
        "湿度传感器，0-100%RH，4-20mA"
    ]
    
    # 创建匹配引擎
    devices_dict = devices if isinstance(devices, dict) else {d.device_id: d for d in devices}
    match_engine = MatchEngine(rules, devices_dict, config)
    
    for i, desc in enumerate(test_descriptions, 1):
        print(f"\n--- 测试 {i}: {desc} ---")
        
        # 预处理
        result = preprocessor.preprocess(desc)
        print(f"提取的特征: {result.features}")
        
        # 匹配
        match_result = match_engine.match(result.features)
        
        print(f"匹配状态: {match_result.match_status}")
        print(f"匹配得分: {match_result.match_score}")
        print(f"匹配设备: {match_result.matched_device_text}")
        print(f"匹配原因: {match_result.match_reason}")
    
    # 4. 分析问题
    print("\n" + "=" * 80)
    print("[问题分析]")
    print("=" * 80)
    
    # 分析默认阈值
    default_threshold = config.get('global_config', {}).get('default_match_threshold', 2.0)
    print(f"\n1. 默认匹配阈值: {default_threshold}")
    
    # 分析规则阈值分布
    thresholds = [r.match_threshold for r in rules]
    avg_threshold = sum(thresholds) / len(thresholds) if thresholds else 0
    print(f"2. 规则阈值平均值: {avg_threshold:.2f}")
    print(f"3. 规则阈值范围: {min(thresholds):.2f} - {max(thresholds):.2f}")
    
    # 分析权重分布
    print(f"\n4. 权重分配分析:")
    if rules:
        sample_rule = rules[0]
        if sample_rule.feature_weights:
            weights = list(sample_rule.feature_weights.values())
            print(f"   - 权重范围: {min(weights):.1f} - {max(weights):.1f}")
            print(f"   - 平均权重: {sum(weights)/len(weights):.2f}")
    
    # 5. 建议
    print("\n" + "=" * 80)
    print("[优化建议]")
    print("=" * 80)
    print("""
1. 提高匹配阈值
   - 当前默认阈值 2.0 可能过低
   - 建议提高到 5.0 或更高，确保需要更多特征匹配才能成功

2. 优化权重分配
   - 设备类型关键词（如"温度传感器"、"压力传感器"）应该有更高权重
   - 品牌和型号权重应该更高
   - 通用参数（如"4-20mA"）权重应该降低

3. 增加必需特征
   - 某些关键特征（如设备类型）应该是必需的
   - 如果缺少关键特征，即使总分达标也不应匹配

4. 实现匹配规则可视化界面
   - 查看每个设备的匹配规则和权重
   - 实时调整权重和阈值
   - 查看匹配过程的详细日志
    """)

if __name__ == '__main__':
    diagnose_matching()
