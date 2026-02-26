"""
规则 CRUD 操作单元测试
测试 DatabaseLoader 的规则添加、更新、删除功能

验证需求: 14.4, 14.5, 14.7, 14.8, 14.9, 22.4, 22.5, 22.6
"""

import os
import sys
import pytest

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.data_loader import Device, Rule
from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator
from modules.models import Device as DeviceModel, Rule as RuleModel


class TestAddRule:
    """测试添加规则功能 - 验证需求 14.4, 14.5, 22.4"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建内存数据库
        self.db_manager = DatabaseManager('sqlite:///:memory:')
        self.db_manager.create_tables()
        
        # 创建数据库加载器
        self.db_loader = DatabaseLoader(self.db_manager)
        
        # 添加测试设备
        self.test_device = Device(
            device_id='TEST_DEVICE_001',
            brand='霍尼韦尔',
            device_name='温度传感器',
            spec_model='T7350A1008',
            detailed_params='测量范围: -40~120℃',
            unit_price=450.0
        )
        self.db_loader.add_device(self.test_device, auto_generate_rule=False)
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        self.db_manager.close()
    
    def test_add_rule_success(self):
        """测试成功添加规则 - 验证需求 14.4, 14.5"""
        # 创建测试规则
        rule = Rule(
            rule_id='TEST_RULE_001',
            target_device_id='TEST_DEVICE_001',
            auto_extracted_features=['霍尼韦尔', '温度传感器', 'T7350A1008'],
            feature_weights={'霍尼韦尔': 3.0, '温度传感器': 2.5, 'T7350A1008': 3.0},
            match_threshold=2.0,
            remark='测试规则'
        )
        
        # 添加规则
        result = self.db_loader.add_rule(rule)
        
        # 验证添加成功
        assert result is True
        
        # 验证规则已保存到数据库
        saved_rule = self.db_loader.get_rule_by_id('TEST_RULE_001')
        assert saved_rule is not None
        assert saved_rule.rule_id == 'TEST_RULE_001'
        assert saved_rule.target_device_id == 'TEST_DEVICE_001'
        assert saved_rule.auto_extracted_features == ['霍尼韦尔', '温度传感器', 'T7350A1008']
        assert saved_rule.feature_weights == {'霍尼韦尔': 3.0, '温度传感器': 2.5, 'T7350A1008': 3.0}
        assert saved_rule.match_threshold == 2.0
        assert saved_rule.remark == '测试规则'
    
    def test_add_rule_with_nonexistent_device(self):
        """测试添加规则时设备不存在 - 验证需求 14.4（外键约束）"""
        # 创建引用不存在设备的规则
        rule = Rule(
            rule_id='TEST_RULE_002',
            target_device_id='NONEXISTENT_DEVICE',
            auto_extracted_features=['测试'],
            feature_weights={'测试': 1.0},
            match_threshold=2.0,
            remark='测试规则'
        )
        
        # 尝试添加规则，应该抛出 ValueError
        with pytest.raises(ValueError) as exc_info:
            self.db_loader.add_rule(rule)
        
        # 验证错误信息
        assert '外键约束失败' in str(exc_info.value)
        assert 'NONEXISTENT_DEVICE' in str(exc_info.value)
        
        # 验证规则未保存到数据库
        saved_rule = self.db_loader.get_rule_by_id('TEST_RULE_002')
        assert saved_rule is None
    
    def test_add_duplicate_rule(self):
        """测试添加重复规则 - 验证需求 14.5（rule_id 唯一性）"""
        # 创建并添加第一个规则
        rule1 = Rule(
            rule_id='TEST_RULE_003',
            target_device_id='TEST_DEVICE_001',
            auto_extracted_features=['霍尼韦尔'],
            feature_weights={'霍尼韦尔': 3.0},
            match_threshold=2.0,
            remark='第一个规则'
        )
        result1 = self.db_loader.add_rule(rule1)
        assert result1 is True
        
        # 尝试添加相同 rule_id 的规则
        rule2 = Rule(
            rule_id='TEST_RULE_003',  # 相同的 rule_id
            target_device_id='TEST_DEVICE_001',
            auto_extracted_features=['温度传感器'],
            feature_weights={'温度传感器': 2.5},
            match_threshold=2.0,
            remark='第二个规则'
        )
        result2 = self.db_loader.add_rule(rule2)
        
        # 验证第二次添加失败
        assert result2 is False
        
        # 验证数据库中只有第一个规则
        saved_rule = self.db_loader.get_rule_by_id('TEST_RULE_003')
        assert saved_rule is not None
        assert saved_rule.remark == '第一个规则'  # 应该是第一个规则的内容
    
    def test_add_rule_with_empty_features(self):
        """测试添加空特征的规则"""
        # 创建空特征的规则
        rule = Rule(
            rule_id='TEST_RULE_004',
            target_device_id='TEST_DEVICE_001',
            auto_extracted_features=[],
            feature_weights={},
            match_threshold=2.0,
            remark='空特征规则'
        )
        
        # 添加规则
        result = self.db_loader.add_rule(rule)
        
        # 验证添加成功（允许空特征）
        assert result is True
        
        # 验证规则已保存
        saved_rule = self.db_loader.get_rule_by_id('TEST_RULE_004')
        assert saved_rule is not None
        assert saved_rule.auto_extracted_features == []
        assert saved_rule.feature_weights == {}


class TestUpdateRule:
    """测试更新规则功能 - 验证需求 14.7, 22.5"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建内存数据库
        self.db_manager = DatabaseManager('sqlite:///:memory:')
        self.db_manager.create_tables()
        
        # 创建数据库加载器
        self.db_loader = DatabaseLoader(self.db_manager)
        
        # 添加测试设备
        self.test_device = Device(
            device_id='TEST_DEVICE_001',
            brand='霍尼韦尔',
            device_name='温度传感器',
            spec_model='T7350A1008',
            detailed_params='测量范围: -40~120℃',
            unit_price=450.0
        )
        self.db_loader.add_device(self.test_device, auto_generate_rule=False)
        
        # 添加测试规则
        self.test_rule = Rule(
            rule_id='TEST_RULE_001',
            target_device_id='TEST_DEVICE_001',
            auto_extracted_features=['霍尼韦尔', '温度传感器'],
            feature_weights={'霍尼韦尔': 3.0, '温度传感器': 2.5},
            match_threshold=2.0,
            remark='原始规则'
        )
        self.db_loader.add_rule(self.test_rule)
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        self.db_manager.close()
    
    def test_update_rule_success(self):
        """测试成功更新规则 - 验证需求 14.7"""
        # 修改规则
        updated_rule = Rule(
            rule_id='TEST_RULE_001',
            target_device_id='TEST_DEVICE_001',
            auto_extracted_features=['霍尼韦尔', '温度传感器', 'T7350A1008'],
            feature_weights={'霍尼韦尔': 3.0, '温度传感器': 2.5, 'T7350A1008': 3.0},
            match_threshold=2.5,
            remark='更新后的规则'
        )
        
        # 更新规则
        result = self.db_loader.update_rule(updated_rule)
        
        # 验证更新成功
        assert result is True
        
        # 验证规则已更新
        saved_rule = self.db_loader.get_rule_by_id('TEST_RULE_001')
        assert saved_rule is not None
        assert saved_rule.auto_extracted_features == ['霍尼韦尔', '温度传感器', 'T7350A1008']
        assert saved_rule.feature_weights == {'霍尼韦尔': 3.0, '温度传感器': 2.5, 'T7350A1008': 3.0}
        assert saved_rule.match_threshold == 2.5
        assert saved_rule.remark == '更新后的规则'
    
    def test_update_nonexistent_rule(self):
        """测试更新不存在的规则 - 验证需求 14.7"""
        # 创建不存在的规则
        rule = Rule(
            rule_id='NONEXISTENT_RULE',
            target_device_id='TEST_DEVICE_001',
            auto_extracted_features=['测试'],
            feature_weights={'测试': 1.0},
            match_threshold=2.0,
            remark='不存在的规则'
        )
        
        # 尝试更新
        result = self.db_loader.update_rule(rule)
        
        # 验证更新失败
        assert result is False
    
    def test_update_rule_preserves_rule_id(self):
        """测试更新规则时保持 rule_id 不变"""
        # 修改规则
        updated_rule = Rule(
            rule_id='TEST_RULE_001',
            target_device_id='TEST_DEVICE_001',
            auto_extracted_features=['新特征'],
            feature_weights={'新特征': 1.0},
            match_threshold=3.0,
            remark='新备注'
        )
        
        # 更新规则
        result = self.db_loader.update_rule(updated_rule)
        assert result is True
        
        # 验证 rule_id 未改变
        saved_rule = self.db_loader.get_rule_by_id('TEST_RULE_001')
        assert saved_rule is not None
        assert saved_rule.rule_id == 'TEST_RULE_001'
        assert saved_rule.remark == '新备注'
    
    def test_update_rule_all_fields(self):
        """测试更新规则的所有字段"""
        # 修改所有字段
        updated_rule = Rule(
            rule_id='TEST_RULE_001',
            target_device_id='TEST_DEVICE_001',
            auto_extracted_features=['特征1', '特征2', '特征3'],
            feature_weights={'特征1': 1.0, '特征2': 2.0, '特征3': 3.0},
            match_threshold=1.5,
            remark='完全更新的规则'
        )
        
        # 更新规则
        result = self.db_loader.update_rule(updated_rule)
        assert result is True
        
        # 验证所有字段都已更新
        saved_rule = self.db_loader.get_rule_by_id('TEST_RULE_001')
        assert saved_rule.target_device_id == 'TEST_DEVICE_001'
        assert saved_rule.auto_extracted_features == ['特征1', '特征2', '特征3']
        assert saved_rule.feature_weights == {'特征1': 1.0, '特征2': 2.0, '特征3': 3.0}
        assert saved_rule.match_threshold == 1.5
        assert saved_rule.remark == '完全更新的规则'


class TestDeleteRule:
    """测试删除规则功能 - 验证需求 14.8, 14.9, 22.6"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建内存数据库
        self.db_manager = DatabaseManager('sqlite:///:memory:')
        self.db_manager.create_tables()
        
        # 创建数据库加载器
        self.db_loader = DatabaseLoader(self.db_manager)
        
        # 添加测试设备
        self.test_device = Device(
            device_id='TEST_DEVICE_001',
            brand='霍尼韦尔',
            device_name='温度传感器',
            spec_model='T7350A1008',
            detailed_params='测量范围: -40~120℃',
            unit_price=450.0
        )
        self.db_loader.add_device(self.test_device, auto_generate_rule=False)
        
        # 添加测试规则
        self.test_rule = Rule(
            rule_id='TEST_RULE_001',
            target_device_id='TEST_DEVICE_001',
            auto_extracted_features=['霍尼韦尔', '温度传感器'],
            feature_weights={'霍尼韦尔': 3.0, '温度传感器': 2.5},
            match_threshold=2.0,
            remark='测试规则'
        )
        self.db_loader.add_rule(self.test_rule)
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        self.db_manager.close()
    
    def test_delete_rule_success(self):
        """测试成功删除规则 - 验证需求 14.8"""
        # 删除规则
        result = self.db_loader.delete_rule('TEST_RULE_001')
        
        # 验证删除成功
        assert result is True
        
        # 验证规则已从数据库删除
        deleted_rule = self.db_loader.get_rule_by_id('TEST_RULE_001')
        assert deleted_rule is None
    
    def test_delete_rule_does_not_affect_device(self):
        """测试删除规则不影响关联的设备 - 验证需求 14.9"""
        # 删除规则
        result = self.db_loader.delete_rule('TEST_RULE_001')
        assert result is True
        
        # 验证设备仍然存在
        device = self.db_loader.get_device_by_id('TEST_DEVICE_001')
        assert device is not None
        assert device.device_id == 'TEST_DEVICE_001'
        assert device.brand == '霍尼韦尔'
    
    def test_delete_nonexistent_rule(self):
        """测试删除不存在的规则 - 验证需求 14.8"""
        # 尝试删除不存在的规则
        result = self.db_loader.delete_rule('NONEXISTENT_RULE')
        
        # 验证删除失败
        assert result is False
    
    def test_delete_rule_multiple_times(self):
        """测试多次删除同一规则"""
        # 第一次删除
        result1 = self.db_loader.delete_rule('TEST_RULE_001')
        assert result1 is True
        
        # 第二次删除（规则已不存在）
        result2 = self.db_loader.delete_rule('TEST_RULE_001')
        assert result2 is False
    
    def test_delete_one_rule_keeps_others(self):
        """测试删除一个规则不影响其他规则"""
        # 添加第二个规则
        rule2 = Rule(
            rule_id='TEST_RULE_002',
            target_device_id='TEST_DEVICE_001',
            auto_extracted_features=['T7350A1008'],
            feature_weights={'T7350A1008': 3.0},
            match_threshold=2.0,
            remark='第二个规则'
        )
        self.db_loader.add_rule(rule2)
        
        # 删除第一个规则
        result = self.db_loader.delete_rule('TEST_RULE_001')
        assert result is True
        
        # 验证第一个规则已删除
        deleted_rule = self.db_loader.get_rule_by_id('TEST_RULE_001')
        assert deleted_rule is None
        
        # 验证第二个规则仍然存在
        remaining_rule = self.db_loader.get_rule_by_id('TEST_RULE_002')
        assert remaining_rule is not None
        assert remaining_rule.rule_id == 'TEST_RULE_002'


class TestGetRuleByDevice:
    """测试按设备查询规则功能 - 验证需求 14.2, 22.3"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建内存数据库
        self.db_manager = DatabaseManager('sqlite:///:memory:')
        self.db_manager.create_tables()
        
        # 创建数据库加载器
        self.db_loader = DatabaseLoader(self.db_manager)
        
        # 添加测试设备
        self.test_device = Device(
            device_id='TEST_DEVICE_001',
            brand='霍尼韦尔',
            device_name='温度传感器',
            spec_model='T7350A1008',
            detailed_params='测量范围: -40~120℃',
            unit_price=450.0
        )
        self.db_loader.add_device(self.test_device, auto_generate_rule=False)
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        self.db_manager.close()
    
    def test_get_rules_by_device_with_multiple_rules(self):
        """测试查询有多个规则的设备"""
        # 添加多个规则
        rule1 = Rule(
            rule_id='TEST_RULE_001',
            target_device_id='TEST_DEVICE_001',
            auto_extracted_features=['霍尼韦尔'],
            feature_weights={'霍尼韦尔': 3.0},
            match_threshold=2.0,
            remark='规则1'
        )
        rule2 = Rule(
            rule_id='TEST_RULE_002',
            target_device_id='TEST_DEVICE_001',
            auto_extracted_features=['温度传感器'],
            feature_weights={'温度传感器': 2.5},
            match_threshold=2.0,
            remark='规则2'
        )
        self.db_loader.add_rule(rule1)
        self.db_loader.add_rule(rule2)
        
        # 查询设备的规则
        rules = self.db_loader.get_rules_by_device('TEST_DEVICE_001')
        
        # 验证返回了所有规则
        assert len(rules) == 2
        rule_ids = [r.rule_id for r in rules]
        assert 'TEST_RULE_001' in rule_ids
        assert 'TEST_RULE_002' in rule_ids
    
    def test_get_rules_by_device_with_no_rules(self):
        """测试查询没有规则的设备"""
        # 查询设备的规则
        rules = self.db_loader.get_rules_by_device('TEST_DEVICE_001')
        
        # 验证返回空列表
        assert len(rules) == 0
        assert rules == []
    
    def test_get_rules_by_nonexistent_device(self):
        """测试查询不存在的设备的规则"""
        # 查询不存在的设备
        rules = self.db_loader.get_rules_by_device('NONEXISTENT_DEVICE')
        
        # 验证返回空列表
        assert len(rules) == 0
        assert rules == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
