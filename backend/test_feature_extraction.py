"""
测试特征提取优化效果
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator
from modules.data_loader import Device
import json

# 加载配置
with open('data/static_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 创建预处理器和规则生成器
preprocessor = TextPreprocessor(config)
rule_generator = RuleGenerator(preprocessor)

# 测试用例1：规格型号拆分
print("=" * 80)
print("测试1：规格型号拆分（使用+作为分隔符）")
print("=" * 80)

spec_model = "二通+DN15+水+V5011N1040/U+V5011系列"
print(f"输入规格型号: {spec_model}")

# 按+拆分
parts = spec_model.split('+')
print(f"\n拆分结果:")
for i, part in enumerate(parts, 1):
    part = part.strip()
    result = preprocessor.preprocess(part)
    print(f"  {i}. 原始: '{part}' -> 归一化: '{result.normalized}'")

# 测试用例2：详细参数解析（括号处理）
print("\n" + "=" * 80)
print("测试2：详细参数解析（括号内容分离）")
print("=" * 80)

detailed_params = """型号：V5011N1040/U
通径：1/2"(DN15)
阀体类型：二通座阀
适用介质：水"""

print(f"输入详细参数:\n{detailed_params}")

# 按行处理
lines = detailed_params.split('\n')
print(f"\n解析结果:")
for line in lines:
    line = line.strip()
    if ':' in line or '：' in line:
        parts = line.split('：') if '：' in line else line.split(':')
        if len(parts) == 2:
            key, value = parts
            print(f"\n  字段: {key.strip()}")
            print(f"  原始值: {value.strip()}")
            
            # 处理值
            result = preprocessor.preprocess(value.strip())
            print(f"  提取特征: {result.features}")

# 测试用例3：完整设备特征提取
print("\n" + "=" * 80)
print("测试3：完整设备特征提取")
print("=" * 80)

device = Device(
    device_id="V5011N1040_U000000000000000001",
    brand="霍尼韦尔",
    device_name="电动调节阀",
    spec_model="二通+DN15+水+V5011N1040/U+V5011系列",
    detailed_params="""型号：V5011N1040/U
通径：1/2"(DN15)
阀体类型：二通座阀
适用介质：水""",
    unit_price=1500.00
)

print(f"设备ID: {device.device_id}")
print(f"品牌: {device.brand}")
print(f"设备名称: {device.device_name}")
print(f"规格型号: {device.spec_model}")
print(f"详细参数:\n{device.detailed_params}")

features = rule_generator.extract_features(device)
print(f"\n提取的特征 (共{len(features)}个):")
for i, feature in enumerate(features, 1):
    print(f"  {i}. {feature}")

# 测试用例4：验证不应该提取的内容
print("\n" + "=" * 80)
print("测试4：验证过滤效果")
print("=" * 80)

test_text = "型号：V5011N1040/U 通径：1/2\"(DN15) u n 1"
print(f"输入文本: {test_text}")

result = preprocessor.preprocess(test_text)
print(f"提取特征: {result.features}")
print(f"\n应该过滤掉的内容:")
print(f"  - '型号'（元数据关键词）")
print(f"  - '通径'（元数据关键词）")
print(f"  - 'u', 'n', '1'（无意义单字符）")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
