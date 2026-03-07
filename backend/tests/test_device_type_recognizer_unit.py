"""
设备类型识别器单元测试

Feature: intelligent-feature-extraction
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.intelligent_extraction.device_type_recognizer import DeviceTypeRecognizer
from .test_intelligent_extraction_config import DEVICE_TYPE_CONFIG


class TestDeviceTypeRecognizerUnit:
    """设备类型识别器单元测试"""
    
    @pytest.fixture
    def recognizer(self):
        """创建识别器实例"""
        return DeviceTypeRecognizer(DEVICE_TYPE_CONFIG)
    
    def test_exact_match(self, recognizer):
        """
        测试精确匹配
        验证需求：2.1.1, 2.1.2
        """
        text = "CO浓度探测器"
        result = recognizer.recognize(text)
        
        assert result.sub_type == "CO浓度探测器"
        assert result.confidence >= 0.95
        assert result.mode == 'exact'
    
    def test_fuzzy_match(self, recognizer):
        """
        测试模糊匹配
        验证需求：2.1.1, 2.1.2
        """
        text = "CO探测器"
        result = recognizer.recognize(text)
        
        assert "探测器" in result.main_type or "探测器" in result.sub_type
        assert 0.85 <= result.confidence < 0.95
    
    def test_keyword_match(self, recognizer):
        """
        测试关键词匹配
        验证需求：2.1.1, 2.1.2
        """
        text = "CO 浓度 探测器"
        result = recognizer.recognize(text)
        
        assert "探测器" in result.main_type or "探测器" in result.sub_type
        assert 0.75 <= result.confidence < 0.85
    
    def test_empty_input(self, recognizer):
        """
        测试空输入边缘情况
        验证需求：2.1.1, 2.1.2
        """
        text = ""
        result = recognizer.recognize(text)
        
        assert result.main_type == "未知"
        assert result.sub_type == "未知"
        assert result.confidence == 0.0
    
    def test_temperature_sensor(self, recognizer):
        """测试温度传感器识别"""
        text = "温度传感器"
        result = recognizer.recognize(text)
        
        assert result.sub_type == "温度传感器"
        assert result.main_type == "传感器"
        assert result.confidence >= 0.95
    
    def test_temperature_humidity_sensor(self, recognizer):
        """测试温湿度传感器识别"""
        text = "温湿度传感器"
        result = recognizer.recognize(text)
        
        assert result.sub_type == "温湿度传感器"
        assert result.main_type == "传感器"
        assert result.confidence >= 0.95
