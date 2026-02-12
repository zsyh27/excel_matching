"""
测试规则生成功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.database import DatabaseManager
from modules.models import Device as DeviceModel, Rule as RuleModel
from config import Config

def test_rule_generation():
    """测试规则生成结果"""
    
    print("=" * 80)
    print("测试规则生成结果")
    print("=" * 80)
    
    # 初始化数据库
    db_manager = DatabaseManager(Config.DATABASE_URL)
    
    try:
        with db_manager.session_scope() as session:
            # 查询设备和规则统计
            total_devices = session.query(DeviceModel).count()
            total_rules = session.query(RuleModel).count()
            
            print(f"\n总设备数: {total_devices}")
            print(f"总规则数: {total_rules}")
            
            # 查询有规则的设备数
            devices_with_rules = session.query(DeviceModel).filter(
                DeviceModel.rules.any()
            ).count()
            
            print(f"有规则的设备数: {devices_with_rules}")
            print(f"无规则的设备数: {total_devices - devices_with_rules}")
            
            # 查看几个示例规则
            print("\n" + "=" * 80)
            print("示例规则（前5个）:")
            print("=" * 80)
            
            sample_rules = session.query(RuleModel).limit(5).all()
            
            for i, rule in enumerate(sample_rules, 1):
                print(f"\n规则 {i}:")
                print(f"  规则ID: {rule.rule_id}")
                print(f"  目标设备ID: {rule.target_device_id}")
                print(f"  特征数量: {len(rule.auto_extracted_features)}")
                print(f"  特征: {rule.auto_extracted_features[:5]}...")  # 只显示前5个
                print(f"  匹配阈值: {rule.match_threshold}")
                print(f"  备注: {rule.remark}")
                
                # 显示部分权重
                weights_sample = dict(list(rule.feature_weights.items())[:3])
                print(f"  权重示例: {weights_sample}")
            
            # 验证规则与设备的关联
            print("\n" + "=" * 80)
            print("验证规则与设备的关联:")
            print("=" * 80)
            
            # 随机选择一个有规则的设备
            device_with_rule = session.query(DeviceModel).filter(
                DeviceModel.rules.any()
            ).first()
            
            if device_with_rule:
                print(f"\n设备: {device_with_rule.device_id}")
                print(f"  品牌: {device_with_rule.brand}")
                print(f"  名称: {device_with_rule.device_name}")
                print(f"  规则数: {len(device_with_rule.rules)}")
                
                for rule in device_with_rule.rules:
                    print(f"\n  关联规则: {rule.rule_id}")
                    print(f"    特征数: {len(rule.auto_extracted_features)}")
                    print(f"    特征: {rule.auto_extracted_features}")
            
            print("\n" + "=" * 80)
            print("测试完成！")
            print("=" * 80)
            
    finally:
        db_manager.close()


if __name__ == '__main__':
    test_rule_generation()
