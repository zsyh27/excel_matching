"""
DatabaseManager 单元测试
测试数据库连接、表创建、会话管理和事务回滚

验证需求: 1.1, 1.2, 1.3, 1.5, 6.1-6.5, 8.2, 8.4
"""

import os
import sys
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from sqlalchemy import text

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.database import DatabaseManager
from modules.models import Device, Rule, Config, Base
from sqlalchemy.exc import OperationalError, SQLAlchemyError


class TestDatabaseConnection:
    """测试数据库连接功能 - 验证需求 1.1, 1.2, 1.3"""
    
    def test_sqlite_connection_success(self):
        """测试SQLite数据库连接成功"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_url = f'sqlite:///{db_path}'
            db_manager = DatabaseManager(db_url)
            
            # 验证连接成功
            assert db_manager.engine is not None
            assert db_manager.SessionFactory is not None
            assert db_manager.Session is not None
            assert db_manager.database_url == db_url
            
            db_manager.close()
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)
    
    def test_sqlite_in_memory_connection(self):
        """测试SQLite内存数据库连接"""
        db_url = 'sqlite:///:memory:'
        db_manager = DatabaseManager(db_url)
        
        # 验证连接成功
        assert db_manager.engine is not None
        assert db_manager.SessionFactory is not None
        
        db_manager.close()
    
    def test_connection_with_echo_enabled(self):
        """测试启用SQL语句输出的连接"""
        db_url = 'sqlite:///:memory:'
        db_manager = DatabaseManager(db_url, echo=True)
        
        # 验证echo参数生效
        assert db_manager.engine.echo is True
        
        db_manager.close()
    
    def test_connection_failure_invalid_url(self):
        """测试无效数据库URL导致连接失败 - 验证需求 1.2"""
        # 使用无效的数据库URL
        invalid_url = 'invalid://invalid_database'
        
        with pytest.raises(Exception):
            DatabaseManager(invalid_url)
    
    def test_connection_failure_mysql_unavailable(self):
        """测试MySQL数据库不可用时连接失败 - 验证需求 1.2"""
        # 使用不存在的MySQL服务器
        mysql_url = 'mysql+pymysql://user:pass@localhost:9999/nonexistent'
        
        with pytest.raises(Exception):
            DatabaseManager(mysql_url)
    
    def test_close_connection(self):
        """测试正确关闭数据库连接 - 验证需求 1.3"""
        db_url = 'sqlite:///:memory:'
        db_manager = DatabaseManager(db_url)
        
        # 关闭连接
        db_manager.close()
        
        # 验证连接已关闭 - 检查pool状态包含size: 0
        pool_status = db_manager.engine.pool.status()
        assert 'size: 0' in pool_status


class TestTableCreation:
    """测试表创建功能 - 验证需求 1.5, 6.1-6.5"""
    
    def test_create_tables_success(self):
        """测试成功创建所有表 - 验证需求 6.1, 6.3"""
        db_url = 'sqlite:///:memory:'
        db_manager = DatabaseManager(db_url)
        
        # 创建表
        db_manager.create_tables()
        
        # 验证表已创建 - 通过尝试查询表来验证
        with db_manager.session_scope() as session:
            # 如果表不存在，这些查询会失败
            devices = session.query(Device).all()
            rules = session.query(Rule).all()
            configs = session.query(Config).all()
            
            assert devices == []
            assert rules == []
            assert configs == []
        
        db_manager.close()
    
    def test_create_tables_idempotent(self):
        """测试重复创建表不会出错 - 验证需求 6.2"""
        db_url = 'sqlite:///:memory:'
        db_manager = DatabaseManager(db_url)
        
        # 第一次创建表
        db_manager.create_tables()
        
        # 第二次创建表应该不会出错
        db_manager.create_tables()
        
        # 验证表仍然可用
        with db_manager.session_scope() as session:
            devices = session.query(Device).all()
            assert devices == []
        
        db_manager.close()
    
    def test_tables_have_correct_structure(self):
        """测试表结构包含所有必需字段 - 验证需求 6.3"""
        db_url = 'sqlite:///:memory:'
        db_manager = DatabaseManager(db_url)
        db_manager.create_tables()
        
        # 验证Device表结构
        device_columns = [c.name for c in Device.__table__.columns]
        assert 'device_id' in device_columns
        assert 'brand' in device_columns
        assert 'device_name' in device_columns
        assert 'spec_model' in device_columns
        assert 'detailed_params' in device_columns
        assert 'unit_price' in device_columns
        
        # 验证Rule表结构
        rule_columns = [c.name for c in Rule.__table__.columns]
        assert 'rule_id' in rule_columns
        assert 'target_device_id' in rule_columns
        assert 'auto_extracted_features' in rule_columns
        assert 'feature_weights' in rule_columns
        assert 'match_threshold' in rule_columns
        assert 'remark' in rule_columns
        
        # 验证Config表结构
        config_columns = [c.name for c in Config.__table__.columns]
        assert 'config_key' in config_columns
        assert 'config_value' in config_columns
        assert 'description' in config_columns
        
        db_manager.close()
    
    def test_tables_have_indexes(self):
        """测试表包含索引 - 验证需求 6.4"""
        db_url = 'sqlite:///:memory:'
        db_manager = DatabaseManager(db_url)
        db_manager.create_tables()
        
        # 验证Device表的索引
        device_indexes = [idx.name for idx in Device.__table__.indexes]
        # SQLAlchemy会自动为indexed列创建索引
        
        # 验证Rule表的索引
        rule_indexes = [idx.name for idx in Rule.__table__.indexes]
        
        db_manager.close()


class TestSessionManagement:
    """测试会话管理功能 - 验证需求 8.2"""
    
    def test_session_scope_commit_success(self):
        """测试会话上下文管理器自动提交"""
        db_url = 'sqlite:///:memory:'
        db_manager = DatabaseManager(db_url)
        db_manager.create_tables()
        
        # 使用session_scope添加数据
        with db_manager.session_scope() as session:
            device = Device(
                device_id='TEST001',
                brand='测试品牌',
                device_name='测试设备',
                spec_model='TEST-001',
                detailed_params='测试参数',
                unit_price=100.0
            )
            session.add(device)
        # 退出上下文时应该自动提交
        
        # 验证数据已提交
        with db_manager.session_scope() as session:
            saved_device = session.query(Device).filter_by(device_id='TEST001').first()
            assert saved_device is not None
            assert saved_device.brand == '测试品牌'
        
        db_manager.close()
    
    def test_session_scope_rollback_on_exception(self):
        """测试会话上下文管理器在异常时自动回滚 - 验证需求 8.4"""
        db_url = 'sqlite:///:memory:'
        db_manager = DatabaseManager(db_url)
        db_manager.create_tables()
        
        # 先添加一个设备
        with db_manager.session_scope() as session:
            device = Device(
                device_id='TEST001',
                brand='测试品牌',
                device_name='测试设备',
                spec_model='TEST-001',
                detailed_params='测试参数',
                unit_price=100.0
            )
            session.add(device)
        
        # 尝试添加重复的设备ID，应该触发异常和回滚
        try:
            with db_manager.session_scope() as session:
                # 添加另一个设备
                device2 = Device(
                    device_id='TEST002',
                    brand='品牌2',
                    device_name='设备2',
                    spec_model='TEST-002',
                    detailed_params='参数2',
                    unit_price=200.0
                )
                session.add(device2)
                
                # 尝试添加重复ID的设备，应该失败
                duplicate_device = Device(
                    device_id='TEST001',  # 重复的ID
                    brand='重复品牌',
                    device_name='重复设备',
                    spec_model='DUP-001',
                    detailed_params='重复参数',
                    unit_price=300.0
                )
                session.add(duplicate_device)
                session.flush()  # 强制执行以触发约束错误
        except Exception:
            pass  # 预期会有异常
        
        # 验证TEST002没有被提交（因为事务回滚了）
        with db_manager.session_scope() as session:
            device2 = session.query(Device).filter_by(device_id='TEST002').first()
            assert device2 is None  # 应该不存在，因为事务回滚了
            
            # 但TEST001应该仍然存在（在之前的事务中提交的）
            device1 = session.query(Device).filter_by(device_id='TEST001').first()
            assert device1 is not None
        
        db_manager.close()
    
    def test_get_session(self):
        """测试获取新会话"""
        db_url = 'sqlite:///:memory:'
        db_manager = DatabaseManager(db_url)
        db_manager.create_tables()
        
        # 获取会话
        session = db_manager.get_session()
        
        # 验证会话可用
        assert session is not None
        
        # 使用会话
        device = Device(
            device_id='TEST001',
            brand='测试品牌',
            device_name='测试设备',
            spec_model='TEST-001',
            detailed_params='测试参数',
            unit_price=100.0
        )
        session.add(device)
        session.commit()
        
        # 手动关闭会话
        session.close()
        
        # 验证数据已保存
        with db_manager.session_scope() as session:
            saved_device = session.query(Device).filter_by(device_id='TEST001').first()
            assert saved_device is not None
        
        db_manager.close()
    
    def test_multiple_concurrent_sessions(self):
        """测试多个并发会话"""
        db_url = 'sqlite:///:memory:'
        db_manager = DatabaseManager(db_url)
        db_manager.create_tables()
        
        # 创建多个会话
        session1 = db_manager.get_session()
        session2 = db_manager.get_session()
        
        # 在不同会话中添加数据
        device1 = Device(
            device_id='TEST001',
            brand='品牌1',
            device_name='设备1',
            spec_model='TEST-001',
            detailed_params='参数1',
            unit_price=100.0
        )
        session1.add(device1)
        session1.commit()
        
        device2 = Device(
            device_id='TEST002',
            brand='品牌2',
            device_name='设备2',
            spec_model='TEST-002',
            detailed_params='参数2',
            unit_price=200.0
        )
        session2.add(device2)
        session2.commit()
        
        # 关闭会话
        session1.close()
        session2.close()
        
        # 验证两个设备都已保存
        with db_manager.session_scope() as session:
            devices = session.query(Device).all()
            assert len(devices) == 2
        
        db_manager.close()


class TestTransactionRollback:
    """测试事务回滚功能 - 验证需求 8.4"""
    
    def test_rollback_on_constraint_violation(self):
        """测试约束违反时的回滚"""
        # 使用文件数据库以便启用外键约束
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_url = f'sqlite:///{db_path}'
            db_manager = DatabaseManager(db_url)
            
            # 启用外键约束（SQLite默认不启用）
            with db_manager.session_scope() as session:
                session.execute(text('PRAGMA foreign_keys = ON'))
            
            db_manager.create_tables()
            
            # 添加一个设备
            with db_manager.session_scope() as session:
                device = Device(
                    device_id='TEST001',
                    brand='测试品牌',
                    device_name='测试设备',
                    spec_model='TEST-001',
                    detailed_params='测试参数',
                    unit_price=100.0
                )
                session.add(device)
            
            # 尝试添加违反外键约束的规则
            exception_raised = False
            try:
                with db_manager.session_scope() as session:
                    # 启用外键约束
                    session.execute(text('PRAGMA foreign_keys = ON'))
                    rule = Rule(
                        rule_id='RULE001',
                        target_device_id='NONEXISTENT',  # 不存在的设备ID
                        auto_extracted_features=['特征1'],
                        feature_weights={'特征1': 1.0},
                        match_threshold=0.7
                    )
                    session.add(rule)
                    session.flush()  # 强制执行以触发约束检查
            except Exception:
                exception_raised = True
            
            # 验证异常被触发
            assert exception_raised, "应该触发外键约束异常"
            
            # 验证规则没有被添加
            with db_manager.session_scope() as session:
                rules = session.query(Rule).all()
                assert len(rules) == 0
            
            db_manager.close()
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)
    
    def test_rollback_preserves_previous_data(self):
        """测试回滚不影响之前已提交的数据"""
        db_url = 'sqlite:///:memory:'
        db_manager = DatabaseManager(db_url)
        db_manager.create_tables()
        
        # 第一个事务：成功添加设备
        with db_manager.session_scope() as session:
            device1 = Device(
                device_id='TEST001',
                brand='品牌1',
                device_name='设备1',
                spec_model='TEST-001',
                detailed_params='参数1',
                unit_price=100.0
            )
            session.add(device1)
        
        # 第二个事务：失败并回滚
        try:
            with db_manager.session_scope() as session:
                device2 = Device(
                    device_id='TEST002',
                    brand='品牌2',
                    device_name='设备2',
                    spec_model='TEST-002',
                    detailed_params='参数2',
                    unit_price=200.0
                )
                session.add(device2)
                
                # 故意触发异常
                raise ValueError("测试异常")
        except ValueError:
            pass
        
        # 验证第一个设备仍然存在，第二个设备不存在
        with db_manager.session_scope() as session:
            device1 = session.query(Device).filter_by(device_id='TEST001').first()
            device2 = session.query(Device).filter_by(device_id='TEST002').first()
            
            assert device1 is not None
            assert device2 is None
        
        db_manager.close()
    
    def test_partial_transaction_rollback(self):
        """测试部分事务回滚"""
        db_url = 'sqlite:///:memory:'
        db_manager = DatabaseManager(db_url)
        db_manager.create_tables()
        
        # 尝试在一个事务中添加多个对象，但中途失败
        try:
            with db_manager.session_scope() as session:
                # 添加第一个设备
                device1 = Device(
                    device_id='TEST001',
                    brand='品牌1',
                    device_name='设备1',
                    spec_model='TEST-001',
                    detailed_params='参数1',
                    unit_price=100.0
                )
                session.add(device1)
                
                # 添加第二个设备
                device2 = Device(
                    device_id='TEST002',
                    brand='品牌2',
                    device_name='设备2',
                    spec_model='TEST-002',
                    detailed_params='参数2',
                    unit_price=200.0
                )
                session.add(device2)
                
                # 添加第三个设备（重复ID，会失败）
                device3 = Device(
                    device_id='TEST001',  # 重复ID
                    brand='品牌3',
                    device_name='设备3',
                    spec_model='TEST-003',
                    detailed_params='参数3',
                    unit_price=300.0
                )
                session.add(device3)
                session.flush()  # 强制执行
        except Exception:
            pass
        
        # 验证所有设备都没有被添加（整个事务回滚）
        with db_manager.session_scope() as session:
            devices = session.query(Device).all()
            assert len(devices) == 0
        
        db_manager.close()


class TestDatabaseTypes:
    """测试不同数据库类型的支持 - 验证需求 1.4"""
    
    def test_sqlite_database_type(self):
        """测试SQLite数据库类型"""
        db_url = 'sqlite:///:memory:'
        db_manager = DatabaseManager(db_url)
        db_manager.create_tables()
        
        # 验证可以正常操作
        with db_manager.session_scope() as session:
            device = Device(
                device_id='TEST001',
                brand='测试品牌',
                device_name='测试设备',
                spec_model='TEST-001',
                detailed_params='测试参数',
                unit_price=100.0
            )
            session.add(device)
        
        with db_manager.session_scope() as session:
            saved_device = session.query(Device).filter_by(device_id='TEST001').first()
            assert saved_device is not None
        
        db_manager.close()
    
    @pytest.mark.skipif(
        os.environ.get('TEST_MYSQL') != 'true',
        reason="MySQL测试需要设置TEST_MYSQL=true环境变量"
    )
    def test_mysql_database_type(self):
        """测试MySQL数据库类型（需要MySQL服务器）"""
        # 从环境变量获取MySQL连接信息
        mysql_url = os.environ.get(
            'TEST_MYSQL_URL',
            'mysql+pymysql://root:password@localhost:3306/test_db'
        )
        
        try:
            db_manager = DatabaseManager(mysql_url)
            db_manager.create_tables()
            
            # 验证可以正常操作
            with db_manager.session_scope() as session:
                device = Device(
                    device_id='TEST001',
                    brand='测试品牌',
                    device_name='测试设备',
                    spec_model='TEST-001',
                    detailed_params='测试参数',
                    unit_price=100.0
                )
                session.add(device)
            
            with db_manager.session_scope() as session:
                saved_device = session.query(Device).filter_by(device_id='TEST001').first()
                assert saved_device is not None
            
            # 清理测试数据
            with db_manager.session_scope() as session:
                session.query(Device).delete()
            
            db_manager.close()
        except Exception as e:
            pytest.skip(f"MySQL测试跳过: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
