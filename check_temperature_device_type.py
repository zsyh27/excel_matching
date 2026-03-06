"""
检查"温度"为什么被识别为设备类型
"""
import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device as DeviceModel, Rule as RuleModel
import os
import json

# 获取数据库URL
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f'sqlite:///{os.path.join(BASE_DIR, "data", "devices.db")}'

# 初始化数据库管理器
db_manager = DatabaseManager(DATABASE_URL)
session = db_manager.get_session()

print("=" * 80)
print("检查设备: 霍尼韦尔_HST-RA_20260306120504787221")
print("=" * 80)

# 查询设备
device_id = "霍尼韦尔_HST-RA_20260306120504787221"
device = session.query(DeviceModel).filter_by(device_id=device_id).first()

if device:
    print(f"\n设备信息:")
    print(f"  设备ID: {device.device_id}")
    print(f"  品牌: {device.brand}")
    print(f"  设备名称: {device.device_name}")
    print(f"  设备类型: {device.device_type}")
    print(f"  规格型号: {device.spec_model}")
    print(f"  详细参数: {device.detailed_params}")
    
    # 查询规则
    rule = session.query(RuleModel).filter_by(target_device_id=device_id).first()
    
    if rule:
        print(f"\n规则信息:")
        print(f"  规则ID: {rule.rule_id}")
        print(f"  特征列表: {rule.auto_extracted_features}")
        print(f"\n特征权重:")
        for feature, weight in rule.feature_weights.items():
            print(f"    {feature}: {weight}")
    else:
        print("\n⚠️ 没有找到规则")
else:
    print(f"\n⚠️ 没有找到设备: {device_id}")

# 检查device_type_keywords配置
print("\n" + "=" * 80)
print("检查device_type_keywords配置")
print("=" * 80)

from modules.models import Config as ConfigModel

config_model = session.query(ConfigModel).filter_by(config_key='device_type_keywords').first()
if config_model:
    device_type_keywords = config_model.config_value
    if isinstance(device_type_keywords, dict) and 'device_type_keywords' in device_type_keywords:
        keywords = device_type_keywords['device_type_keywords']
    else:
        keywords = device_type_keywords
    
    print(f"\n设备类型关键词列表 (共{len(keywords)}个):")
    
    # 检查是否包含"温度"
    if '温度' in keywords:
        print(f"  ❌ 发现问题: '温度' 在设备类型关键词中")
        print(f"  位置: 第{keywords.index('温度') + 1}个")
    else:
        print(f"  ✅ '温度' 不在设备类型关键词中")
    
    # 检查是否包含"温度传感器"
    if '温度传感器' in keywords:
        print(f"  ✅ '温度传感器' 在设备类型关键词中")
        print(f"  位置: 第{keywords.index('温度传感器') + 1}个")
    else:
        print(f"  ❌ '温度传感器' 不在设备类型关键词中")
    
    # 显示所有包含"温度"的关键词
    temp_keywords = [k for k in keywords if '温度' in k]
    if temp_keywords:
        print(f"\n  包含'温度'的关键词:")
        for k in temp_keywords:
            print(f"    - {k}")

session.close()
