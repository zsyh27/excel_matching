"""
测试真实设备数据中"水"特征的提取

用户提供的设备数据：
- 介质: 水
- 执行器品牌: 霍尼韦尔
- 执行器型号: ML7420A8088
- 通径: DN10
- 通数: 二通
- 阀体类型: 座阀
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator

print("=" * 80)
print("测试真实设备数据中'水'特征的提取")
print("=" * 80)

# 加载配置
with open('../data/static_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 创建预处理器和规则生成器
preprocessor = TextPreprocessor(config)
rule_generator = RuleGenerator(config, preprocessor)

# 模拟真实设备数据
device_data = {
    'device_id': 'TEST_DEVICE_001',
    'device_name': '电动调节阀',
    'device_type': '电动调节阀',
    'brand': '霍尼韦尔',
    'spec_model': 'ML7420A8088',
    'key_params': {
        '介质': '水',
        '执行器品牌': '霍尼韦尔',
        '执行器型号': 'ML7420A8088',
        '通径': 'DN10',
        '通数': '二通',
        '阀体类型': '座阀'
    }
}

print("\n【步骤1】设备数据")
print("-" * 80)
print(f"设备名称: {device_data['device_name']}")
print(f"设备类型: {device_data['device_type']}")
print(f"品牌: {device_data['brand']}")
print(f"规格型号: {device_data['spec_model']}")
print(f"关键参数: {device_data['key_params']}")

# 测试key_params的处理
print("\n【步骤2】测试key_params处理")
print("-" * 80)

# 将key_params转换为文本（手动格式化）
key_params_items = []
for key, value in device_data['key_params'].items():
    key_params_items.append(f"{key}: {value}")
key_params_text = "+".join(key_params_items)
print(f"格式化后的key_params文本: {key_params_text}")

# 预处理key_params文本
result = preprocessor.preprocess(key_params_text, mode='device')
print(f"\n预处理结果:")
print(f"  原始文本: {result.original}")
print(f"  清理后: {result.cleaned}")
print(f"  归一化后: {result.normalized}")
print(f"  提取的特征: {result.features}")

if '水' in result.features:
    print(f"\n✓ '水'在预处理阶段被成功提取")
else:
    print(f"\n✗ '水'在预处理阶段被过滤")
    
    # 详细分析
    print(f"\n详细分析:")
    
    # 测试单独的"介质: 水"
    test_text = "介质: 水"
    test_result = preprocessor.preprocess(test_text, mode='device')
    print(f"\n  测试 '{test_text}':")
    print(f"    清理后: {test_result.cleaned}")
    print(f"    归一化后: {test_result.normalized}")
    print(f"    提取的特征: {test_result.features}")
    
    # 测试质量评分
    quality_score = preprocessor._calculate_feature_quality('水')
    print(f"\n  '水'的质量评分: {quality_score}")
    
    min_quality_score = config.get('intelligent_extraction', {}).get('feature_quality_scoring', {}).get('min_quality_score', 50)
    print(f"  最小质量阈值: {min_quality_score}")
    
    if quality_score < min_quality_score:
        print(f"  ✗ 质量评分低于阈值，被过滤")
    else:
        print(f"  ✓ 质量评分达到阈值")

# 测试完整的key_params字符串
print("\n【步骤3】测试完整的key_params字符串")
print("-" * 80)

# 模拟实际存储的格式
full_key_params_text = "介质: 水+执行器品牌: 霍尼韦尔+执行器型号: ML7420A8088+通径: DN10+通数: 二通+阀体类型: 座阀"
print(f"完整的key_params文本: {full_key_params_text}")

full_result = preprocessor.preprocess(full_key_params_text, mode='device')
print(f"\n预处理结果:")
print(f"  清理后: {full_result.cleaned}")
print(f"  归一化后: {full_result.normalized}")
print(f"  提取的特征: {full_result.features}")

if '水' in full_result.features:
    print(f"\n✓ '水'在完整文本中被成功提取")
else:
    print(f"\n✗ '水'在完整文本中被过滤")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
