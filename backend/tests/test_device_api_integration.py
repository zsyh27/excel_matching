"""
设备管理 API 集成测试（使用测试数据库）

验证需求: 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7
"""

import pytest
import json
import os
import sys
import tempfile

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.rule_generator import RuleGenerator
from modules.text_preprocessor import TextPreprocessor
from modules.data_loader import Device, Rule


@pytest.fixture
def test_db():
    """创建测试数据库"""
    # 创建临时数据库文件
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    db_url = f'sqlite:///{db_path}'
    
    # 初始化数据库
    db_manager = DatabaseManager(db_url)
    db_manager.create_tables()
    
    yield db_manager, db_path
    
    # 清理
    db_manager.close()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def db_loader(test_db):
    """创建数据库加载器"""
    db_manager, _ = test_db
    
    # 创建简单的配置用于预处理器
    config = {
        'text_preprocessing': {
            'feature_split_chars': [',', '，', ' '],
            'normalize_chars': {'（': '(', '）': ')'}
        },
        'global_config': {
            'default_match_threshold': 0.7
        }
    }
    
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor)
    
    loader = DatabaseLoader(db_manager, preprocessor, rule_generator)
    return loader


@pytest.fixture
def sample_device():
    """创建示例设备"""
    return Device(
        device_id='TEST_DEVICE_001',
        brand='测试品牌',
        device_name='测试温度传感器',
        spec_model='TEST-MODEL-001',
        detailed_params='测试参数：温度范围 0-100℃，精度 ±0.5℃',
        unit_price=999.99
    )


class TestDeviceAPIIntegration:
    """设备管理 API 集成测试"""
    
    def test_full_crud_cycle(self, db_loader, sample_device):
        """
        测试完整的 CRUD 周期
        验证需求: 21.3, 21.2, 21.4, 21.5
        """
        # 1. 创建设备（带自动规则生成）
        success = db_loader.add_device(sample_device, auto_generate_rule=True)
        assert success is True
        
        # 验证设备已创建
        device = db_loader.get_device_by_id(sample_device.device_id)
        assert device is not None
        assert device.device_id == sample_device.device_id
        assert device.brand == sample_device.brand
        
        # 验证规则已自动生成
        rules = db_loader.get_rules_by_device(sample_device.device_id)
        assert len(rules) > 0
        
        # 2. 读取设备详情
        device = db_loader.get_device_by_id(sample_device.device_id)
        assert device is not None
        assert device.device_name == '测试温度传感器'
        
        # 3. 更新设备（带规则重新生成）
        updated_device = Device(
            device_id=sample_device.device_id,
            brand='新测试品牌',
            device_name='更新后的温度传感器',
            spec_model='TEST-MODEL-002',
            detailed_params='更新后的参数：温度范围 -20-150℃',
            unit_price=1299.99
        )
        
        success = db_loader.update_device(updated_device, regenerate_rule=True)
        assert success is True
        
        # 验证设备已更新
        device = db_loader.get_device_by_id(sample_device.device_id)
        assert device.brand == '新测试品牌'
        assert device.device_name == '更新后的温度传感器'
        assert device.unit_price == 1299.99
        
        # 4. 删除设备（级联删除规则）
        success, rules_deleted = db_loader.delete_device(sample_device.device_id)
        assert success is True
        assert rules_deleted > 0
        
        # 验证设备已删除
        device = db_loader.get_device_by_id(sample_device.device_id)
        assert device is None
        
        # 验证规则也已删除
        rules = db_loader.get_rules_by_device(sample_device.device_id)
        assert len(rules) == 0
    
    def test_create_device_without_auto_rule(self, db_loader):
        """
        测试创建设备但不自动生成规则
        验证需求: 21.3
        """
        device = Device(
            device_id='TEST_NO_RULE',
            brand='测试品牌',
            device_name='无规则设备',
            spec_model='NO-RULE-001',
            detailed_params='测试参数',
            unit_price=500.00
        )
        
        success = db_loader.add_device(device, auto_generate_rule=False)
        assert success is True
        
        # 验证设备已创建
        created_device = db_loader.get_device_by_id(device.device_id)
        assert created_device is not None
        
        # 验证没有生成规则
        rules = db_loader.get_rules_by_device(device.device_id)
        assert len(rules) == 0
        
        # 清理
        db_loader.delete_device(device.device_id)
    
    def test_create_duplicate_device(self, db_loader, sample_device):
        """
        测试创建重复设备
        验证需求: 21.3, 21.6, 21.7
        """
        # 第一次创建应该成功
        success = db_loader.add_device(sample_device, auto_generate_rule=False)
        assert success is True
        
        # 第二次创建相同 device_id 应该失败
        success = db_loader.add_device(sample_device, auto_generate_rule=False)
        assert success is False
        
        # 清理
        db_loader.delete_device(sample_device.device_id)
    
    def test_update_nonexistent_device(self, db_loader):
        """
        测试更新不存在的设备
        验证需求: 21.4, 21.6, 21.7
        """
        device = Device(
            device_id='NONEXISTENT',
            brand='测试',
            device_name='不存在',
            spec_model='XXX',
            detailed_params='测试',
            unit_price=100.00
        )
        
        success = db_loader.update_device(device, regenerate_rule=False)
        assert success is False
    
    def test_delete_nonexistent_device(self, db_loader):
        """
        测试删除不存在的设备
        验证需求: 21.5, 21.6, 21.7
        """
        success, rules_deleted = db_loader.delete_device('NONEXISTENT')
        assert success is False
        assert rules_deleted == 0
    
    def test_get_devices_filtering(self, db_loader):
        """
        测试设备列表过滤功能
        验证需求: 21.1
        """
        # 创建多个测试设备
        devices = [
            Device('DEV001', '霍尼韦尔', '温度传感器A', 'MODEL-A', '参数A', 500.00),
            Device('DEV002', '霍尼韦尔', '温度传感器B', 'MODEL-B', '参数B', 800.00),
            Device('DEV003', '西门子', '压力传感器', 'MODEL-C', '参数C', 1200.00),
        ]
        
        for device in devices:
            db_loader.add_device(device, auto_generate_rule=False)
        
        # 测试加载所有设备
        all_devices = db_loader.load_devices()
        assert len(all_devices) >= 3
        
        # 验证设备数据正确
        assert 'DEV001' in all_devices
        assert all_devices['DEV001'].brand == '霍尼韦尔'
        
        # 清理
        for device in devices:
            db_loader.delete_device(device.device_id)
    
    def test_cascade_delete_rules(self, db_loader, sample_device):
        """
        测试级联删除规则
        验证需求: 21.5
        """
        # 创建设备并自动生成规则
        success = db_loader.add_device(sample_device, auto_generate_rule=True)
        assert success is True
        
        # 验证规则已生成
        rules_before = db_loader.get_rules_by_device(sample_device.device_id)
        assert len(rules_before) > 0
        
        # 删除设备
        success, rules_deleted = db_loader.delete_device(sample_device.device_id)
        assert success is True
        assert rules_deleted == len(rules_before)
        
        # 验证规则已被级联删除
        rules_after = db_loader.get_rules_by_device(sample_device.device_id)
        assert len(rules_after) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
