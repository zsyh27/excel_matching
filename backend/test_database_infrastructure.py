"""
测试数据库基础设施
验证ORM模型和DatabaseManager的基本功能
"""

import os
import tempfile
from modules.database import DatabaseManager
from modules.models import Device, Rule, Config


def test_database_creation():
    """测试数据库创建"""
    # 使用临时文件作为SQLite数据库
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # 创建数据库管理器
        db_url = f'sqlite:///{db_path}'
        db_manager = DatabaseManager(db_url)
        
        # 创建表
        db_manager.create_tables()
        
        # 验证可以创建会话
        with db_manager.session_scope() as session:
            # 测试添加设备
            device = Device(
                device_id='TEST001',
                brand='测试品牌',
                device_name='测试设备',
                spec_model='TEST-MODEL-001',
                detailed_params='测试参数',
                unit_price=1000.0
            )
            session.add(device)
        
        # 验证设备已保存
        with db_manager.session_scope() as session:
            saved_device = session.query(Device).filter_by(device_id='TEST001').first()
            assert saved_device is not None
            assert saved_device.brand == '测试品牌'
            assert saved_device.device_name == '测试设备'
            assert saved_device.unit_price == 1000.0
        
        # 测试添加规则
        with db_manager.session_scope() as session:
            rule = Rule(
                rule_id='RULE001',
                target_device_id='TEST001',
                auto_extracted_features=['特征1', '特征2'],
                feature_weights={'特征1': 0.6, '特征2': 0.4},
                match_threshold=0.7,
                remark='测试规则'
            )
            session.add(rule)
        
        # 验证规则已保存
        with db_manager.session_scope() as session:
            saved_rule = session.query(Rule).filter_by(rule_id='RULE001').first()
            assert saved_rule is not None
            assert saved_rule.target_device_id == 'TEST001'
            assert saved_rule.match_threshold == 0.7
        
        # 测试配置
        with db_manager.session_scope() as session:
            config = Config(
                config_key='test_config',
                config_value={'key': 'value'},
                description='测试配置'
            )
            session.add(config)
        
        # 验证配置已保存
        with db_manager.session_scope() as session:
            saved_config = session.query(Config).filter_by(config_key='test_config').first()
            assert saved_config is not None
            assert saved_config.config_value == {'key': 'value'}
        
        # 测试级联删除
        with db_manager.session_scope() as session:
            device_to_delete = session.query(Device).filter_by(device_id='TEST001').first()
            session.delete(device_to_delete)
        
        # 验证设备和规则都被删除
        with db_manager.session_scope() as session:
            deleted_device = session.query(Device).filter_by(device_id='TEST001').first()
            deleted_rule = session.query(Rule).filter_by(rule_id='RULE001').first()
            assert deleted_device is None
            assert deleted_rule is None
        
        # 关闭数据库连接
        db_manager.close()
        
        print("✓ 数据库基础设施测试通过")
        print("✓ ORM模型创建成功")
        print("✓ DatabaseManager功能正常")
        print("✓ 级联删除功能正常")
        
    finally:
        # 清理临时文件
        if os.path.exists(db_path):
            os.remove(db_path)


if __name__ == '__main__':
    test_database_creation()
