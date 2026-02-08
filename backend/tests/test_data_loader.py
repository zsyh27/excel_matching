"""
数据加载模块测试
"""

import pytest
import json
import os
import sys
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_loader import (
    DataLoader, ConfigManager, Device, Rule, DataIntegrityError
)
from modules.text_preprocessor import TextPreprocessor


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_devices():
    """示例设备数据"""
    return [
        {
            "device_id": "TEST001",
            "brand": "测试品牌",
            "device_name": "测试传感器",
            "spec_model": "TEST-001",
            "detailed_params": "0-100PPM,4-20mA",
            "unit_price": 100.50
        },
        {
            "device_id": "TEST002",
            "brand": "另一品牌",
            "device_name": "温度传感器",
            "spec_model": "TEMP-001",
            "detailed_params": "0-50摄氏度,壁挂式",
            "unit_price": 200.00
        }
    ]


@pytest.fixture
def sample_rules():
    """示例规则数据"""
    return [
        {
            "rule_id": "R001",
            "target_device_id": "TEST001",
            "auto_extracted_features": ["测试品牌", "测试传感器", "TEST-001", "0-100ppm", "4-20ma"],
            "feature_weights": {"测试品牌": 3, "TEST-001": 3, "0-100ppm": 2},
            "match_threshold": 3,
            "remark": "测试规则"
        }
    ]


@pytest.fixture
def sample_config():
    """示例配置数据"""
    return {
        "normalization_map": {
            "~": "-",
            "PPM": "ppm"
        },
        "feature_split_chars": [",", ";"],
        "ignore_keywords": ["测试"],
        "global_config": {
            "default_match_threshold": 2,
            "unify_lowercase": True
        }
    }


@pytest.fixture
def data_files(temp_dir, sample_devices, sample_rules, sample_config):
    """创建测试数据文件"""
    device_file = os.path.join(temp_dir, "devices.json")
    rule_file = os.path.join(temp_dir, "rules.json")
    config_file = os.path.join(temp_dir, "config.json")
    
    with open(device_file, 'w', encoding='utf-8') as f:
        json.dump(sample_devices, f, ensure_ascii=False, indent=2)
    
    with open(rule_file, 'w', encoding='utf-8') as f:
        json.dump(sample_rules, f, ensure_ascii=False, indent=2)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, ensure_ascii=False, indent=2)
    
    return device_file, rule_file, config_file


class TestDevice:
    """测试 Device 数据模型"""
    
    def test_from_dict(self):
        """测试从字典创建设备"""
        data = {
            "device_id": "TEST001",
            "brand": "测试品牌",
            "device_name": "测试设备",
            "spec_model": "TEST-001",
            "detailed_params": "参数1,参数2",
            "unit_price": 100.50
        }
        device = Device.from_dict(data)
        assert device.device_id == "TEST001"
        assert device.brand == "测试品牌"
        assert device.unit_price == 100.50
    
    def test_to_dict(self):
        """测试转换为字典"""
        device = Device(
            device_id="TEST001",
            brand="测试品牌",
            device_name="测试设备",
            spec_model="TEST-001",
            detailed_params="参数1,参数2",
            unit_price=100.50
        )
        data = device.to_dict()
        assert data['device_id'] == "TEST001"
        assert data['unit_price'] == 100.50
    
    def test_get_display_text(self):
        """测试获取显示文本"""
        device = Device(
            device_id="TEST001",
            brand="测试品牌",
            device_name="测试设备",
            spec_model="TEST-001",
            detailed_params="参数1,参数2",
            unit_price=100.50
        )
        display_text = device.get_display_text()
        assert "测试品牌" in display_text
        assert "测试设备" in display_text
        assert "TEST-001" in display_text
        assert "参数1,参数2" in display_text


class TestRule:
    """测试 Rule 数据模型"""
    
    def test_from_dict(self):
        """测试从字典创建规则"""
        data = {
            "rule_id": "R001",
            "target_device_id": "TEST001",
            "auto_extracted_features": ["特征1", "特征2"],
            "feature_weights": {"特征1": 3, "特征2": 2},
            "match_threshold": 3,
            "remark": "测试规则"
        }
        rule = Rule.from_dict(data)
        assert rule.rule_id == "R001"
        assert rule.target_device_id == "TEST001"
        assert len(rule.auto_extracted_features) == 2
    
    def test_to_dict(self):
        """测试转换为字典"""
        rule = Rule(
            rule_id="R001",
            target_device_id="TEST001",
            auto_extracted_features=["特征1", "特征2"],
            feature_weights={"特征1": 3},
            match_threshold=3,
            remark="测试"
        )
        data = rule.to_dict()
        assert data['rule_id'] == "R001"
        assert data['match_threshold'] == 3


class TestConfigManager:
    """测试 ConfigManager"""
    
    def test_load_config(self, data_files):
        """测试加载配置"""
        _, _, config_file = data_files
        manager = ConfigManager(config_file)
        config = manager.get_config()
        assert 'normalization_map' in config
        assert 'global_config' in config
    
    def test_config_hot_reload(self, data_files, sample_config):
        """测试配置热加载"""
        _, _, config_file = data_files
        manager = ConfigManager(config_file)
        
        # 第一次获取配置
        config1 = manager.get_config()
        assert config1['global_config']['default_match_threshold'] == 2
        
        # 修改配置文件
        sample_config['global_config']['default_match_threshold'] = 5
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, ensure_ascii=False, indent=2)
        
        # 再次获取配置，应该自动重新加载
        config2 = manager.get_config()
        assert config2['global_config']['default_match_threshold'] == 5
    
    def test_update_config(self, data_files):
        """测试更新配置"""
        _, _, config_file = data_files
        manager = ConfigManager(config_file)
        
        # 更新配置
        updates = {
            'global_config': {
                'default_match_threshold': 10
            }
        }
        success = manager.update_config(updates)
        assert success
        
        # 验证更新
        config = manager.get_config()
        assert config['global_config']['default_match_threshold'] == 10


class TestDataLoader:
    """测试 DataLoader"""
    
    def test_load_devices(self, data_files):
        """测试加载设备表"""
        device_file, rule_file, config_file = data_files
        loader = DataLoader(device_file, rule_file, config_file)
        
        devices = loader.load_devices()
        assert len(devices) == 2
        assert "TEST001" in devices
        assert devices["TEST001"].brand == "测试品牌"
    
    def test_load_rules(self, data_files):
        """测试加载规则表"""
        device_file, rule_file, config_file = data_files
        loader = DataLoader(device_file, rule_file, config_file)
        
        rules = loader.load_rules()
        assert len(rules) == 1
        assert rules[0].rule_id == "R001"
    
    def test_load_config(self, data_files):
        """测试加载配置"""
        device_file, rule_file, config_file = data_files
        loader = DataLoader(device_file, rule_file, config_file)
        
        config = loader.load_config()
        assert 'normalization_map' in config
    
    def test_validate_data_integrity_success(self, data_files):
        """测试数据完整性验证 - 成功"""
        device_file, rule_file, config_file = data_files
        loader = DataLoader(device_file, rule_file, config_file)
        
        # 应该验证通过
        assert loader.validate_data_integrity() == True
    
    def test_validate_data_integrity_missing_device(self, data_files, sample_rules):
        """测试数据完整性验证 - 设备不存在"""
        device_file, rule_file, config_file = data_files
        
        # 添加一个指向不存在设备的规则
        sample_rules.append({
            "rule_id": "R999",
            "target_device_id": "NONEXISTENT",
            "auto_extracted_features": ["test"],
            "feature_weights": {"test": 1},
            "match_threshold": 1,
            "remark": "无效规则"
        })
        
        with open(rule_file, 'w', encoding='utf-8') as f:
            json.dump(sample_rules, f, ensure_ascii=False, indent=2)
        
        loader = DataLoader(device_file, rule_file, config_file)
        
        # 应该抛出异常
        with pytest.raises(DataIntegrityError) as exc_info:
            loader.validate_data_integrity()
        assert "NONEXISTENT" in str(exc_info.value)
    
    def test_validate_data_integrity_empty_features(self, data_files, sample_rules):
        """测试数据完整性验证 - 特征为空"""
        device_file, rule_file, config_file = data_files
        
        # 修改规则，使特征为空
        sample_rules[0]['auto_extracted_features'] = []
        
        with open(rule_file, 'w', encoding='utf-8') as f:
            json.dump(sample_rules, f, ensure_ascii=False, indent=2)
        
        loader = DataLoader(device_file, rule_file, config_file)
        
        # 应该抛出异常
        with pytest.raises(DataIntegrityError) as exc_info:
            loader.validate_data_integrity()
        assert "auto_extracted_features" in str(exc_info.value)
    
    def test_auto_generate_features(self, data_files):
        """测试自动生成特征"""
        device_file, rule_file, config_file = data_files
        
        # 创建预处理器
        config = json.load(open(config_file, 'r', encoding='utf-8'))
        preprocessor = TextPreprocessor(config)
        
        loader = DataLoader(device_file, rule_file, config_file, preprocessor)
        
        # 创建测试设备
        device = Device(
            device_id="TEST003",
            brand="测试品牌",
            device_name="CO传感器",
            spec_model="TEST-003",
            detailed_params="0~100PPM,4-20mA",
            unit_price=100.0
        )
        
        # 生成特征
        features = loader.auto_generate_features(device)
        
        # 验证特征包含品牌、设备名称、规格型号
        assert "测试品牌" in features
        assert "CO传感器" in features
        assert "TEST-003" in features
        
        # 验证详细参数被拆分
        assert len(features) > 3  # 应该包含拆分后的参数
    
    def test_auto_sync_rules_with_devices(self, data_files, sample_devices):
        """测试自动同步规则表与设备表"""
        device_file, rule_file, config_file = data_files
        
        # 创建预处理器
        config = json.load(open(config_file, 'r', encoding='utf-8'))
        preprocessor = TextPreprocessor(config)
        
        loader = DataLoader(device_file, rule_file, config_file, preprocessor)
        
        # 同步规则（TEST002 没有规则）
        result = loader.auto_sync_rules_with_devices()
        assert result == True
        
        # 验证新规则已生成
        rules = loader.get_all_rules()
        assert len(rules) == 2
        
        # 验证新规则的 target_device_id
        device_ids = [rule.target_device_id for rule in rules]
        assert "TEST002" in device_ids
    
    def test_get_device_by_id(self, data_files):
        """测试根据 ID 获取设备"""
        device_file, rule_file, config_file = data_files
        loader = DataLoader(device_file, rule_file, config_file)
        
        device = loader.get_device_by_id("TEST001")
        assert device is not None
        assert device.device_id == "TEST001"
        
        # 测试不存在的设备
        device = loader.get_device_by_id("NONEXISTENT")
        assert device is None
    
    def test_get_all_devices(self, data_files):
        """测试获取所有设备"""
        device_file, rule_file, config_file = data_files
        loader = DataLoader(device_file, rule_file, config_file)
        
        devices = loader.get_all_devices()
        assert len(devices) == 2
        assert "TEST001" in devices
        assert "TEST002" in devices
    
    def test_get_all_rules(self, data_files):
        """测试获取所有规则"""
        device_file, rule_file, config_file = data_files
        loader = DataLoader(device_file, rule_file, config_file)
        
        rules = loader.get_all_rules()
        assert len(rules) == 1
        assert rules[0].rule_id == "R001"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
