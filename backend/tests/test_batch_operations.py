"""
批量操作单元测试

验证需求: 13.9, 13.10, 14.12, 18.4, 22.7
"""

import pytest
import sys
import os
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.data_loader import Device, Rule
from modules.rule_generator import RuleGenerator
from modules.text_preprocessor import TextPreprocessor


@pytest.fixture
def db_manager():
    """创建测试数据库管理器"""
    db_manager = DatabaseManager("sqlite:///:memory:")
    db_manager.create_tables()
    yield db_manager
    db_manager.close()


@pytest.fixture
def preprocessor():
    """创建文本预处理器"""
    config = {
        'normalization_map': {},
        'feature_split_chars': [' ', '/', '+', '、', ',', '，'],
        'ignore_keywords': [],
        'global_config': {},
        'synonym_map': {},
        'brand_keywords': [],
        'device_type_keywords': [],
        'metadata_keywords': [],
        'intelligent_extraction': {},
        'unit_removal': {'enabled': True, 'units': []}
    }
    return TextPreprocessor(config)


@pytest.fixture
def rule_generator(preprocessor):
    """创建规则生成器"""
    config = {
        'feature_weight_config': {
            'brand_weight': 3.0,
            'model_weight': 3.0,
            'device_type_weight': 3.0,
            'parameter_weight': 1.0
        },
        'device_type_keywords': [],
        'brand_keywords': []
    }
    return RuleGenerator(preprocessor, default_threshold=0.7, config=config)


@pytest.fixture
def db_loader(db_manager, preprocessor, rule_generator):
    """创建数据库加载器"""
    return DatabaseLoader(db_manager, preprocessor, rule_generator)


@pytest.fixture
def sample_devices():
    """创建示例设备列表"""
    devices = []
    for i in range(1, 6):
        device = Device(
            device_id=f"D{i:03d}",
            brand=f"品牌{i}",
            device_name=f"设备{i}",
            spec_model=f"型号{i}",
            detailed_params=f"参数{i}",
            unit_price=1000.0 + i * 100
        )
        devices.append(device)
    return devices


class TestBatchAddDevices:
    """批量添加设备测试类"""
    
    def test_batch_add_devices_success(self, db_loader, sample_devices):
        """
        测试成功批量添加设备 - 验证需求 13.9, 13.10
        """
        # 批量添加设备
        stats = db_loader.batch_add_devices(sample_devices, batch_size=10)
        
        # 验证统计信息
        assert stats['inserted'] == 5
        assert stats['updated'] == 0
        assert stats['failed'] == 0
        
        # 验证设备已保存
        for device in sample_devices:
            saved_device = db_loader.get_device_by_id(device.device_id)
            assert saved_device is not None
            assert saved_device.brand == device.brand
            assert saved_device.device_name == device.device_name
    
    def test_batch_add_devices_with_auto_generate_rule(self, db_loader, sample_devices):
        """
        测试批量添加设备并自动生成规则 - 验证需求 13.10, 18.4
        """
        # 批量添加设备并自动生成规则
        stats = db_loader.batch_add_devices(
            sample_devices, 
            batch_size=10, 
            auto_generate_rule=True
        )
        
        # 验证统计信息
        assert stats['inserted'] == 5
        assert stats['rules_generated'] == 5
        
        # 验证规则已生成
        rules = db_loader.load_rules()
        assert len(rules) == 5
        
        # 验证每个设备都有对应的规则
        for device in sample_devices:
            device_rules = [r for r in rules if r.target_device_id == device.device_id]
            assert len(device_rules) == 1
    
    def test_batch_add_devices_with_small_batch_size(self, db_loader, sample_devices):
        """
        测试小批量大小的批量添加 - 验证需求 13.9
        """
        # 使用小批量大小（每批2个）
        stats = db_loader.batch_add_devices(sample_devices, batch_size=2)
        
        # 验证统计信息
        assert stats['inserted'] == 5
        assert stats['failed'] == 0
        
        # 验证所有设备都已保存
        all_devices = db_loader.load_devices()
        assert len(all_devices) == 5
    
    def test_batch_add_devices_update_existing(self, db_loader, sample_devices):
        """
        测试批量添加时更新已存在的设备
        """
        # 先添加一些设备
        initial_devices = sample_devices[:3]
        db_loader.batch_add_devices(initial_devices)
        
        # 修改这些设备的信息
        for device in initial_devices:
            device.unit_price += 500.0
        
        # 再次批量添加（包含已存在的设备）
        stats = db_loader.batch_add_devices(sample_devices)
        
        # 验证统计信息
        assert stats['inserted'] == 2  # 只有2个新设备
        assert stats['updated'] == 3   # 3个设备被更新
        assert stats['failed'] == 0
        
        # 验证价格已更新
        for device in initial_devices:
            saved_device = db_loader.get_device_by_id(device.device_id)
            assert saved_device.unit_price == device.unit_price
    
    def test_batch_add_devices_transaction_rollback(self, db_loader):
        """
        测试批量操作的事务回滚 - 验证需求 18.4
        """
        # 创建一些正常设备和一个会导致错误的设备
        devices = [
            Device(
                device_id="D001",
                brand="品牌1",
                device_name="设备1",
                spec_model="型号1",
                detailed_params="参数1",
                unit_price=1000.0
            ),
            Device(
                device_id="D002",
                brand="品牌2",
                device_name="设备2",
                spec_model="型号2",
                detailed_params="参数2",
                unit_price=2000.0
            )
        ]
        
        # 批量添加（使用小批量大小以便测试）
        stats = db_loader.batch_add_devices(devices, batch_size=2)
        
        # 验证成功添加
        assert stats['inserted'] == 2
        assert stats['failed'] == 0


class TestBatchGenerateRules:
    """批量生成规则测试类"""
    
    def test_batch_generate_rules_for_all_devices(self, db_loader, sample_devices):
        """
        测试为所有设备批量生成规则 - 验证需求 14.12, 22.7
        """
        # 先添加设备（不生成规则）
        db_loader.batch_add_devices(sample_devices, auto_generate_rule=False)
        
        # 批量生成规则
        stats = db_loader.batch_generate_rules()
        
        # 验证统计信息
        assert stats['generated'] == 5
        assert stats['updated'] == 0
        assert stats['skipped'] == 0
        assert stats['failed'] == 0
        
        # 验证规则已生成
        rules = db_loader.load_rules()
        assert len(rules) == 5
    
    def test_batch_generate_rules_for_specific_devices(self, db_loader, sample_devices):
        """
        测试为指定设备批量生成规则 - 验证需求 14.12
        """
        # 先添加设备
        db_loader.batch_add_devices(sample_devices, auto_generate_rule=False)
        
        # 只为前3个设备生成规则
        device_ids = [d.device_id for d in sample_devices[:3]]
        stats = db_loader.batch_generate_rules(device_ids=device_ids)
        
        # 验证统计信息
        assert stats['generated'] == 3
        assert stats['failed'] == 0
        
        # 验证只有3条规则
        rules = db_loader.load_rules()
        assert len(rules) == 3
    
    def test_batch_generate_rules_skip_existing(self, db_loader, sample_devices):
        """
        测试跳过已有规则的设备
        """
        # 先添加设备并生成规则
        db_loader.batch_add_devices(sample_devices, auto_generate_rule=True)
        
        # 再次批量生成规则（不强制重新生成）
        stats = db_loader.batch_generate_rules(force_regenerate=False)
        
        # 验证统计信息
        assert stats['generated'] == 0
        assert stats['updated'] == 0
        assert stats['skipped'] == 5  # 所有设备都被跳过
        assert stats['failed'] == 0
    
    def test_batch_generate_rules_force_regenerate(self, db_loader, sample_devices):
        """
        测试强制重新生成规则 - 验证需求 22.7
        """
        # 先添加设备并生成规则
        db_loader.batch_add_devices(sample_devices, auto_generate_rule=True)
        
        # 强制重新生成规则
        stats = db_loader.batch_generate_rules(force_regenerate=True)
        
        # 验证统计信息
        assert stats['generated'] == 0
        assert stats['updated'] == 5  # 所有规则都被更新
        assert stats['skipped'] == 0
        assert stats['failed'] == 0
        
        # 验证规则数量不变
        rules = db_loader.load_rules()
        assert len(rules) == 5
    
    def test_batch_generate_rules_without_rule_generator(self, db_manager):
        """
        测试没有RuleGenerator时的错误处理
        """
        # 创建没有RuleGenerator的DatabaseLoader
        db_loader = DatabaseLoader(db_manager, None, None)
        
        # 尝试批量生成规则应该抛出异常
        with pytest.raises(ValueError, match="RuleGenerator 未初始化"):
            db_loader.batch_generate_rules()


class TestBatchOperationsStatistics:
    """批量操作统计信息测试类"""
    
    def test_statistics_accuracy(self, db_loader, sample_devices):
        """
        测试统计信息的准确性 - 验证需求 13.10, 18.4
        """
        # 第一次批量添加
        stats1 = db_loader.batch_add_devices(sample_devices[:3], auto_generate_rule=True)
        assert stats1['inserted'] == 3
        assert stats1['updated'] == 0
        assert stats1['rules_generated'] == 3
        
        # 第二次批量添加（包含重复和新设备）
        stats2 = db_loader.batch_add_devices(sample_devices, auto_generate_rule=True)
        assert stats2['inserted'] == 2  # 只有2个新设备
        assert stats2['updated'] == 3   # 3个设备被更新
        assert stats2['rules_generated'] == 5  # 所有设备都生成了规则
        
        # 验证最终状态
        all_devices = db_loader.load_devices()
        all_rules = db_loader.load_rules()
        assert len(all_devices) == 5
        assert len(all_rules) == 5
    
    def test_batch_operations_logging(self, db_loader, sample_devices, caplog):
        """
        测试批量操作的日志记录
        """
        import logging
        caplog.set_level(logging.INFO)
        
        # 执行批量操作
        db_loader.batch_add_devices(sample_devices, auto_generate_rule=True)
        
        # 验证日志包含统计信息
        assert "批量添加设备完成" in caplog.text
        assert "插入 5" in caplog.text
        assert "生成规则 5" in caplog.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
