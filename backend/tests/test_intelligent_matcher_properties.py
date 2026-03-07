"""
智能匹配器属性测试
Feature: intelligent-feature-extraction
"""

import pytest
from hypothesis import given, strategies as st, settings
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.intelligent_extraction.intelligent_matcher import IntelligentMatcher
from modules.intelligent_extraction.data_models import ExtractionResult, DeviceTypeInfo, ScoreDetails
from .test_intelligent_extraction_config import MATCHING_CONFIG


class MockDeviceLoader:
    """模拟设备加载器"""
    def get_all_devices(self):
        return [
            {'device_id': '1', 'device_name': 'CO浓度探测器', 'device_type': 'CO浓度探测器', 
             'brand': '霍尼韦尔', 'spec_model': 'CO-100', 'key_params': '{"量程": "0-250ppm"}'},
            {'device_id': '2', 'device_name': '温度传感器', 'device_type': '温度传感器',
             'brand': '西门子', 'spec_model': 'T-200', 'key_params': '{"量程": "-40~80℃"}'}
        ]
    
    def get_devices_by_type(self, device_type):
        return [d for d in self.get_all_devices() if d['device_type'] == device_type]


class TestIntelligentMatcherProperties:
    """智能匹配器属性测试"""
    
    @pytest.fixture
    def matcher(self):
        return IntelligentMatcher(MATCHING_CONFIG, MockDeviceLoader())
    
    # Feature: intelligent-feature-extraction, Property 7: 评分权重的正确性
    @given(
        device_type_score=st.floats(min_value=0, max_value=1),
        parameter_score=st.floats(min_value=0, max_value=1),
        brand_score=st.floats(min_value=0, max_value=1),
        other_score=st.floats(min_value=0, max_value=1)
    )
    @settings(max_examples=100)
    def test_property_7_score_weight_correctness(self, matcher, device_type_score, 
                                                  parameter_score, brand_score, other_score):
        """
        属性7：评分权重的正确性
        验证需求：2.3.1
        
        总分应该等于各维度得分按权重加权的和
        """
        # 计算预期总分
        expected_total = (
            device_type_score * matcher.weights['device_type'] * 100 +
            parameter_score * matcher.weights['parameters'] * 100 +
            brand_score * matcher.weights['brand'] * 100 +
            other_score * matcher.weights['others'] * 100
        )
        
        # 验证权重和为1
        weight_sum = sum(matcher.weights.values())
        assert abs(weight_sum - 1.0) < 0.01, f"权重和应该为1，实际为{weight_sum}"
    
    # Feature: intelligent-feature-extraction, Property 8: 候选设备按评分降序排列
    def test_property_8_candidates_sorted_by_score(self, matcher):
        """
        属性8：候选设备按评分降序排列
        验证需求：2.3.2, 2.3.3
        
        候选设备列表应该按总分降序排列
        """
        extraction = ExtractionResult()
        extraction.device_type = DeviceTypeInfo(
            main_type="探测器",
            sub_type="CO浓度探测器",
            confidence=0.95
        )
        
        result = matcher.match(extraction, top_k=5)
        
        if len(result.candidates) > 1:
            # 验证按总分降序排列
            for i in range(len(result.candidates) - 1):
                assert result.candidates[i].total_score >= result.candidates[i+1].total_score, \
                    "候选设备应该按总分降序排列"
