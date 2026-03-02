# -*- coding: utf-8 -*-
"""
配置管理器单元测试
"""

import pytest
import os
import tempfile
import yaml
from modules.intelligent_device.configuration_manager import ConfigurationManager, ParamRule


class TestConfigurationManager:
    """配置管理器测试类"""
    
    @pytest.fixture
    def sample_config(self):
        """创建示例配置数据"""
        return {
            'brands': {
                '西门子': {
                    'keywords': ['西门子', 'SIEMENS', 'siemens']
                },
                '霍尼韦尔': {
                    'keywords': ['霍尼韦尔', 'HONEYWELL', 'honeywell']
                }
            },
            'device_types': {
                'CO2传感器': {
                    'keywords': ['CO2传感器', '二氧化碳传感器'],
                    'params': [
                        {
                            'name': '量程',
                            'pattern': r'量程[:：]?\s*([0-9]+-[0-9]+\s*ppm)',
                            'required': True,
                            'data_type': 'range',
                            'unit': 'ppm'
                        },
                        {
                            'name': '输出信号',
                            'pattern': r'输出[:：]?\s*([0-9]+-[0-9]+\s*[mM][aA])',
                            'required': True,
                            'data_type': 'string',
                            'unit': 'mA'
                        }
                    ]
                },
                '座阀': {
                    'keywords': ['座阀', '调节阀'],
                    'params': [
                        {
                            'name': '通径',
                            'pattern': r'DN\s*([0-9]+)',
                            'required': True,
                            'data_type': 'number',
                            'unit': 'mm'
                        }
                    ]
                }
            }
        }
    
    @pytest.fixture
    def temp_config_file(self, sample_config):
        """创建临时配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(sample_config, f, allow_unicode=True)
            temp_path = f.name
        
        yield temp_path
        
        # 清理临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def config_manager(self, temp_config_file):
        """创建配置管理器实例"""
        return ConfigurationManager(temp_config_file)
    
    def test_init_loads_config(self, temp_config_file):
        """测试初始化时加载配置文件"""
        manager = ConfigurationManager(temp_config_file)
        assert manager._config is not None
        assert 'brands' in manager._config
        assert 'device_types' in manager._config
    
    def test_init_with_nonexistent_file(self):
        """测试使用不存在的配置文件初始化"""
        with pytest.raises(FileNotFoundError):
            ConfigurationManager('/nonexistent/path/config.yaml')
    
    def test_init_with_invalid_yaml(self):
        """测试使用无效的YAML文件初始化"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            f.write("invalid: yaml: content: [")
            temp_path = f.name
        
        try:
            with pytest.raises(yaml.YAMLError):
                ConfigurationManager(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_get_brand_keywords(self, config_manager):
        """测试获取品牌关键词映射"""
        brand_keywords = config_manager.get_brand_keywords()
        
        assert isinstance(brand_keywords, dict)
        assert '西门子' in brand_keywords
        assert '霍尼韦尔' in brand_keywords
        assert brand_keywords['西门子'] == ['西门子', 'SIEMENS', 'siemens']
        assert brand_keywords['霍尼韦尔'] == ['霍尼韦尔', 'HONEYWELL', 'honeywell']
    
    def test_get_brand_keywords_empty_config(self):
        """测试空配置时获取品牌关键词"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump({}, f)
            temp_path = f.name
        
        try:
            manager = ConfigurationManager(temp_path)
            brand_keywords = manager.get_brand_keywords()
            assert brand_keywords == {}
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_get_device_type_keywords(self, config_manager):
        """测试获取设备类型关键词映射"""
        device_type_keywords = config_manager.get_device_type_keywords()
        
        assert isinstance(device_type_keywords, dict)
        assert 'CO2传感器' in device_type_keywords
        assert '座阀' in device_type_keywords
        assert device_type_keywords['CO2传感器'] == ['CO2传感器', '二氧化碳传感器']
        assert device_type_keywords['座阀'] == ['座阀', '调节阀']
    
    def test_get_device_type_keywords_empty_config(self):
        """测试空配置时获取设备类型关键词"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump({}, f)
            temp_path = f.name
        
        try:
            manager = ConfigurationManager(temp_path)
            device_type_keywords = manager.get_device_type_keywords()
            assert device_type_keywords == {}
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_get_param_rules_co2_sensor(self, config_manager):
        """测试获取CO2传感器的参数规则"""
        param_rules = config_manager.get_param_rules('CO2传感器')
        
        assert isinstance(param_rules, list)
        assert len(param_rules) == 2
        
        # 检查第一个参数规则（量程）
        rule1 = param_rules[0]
        assert isinstance(rule1, ParamRule)
        assert rule1.param_name == '量程'
        assert rule1.pattern == r'量程[:：]?\s*([0-9]+-[0-9]+\s*ppm)'
        assert rule1.required is True
        assert rule1.data_type == 'range'
        assert rule1.unit == 'ppm'
        
        # 检查第二个参数规则（输出信号）
        rule2 = param_rules[1]
        assert isinstance(rule2, ParamRule)
        assert rule2.param_name == '输出信号'
        assert rule2.pattern == r'输出[:：]?\s*([0-9]+-[0-9]+\s*[mM][aA])'
        assert rule2.required is True
        assert rule2.data_type == 'string'
        assert rule2.unit == 'mA'
    
    def test_get_param_rules_valve(self, config_manager):
        """测试获取座阀的参数规则"""
        param_rules = config_manager.get_param_rules('座阀')
        
        assert isinstance(param_rules, list)
        assert len(param_rules) == 1
        
        rule = param_rules[0]
        assert isinstance(rule, ParamRule)
        assert rule.param_name == '通径'
        assert rule.pattern == r'DN\s*([0-9]+)'
        assert rule.required is True
        assert rule.data_type == 'number'
        assert rule.unit == 'mm'
    
    def test_get_param_rules_nonexistent_device_type(self, config_manager):
        """测试获取不存在的设备类型的参数规则"""
        param_rules = config_manager.get_param_rules('不存在的设备类型')
        
        assert isinstance(param_rules, list)
        assert len(param_rules) == 0
    
    def test_get_param_rules_device_type_without_params(self):
        """测试获取没有参数配置的设备类型的规则"""
        config = {
            'device_types': {
                '无参数设备': {
                    'keywords': ['无参数设备']
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)
            temp_path = f.name
        
        try:
            manager = ConfigurationManager(temp_path)
            param_rules = manager.get_param_rules('无参数设备')
            assert param_rules == []
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_reload_config(self, temp_config_file, sample_config):
        """测试配置重载功能"""
        manager = ConfigurationManager(temp_config_file)
        
        # 获取初始品牌数量
        initial_brands = manager.get_brand_keywords()
        assert len(initial_brands) == 2
        
        # 修改配置文件，添加新品牌
        sample_config['brands']['施耐德'] = {
            'keywords': ['施耐德', 'SCHNEIDER']
        }
        
        with open(temp_config_file, 'w', encoding='utf-8') as f:
            yaml.dump(sample_config, f, allow_unicode=True)
        
        # 重新加载配置
        manager.reload()
        
        # 验证新配置已加载
        updated_brands = manager.get_brand_keywords()
        assert len(updated_brands) == 3
        assert '施耐德' in updated_brands
        assert updated_brands['施耐德'] == ['施耐德', 'SCHNEIDER']
    
    def test_reload_config_with_invalid_file(self, temp_config_file):
        """测试重载无效配置文件"""
        manager = ConfigurationManager(temp_config_file)
        
        # 写入无效的YAML内容
        with open(temp_config_file, 'w', encoding='utf-8') as f:
            f.write("invalid: yaml: [")
        
        # 重载应该抛出异常
        with pytest.raises(yaml.YAMLError):
            manager.reload()
    
    def test_param_rule_with_optional_unit(self):
        """测试没有单位的参数规则"""
        config = {
            'device_types': {
                '测试设备': {
                    'keywords': ['测试设备'],
                    'params': [
                        {
                            'name': '无单位参数',
                            'pattern': r'test',
                            'required': False,
                            'data_type': 'string'
                        }
                    ]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)
            temp_path = f.name
        
        try:
            manager = ConfigurationManager(temp_path)
            param_rules = manager.get_param_rules('测试设备')
            
            assert len(param_rules) == 1
            assert param_rules[0].unit is None
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_real_config_file_loads_successfully(self):
        """测试实际配置文件能够成功加载"""
        config_path = 'backend/config/device_params.yaml'
        
        # 如果实际配置文件存在，测试加载
        if os.path.exists(config_path):
            manager = ConfigurationManager(config_path)
            
            # 验证基本结构
            brand_keywords = manager.get_brand_keywords()
            assert len(brand_keywords) > 0
            
            device_type_keywords = manager.get_device_type_keywords()
            assert len(device_type_keywords) > 0
            
            # 验证至少有一个设备类型有参数规则
            has_params = False
            for device_type in device_type_keywords.keys():
                param_rules = manager.get_param_rules(device_type)
                if len(param_rules) > 0:
                    has_params = True
                    break
            
            assert has_params, "至少应该有一个设备类型配置了参数规则"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
