"""
临时脚本：为所有设备生成匹配规则
"""
import json
import sys
sys.path.insert(0, 'backend')

from modules.text_preprocessor import TextPreprocessor
from modules.data_loader import DataLoader

# 文件路径
DEVICE_FILE = 'data/static_device.json'
RULE_FILE = 'data/static_rule.json'
CONFIG_FILE = 'data/static_config.json'

# 加载配置
with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 创建预处理器和数据加载器
preprocessor = TextPreprocessor(config)
loader = DataLoader(DEVICE_FILE, RULE_FILE, CONFIG_FILE, preprocessor)

# 加载设备
devices = loader.load_devices()

# 为所有设备生成规则
print(f"正在为 {len(devices)} 个设备生成匹配规则...")

rules = []
for device_id, device in devices.items():
    rule = loader._generate_rule_for_device(device)
    rules.append(rule)
    print(f"  ✓ {device_id}: {device.brand} {device.device_name}")

# 保存规则
loader._rules = rules
loader._save_rules(rules)

print(f"\n成功生成 {len(rules)} 条规则！")
print(f"规则已保存到: {RULE_FILE}")
