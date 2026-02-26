"""
测试 DatabaseLoader 配置 CRUD 操作
任务 2.4.2: 编写配置 CRUD 单元测试
"""

import pytest
import json
from modules.database_loader import DatabaseLoader
from modules.rule_generator import RuleGenerator
from modules.text_preprocessor import TextPreprocessor


@pytest.fixture
def db_loader(db_manager):
    """创建 DatabaseLoader 实例"""
    # 创建基本配置
    config = {
        'normalization_map': {},
        'feature_split_chars': [' ', '/', '-', '（', '）', '(', ')'],
        'ignore_keywords': [],
        'global_config': {
            'default_match_threshold': 0.6
        }
    }
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor)
    loader = DatabaseLoader(db_manager, rule_generator)
    return loader


class TestAddConfig:
    """测试添加配置功能"""
    
    def test_add_config_basic(self, db_loader):
        """测试基本添加配置功能"""
        config_data = {
            'config_key': 'test_config',
            'config_value': {'setting1': 'value1', 'setting2': 100}
        }
        
        result = db_loader.add_config(config_data)
        
        assert result is not None
        assert result.config_key == 'test_config'
        assert result.config_value == {'setting1': 'value1', 'setting2': 100}
    
    def test_add_config_with_string_value(self, db_loader):
        """测试添加字符串类型的配置值"""
        config_data = {
            'config_key': 'string_config',
            'config_value': 'simple string value'
        }
        
        result = db_loader.add_config(config_data)
        
        assert result is not None
        assert result.config_value == 'simple string value'
    
    def test_add_config_with_number_value(self, db_loader):
        """测试添加数字类型的配置值"""
        config_data = {
            'config_key': 'number_config',
            'config_value': 42
        }
        
        result = db_loader.add_config(config_data)
        
        assert result is not None
        assert result.config_value == 42
    
    def test_add_config_with_list_value(self, db_loader):
        """测试添加列表类型的配置值"""
        config_data = {
            'config_key': 'list_config',
            'config_value': ['item1', 'item2', 'item3']
        }
        
        result = db_loader.add_config(config_data)
        
        assert result is not None
        assert result.config_value == ['item1', 'item2', 'item3']
    
    def test_add_config_with_nested_json(self, db_loader):
        """测试添加嵌套 JSON 配置"""
        config_data = {
            'config_key': 'nested_config',
            'config_value': {
                'level1': {
                    'level2': {
                        'level3': 'deep value'
                    }
                },
                'array': [1, 2, 3]
            }
        }
        
        result = db_loader.add_config(config_data)
        
        assert result is not None
        assert result.config_value['level1']['level2']['level3'] == 'deep value'
        assert result.config_value['array'] == [1, 2, 3]
    
    def test_add_config_duplicate_key(self, db_loader):
        """测试添加重复 config_key 的配置"""
        config_data = {
            'config_key': 'duplicate_config',
            'config_value': {'value': 1}
        }
        
        # 第一次添加成功
        db_loader.add_config(config_data)
        
        # 第二次添加应该抛出异常
        with pytest.raises(Exception):
            db_loader.add_config(config_data)
    
    def test_add_config_with_boolean_value(self, db_loader):
        """测试添加布尔类型的配置值"""
        config_data = {
            'config_key': 'boolean_config',
            'config_value': True
        }
        
        result = db_loader.add_config(config_data)
        
        assert result is not None
        assert result.config_value is True


class TestUpdateConfig:
    """测试更新配置功能"""
    
    def test_update_config_basic(self, db_loader):
        """测试基本更新配置功能"""
        # 添加配置
        config_data = {
            'config_key': 'update_test',
            'config_value': {'old': 'value'}
        }
        db_loader.add_config(config_data)
        
        # 更新配置
        update_data = {
            'config_value': {'new': 'value', 'updated': True}
        }
        result = db_loader.update_config('update_test', update_data)
        
        assert result is not None
        assert result.config_value == {'new': 'value', 'updated': True}
        assert result.config_key == 'update_test'  # key 不变
    
    def test_update_config_change_type(self, db_loader):
        """测试更新配置时改变值类型"""
        # 添加字典类型配置
        config_data = {
            'config_key': 'type_change',
            'config_value': {'dict': 'value'}
        }
        db_loader.add_config(config_data)
        
        # 更新为字符串类型
        update_data = {'config_value': 'string value'}
        result = db_loader.update_config('type_change', update_data)
        
        assert result is not None
        assert result.config_value == 'string value'
    
    def test_update_config_not_found(self, db_loader):
        """测试更新不存在的配置"""
        update_data = {'config_value': {'new': 'value'}}
        
        result = db_loader.update_config('nonexistent', update_data)
        assert result is None
    
    def test_update_config_to_null(self, db_loader):
        """测试更新配置为 null"""
        # 添加配置
        config_data = {
            'config_key': 'null_test',
            'config_value': {'some': 'value'}
        }
        db_loader.add_config(config_data)
        
        # 更新为 null
        update_data = {'config_value': None}
        result = db_loader.update_config('null_test', update_data)
        
        assert result is not None
        assert result.config_value is None


class TestDeleteConfig:
    """测试删除配置功能"""
    
    def test_delete_config_basic(self, db_loader):
        """测试基本删除配置功能"""
        # 添加配置
        config_data = {
            'config_key': 'delete_test',
            'config_value': {'test': 'value'}
        }
        db_loader.add_config(config_data)
        
        # 删除配置
        result = db_loader.delete_config('delete_test')
        
        assert result is not None
        assert result.config_key == 'delete_test'
        
        # 验证配置已删除
        config = db_loader.get_config_by_key('delete_test')
        assert config is None
    
    def test_delete_config_not_found(self, db_loader):
        """测试删除不存在的配置"""
        result = db_loader.delete_config('nonexistent')
        assert result is None


class TestGetConfig:
    """测试查询配置功能"""
    
    def test_get_config_by_key(self, db_loader):
        """测试按 key 查询配置"""
        # 添加配置
        config_data = {
            'config_key': 'get_test',
            'config_value': {'test': 'value'}
        }
        db_loader.add_config(config_data)
        
        # 查询配置
        result = db_loader.get_config_by_key('get_test')
        
        assert result is not None
        assert result.config_key == 'get_test'
        assert result.config_value == {'test': 'value'}
    
    def test_get_config_not_found(self, db_loader):
        """测试查询不存在的配置"""
        result = db_loader.get_config_by_key('nonexistent')
        assert result is None
    
    def test_load_all_configs(self, db_loader):
        """测试加载所有配置"""
        # 添加多个配置
        configs = [
            {'config_key': 'config1', 'config_value': {'value': 1}},
            {'config_key': 'config2', 'config_value': {'value': 2}},
            {'config_key': 'config3', 'config_value': {'value': 3}}
        ]
        for config in configs:
            db_loader.add_config(config)
        
        # 加载所有配置
        result = db_loader.load_config()
        
        assert len(result) >= 3
        config_keys = [c.config_key for c in result]
        assert 'config1' in config_keys
        assert 'config2' in config_keys
        assert 'config3' in config_keys


class TestJSONValidation:
    """测试 JSON 格式验证"""
    
    def test_add_config_with_valid_json(self, db_loader):
        """测试添加有效 JSON 格式的配置"""
        config_data = {
            'config_key': 'valid_json',
            'config_value': {
                'string': 'text',
                'number': 123,
                'boolean': True,
                'null': None,
                'array': [1, 2, 3],
                'object': {'nested': 'value'}
            }
        }
        
        result = db_loader.add_config(config_data)
        
        assert result is not None
        assert result.config_value['string'] == 'text'
        assert result.config_value['number'] == 123
        assert result.config_value['boolean'] is True
        assert result.config_value['null'] is None
        assert result.config_value['array'] == [1, 2, 3]
        assert result.config_value['object']['nested'] == 'value'
    
    def test_config_value_serialization(self, db_loader):
        """测试配置值的序列化和反序列化"""
        original_value = {
            'complex': {
                'data': [1, 2, {'nested': True}]
            }
        }
        
        config_data = {
            'config_key': 'serialization_test',
            'config_value': original_value
        }
        
        # 添加配置
        db_loader.add_config(config_data)
        
        # 重新查询
        result = db_loader.get_config_by_key('serialization_test')
        
        assert result is not None
        assert result.config_value == original_value
        assert result.config_value['complex']['data'][2]['nested'] is True


class TestConfigEdgeCases:
    """测试配置边界情况"""
    
    def test_add_config_with_empty_dict(self, db_loader):
        """测试添加空字典配置"""
        config_data = {
            'config_key': 'empty_dict',
            'config_value': {}
        }
        
        result = db_loader.add_config(config_data)
        
        assert result is not None
        assert result.config_value == {}
    
    def test_add_config_with_empty_list(self, db_loader):
        """测试添加空列表配置"""
        config_data = {
            'config_key': 'empty_list',
            'config_value': []
        }
        
        result = db_loader.add_config(config_data)
        
        assert result is not None
        assert result.config_value == []
    
    def test_add_config_with_zero_value(self, db_loader):
        """测试添加值为 0 的配置"""
        config_data = {
            'config_key': 'zero_value',
            'config_value': 0
        }
        
        result = db_loader.add_config(config_data)
        
        assert result is not None
        assert result.config_value == 0
    
    def test_add_config_with_empty_string(self, db_loader):
        """测试添加空字符串配置"""
        config_data = {
            'config_key': 'empty_string',
            'config_value': ''
        }
        
        result = db_loader.add_config(config_data)
        
        assert result is not None
        assert result.config_value == ''
    
    def test_add_config_with_unicode(self, db_loader):
        """测试添加包含 Unicode 字符的配置"""
        config_data = {
            'config_key': 'unicode_config',
            'config_value': {
                'chinese': '中文测试',
                'emoji': '😀🎉',
                'special': '©®™'
            }
        }
        
        result = db_loader.add_config(config_data)
        
        assert result is not None
        assert result.config_value['chinese'] == '中文测试'
        assert result.config_value['emoji'] == '😀🎉'
        assert result.config_value['special'] == '©®™'
