"""
参数提取器单元测试

Feature: intelligent-feature-extraction
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.intelligent_extraction.parameter_extractor import ParameterExtractor
from .test_intelligent_extraction_config import PARAMETER_CONFIG


class TestParameterExtractorUnit:
    """参数提取器单元测试"""
    
    @pytest.fixture
    def extractor(self):
        """创建提取器实例"""
        return ParameterExtractor(PARAMETER_CONFIG)
    
    def test_range_extraction_with_label(self, extractor):
        """
        测试带标签的量程提取
        验证需求：2.2.1, 3.2.1
        """
        text = "量程0~250ppm"
        result = extractor._extract_range(text)
        
        assert result is not None
        assert result.value == "0~250ppm"
        assert result.normalized['min'] == 0
        assert result.normalized['max'] == 250
        assert result.normalized['unit'] == "ppm"
        assert result.confidence >= 0.95
    
    def test_range_extraction_without_label(self, extractor):
        """
        测试无标签的量程提取
        验证需求：2.2.1, 3.2.1
        """
        text = "0~250ppm"
        result = extractor._extract_range(text)
        
        assert result is not None
        assert "0~250ppm" in result.value
        assert result.normalized['min'] == 0
        assert result.normalized['max'] == 250
        assert result.normalized['unit'] == "ppm"
        assert 0.75 <= result.confidence < 0.95
    
    def test_output_extraction(self, extractor):
        """
        测试输出信号提取
        验证需求：2.2.1, 3.2.2
        """
        text = "输出4~20mA"
        result = extractor._extract_output(text)
        
        assert result is not None
        assert "4~20mA" in result.value or "4-20mA" in result.value
        assert result.normalized['min'] == 4
        assert result.normalized['max'] == 20
        assert result.normalized['unit'] == "mA"
        assert result.normalized['type'] == 'analog'
        assert result.confidence >= 0.80
    
    def test_accuracy_extraction(self, extractor):
        """
        测试精度提取
        验证需求：2.2.1, 3.2.3
        """
        text = "精度±5%"
        result = extractor._extract_accuracy(text)
        
        assert result is not None
        assert "±5%" in result.value
        assert result.normalized['value'] == 5
        assert result.normalized['unit'] == "%"
        assert result.confidence >= 0.80
    
    def test_specs_extraction(self, extractor):
        """
        测试规格提取
        验证需求：2.2.1, 3.2.4
        """
        text = "DN50 PN16"
        result = extractor._extract_specs(text)
        
        assert result is not None
        assert len(result) == 2
        assert "DN50" in result
        assert "PN16" in result
    
    def test_temperature_range(self, extractor):
        """测试温度量程提取"""
        text = "量程-40~80℃"
        result = extractor._extract_range(text)
        
        assert result is not None
        assert result.normalized['min'] == -40
        assert result.normalized['max'] == 80
        assert result.normalized['unit'] == "℃"
    
    def test_digital_output(self, extractor):
        """测试数字信号提取"""
        text = "输出RS485"
        result = extractor._extract_output(text)
        
        assert result is not None
        assert result.normalized['protocol'] == "RS485"
        assert result.normalized['type'] == 'digital'
    
    def test_complete_extraction(self, extractor):
        """测试完整参数提取"""
        text = "CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%"
        result = extractor.extract(text)
        
        # 验证量程
        assert result.range is not None
        assert result.range.normalized['min'] == 0
        assert result.range.normalized['max'] == 250
        
        # 验证输出
        assert result.output is not None
        assert result.output.normalized['min'] == 4
        assert result.output.normalized['max'] == 20
        
        # 验证精度
        assert result.accuracy is not None
        assert result.accuracy.normalized['value'] == 5
