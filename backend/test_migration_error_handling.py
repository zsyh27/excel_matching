"""
测试迁移脚本的错误处理能力
"""

import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.database import DatabaseManager
from modules.models import Device, Rule, Config
from migrate_json_to_db import migrate_devices, migrate_rules, MigrationStats

def test_missing_required_fields():
    """测试缺少必需字段的情况"""
    print("\n测试1: 缺少必需字段")
    print("-" * 60)
    
    # 创建临时数据库
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_file = tmp.name
    
    database_url = f'sqlite:///{db_file}'
    db_manager = DatabaseManager(database_url)
    db_manager.create_tables()
    
    # 测试数据 - 缺少必需字段
    invalid_devices = [
        {
            "device_id": "TEST001",
            "brand": "测试品牌",
            # 缺少 device_name
            "spec_model": "TEST-001",
            "detailed_params": "测试参数",
            "unit_price": 100.0
        },
        {
            "device_id": "TEST002",
            "brand": "测试品牌",
            "device_name": "测试设备",
            "spec_model": "TEST-002",
            "detailed_params": "测试参数",
            "unit_price": 200.0
        }
    ]
    
    stats = MigrationStats()
    migrate_devices(db_manager, invalid_devices, stats)
    
    print(f"总数: {stats.devices_total}")
    print(f"成功: {stats.devices_migrated}")
    print(f"跳过: {stats.devices_skipped}")
    print(f"错误: {len(stats.errors)}")
    
    if stats.errors:
        print("错误信息:")
        for error in stats.errors:
            print(f"  - {error}")
    
    # 验证只有有效设备被插入
    with db_manager.session_scope() as session:
        device_count = session.query(Device).count()
        print(f"\n数据库中的设备数: {device_count}")
        assert device_count == 1, "应该只有1个有效设备被插入"
    
    db_manager.close()
    Path(db_file).unlink()
    print("✅ 测试通过")


def test_foreign_key_violation():
    """测试外键约束违反的情况"""
    print("\n测试2: 外键约束违反")
    print("-" * 60)
    
    # 创建临时数据库
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_file = tmp.name
    
    database_url = f'sqlite:///{db_file}'
    db_manager = DatabaseManager(database_url)
    db_manager.create_tables()
    
    # 先插入一个设备
    valid_device = {
        "device_id": "TEST001",
        "brand": "测试品牌",
        "device_name": "测试设备",
        "spec_model": "TEST-001",
        "detailed_params": "测试参数",
        "unit_price": 100.0
    }
    
    device_stats = MigrationStats()
    migrate_devices(db_manager, [valid_device], device_stats)
    
    # 测试规则 - 引用不存在的设备
    invalid_rules = [
        {
            "rule_id": "R_TEST001",
            "target_device_id": "TEST001",  # 存在
            "auto_extracted_features": ["测试", "特征"],
            "feature_weights": {"测试": 1.0, "特征": 1.0},
            "match_threshold": 2.0,
            "remark": "有效规则"
        },
        {
            "rule_id": "R_TEST002",
            "target_device_id": "NONEXISTENT",  # 不存在
            "auto_extracted_features": ["测试", "特征"],
            "feature_weights": {"测试": 1.0, "特征": 1.0},
            "match_threshold": 2.0,
            "remark": "无效规则"
        }
    ]
    
    rule_stats = MigrationStats()
    migrate_rules(db_manager, invalid_rules, rule_stats)
    
    print(f"总数: {rule_stats.rules_total}")
    print(f"成功: {rule_stats.rules_migrated}")
    print(f"跳过: {rule_stats.rules_skipped}")
    print(f"错误: {len(rule_stats.errors)}")
    
    if rule_stats.errors:
        print("错误信息:")
        for error in rule_stats.errors:
            print(f"  - {error}")
    
    # 验证只有有效规则被插入
    with db_manager.session_scope() as session:
        rule_count = session.query(Rule).count()
        print(f"\n数据库中的规则数: {rule_count}")
        assert rule_count == 1, "应该只有1条有效规则被插入"
    
    db_manager.close()
    Path(db_file).unlink()
    print("✅ 测试通过")


def test_transaction_rollback():
    """测试事务回滚（每个迁移函数使用独立事务）"""
    print("\n测试3: 事务管理")
    print("-" * 60)
    
    # 创建临时数据库
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_file = tmp.name
    
    database_url = f'sqlite:///{db_file}'
    db_manager = DatabaseManager(database_url)
    db_manager.create_tables()
    
    # 混合有效和无效数据
    mixed_devices = [
        {
            "device_id": "TEST001",
            "brand": "测试品牌",
            "device_name": "测试设备1",
            "spec_model": "TEST-001",
            "detailed_params": "测试参数",
            "unit_price": 100.0
        },
        {
            "device_id": "TEST002",
            "brand": "测试品牌",
            # 缺少 device_name
            "spec_model": "TEST-002",
            "detailed_params": "测试参数",
            "unit_price": 200.0
        },
        {
            "device_id": "TEST003",
            "brand": "测试品牌",
            "device_name": "测试设备3",
            "spec_model": "TEST-003",
            "detailed_params": "测试参数",
            "unit_price": 300.0
        }
    ]
    
    stats = MigrationStats()
    migrate_devices(db_manager, mixed_devices, stats)
    
    print(f"总数: {stats.devices_total}")
    print(f"成功: {stats.devices_migrated}")
    print(f"跳过: {stats.devices_skipped}")
    
    # 验证有效数据被保留
    with db_manager.session_scope() as session:
        device_count = session.query(Device).count()
        print(f"\n数据库中的设备数: {device_count}")
        assert device_count == 2, "应该有2个有效设备被插入"
        
        # 验证具体设备
        devices = session.query(Device).all()
        device_ids = [d.device_id for d in devices]
        print(f"设备ID: {device_ids}")
        assert "TEST001" in device_ids
        assert "TEST002" not in device_ids  # 无效数据应该被跳过
        assert "TEST003" in device_ids
    
    db_manager.close()
    Path(db_file).unlink()
    print("✅ 测试通过")


def main():
    print("\n" + "="*60)
    print("迁移脚本错误处理测试")
    print("="*60)
    
    try:
        test_missing_required_fields()
        test_foreign_key_violation()
        test_transaction_rollback()
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！")
        print("="*60 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 测试错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
