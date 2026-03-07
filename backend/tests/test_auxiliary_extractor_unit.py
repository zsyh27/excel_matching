"""
辅助信息提取器单元测试
Feature: intelligent-feature-extraction
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.intelligent_extraction.auxiliary_extractor import AuxiliaryExtractor
from .test_intelligent_extraction_config import AUXILIARY_CONFIG


class TestAuxiliaryExtractorUnit:
    """辅助信息提取器单元测试"""
    
    @pytest.fixture
    def extractor(self):
        return AuxiliaryExtractor(AUXILIARY_CONFIG)
    
    def test_brand_extraction(self, extractor):
        """测试品牌提取 - 验证需求：3.3.1"""
        text = "霍尼韦尔温度传感器"
        result = extractor._extract_brand(text)
        assert result == "霍尼韦尔"
    
    def test_medium_extraction(self, extractor):
        """测试介质提取 - 验证需求：3.3.2"""
        text = "水介质温度传感器"
        result = extractor._extract_medium(text)
        assert result == "水"
    
    def test_model_extraction(self, extractor):
        """测试型号提取 - 验证需求：3.3.3"""
        text = "HST-RA温度传感器"
        result = extractor._extract_model(text)
        assert result == "HST-RA"
