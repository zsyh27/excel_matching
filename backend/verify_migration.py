"""
验证迁移结果的脚本
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.database import DatabaseManager
from modules.models import Device, Rule, Config

def main():
    # 连接数据库
    data_dir = Path(__file__).parent.parent / 'data'
    db_file = data_dir / 'devices.db'
    database_url = f'sqlite:///{db_file}'
    db_manager = DatabaseManager(database_url)
    
    print("\n验证迁移结果:")
    print("="*60)
    
    with db_manager.session_scope() as session:
        # 检查设备数量
        device_count = session.query(Device).count()
        print(f"\n设备总数: {device_count}")
        
        # 显示前3个设备
        devices = session.query(Device).limit(3).all()
        print("\n前3个设备:")
        for device in devices:
            print(f"  - {device.device_id}: {device.brand} {device.device_name} (¥{device.unit_price})")
        
        # 检查规则数量
        rule_count = session.query(Rule).count()
        print(f"\n规则总数: {rule_count}")
        
        # 显示前3条规则
        rules = session.query(Rule).limit(3).all()
        print("\n前3条规则:")
        for rule in rules:
            print(f"  - {rule.rule_id}: 目标设备={rule.target_device_id}, 特征数={len(rule.auto_extracted_features)}")
        
        # 检查配置数量
        config_count = session.query(Config).count()
        print(f"\n配置总数: {config_count}")
        
        # 显示所有配置键
        configs = session.query(Config).all()
        print("\n配置项:")
        for config in configs:
            print(f"  - {config.config_key}")
        
        # 验证外键关联
        print("\n验证外键关联:")
        orphan_rules = session.query(Rule).filter(
            ~Rule.target_device_id.in_(
                session.query(Device.device_id)
            )
        ).count()
        print(f"  孤立规则数（无关联设备）: {orphan_rules}")
        
    print("\n" + "="*60)
    print("✅ 验证完成！")
    
    db_manager.close()

if __name__ == '__main__':
    main()
