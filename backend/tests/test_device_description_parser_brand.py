# -*- coding: utf-8 -*-
"""
设备描述解析器品牌识别测试

验证 DeviceDescriptionParser 的品牌识别功能
"""

import pytest
from modules.intelligent_device import (
    DeviceDescriptionParser,
    ConfigurationManager
)


@pytest.fixture
def parser(tmp_path):
    """创建带有品牌配置的解析器实例"""
    config_file = tmp_path / "device_params.yaml"
    config_file.write_text("""
brands:
  西门子:
    keywords: ["西门子", "SIEMENS", "siemens", "Siemens"]
  霍尼韦尔:
    keywords: ["霍尼韦尔", "HONEYWELL", "honeywell", "Honeywell"]
  施耐德:
    keywords: ["施耐德", "SCHNEIDER", "schneider", "Schneider"]
  江森自控:
    keywords: ["江森自控", "江森", "JOHNSON", "johnson", "Johnson"]

device_types: {}
""", encoding='utf-8')
    
    config_manager = ConfigurationManager(str(config_file))
    return DeviceDescriptionParser(config_manager)


class TestBrandRecognition:
    """测试品牌识别功能"""
    
    def test_extract_brand_chinese_keyword(self, parser):
        """测试识别中文品牌关键词"""
        text = "西门子 CO2传感器 QAA2061"
        brand = parser.extract_brand(text)
        assert brand == "西门子"
    
    def test_extract_brand_english_uppercase(self, parser):
        """测试识别英文大写品牌关键词"""
        text = "SIEMENS CO2 sensor QAA2061"
        brand = parser.extract_brand(text)
        assert brand == "西门子"
    
    def test_extract_brand_english_lowercase(self, parser):
        """测试识别英文小写品牌关键词"""
        text = "siemens co2 sensor qaa2061"
        brand = parser.extract_brand(text)
        assert brand == "西门子"
    
    def test_extract_brand_mixed_case(self, parser):
        """测试识别混合大小写品牌关键词"""
        text = "Siemens CO2 Sensor QAA2061"
        brand = parser.extract_brand(text)
        assert brand == "西门子"
    
    def test_extract_brand_with_spaces(self, parser):
        """测试品牌关键词周围有空格的情况"""
        text = "  西门子  CO2传感器  "
        brand = parser.extract_brand(text)
        assert brand == "西门子"
    
    def test_extract_brand_multiple_brands_first_wins(self, parser):
        """测试多个品牌关键词时选择首次出现的"""
        text = "西门子 CO2传感器 霍尼韦尔 温度传感器"
        brand = parser.extract_brand(text)
        assert brand == "西门子"
    
    def test_extract_brand_multiple_brands_order_matters(self, parser):
        """测试多个品牌关键词时顺序影响选择"""
        text = "霍尼韦尔 温度传感器 西门子 CO2传感器"
        brand = parser.extract_brand(text)
        assert brand == "霍尼韦尔"
    
    def test_extract_brand_no_brand_returns_none(self, parser):
        """测试无品牌关键词时返回 None"""
        text = "CO2传感器 QAA2061 量程0-2000ppm"
        brand = parser.extract_brand(text)
        assert brand is None
    
    def test_extract_brand_empty_text_returns_none(self, parser):
        """测试空文本返回 None"""
        brand = parser.extract_brand("")
        assert brand is None
    
    def test_extract_brand_none_text_returns_none(self, parser):
        """测试 None 文本返回 None"""
        brand = parser.extract_brand(None)
        assert brand is None
    
    def test_extract_brand_alias_support(self, parser):
        """测试品牌别名支持"""
        # 江森自控有别名"江森"
        text = "江森 温度传感器 T5100"
        brand = parser.extract_brand(text)
        assert brand == "江森自控"
    
    def test_extract_brand_in_middle_of_text(self, parser):
        """测试品牌关键词在文本中间"""
        text = "量程0-2000ppm 西门子 CO2传感器 输出4-20mA"
        brand = parser.extract_brand(text)
        assert brand == "西门子"
    
    def test_extract_brand_at_end_of_text(self, parser):
        """测试品牌关键词在文本末尾"""
        text = "CO2传感器 QAA2061 量程0-2000ppm 西门子"
        brand = parser.extract_brand(text)
        assert brand == "西门子"
    
    def test_extract_brand_case_insensitive_matching(self, parser):
        """测试不区分大小写的匹配"""
        # 测试各种大小写组合
        test_cases = [
            "HONEYWELL sensor",
            "honeywell sensor",
            "Honeywell sensor",
            "HoNeYwElL sensor"
        ]
        for text in test_cases:
            brand = parser.extract_brand(text)
            assert brand == "霍尼韦尔", f"Failed for text: {text}"


class TestBrandRecognitionEdgeCases:
    """测试品牌识别边界情况"""
    
    def test_extract_brand_with_special_characters(self, parser):
        """测试包含特殊字符的文本"""
        text = "西门子（SIEMENS）CO2传感器"
        brand = parser.extract_brand(text)
        assert brand == "西门子"
    
    def test_extract_brand_with_numbers(self, parser):
        """测试包含数字的文本"""
        text = "西门子123 CO2传感器456"
        brand = parser.extract_brand(text)
        assert brand == "西门子"
    
    def test_extract_brand_very_long_text(self, parser):
        """测试很长的文本"""
        text = "这是一段很长的设备描述文本，" * 10 + "西门子 CO2传感器"
        brand = parser.extract_brand(text)
        assert brand == "西门子"
    
    def test_extract_brand_with_newlines(self, parser):
        """测试包含换行符的文本"""
        text = "西门子\nCO2传感器\nQAA2061"
        brand = parser.extract_brand(text)
        assert brand == "西门子"
    
    def test_extract_brand_with_tabs(self, parser):
        """测试包含制表符的文本"""
        text = "西门子\tCO2传感器\tQAA2061"
        brand = parser.extract_brand(text)
        assert brand == "西门子"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
