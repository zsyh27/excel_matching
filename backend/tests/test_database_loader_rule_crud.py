"""
测试 DatabaseLoader 规则 CRUD 操作
任务 2.3.4: 编写规则 CRUD 单元测试
"""

import pytest
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


@pytest.fixture
def sample_device(db_loader):
    """创建示例设备"""
    device_data = {
        'device_id': 'DEVICE001',
        'brand': '海康威视',
        'device_name': '网络摄像机',
        'spec_model': 'DS-2CD2345-I',
        'price': 800.0
    }
    return db_loader.add_device(device_data)


class TestAddRule:
    """测试添加规则功能"""
    
    def test_add_rule_basic(self, db_loader, sample_device):
        """测试基本添加规则功能"""
        rule_data = {
            'rule_id': 'RULE001',
            'target_device_id': 'DEVICE001',
            'keywords': ['网络', '摄像机', '海康'],
            'weights': [2.0, 2.0, 3.0],
            'match_threshold': 0.65
        }
        
        result = db_loader.add_rule(rule_data)
        
        assert result is not None
        assert result.rule_id == 'RULE001'
        assert result.target_device_id == 'DEVICE001'
        assert result.keywords == ['网络', '摄像机', '海康']
        assert result.weights == [2.0, 2.0, 3.0]
        assert result.match_threshold == 0.65
    
    def test_add_rule_with_invalid_device_id(self, db_loader):
        """测试添加规则时 target_device_id 不存在"""
        rule_data = {
            'rule_id': 'RULE002',
            'target_device_id': 'NONEXISTENT',
            'keywords': ['测试'],
            'weights': [1.0],
            'match_threshold': 0.6
        }
        
        # 应该抛出外键约束错误
        with pytest.raises(Exception):
            db_loader.add_rule(rule_data)
    
    def test_add_rule_duplicate_id(self, db_loader, sample_device):
        """测试添加重复 rule_id 的规则"""
        rule_data = {
            'rule_id': 'RULE003',
            'target_device_id': 'DEVICE001',
            'keywords': ['测试'],
            'weights': [1.0],
            'match_threshold': 0.6
        }
        
        # 第一次添加成功
        db_loader.add_rule(rule_data)
        
        # 第二次添加应该抛出异常
        with pytest.raises(Exception):
            db_loader.add_rule(rule_data)
    
    def test_add_rule_with_empty_keywords(self, db_loader, sample_device):
        """测试添加规则时关键词为空"""
        rule_data = {
            'rule_id': 'RULE004',
            'target_device_id': 'DEVICE001',
            'keywords': [],
            'weights': [],
            'match_threshold': 0.6
        }
        
        result = db_loader.add_rule(rule_data)
        assert result is not None
        assert result.keywords == []
    
    def test_add_rule_with_mismatched_weights(self, db_loader, sample_device):
        """测试添加规则时关键词和权重数量不匹配"""
        rule_data = {
            'rule_id': 'RULE005',
            'target_device_id': 'DEVICE001',
            'keywords': ['测试', '设备'],
            'weights': [1.0],  # 权重数量不匹配
            'match_threshold': 0.6
        }
        
        # 根据实现，可能接受或抛出异常
        result = db_loader.add_rule(rule_data)
        assert result is not None


class TestUpdateRule:
    """测试更新规则功能"""
    
    def test_update_rule_basic(self, db_loader, sample_device):
        """测试基本更新规则功能"""
        # 添加规则
        rule_data = {
            'rule_id': 'RULE010',
            'target_device_id': 'DEVICE001',
            'keywords': ['原关键词'],
            'weights': [1.0],
            'match_threshold': 0.6
        }
        db_loader.add_rule(rule_data)
        
        # 更新规则
        update_data = {
            'keywords': ['新关键词', '更新'],
            'weights': [2.0, 2.0],
            'match_threshold': 0.7
        }
        result = db_loader.update_rule('RULE010', update_data)
        
        assert result is not None
        assert result.keywords == ['新关键词', '更新']
        assert result.weights == [2.0, 2.0]
        assert result.match_threshold == 0.7
        assert result.rule_id == 'RULE010'  # rule_id 不变
    
    def test_update_rule_partial_fields(self, db_loader, sample_device):
        """测试部分字段更新"""
        # 添加规则
        rule_data = {
            'rule_id': 'RULE011',
            'target_device_id': 'DEVICE001',
            'keywords': ['测试'],
            'weights': [1.0],
            'match_threshold': 0.6
        }
        db_loader.add_rule(rule_data)
        
        # 只更新阈值
        update_data = {'match_threshold': 0.8}
        result = db_loader.update_rule('RULE011', update_data)
        
        assert result is not None
        assert result.match_threshold == 0.8
        assert result.keywords == ['测试']  # 其他字段不变
    
    def test_update_rule_not_found(self, db_loader):
        """测试更新不存在的规则"""
        update_data = {
            'keywords': ['新关键词'],
            'weights': [1.0]
        }
        
        result = db_loader.update_rule('NONEXISTENT', update_data)
        assert result is None
    
    def test_update_rule_change_device_id(self, db_loader, sample_device):
        """测试更新规则时更改 target_device_id"""
        # 添加第二个设备
        device_data = {
            'device_id': 'DEVICE002',
            'brand': '大华',
            'device_name': '录像机',
            'price': 1200.0
        }
        db_loader.add_device(device_data)
        
        # 添加规则
        rule_data = {
            'rule_id': 'RULE012',
            'target_device_id': 'DEVICE001',
            'keywords': ['测试'],
            'weights': [1.0],
            'match_threshold': 0.6
        }
        db_loader.add_rule(rule_data)
        
        # 更新 target_device_id
        update_data = {'target_device_id': 'DEVICE002'}
        result = db_loader.update_rule('RULE012', update_data)
        
        assert result is not None
        assert result.target_device_id == 'DEVICE002'


class TestDeleteRule:
    """测试删除规则功能"""
    
    def test_delete_rule_basic(self, db_loader, sample_device):
        """测试基本删除规则功能"""
        # 添加规则
        rule_data = {
            'rule_id': 'RULE020',
            'target_device_id': 'DEVICE001',
            'keywords': ['测试'],
            'weights': [1.0],
            'match_threshold': 0.6
        }
        db_loader.add_rule(rule_data)
        
        # 删除规则
        result = db_loader.delete_rule('RULE020')
        
        assert result is not None
        assert result.rule_id == 'RULE020'
        
        # 验证规则已删除
        rule = db_loader.get_rule_by_id('RULE020')
        assert rule is None
    
    def test_delete_rule_not_found(self, db_loader):
        """测试删除不存在的规则"""
        result = db_loader.delete_rule('NONEXISTENT')
        assert result is None
    
    def test_delete_rule_does_not_affect_device(self, db_loader, sample_device):
        """测试删除规则不影响关联的设备"""
        # 添加规则
        rule_data = {
            'rule_id': 'RULE021',
            'target_device_id': 'DEVICE001',
            'keywords': ['测试'],
            'weights': [1.0],
            'match_threshold': 0.6
        }
        db_loader.add_rule(rule_data)
        
        # 删除规则
        db_loader.delete_rule('RULE021')
        
        # 验证设备仍然存在
        device = db_loader.get_device_by_id('DEVICE001')
        assert device is not None
        assert device.device_id == 'DEVICE001'


class TestForeignKeyConstraints:
    """测试外键约束"""
    
    def test_cannot_add_rule_without_device(self, db_loader):
        """测试不能为不存在的设备添加规则"""
        rule_data = {
            'rule_id': 'RULE030',
            'target_device_id': 'NONEXISTENT_DEVICE',
            'keywords': ['测试'],
            'weights': [1.0],
            'match_threshold': 0.6
        }
        
        with pytest.raises(Exception):
            db_loader.add_rule(rule_data)
    
    def test_delete_device_cascades_to_rules(self, db_loader):
        """测试删除设备会级联删除规则"""
        # 添加设备
        device_data = {
            'device_id': 'DEVICE030',
            'brand': '测试品牌',
            'device_name': '测试设备',
            'price': 1000.0
        }
        db_loader.add_device(device_data)
        
        # 添加规则
        rule_data = {
            'rule_id': 'RULE031',
            'target_device_id': 'DEVICE030',
            'keywords': ['测试'],
            'weights': [1.0],
            'match_threshold': 0.6
        }
        db_loader.add_rule(rule_data)
        
        # 删除设备
        db_loader.delete_device('DEVICE030')
        
        # 验证规则也被删除
        rule = db_loader.get_rule_by_id('RULE031')
        assert rule is None


class TestGetRulesByDevice:
    """测试按设备查询规则"""
    
    def test_get_rules_by_device_single_rule(self, db_loader, sample_device):
        """测试查询单个规则"""
        rule_data = {
            'rule_id': 'RULE040',
            'target_device_id': 'DEVICE001',
            'keywords': ['测试'],
            'weights': [1.0],
            'match_threshold': 0.6
        }
        db_loader.add_rule(rule_data)
        
        rules = db_loader.get_rules_by_device('DEVICE001')
        
        assert len(rules) == 1
        assert rules[0].rule_id == 'RULE040'
    
    def test_get_rules_by_device_multiple_rules(self, db_loader, sample_device):
        """测试查询多个规则"""
        rule_data_1 = {
            'rule_id': 'RULE041',
            'target_device_id': 'DEVICE001',
            'keywords': ['测试1'],
            'weights': [1.0],
            'match_threshold': 0.6
        }
        rule_data_2 = {
            'rule_id': 'RULE042',
            'target_device_id': 'DEVICE001',
            'keywords': ['测试2'],
            'weights': [1.0],
            'match_threshold': 0.7
        }
        db_loader.add_rule(rule_data_1)
        db_loader.add_rule(rule_data_2)
        
        rules = db_loader.get_rules_by_device('DEVICE001')
        
        assert len(rules) == 2
        rule_ids = [r.rule_id for r in rules]
        assert 'RULE041' in rule_ids
        assert 'RULE042' in rule_ids
    
    def test_get_rules_by_device_no_rules(self, db_loader, sample_device):
        """测试查询没有规则的设备"""
        rules = db_loader.get_rules_by_device('DEVICE001')
        assert len(rules) == 0
    
    def test_get_rules_by_nonexistent_device(self, db_loader):
        """测试查询不存在的设备的规则"""
        rules = db_loader.get_rules_by_device('NONEXISTENT')
        assert len(rules) == 0
