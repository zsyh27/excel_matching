"""
测试规则生成和匹配的特征提取一致性
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator
from modules.data_loader import Device
import json


def test_feature_extraction_consistency():
    """测试特征提取一致性"""
    
    print("=" * 80)
    print("特征提取一致性测试")
    print("=" * 80)
    
    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'static_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 创建预处理器和规则生成器
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, config=config)
    
    # 测试用例：模拟一个设备
    test_device = Device(
        device_id="TEST001",
        brand="霍尼韦尔",
        device_name="座阀",
        spec_model="二通+DN15+水+V5011N1040/U+V5011系列",
        detailed_params="型号：V5011N1040/U\n通径：1/2\"(DN15)\n阀体类型：二通座阀\n适用介质：水",
        unit_price=2603.0
    )
    
    print("\n测试设备信息:")
    print(f"  品牌: {test_device.brand}")
    print(f"  设备名称: {test_device.device_name}")
    print(f"  规格型号: {test_device.spec_model}")
    print(f"  详细参数: {test_device.detailed_params[:50]}...")
    
    # 1. 使用规则生成器提取特征（设备库模式）
    print("\n" + "=" * 80)
    print("1. 规则生成器提取特征（设备库模式）")
    print("=" * 80)
    
    device_features = rule_generator.extract_features(test_device)
    print(f"\n提取的特征（共{len(device_features)}个）:")
    for i, feature in enumerate(device_features, 1):
        print(f"  {i}. {feature}")
    
    # 2. 模拟Excel输入（匹配模式）
    print("\n" + "=" * 80)
    print("2. 匹配引擎预处理Excel输入（匹配模式）")
    print("=" * 80)
    
    # 构造类似的Excel输入文本
    excel_text = "霍尼韦尔+座阀+二通+DN15+水+V5011N1040/U+V5011系列+V5011N1040/U+1/2\"(DN15)+二通座阀+水"
    print(f"\nExcel输入文本: {excel_text}")
    
    excel_result = preprocessor.preprocess(excel_text, mode='matching')
    print(f"\n提取的特征（共{len(excel_result.features)}个）:")
    for i, feature in enumerate(excel_result.features, 1):
        print(f"  {i}. {feature}")
    
    # 3. 对比分析
    print("\n" + "=" * 80)
    print("3. 一致性分析")
    print("=" * 80)
    
    device_set = set(device_features)
    excel_set = set(excel_result.features)
    
    common_features = device_set & excel_set
    device_only = device_set - excel_set
    excel_only = excel_set - device_set
    
    print(f"\n共同特征（{len(common_features)}个）:")
    for feature in sorted(common_features):
        print(f"  ✓ {feature}")
    
    if device_only:
        print(f"\n仅在设备库中（{len(device_only)}个）:")
        for feature in sorted(device_only):
            print(f"  - {feature}")
    
    if excel_only:
        print(f"\n仅在Excel中（{len(excel_only)}个）:")
        for feature in sorted(excel_only):
            print(f"  + {feature}")
    
    # 4. 计算相似度
    if device_set or excel_set:
        similarity = len(common_features) / len(device_set | excel_set) * 100
        print(f"\n特征集相似度: {similarity:.1f}%")
        
        if similarity >= 80:
            print("  ✓ 特征提取一致性良好")
        elif similarity >= 60:
            print("  ⚠ 特征提取存在一定差异")
        else:
            print("  ✗ 特征提取差异较大，需要进一步优化")
    
    # 5. 测试mode参数的影响
    print("\n" + "=" * 80)
    print("4. mode参数影响测试")
    print("=" * 80)
    
    test_text = "温度：25℃+精度±5%"
    
    device_mode_result = preprocessor.preprocess(test_text, mode='device')
    matching_mode_result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"\n测试文本: {test_text}")
    print(f"\ndevice模式特征: {device_mode_result.features}")
    print(f"matching模式特征: {matching_mode_result.features}")
    
    if device_mode_result.features != matching_mode_result.features:
        print("\n  ℹ mode参数会影响特征提取（如温度单位处理）")
    else:
        print("\n  ℹ mode参数对此文本无影响")


if __name__ == '__main__':
    test_feature_extraction_consistency()
