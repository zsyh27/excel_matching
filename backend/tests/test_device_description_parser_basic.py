# -*- coding: utf-8 -*-
"""
设备描述解析器基础测试

验证 DeviceDescriptionParser 类和数据模型的基本结构
"""

import pytest
from modules.intelligent_device import (
    DeviceDescriptionParser,
    ParseResult,
    ConfigurationManager,
    ParamRule
)


class TestParseResultDataModel:
    """测试 ParseResult 数据模型"""
    
    def test_parse_result_initialization_with_defaults(self):
        """测试 ParseResult 使用默认值初始化"""
        result = ParseResult()
        
        assert result.brand is None
        assert result.device_type is None
        assert result.model is None
        assert result.key_params == {}
        assert result.confidence_score == 0.0
        assert result.unrecognized_text == []
        assert result.raw_description == ""
    
    def test_parse_result_initialization_with_values(self):
        """测试 ParseResult 使用指定值初始化"""
        result = ParseResult(
            brand="西门子",
            device_type="CO2传感器",
            model="QAA2061",
            key_params={"量程": "0-2000ppm", "输出信号": "4-20mA"},
            confidence_score=0.92,
            unrecognized_text=["未知文本"],
            raw_description="西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA"
        )
        
        assert result.brand == "西门子"
        assert result.device_type == "CO2传感器"
        assert result.model == "QAA2061"
        assert result.key_params == {"量程": "0-2000ppm", "输出信号": "4-20mA"}
        assert result.confidence_score == 0.92
        assert result.unrecognized_text == ["未知文本"]
        assert result.raw_description == "西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA"
    
    def test_parse_result_mutable_defaults(self):
        """测试 ParseResult 的可变默认值不会在实例间共享"""
        result1 = ParseResult()
        result2 = ParseResult()
        
        result1.key_params["test"] = "value"
        result1.unrecognized_text.append("text")
        
        # 验证 result2 不受影响
        assert "test" not in result2.key_params
        assert len(result2.unrecognized_text) == 0


class TestParamRuleDataModel:
    """测试 ParamRule 数据模型"""
    
    def test_param_rule_initialization(self):
        """测试 ParamRule 初始化"""
        rule = ParamRule(
            param_name="量程",
            pattern=r"量程[:：]?\s*([0-9]+-[0-9]+\s*ppm)",
            required=True,
            data_type="range",
            unit="ppm"
        )
        
        assert rule.param_name == "量程"
        assert rule.pattern == r"量程[:：]?\s*([0-9]+-[0-9]+\s*ppm)"
        assert rule.required is True
        assert rule.data_type == "range"
        assert rule.unit == "ppm"
    
    def test_param_rule_optional_unit(self):
        """测试 ParamRule 可选的 unit 字段"""
        rule = ParamRule(
            param_name="型号",
            pattern=r"[A-Z]+[0-9]+",
            required=False,
            data_type="string"
        )
        
        assert rule.unit is None


class TestDeviceDescriptionParserInitialization:
    """测试 DeviceDescriptionParser 初始化"""
    
    def test_parser_initialization(self, tmp_path):
        """测试解析器初始化"""
        # 创建临时配置文件
        config_file = tmp_path / "device_params.yaml"
        config_file.write_text("""
brands:
  西门子:
    keywords: ["西门子", "SIEMENS"]

device_types:
  CO2传感器:
    keywords: ["CO2传感器"]
    params: []
""", encoding='utf-8')
        
        config_manager = ConfigurationManager(str(config_file))
        parser = DeviceDescriptionParser(config_manager)
        
        assert parser.config_manager is config_manager
    
    def test_parser_has_required_methods(self, tmp_path):
        """测试解析器具有所有必需的方法"""
        config_file = tmp_path / "device_params.yaml"
        config_file.write_text("brands: {}\ndevice_types: {}", encoding='utf-8')
        
        config_manager = ConfigurationManager(str(config_file))
        parser = DeviceDescriptionParser(config_manager)
        
        # 验证所有必需的方法存在
        assert hasattr(parser, 'parse')
        assert hasattr(parser, 'extract_brand')
        assert hasattr(parser, 'extract_device_type')
        assert hasattr(parser, 'extract_model')
        assert hasattr(parser, 'extract_key_params')
        assert hasattr(parser, 'calculate_confidence')
        
        # 验证方法可调用
        assert callable(parser.parse)
        assert callable(parser.extract_brand)
        assert callable(parser.extract_device_type)
        assert callable(parser.extract_model)
        assert callable(parser.extract_key_params)
        assert callable(parser.calculate_confidence)


class TestDeviceDescriptionParserBasicParse:
    """测试 DeviceDescriptionParser 基本解析功能"""
    
    def test_parse_returns_parse_result(self, tmp_path):
        """测试 parse 方法返回 ParseResult 对象"""
        config_file = tmp_path / "device_params.yaml"
        config_file.write_text("brands: {}\ndevice_types: {}", encoding='utf-8')
        
        config_manager = ConfigurationManager(str(config_file))
        parser = DeviceDescriptionParser(config_manager)
        
        result = parser.parse("测试设备描述")
        
        assert isinstance(result, ParseResult)
    
    def test_parse_preserves_raw_description(self, tmp_path):
        """测试 parse 方法保留原始描述文本"""
        config_file = tmp_path / "device_params.yaml"
        config_file.write_text("brands: {}\ndevice_types: {}", encoding='utf-8')
        
        config_manager = ConfigurationManager(str(config_file))
        parser = DeviceDescriptionParser(config_manager)
        
        description = "西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA"
        result = parser.parse(description)
        
        assert result.raw_description == description


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
