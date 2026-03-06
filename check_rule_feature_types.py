"""
检查规则特征的类型判断逻辑
"""
import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device as DeviceModel, Rule as RuleModel, Config as ConfigModel
import os
import json

# 获取数据库URL
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f'sqlite:///{os.path.join(BASE_DIR, "data", "devices.db")}'

# 初始化数据库管理器
db_manager = DatabaseManager(DATABASE_URL)
session = db_manager.get_session()

print("=" * 80)
print("检查规则特征类型判断逻辑")
print("=" * 80)

# 加载配置
config_dict = {}
configs = session.query(ConfigModel).all()
for config in configs:
    config_dict[config.config_key] = config.config_value

# 获取device_type_keywords
device_type_keywords_config = config_dict.get('device_type_keywords', {})
if isinstance(device_type_keywords_config, dict) and 'device_type_keywords' in device_type_keywords_config:
    device_type_keywords = device_type_keywords_config['device_type_keywords']
else:
    device_type_keywords = device_type_keywords_config

# 获取brand_keywords
brand_keywords = config_dict.get('brand_keywords', [])

print(f"\n设备类型关键词: {device_type_keywords}")
print(f"\n品牌关键词: {brand_keywords}")

# 测试特征
test_features = ['温度', '温度传感器', '室内温度传感器', '霍尼韦尔']

print("\n" + "=" * 80)
print("测试特征类型判断")
print("=" * 80)

def is_device_type_keyword(feature, keywords):
    """判断是否是设备类型关键词"""
    feature_lower = feature.lower()
    for keyword in keywords:
        if keyword.lower() in feature_lower:
            return True, keyword
    return False, None

def is_brand_keyword(feature, keywords):
    """判断是否是品牌关键词"""
    feature_lower = feature.lower()
    for keyword in keywords:
        if keyword.lower() in feature_lower:
            return True, keyword
    return False, None

for feature in test_features:
    print(f"\n特征: '{feature}'")
    
    # 检查是否是设备类型
    is_device_type, matched_keyword = is_device_type_keyword(feature, device_type_keywords)
    if is_device_type:
        print(f"  ✅ 是设备类型 (匹配关键词: '{matched_keyword}')")
    else:
        print(f"  ❌ 不是设备类型")
    
    # 检查是否是品牌
    is_brand, matched_keyword = is_brand_keyword(feature, brand_keywords)
    if is_brand:
        print(f"  ✅ 是品牌 (匹配关键词: '{matched_keyword}')")
    else:
        print(f"  ❌ 不是品牌")

session.close()
