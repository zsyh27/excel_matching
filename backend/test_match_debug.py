"""
调试匹配功能

测试特征提取和匹配过程
"""

from modules.data_loader import DataLoader
from modules.text_preprocessor import TextPreprocessor
from modules.match_engine import MatchEngine

# 初始化组件
print("=" * 80)
print("调试匹配功能")
print("=" * 80)
print()

# 1. 加载数据
print("1. 加载数据...")
data_loader = DataLoader(
    device_file='data/static_device.json',
    rule_file='data/static_rule.json',
    config_file='data/static_config.json'
)

config = data_loader.load_config()
preprocessor = TextPreprocessor(config)
data_loader.preprocessor = preprocessor

devices = data_loader.load_devices()
rules = data_loader.load_rules()

print(f"   加载了 {len(devices)} 个设备")
print(f"   加载了 {len(rules)} 条规则")
print()

# 2. 初始化匹配引擎
print("2. 初始化匹配引擎...")
match_engine = MatchEngine(rules=rules, devices=devices, config=config)
print("   匹配引擎初始化完成")
print()

# 3. 测试设备描述
test_cases = [
    "1 CO传感器 霍尼韦尔 HSCM-R100U 0-100PPM 4-20mA 台 1",
    "2 温度传感器 西门子 QAA2061 0~50℃ 4-20mA 台 2",
    "3 DDC控制器 江森自控 FX-PCV3624E 24点位 以太网 台 1",
    "CO传感器，霍尼韦尔，HSCM-R100U，0-100PPM，4-20mA",
    "温度传感器，西门子，QAA2061，0~50℃，4-20mA",
]

print("3. 测试匹配...")
print()

for i, description in enumerate(test_cases, 1):
    print(f"测试 {i}: {description}")
    print("-" * 80)
    
    # 提取特征
    features = preprocessor.extract_features(description)
    print(f"提取的特征 ({len(features)} 个):")
    for feature in features[:10]:  # 只显示前10个
        print(f"  - {feature}")
    if len(features) > 10:
        print(f"  ... 还有 {len(features) - 10} 个特征")
    print()
    
    # 执行匹配
    match_result = match_engine.match(features)
    
    print(f"匹配结果:")
    print(f"  状态: {match_result.match_status}")
    if match_result.match_status == 'success':
        print(f"  设备ID: {match_result.device_id}")
        print(f"  设备名称: {match_result.matched_device_text}")
        print(f"  匹配得分: {match_result.match_score}")
        print(f"  单价: {match_result.unit_price}")
    else:
        print(f"  失败原因: {match_result.match_reason}")
    print()
    print()

print("=" * 80)
