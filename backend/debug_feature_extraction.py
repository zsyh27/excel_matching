"""调试特征提取"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.database import DatabaseManager
from modules.models import Device
from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator
import json

# 加载配置
with open('data/static_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

preprocessor = TextPreprocessor(config)
rule_generator = RuleGenerator(preprocessor)

# 从数据库加载设备
db = DatabaseManager('sqlite:///data/devices.db')
session = db.Session()
device = session.query(Device).filter(Device.device_id.like('V5011N1040%')).first()

if device:
    print('=' * 80)
    print('设备信息')
    print('=' * 80)
    print(f'设备ID: {device.device_id}')
    print(f'品牌: {device.brand}')
    print(f'设备名称: {device.device_name}')
    print(f'规格型号: {device.spec_model}')
    print(f'详细参数: {repr(device.detailed_params)}')
    
    print('\n' + '=' * 80)
    print('特征提取过程')
    print('=' * 80)
    
    # 提取特征
    features = rule_generator.extract_features(device)
    
    print(f'\n提取的特征 (共{len(features)}个):')
    for i, feature in enumerate(features, 1):
        print(f'  {i}. {feature}')

session.close()
