"""
DatabaseLoader 单元测试
测试设备 CRUD 操作和自动规则生成功能

验证需求: 9.1, 13.3, 13.4, 13.5, 18.1, 18.2, 19.4
"""

import os
import sys
import pytest
import tempfile

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.data_loader import Device, Rule
from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator
from modules.models import Device as DeviceModel, Rule as RuleModel


class TestAddDeviceWithAutoRule:
    """测试添加设备时自动生成规则功能 - 验证需求 13.4, 18.1, 18.2"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建内存数据库
        self.db_manager = DatabaseManager('sqlite:///:memory:')
        self.db_manager.create_tables()
        
        # 创建预处理器配置
        config = {
            'normalization_map': {
                '（': '(',
                '）': ')',
                '，': ',',
                '：': ':',
                '；': ';'
            },
            'feature_split_chars': [',', '，', ' ', ';', '；'],
            'ignore_keywords': ['的', '和', '或', '与'],
            'global_config': {
                'default_match_threshold': 2.0
            }
        }
        
        # 创建预处理器和规则生成器
        self.preprocessor = TextPreprocessor(config)
        self.rule_generator = RuleGenerator(self.preprocessor, default_threshold=2.0)
        
        # 创建数据库加载器
        self.db_loader = DatabaseLoader(
            self.db_manager,
            preprocessor=self.preprocessor,
            rule_generator=self.rule_generator
        )
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        self.db_manager.close()
    
    def test_add_device_with_auto_generate_rule_enabled(self):
        """测试添加设备时自动生成规则（默认启用） - 验证需求 13.4, 18.1"""
        # 创建测试设备
        device = Device(
            device_id='TEST001',
            brand='霍尼韦尔',
            device_name='温度传感器',
            spec_model='T7350A1008',
            detailed_params='测量范围: -40~120℃, 精度: ±0.5℃',
            unit_price=450.0
        )
        
        # 添加设备（默认 auto_generate_rule=True）
        result = self.db_loader.add_device(device)
        
        # 验证设备添加成功
        assert result is True
        
        # 验证设备已保存到数据库
        saved_device = self.db_loader.get_device_by_id('TEST001')
        assert saved_device is not None
        assert saved_device.brand == '霍尼韦尔'
        
        # 验证规则已自动生成并保存
        with self.db_manager.session_scope() as session:
            rule = session.query(RuleModel).filter_by(rule_id='R_TEST001').first()
            assert rule is not None
            assert rule.target_device_id == 'TEST001'
            assert len(rule.auto_extracted_features) > 0
            assert len(rule.feature_weights) > 0
            assert rule.match_threshold == 2.0
    
    def test_add_device_with_auto_generate_rule_disabled(self):
        """测试添加设备时禁用自动生成规则 - 验证需求 18.1"""
        # 创建测试设备
        device = Device(
            device_id='TEST002',
            brand='西门子',
            device_name='压力传感器',
            spec_model='QBE2003-P25',
            detailed_params='测量范围: 0-25bar',
            unit_price=680.0
        )
        
        # 添加设备，禁用自动生成规则
        result = self.db_loader.add_device(device, auto_generate_rule=False)
        
        # 验证设备添加成功
        assert result is True
        
        # 验证设备已保存到数据库
        saved_device = self.db_loader.get_device_by_id('TEST002')
        assert saved_device is not None
        
        # 验证规则未生成
        with self.db_manager.session_scope() as session:
            rule = session.query(RuleModel).filter_by(rule_id='R_TEST002').first()
            assert rule is None
    
    def test_add_device_rule_generation_uses_correct_logic(self):
        """测试自动生成规则使用正确的逻辑 - 验证需求 18.2"""
        # 创建测试设备
        device = Device(
            device_id='TEST003',
            brand='施耐德',
            device_name='DDC控制器',
            spec_model='SE8000',
            detailed_params='8点输入输出, 支持BACnet协议',
            unit_price=1200.0
        )
        
        # 添加设备
        result = self.db_loader.add_device(device)
        assert result is True
        
        # 验证规则生成使用了需求 3 中定义的逻辑
        with self.db_manager.session_scope() as session:
            rule = session.query(RuleModel).filter_by(rule_id='R_TEST003').first()
            assert rule is not None
            
            # 验证特征提取（需求 3.1）
            features = rule.auto_extracted_features
            assert len(features) > 0
            # 应该包含品牌、设备名称等关键特征
            assert any('施耐德' in f or 'Schneider' in f for f in features)
            
            # 验证权重分配（需求 3.2）
            weights = rule.feature_weights
            assert len(weights) > 0
            # 品牌和型号应该有较高权重（3.0）
            # 设备类型关键词应该有中等权重（2.5）
            for feature, weight in weights.items():
                assert weight in [1.0, 2.5, 3.0]
            
            # 验证使用默认阈值（需求 3.3）
            assert rule.match_threshold == 2.0
    
    def test_add_device_rule_generation_failure_does_not_rollback(self):
        """测试规则生成失败时不回滚设备插入 - 验证需求 13.5, 18.2"""
        # 创建一个没有足够信息生成规则的设备
        device = Device(
            device_id='TEST004',
            brand='',  # 空品牌
            device_name='',  # 空名称
            spec_model='',  # 空型号
            detailed_params='',  # 空参数
            unit_price=100.0
        )
        
        # 添加设备（规则生成可能失败）
        result = self.db_loader.add_device(device)
        
        # 验证设备仍然添加成功
        assert result is True
        
        # 验证设备已保存到数据库
        saved_device = self.db_loader.get_device_by_id('TEST004')
        assert saved_device is not None
        
        # 规则可能生成失败或生成了空规则，但设备应该保存成功
        # 这验证了规则生成失败不会回滚设备插入
    
    def test_add_device_updates_existing_rule(self):
        """测试添加设备时更新已存在的规则 - 验证需求 3.5"""
        # 创建测试设备
        device = Device(
            device_id='TEST005',
            brand='霍尼韦尔',
            device_name='温度传感器',
            spec_model='T7350A1008',
            detailed_params='测量范围: -40~120℃',
            unit_price=450.0
        )
        
        # 第一次添加设备
        result = self.db_loader.add_device(device)
        assert result is True
        
        # 获取生成的规则
        with self.db_manager.session_scope() as session:
            rule1 = session.query(RuleModel).filter_by(rule_id='R_TEST005').first()
            assert rule1 is not None
            original_features = rule1.auto_extracted_features.copy()
        
        # 删除设备（会级联删除规则）
        success, _ = self.db_loader.delete_device('TEST005')
        assert success is True
        
        # 修改设备信息
        device.detailed_params = '测量范围: -40~120℃, 精度: ±0.5℃, 输出: 4-20mA'
        
        # 再次添加设备
        result = self.db_loader.add_device(device)
        assert result is True
        
        # 验证规则被重新生成
        with self.db_manager.session_scope() as session:
            rule2 = session.query(RuleModel).filter_by(rule_id='R_TEST005').first()
            assert rule2 is not None
            # 新规则的特征可能不同（因为设备参数变了）
            new_features = rule2.auto_extracted_features
            assert len(new_features) > 0
    
    def test_add_device_without_rule_generator(self):
        """测试没有规则生成器时添加设备"""
        # 创建没有规则生成器的加载器
        db_loader_no_gen = DatabaseLoader(
            self.db_manager,
            preprocessor=self.preprocessor,
            rule_generator=None  # 没有规则生成器
        )
        
        # 创建测试设备
        device = Device(
            device_id='TEST006',
            brand='西门子',
            device_name='压力传感器',
            spec_model='QBE2003-P25',
            detailed_params='测量范围: 0-25bar',
            unit_price=680.0
        )
        
        # 添加设备（即使 auto_generate_rule=True，也不会生成规则）
        result = db_loader_no_gen.add_device(device, auto_generate_rule=True)
        
        # 验证设备添加成功
        assert result is True
        
        # 验证设备已保存
        saved_device = db_loader_no_gen.get_device_by_id('TEST006')
        assert saved_device is not None
        
        # 验证规则未生成（因为没有规则生成器）
        with self.db_manager.session_scope() as session:
            rule = session.query(RuleModel).filter_by(rule_id='R_TEST006').first()
            assert rule is None
    
    def test_add_duplicate_device_returns_false(self):
        """测试添加重复设备返回 False - 验证需求 9.1"""
        # 创建测试设备
        device = Device(
            device_id='TEST007',
            brand='霍尼韦尔',
            device_name='温度传感器',
            spec_model='T7350A1008',
            detailed_params='测量范围: -40~120℃',
            unit_price=450.0
        )
        
        # 第一次添加设备
        result1 = self.db_loader.add_device(device)
        assert result1 is True
        
        # 尝试添加相同 device_id 的设备
        result2 = self.db_loader.add_device(device)
        assert result2 is False
        
        # 验证数据库中只有一个设备
        with self.db_manager.session_scope() as session:
            devices = session.query(DeviceModel).filter_by(device_id='TEST007').all()
            assert len(devices) == 1


class TestAddDeviceValidation:
    """测试添加设备时的数据验证 - 验证需求 9.1, 13.3"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.db_manager = DatabaseManager('sqlite:///:memory:')
        self.db_manager.create_tables()
        
        # 创建预处理器配置
        config = {
            'normalization_map': {
                '（': '(',
                '）': ')',
                '，': ',',
                '：': ':',
                '；': ';'
            },
            'feature_split_chars': [',', '，', ' ', ';', '；'],
            'ignore_keywords': ['的', '和', '或', '与'],
            'global_config': {
                'default_match_threshold': 2.0
            }
        }
        
        self.preprocessor = TextPreprocessor(config)
        self.rule_generator = RuleGenerator(self.preprocessor)
        
        self.db_loader = DatabaseLoader(
            self.db_manager,
            preprocessor=self.preprocessor,
            rule_generator=self.rule_generator
        )
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        self.db_manager.close()
    
    def test_add_device_with_complete_data(self):
        """测试添加完整数据的设备 - 验证需求 13.3"""
        device = Device(
            device_id='VALID001',
            brand='霍尼韦尔',
            device_name='温度传感器',
            spec_model='T7350A1008',
            detailed_params='测量范围: -40~120℃, 精度: ±0.5℃',
            unit_price=450.0
        )
        
        result = self.db_loader.add_device(device)
        assert result is True
        
        # 验证数据完整性
        saved_device = self.db_loader.get_device_by_id('VALID001')
        assert saved_device.device_id == 'VALID001'
        assert saved_device.brand == '霍尼韦尔'
        assert saved_device.device_name == '温度传感器'
        assert saved_device.spec_model == 'T7350A1008'
        assert saved_device.detailed_params == '测量范围: -40~120℃, 精度: ±0.5℃'
        assert saved_device.unit_price == 450.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])



class TestUpdateDeviceWithRegenerateRule:
    """测试更新设备时重新生成规则功能 - 验证需求 13.7, 18.7"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建内存数据库
        self.db_manager = DatabaseManager('sqlite:///:memory:')
        self.db_manager.create_tables()
        
        # 创建预处理器配置
        config = {
            'normalization_map': {
                '（': '(',
                '）': ')',
                '，': ',',
                '：': ':',
                '；': ';'
            },
            'feature_split_chars': [',', '，', ' ', ';', '；'],
            'ignore_keywords': ['的', '和', '或', '与'],
            'global_config': {
                'default_match_threshold': 2.0
            }
        }
        
        # 创建预处理器和规则生成器
        self.preprocessor = TextPreprocessor(config)
        self.rule_generator = RuleGenerator(self.preprocessor, default_threshold=2.0)
        
        # 创建数据库加载器
        self.db_loader = DatabaseLoader(
            self.db_manager,
            preprocessor=self.preprocessor,
            rule_generator=self.rule_generator
        )
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        self.db_manager.close()
    
    def test_update_device_without_regenerate_rule(self):
        """测试更新设备时不重新生成规则（默认行为） - 验证需求 13.6"""
        # 创建并添加测试设备
        device = Device(
            device_id='UPDATE001',
            brand='霍尼韦尔',
            device_name='温度传感器',
            spec_model='T7350A1008',
            detailed_params='测量范围: -40~120℃',
            unit_price=450.0
        )
        self.db_loader.add_device(device)
        
        # 获取原始规则
        with self.db_manager.session_scope() as session:
            original_rule = session.query(RuleModel).filter_by(rule_id='R_UPDATE001').first()
            assert original_rule is not None
            original_features = original_rule.auto_extracted_features.copy()
        
        # 更新设备信息（不重新生成规则）
        device.detailed_params = '测量范围: -40~120℃, 精度: ±0.5℃, 输出: 4-20mA'
        device.unit_price = 480.0
        result = self.db_loader.update_device(device, regenerate_rule=False)
        
        # 验证更新成功
        assert result is True
        
        # 验证设备信息已更新
        updated_device = self.db_loader.get_device_by_id('UPDATE001')
        assert updated_device.detailed_params == '测量范围: -40~120℃, 精度: ±0.5℃, 输出: 4-20mA'
        assert updated_device.unit_price == 480.0
        
        # 验证规则未改变
        with self.db_manager.session_scope() as session:
            current_rule = session.query(RuleModel).filter_by(rule_id='R_UPDATE001').first()
            assert current_rule is not None
            assert current_rule.auto_extracted_features == original_features
    
    def test_update_device_with_regenerate_rule_enabled(self):
        """测试更新设备时重新生成规则 - 验证需求 13.7, 18.7"""
        # 创建并添加测试设备
        device = Device(
            device_id='UPDATE002',
            brand='西门子',
            device_name='压力传感器',
            spec_model='QBE2003-P25',
            detailed_params='测量范围: 0-25bar',
            unit_price=680.0
        )
        self.db_loader.add_device(device)
        
        # 获取原始规则
        with self.db_manager.session_scope() as session:
            original_rule = session.query(RuleModel).filter_by(rule_id='R_UPDATE002').first()
            assert original_rule is not None
            original_features = original_rule.auto_extracted_features.copy()
            original_weights = original_rule.feature_weights.copy()
        
        # 更新设备信息（重新生成规则）
        device.detailed_params = '测量范围: 0-25bar, 精度: ±0.5%, 输出: 4-20mA, 防护等级: IP65'
        device.spec_model = 'QBE2003-P25U'  # 修改型号
        result = self.db_loader.update_device(device, regenerate_rule=True)
        
        # 验证更新成功
        assert result is True
        
        # 验证设备信息已更新
        updated_device = self.db_loader.get_device_by_id('UPDATE002')
        assert updated_device.detailed_params == '测量范围: 0-25bar, 精度: ±0.5%, 输出: 4-20mA, 防护等级: IP65'
        assert updated_device.spec_model == 'QBE2003-P25U'
        
        # 验证规则已重新生成
        with self.db_manager.session_scope() as session:
            updated_rule = session.query(RuleModel).filter_by(rule_id='R_UPDATE002').first()
            assert updated_rule is not None
            # 规则应该已更新（特征可能不同）
            # 由于设备参数变化，特征列表应该有所不同
            assert len(updated_rule.auto_extracted_features) > 0
    
    def test_update_device_regenerate_rule_creates_new_if_not_exists(self):
        """测试更新设备时如果规则不存在则创建新规则 - 验证需求 13.7"""
        # 创建并添加测试设备（不生成规则）
        device = Device(
            device_id='UPDATE003',
            brand='施耐德',
            device_name='DDC控制器',
            spec_model='SE8000',
            detailed_params='8点输入输出',
            unit_price=1200.0
        )
        self.db_loader.add_device(device, auto_generate_rule=False)
        
        # 验证规则不存在
        with self.db_manager.session_scope() as session:
            rule = session.query(RuleModel).filter_by(rule_id='R_UPDATE003').first()
            assert rule is None
        
        # 更新设备并生成规则
        device.detailed_params = '8点输入输出, 支持BACnet协议'
        result = self.db_loader.update_device(device, regenerate_rule=True)
        
        # 验证更新成功
        assert result is True
        
        # 验证规则已创建
        with self.db_manager.session_scope() as session:
            new_rule = session.query(RuleModel).filter_by(rule_id='R_UPDATE003').first()
            assert new_rule is not None
            assert new_rule.target_device_id == 'UPDATE003'
            assert len(new_rule.auto_extracted_features) > 0
    
    def test_update_device_regenerate_rule_without_generator(self):
        """测试没有规则生成器时更新设备"""
        # 创建没有规则生成器的加载器
        db_loader_no_gen = DatabaseLoader(
            self.db_manager,
            preprocessor=self.preprocessor,
            rule_generator=None
        )
        
        # 创建并添加测试设备
        device = Device(
            device_id='UPDATE004',
            brand='霍尼韦尔',
            device_name='温度传感器',
            spec_model='T7350A1008',
            detailed_params='测量范围: -40~120℃',
            unit_price=450.0
        )
        # 使用有规则生成器的加载器添加设备
        self.db_loader.add_device(device)
        
        # 使用没有规则生成器的加载器更新设备
        device.unit_price = 480.0
        result = db_loader_no_gen.update_device(device, regenerate_rule=True)
        
        # 验证更新成功（即使请求重新生成规则）
        assert result is True
        
        # 验证设备已更新
        updated_device = db_loader_no_gen.get_device_by_id('UPDATE004')
        assert updated_device.unit_price == 480.0
    
    def test_update_device_regenerate_rule_failure_does_not_rollback(self):
        """测试规则重新生成失败时不回滚设备更新 - 验证需求 18.7"""
        # 创建并添加测试设备
        device = Device(
            device_id='UPDATE005',
            brand='西门子',
            device_name='压力传感器',
            spec_model='QBE2003-P25',
            detailed_params='测量范围: 0-25bar',
            unit_price=680.0
        )
        self.db_loader.add_device(device)
        
        # 更新设备为空信息（可能导致规则生成失败）
        device.brand = ''
        device.device_name = ''
        device.spec_model = ''
        device.detailed_params = ''
        device.unit_price = 700.0
        
        result = self.db_loader.update_device(device, regenerate_rule=True)
        
        # 验证设备更新仍然成功
        assert result is True
        
        # 验证设备信息已更新
        updated_device = self.db_loader.get_device_by_id('UPDATE005')
        assert updated_device.unit_price == 700.0
        assert updated_device.brand == ''
    
    def test_update_nonexistent_device_returns_false(self):
        """测试更新不存在的设备返回 False - 验证需求 9.2"""
        device = Device(
            device_id='NONEXISTENT',
            brand='霍尼韦尔',
            device_name='温度传感器',
            spec_model='T7350A1008',
            detailed_params='测量范围: -40~120℃',
            unit_price=450.0
        )
        
        result = self.db_loader.update_device(device, regenerate_rule=False)
        assert result is False
    
    def test_update_device_preserves_device_id(self):
        """测试更新设备时保持 device_id 不变 - 验证需求 9.2"""
        # 创建并添加测试设备
        device = Device(
            device_id='UPDATE006',
            brand='霍尼韦尔',
            device_name='温度传感器',
            spec_model='T7350A1008',
            detailed_params='测量范围: -40~120℃',
            unit_price=450.0
        )
        self.db_loader.add_device(device)
        
        # 更新设备
        device.brand = '西门子'
        device.device_name = '压力传感器'
        result = self.db_loader.update_device(device)
        
        # 验证更新成功
        assert result is True
        
        # 验证 device_id 未改变
        updated_device = self.db_loader.get_device_by_id('UPDATE006')
        assert updated_device is not None
        assert updated_device.device_id == 'UPDATE006'
        assert updated_device.brand == '西门子'
        assert updated_device.device_name == '压力传感器'



class TestDeleteDeviceEnhanced:
    """测试删除设备功能增强 - 验证需求 9.3, 13.8, 19.6"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建内存数据库
        self.db_manager = DatabaseManager('sqlite:///:memory:')
        self.db_manager.create_tables()
        
        # 创建预处理器配置
        config = {
            'normalization_map': {
                '（': '(',
                '）': ')',
                '，': ',',
                '：': ':',
                '；': ';'
            },
            'feature_split_chars': [',', '，', ' ', ';', '；'],
            'ignore_keywords': ['的', '和', '或', '与'],
            'global_config': {
                'default_match_threshold': 2.0
            }
        }
        
        # 创建预处理器和规则生成器
        self.preprocessor = TextPreprocessor(config)
        self.rule_generator = RuleGenerator(self.preprocessor, default_threshold=2.0)
        
        # 创建数据库加载器
        self.db_loader = DatabaseLoader(
            self.db_manager,
            preprocessor=self.preprocessor,
            rule_generator=self.rule_generator
        )
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        self.db_manager.close()
    
    def test_delete_device_returns_tuple(self):
        """测试删除设备返回元组 (成功标志, 规则数量) - 验证需求 19.6"""
        # 创建并添加测试设备（自动生成规则）
        device = Device(
            device_id='DELETE001',
            brand='霍尼韦尔',
            device_name='温度传感器',
            spec_model='T7350A1008',
            detailed_params='测量范围: -40~120℃',
            unit_price=450.0
        )
        self.db_loader.add_device(device, auto_generate_rule=True)
        
        # 删除设备
        success, rules_count = self.db_loader.delete_device('DELETE001')
        
        # 验证返回值类型和内容
        assert isinstance(success, bool)
        assert isinstance(rules_count, int)
        assert success is True
        assert rules_count == 1  # 应该有1条规则被级联删除
    
    def test_delete_device_with_multiple_rules(self):
        """测试删除有多条规则的设备 - 验证需求 13.8"""
        # 创建并添加测试设备
        device = Device(
            device_id='DELETE002',
            brand='西门子',
            device_name='压力传感器',
            spec_model='QBE2003-P25',
            detailed_params='测量范围: 0-25bar',
            unit_price=680.0
        )
        self.db_loader.add_device(device, auto_generate_rule=True)
        
        # 手动添加额外的规则（模拟多条规则的情况）
        with self.db_manager.session_scope() as session:
            extra_rule = RuleModel(
                rule_id='R_DELETE002_EXTRA',
                target_device_id='DELETE002',
                auto_extracted_features=['西门子', '压力传感器'],
                feature_weights={'西门子': 3.0, '压力传感器': 2.5},
                match_threshold=2.0,
                remark='额外的测试规则'
            )
            session.add(extra_rule)
        
        # 验证有2条规则
        with self.db_manager.session_scope() as session:
            rules_before = session.query(RuleModel).filter_by(target_device_id='DELETE002').count()
            assert rules_before == 2
        
        # 删除设备
        success, rules_count = self.db_loader.delete_device('DELETE002')
        
        # 验证删除成功并返回正确的规则数量
        assert success is True
        assert rules_count == 2  # 应该有2条规则被级联删除
        
        # 验证设备和规则都已删除
        deleted_device = self.db_loader.get_device_by_id('DELETE002')
        assert deleted_device is None
        
        with self.db_manager.session_scope() as session:
            rules_after = session.query(RuleModel).filter_by(target_device_id='DELETE002').count()
            assert rules_after == 0
    
    def test_delete_device_without_rules(self):
        """测试删除没有规则的设备 - 验证需求 9.3"""
        # 创建并添加测试设备（不生成规则）
        device = Device(
            device_id='DELETE003',
            brand='施耐德',
            device_name='DDC控制器',
            spec_model='SE8000',
            detailed_params='8点输入输出',
            unit_price=1200.0
        )
        self.db_loader.add_device(device, auto_generate_rule=False)
        
        # 验证没有规则
        with self.db_manager.session_scope() as session:
            rules_before = session.query(RuleModel).filter_by(target_device_id='DELETE003').count()
            assert rules_before == 0
        
        # 删除设备
        success, rules_count = self.db_loader.delete_device('DELETE003')
        
        # 验证删除成功，规则数量为0
        assert success is True
        assert rules_count == 0
        
        # 验证设备已删除
        deleted_device = self.db_loader.get_device_by_id('DELETE003')
        assert deleted_device is None
    
    def test_delete_nonexistent_device(self):
        """测试删除不存在的设备 - 验证需求 9.3"""
        # 尝试删除不存在的设备
        success, rules_count = self.db_loader.delete_device('NONEXISTENT')
        
        # 验证返回失败和0条规则
        assert success is False
        assert rules_count == 0
    
    def test_cascade_delete_verification(self):
        """测试级联删除正常工作 - 验证需求 13.8"""
        # 创建并添加测试设备
        device = Device(
            device_id='DELETE004',
            brand='霍尼韦尔',
            device_name='温度传感器',
            spec_model='T7350A1008',
            detailed_params='测量范围: -40~120℃',
            unit_price=450.0
        )
        self.db_loader.add_device(device, auto_generate_rule=True)
        
        # 验证设备和规则都存在
        device_before = self.db_loader.get_device_by_id('DELETE004')
        assert device_before is not None
        
        with self.db_manager.session_scope() as session:
            rule_before = session.query(RuleModel).filter_by(rule_id='R_DELETE004').first()
            assert rule_before is not None
        
        # 删除设备
        success, rules_count = self.db_loader.delete_device('DELETE004')
        assert success is True
        assert rules_count == 1
        
        # 验证设备已删除
        device_after = self.db_loader.get_device_by_id('DELETE004')
        assert device_after is None
        
        # 验证规则也被级联删除
        with self.db_manager.session_scope() as session:
            rule_after = session.query(RuleModel).filter_by(rule_id='R_DELETE004').first()
            assert rule_after is None
    
    def test_delete_device_logs_correct_info(self):
        """测试删除设备时记录正确的日志信息 - 验证需求 13.8"""
        # 创建并添加测试设备
        device = Device(
            device_id='DELETE005',
            brand='西门子',
            device_name='压力传感器',
            spec_model='QBE2003-P25',
            detailed_params='测量范围: 0-25bar',
            unit_price=680.0
        )
        self.db_loader.add_device(device, auto_generate_rule=True)
        
        # 删除设备（日志应该包含级联删除的规则数量）
        success, rules_count = self.db_loader.delete_device('DELETE005')
        
        # 验证返回值正确
        assert success is True
        assert rules_count == 1
        
        # 注意：实际的日志验证需要使用日志捕获工具，这里只验证功能正确性



class TestConfigCRUD:
    """测试配置 CRUD 操作 - 验证需求 15.3-15.7, 23.3-23.5"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建内存数据库
        self.db_manager = DatabaseManager('sqlite:///:memory:')
        self.db_manager.create_tables()
        
        # 创建数据库加载器
        self.db_loader = DatabaseLoader(self.db_manager)
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        self.db_manager.close()
    
    def test_add_config_success(self):
        """测试添加配置成功 - 验证需求 15.3, 23.4"""
        # 添加配置
        result = self.db_loader.add_config(
            config_key='test_config',
            config_value={'threshold': 0.7, 'max_results': 5},
            description='测试配置'
        )
        
        # 验证添加成功
        assert result is True
        
        # 验证配置已保存
        config_value = self.db_loader.get_config_by_key('test_config')
        assert config_value is not None
        assert config_value['threshold'] == 0.7
        assert config_value['max_results'] == 5
    
    def test_add_config_duplicate_key_returns_false(self):
        """测试添加重复键的配置返回 False - 验证需求 15.3"""
        # 添加第一个配置
        result1 = self.db_loader.add_config(
            config_key='duplicate_key',
            config_value={'value': 1}
        )
        assert result1 is True
        
        # 尝试添加相同键的配置
        result2 = self.db_loader.add_config(
            config_key='duplicate_key',
            config_value={'value': 2}
        )
        assert result2 is False
        
        # 验证原配置未被修改
        config_value = self.db_loader.get_config_by_key('duplicate_key')
        assert config_value['value'] == 1
    
    def test_add_config_with_json_string(self):
        """测试添加 JSON 字符串格式的配置 - 验证需求 15.6, 23.7"""
        import json
        
        # 添加 JSON 字符串格式的配置
        json_string = json.dumps({'key1': 'value1', 'key2': 'value2'})
        result = self.db_loader.add_config(
            config_key='json_string_config',
            config_value=json_string
        )
        
        # 验证添加成功
        assert result is True
    
    def test_add_config_with_invalid_json_raises_error(self):
        """测试添加无效 JSON 格式的配置抛出异常 - 验证需求 15.6, 23.7"""
        # 尝试添加无效的 JSON 字符串
        with pytest.raises(ValueError) as exc_info:
            self.db_loader.add_config(
                config_key='invalid_json',
                config_value='{"invalid": json}'  # 无效的 JSON
            )
        
        assert '无效的 JSON 格式' in str(exc_info.value)
    
    def test_update_config_success(self):
        """测试更新配置成功 - 验证需求 15.4, 23.3"""
        # 先添加配置
        self.db_loader.add_config(
            config_key='update_test',
            config_value={'old_value': 100}
        )
        
        # 更新配置
        result = self.db_loader.update_config(
            config_key='update_test',
            config_value={'new_value': 200}
        )
        
        # 验证更新成功
        assert result is True
        
        # 验证配置已更新
        config_value = self.db_loader.get_config_by_key('update_test')
        assert config_value is not None
        assert 'new_value' in config_value
        assert config_value['new_value'] == 200
        assert 'old_value' not in config_value
    
    def test_update_nonexistent_config_returns_false(self):
        """测试更新不存在的配置返回 False - 验证需求 15.4"""
        # 尝试更新不存在的配置
        result = self.db_loader.update_config(
            config_key='nonexistent',
            config_value={'value': 123}
        )
        
        # 验证返回 False
        assert result is False
    
    def test_update_config_with_invalid_json_raises_error(self):
        """测试更新配置时使用无效 JSON 格式抛出异常 - 验证需求 15.6, 23.7"""
        # 先添加配置
        self.db_loader.add_config(
            config_key='update_invalid',
            config_value={'value': 1}
        )
        
        # 尝试用无效 JSON 更新
        with pytest.raises(ValueError) as exc_info:
            self.db_loader.update_config(
                config_key='update_invalid',
                config_value='invalid json string'
            )
        
        assert '无效的 JSON 格式' in str(exc_info.value)
        
        # 验证原配置未被修改
        config_value = self.db_loader.get_config_by_key('update_invalid')
        assert config_value['value'] == 1
    
    def test_delete_config_success(self):
        """测试删除配置成功 - 验证需求 15.5, 23.5"""
        # 先添加配置
        self.db_loader.add_config(
            config_key='delete_test',
            config_value={'value': 999}
        )
        
        # 验证配置存在
        config_value = self.db_loader.get_config_by_key('delete_test')
        assert config_value is not None
        
        # 删除配置
        result = self.db_loader.delete_config('delete_test')
        
        # 验证删除成功
        assert result is True
        
        # 验证配置已删除
        config_value = self.db_loader.get_config_by_key('delete_test')
        assert config_value is None
    
    def test_delete_nonexistent_config_returns_false(self):
        """测试删除不存在的配置返回 False - 验证需求 15.5"""
        # 尝试删除不存在的配置
        result = self.db_loader.delete_config('nonexistent')
        
        # 验证返回 False
        assert result is False
    
    def test_get_config_by_key_returns_none_for_nonexistent(self):
        """测试查询不存在的配置返回 None - 验证需求 15.7"""
        # 查询不存在的配置
        config_value = self.db_loader.get_config_by_key('nonexistent_key')
        
        # 验证返回 None
        assert config_value is None
    
    def test_load_config_returns_all_configs(self):
        """测试加载所有配置 - 验证需求 15.1, 23.1"""
        # 添加多个配置
        self.db_loader.add_config('config1', {'value': 1})
        self.db_loader.add_config('config2', {'value': 2})
        self.db_loader.add_config('config3', {'value': 3})
        
        # 加载所有配置
        all_configs = self.db_loader.load_config()
        
        # 验证返回所有配置
        assert len(all_configs) == 3
        assert 'config1' in all_configs
        assert 'config2' in all_configs
        assert 'config3' in all_configs
        assert all_configs['config1']['value'] == 1
        assert all_configs['config2']['value'] == 2
        assert all_configs['config3']['value'] == 3
    
    def test_config_with_complex_json_structure(self):
        """测试复杂 JSON 结构的配置"""
        # 添加复杂结构的配置
        complex_config = {
            'preprocessing': {
                'normalization_map': {'（': '(', '）': ')'},
                'feature_split_chars': [',', ' ', ';'],
                'ignore_keywords': ['的', '和', '或']
            },
            'matching': {
                'threshold': 0.7,
                'max_results': 10,
                'weights': {
                    'brand': 3.0,
                    'model': 3.0,
                    'type': 2.5
                }
            }
        }
        
        result = self.db_loader.add_config(
            config_key='complex_config',
            config_value=complex_config,
            description='复杂配置结构'
        )
        
        # 验证添加成功
        assert result is True
        
        # 验证可以正确读取
        saved_config = self.db_loader.get_config_by_key('complex_config')
        assert saved_config is not None
        assert 'preprocessing' in saved_config
        assert 'matching' in saved_config
        assert saved_config['preprocessing']['normalization_map']['（'] == '('
        assert saved_config['matching']['threshold'] == 0.7
        assert saved_config['matching']['weights']['brand'] == 3.0
