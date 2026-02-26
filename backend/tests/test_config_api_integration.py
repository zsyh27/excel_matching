"""
配置管理 API 集成测试

验证需求: 23.1-23.7

这个测试文件使用真实的数据库连接进行集成测试
"""

import os
import sys
import pytest
import tempfile

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Config as ConfigModel


class TestConfigCRUD:
    """配置 CRUD 操作集成测试"""
    
    @pytest.fixture
    def db_manager(self):
        """创建临时数据库"""
        # 使用临时文件作为数据库
        db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db_file.close()
        db_path = db_file.name
        
        db_manager = DatabaseManager(f'sqlite:///{db_path}')
        db_manager.create_tables()
        
        yield db_manager
        
        # 清理
        db_manager.close()
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def db_loader(self, db_manager):
        """创建数据库加载器"""
        return DatabaseLoader(db_manager)
    
    def test_add_config_success(self, db_loader):
        """测试添加配置成功 - 验证需求: 23.4"""
        # 添加配置
        success = db_loader.add_config(
            config_key='test_key',
            config_value={'setting1': 'value1', 'setting2': 123},
            description='测试配置'
        )
        
        assert success is True
        
        # 验证配置已添加
        config_detail = db_loader.get_config_detail_by_key('test_key')
        assert config_detail is not None
        assert config_detail['config_key'] == 'test_key'
        assert config_detail['config_value'] == {'setting1': 'value1', 'setting2': 123}
        assert config_detail['description'] == '测试配置'
    
    def test_add_config_duplicate(self, db_loader):
        """测试添加重复配置 - 应返回 False"""
        # 第一次添加
        success1 = db_loader.add_config('duplicate_key', {'value': 1})
        assert success1 is True
        
        # 第二次添加相同的键
        success2 = db_loader.add_config('duplicate_key', {'value': 2})
        assert success2 is False
    
    def test_add_config_invalid_json(self, db_loader):
        """测试添加无效 JSON 格式的配置 - 验证需求: 23.7"""
        # 尝试添加无效的 JSON 字符串
        with pytest.raises(ValueError):
            db_loader.add_config('invalid_key', '{invalid json}')
    
    def test_get_config_by_key_success(self, db_loader):
        """测试获取配置成功 - 验证需求: 23.2"""
        # 先添加配置
        db_loader.add_config('get_test_key', {'data': 'test'}, 'Get test')
        
        # 获取配置值
        config_value = db_loader.get_config_by_key('get_test_key')
        assert config_value == {'data': 'test'}
        
        # 获取配置详情
        config_detail = db_loader.get_config_detail_by_key('get_test_key')
        assert config_detail['config_key'] == 'get_test_key'
        assert config_detail['config_value'] == {'data': 'test'}
        assert config_detail['description'] == 'Get test'
    
    def test_get_config_by_key_not_found(self, db_loader):
        """测试获取不存在的配置 - 应返回 None"""
        config_value = db_loader.get_config_by_key('nonexistent_key')
        assert config_value is None
        
        config_detail = db_loader.get_config_detail_by_key('nonexistent_key')
        assert config_detail is None
    
    def test_update_config_success(self, db_loader):
        """测试更新配置成功 - 验证需求: 23.3"""
        # 先添加配置
        db_loader.add_config('update_test_key', {'old': 'value'}, 'Original')
        
        # 更新配置
        success = db_loader.update_config('update_test_key', {'new': 'value'})
        assert success is True
        
        # 验证配置已更新
        config_value = db_loader.get_config_by_key('update_test_key')
        assert config_value == {'new': 'value'}
    
    def test_update_config_not_found(self, db_loader):
        """测试更新不存在的配置 - 应返回 False"""
        success = db_loader.update_config('nonexistent_key', {'value': 'test'})
        assert success is False
    
    def test_update_config_invalid_json(self, db_loader):
        """测试更新配置时使用无效 JSON - 验证需求: 23.7"""
        # 先添加配置
        db_loader.add_config('update_invalid_key', {'valid': 'json'})
        
        # 尝试更新为无效 JSON
        with pytest.raises(ValueError):
            db_loader.update_config('update_invalid_key', '{invalid json}')
    
    def test_delete_config_success(self, db_loader):
        """测试删除配置成功 - 验证需求: 23.5"""
        # 先添加配置
        db_loader.add_config('delete_test_key', {'data': 'test'})
        
        # 删除配置
        success = db_loader.delete_config('delete_test_key')
        assert success is True
        
        # 验证配置已删除
        config_value = db_loader.get_config_by_key('delete_test_key')
        assert config_value is None
    
    def test_delete_config_not_found(self, db_loader):
        """测试删除不存在的配置 - 应返回 False"""
        success = db_loader.delete_config('nonexistent_key')
        assert success is False
    
    def test_load_all_configs(self, db_loader):
        """测试加载所有配置 - 验证需求: 23.1"""
        # 添加多个配置
        db_loader.add_config('config1', {'value': 1})
        db_loader.add_config('config2', {'value': 2})
        db_loader.add_config('config3', {'value': 3})
        
        # 加载所有配置
        all_configs = db_loader.load_config()
        
        assert len(all_configs) >= 3
        assert 'config1' in all_configs
        assert 'config2' in all_configs
        assert 'config3' in all_configs
        assert all_configs['config1'] == {'value': 1}
        assert all_configs['config2'] == {'value': 2}
        assert all_configs['config3'] == {'value': 3}
    
    def test_config_crud_flow(self, db_loader):
        """测试完整的配置 CRUD 流程"""
        config_key = 'flow_test_key'
        
        # 1. 创建配置
        success = db_loader.add_config(
            config_key,
            {'initial': 'value'},
            'Flow test config'
        )
        assert success is True
        
        # 2. 读取配置
        config_detail = db_loader.get_config_detail_by_key(config_key)
        assert config_detail is not None
        assert config_detail['config_value'] == {'initial': 'value'}
        
        # 3. 更新配置
        success = db_loader.update_config(config_key, {'updated': 'value'})
        assert success is True
        
        # 4. 验证更新
        config_value = db_loader.get_config_by_key(config_key)
        assert config_value == {'updated': 'value'}
        
        # 5. 删除配置
        success = db_loader.delete_config(config_key)
        assert success is True
        
        # 6. 验证删除
        config_value = db_loader.get_config_by_key(config_key)
        assert config_value is None


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
