"""验证新生成的规则"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.database import DatabaseManager
from modules.models import Rule
from datetime import datetime

db = DatabaseManager('sqlite:///data/devices.db')
session = db.Session()

# 查询示例规则
rule = session.query(Rule).filter(Rule.target_device_id.like('V5011N1040%')).first()

if rule:
    print('规则ID:', rule.rule_id)
    print('目标设备:', rule.target_device_id)
    print('\n提取的特征 (共{}个):'.format(len(rule.auto_extracted_features)))
    for i, f in enumerate(rule.auto_extracted_features, 1):
        print(f'  {i}. {f}')
    
    print('\n特征权重 (共{}个):'.format(len(rule.feature_weights)))
    for f, w in rule.feature_weights.items():
        print(f'  {f}: {w}')
    
    # 检查特征是否正确
    print('\n特征检查:')
    expected_features = ['霍尼韦尔', '座阀', '二通', 'dn15', '水', 'v5011n1040/u', 'v5011系列', '1/2"', '二通座阀']
    print(f'期望特征数: {len(expected_features)}')
    print(f'实际特征数: {len(rule.auto_extracted_features)}')
    
    if len(rule.auto_extracted_features) == len(expected_features):
        print('✓ 特征数量正确')
    else:
        print('✗ 特征数量不正确')
        print('缺少的特征:', set(expected_features) - set(rule.auto_extracted_features))
        print('多余的特征:', set(rule.auto_extracted_features) - set(expected_features))
else:
    print('未找到规则')

session.close()
