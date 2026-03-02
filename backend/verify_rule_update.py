"""
验证规则更新是否成功
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from modules.database import DatabaseManager
from modules.models import Rule, Device

def verify_rule_update():
    """验证规则更新"""
    
    print("=" * 80)
    print("验证规则更新")
    print("=" * 80)
    
    # 连接数据库
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')
    db_manager = DatabaseManager(f'sqlite:///{db_path}')
    
    with db_manager.session_scope() as session:
        # 随机选择几个设备检查规则
        devices = session.query(Device).limit(5).all()
        
        print(f"\n检查前5个设备的规则:")
        print("-" * 80)
        
        for device in devices:
            # 查找对应的规则
            rule = session.query(Rule).filter_by(
                target_device_id=device.device_id
            ).first()
            
            if rule:
                print(f"\n设备: {device.brand} {device.device_name}")
                print(f"  设备ID: {device.device_id}")
                print(f"  规则ID: {rule.rule_id}")
                print(f"  特征数量: {len(rule.auto_extracted_features)}")
                print(f"  特征: {', '.join(rule.auto_extracted_features[:5])}")
                if len(rule.auto_extracted_features) > 5:
                    print(f"        ... 等{len(rule.auto_extracted_features)}个特征")
                print(f"  匹配阈值: {rule.match_threshold}")
            else:
                print(f"\n⚠️  设备 {device.device_id} 没有对应的规则")
        
        # 统计信息
        total_devices = session.query(Device).count()
        total_rules = session.query(Rule).count()
        
        print(f"\n" + "=" * 80)
        print(f"统计信息")
        print(f"=" * 80)
        print(f"  总设备数: {total_devices}")
        print(f"  总规则数: {total_rules}")
        print(f"  覆盖率: {total_rules*100//total_devices}%")
        
        if total_devices == total_rules:
            print(f"\n✓ 所有设备都有对应的规则")
        else:
            print(f"\n⚠️  有 {total_devices - total_rules} 个设备缺少规则")

if __name__ == '__main__':
    verify_rule_update()
