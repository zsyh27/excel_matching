"""验证规则是否已更新"""
import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modules.models import Rule

# 连接数据库
engine = create_engine('sqlite:///data/devices.db')
Session = sessionmaker(bind=engine)
session = Session()

# 查询测试设备的规则
device_id = '霍尼韦尔_HST-RA_20260306125609359915'
rule = session.query(Rule).filter_by(target_device_id=device_id).first()

if rule:
    print(f"设备ID: {device_id}")
    print(f"规则ID: {rule.rule_id}")
    print(f"\n自动提取特征:")
    for feature in rule.auto_extracted_features:
        print(f"  - {feature}")
    
    print(f"\n特征权重:")
    for feature, weight in rule.feature_weights.items():
        print(f"  {feature}: {weight}")
    
    # 检查规格型号
    spec_model = 'hst-ra'
    if spec_model in rule.auto_extracted_features:
        print(f"\n✅ 规格型号特征 '{spec_model}' 存在")
        print(f"   权重: {rule.feature_weights.get(spec_model, 'N/A')}")
    else:
        print(f"\n❌ 规格型号特征 '{spec_model}' 不存在")
        # 查找可能的匹配
        possible = [f for f in rule.auto_extracted_features if 'hst' in f.lower()]
        if possible:
            print(f"   可能的匹配: {possible}")
else:
    print(f"❌ 未找到设备 {device_id} 的规则")

session.close()
