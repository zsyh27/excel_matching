"""
智能匹配器单元测试
Feature: intelligent-feature-extraction
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.intelligent_extraction.intelligent_matcher import IntelligentMatcher
from modules.intelligent_extraction.data_models import ExtractionResult, DeviceTypeInfo, ParameterInfo, RangeParam
from .test_intelligent_extraction_config import MATCHING_CONFIG


class MockDeviceLoader:
    def get_all_devices(self):
        return [
            {'device_id': '1', 'device_name': 'CO浓度探测器', 'device_type': 'CO浓度探测器', 
             'brand': '霍尼韦尔', 'spec_model': 'CO-100', 'key_params': '{"量程": "0-250ppm", "输出": "4-20mA"}'},
        ]
    
    def get_devices_by_type(self, device_type):
        return [d for d in self.get_all_devices() if d['device_type'] == device_type]


class TestIntelligentMatcherUnit:
    """智能匹配器单元测试"""
    
    @pytest.fixture
    def matcher(self):
        return IntelligentMatcher(MATCHING_CONFIG, MockDeviceLoader())
    
    def test_score_calculation(self, matcher):
        """测试评分计算 - 验证需求：2.3.1, 3.4.2"""
        extraction = ExtractionResult()
        extraction.device_type = DeviceTypeInfo(
            main_type="探测器",
            sub_type="CO浓度探测器",
            confidence=0.95
        )
        
        result = matcher.match(extraction, top_k=5)
        
        assert len(result.candidates) > 0
        assert result.candidates[0].total_score > 0
    
    def test_sorting(self, matcher):
        """测试排序功能 - 验证需求：2.3.2"""
        extraction = ExtractionResult()
        extraction.device_type = DeviceTypeInfo(
            main_type="探测器",
            sub_type="CO浓度探测器",
            confidence=0.95
        )
        
        result = matcher.match(extraction, top_k=5)
        
        # 验证按评分降序排列
        if len(result.candidates) > 1:
            for i in range(len(result.candidates) - 1):
                assert result.candidates[i].total_score >= result.candidates[i+1].total_score
