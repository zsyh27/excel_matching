"""
参数提取器属性测试

使用hypothesis进行属性测试
Feature: intelligent-feature-extraction
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.intelligent_extraction.parameter_extractor import ParameterExtractor
from .test_intelligent_extraction_config import PARAMETER_CONFIG


class TestParameterExtractorProperties:
    """参数提取器属性测试"""
    
    @pytest.fixture
    def extractor(self):
        """创建提取器实例"""
        return ParameterExtractor(PARAMETER_CONFIG)
    
    # Feature: intelligent-feature-extraction, Property 4: 参数归一化的一致性
    @given(
        min_val=st.integers(min_value=0, max_value=1000),
        max_val=st.integers(min_value=0, max_value=10000),
        unit=st.sampled_from(['ppm', '℃', 'bar', '%', 'mA', 'V'])
    )
    @settings(max_examples=100)
    def test_property_4_parameter_normalization_consistency(self, extractor, min_val, max_val, unit):
        """
        属性4：参数归一化的一致性
        验证需求：2.2.2
        
        对于任何成功提取的参数，归一化结果应该包含结构化的数值和单位信息
        """
        assume(min_val < max_val)  # 确保min < max
        
        # 构造量程文本
        text = f"量程{min_val}~{max_val}{unit}"
        
        result = extractor._extract_range(text)
        
        if result is not None:
            # 验证归一化结果包含必需字段
            assert 'normalized' in result.__dict__, "应该包含normalized字段"
            assert result.normalized is not None, "normalized不应该为None"
            
            # 验证归一化结果包含min, max, unit
            assert 'min' in result.normalized, "归一化结果应该包含min字段"
            assert 'max' in result.normalized, "归一化结果应该包含max字段"
            assert 'unit' in result.normalized, "归一化结果应该包含unit字段"
            
            # 验证数值正确
            assert result.normalized['min'] == min_val, f"min值应该为{min_val}"
            assert result.normalized['max'] == max_val, f"max值应该为{max_val}"
            assert result.normalized['unit'] == unit, f"unit应该为{unit}"
    
    # Feature: intelligent-feature-extraction, Property 5: 参数提取总是返回置信度
    @given(
        param_text=st.one_of(
            st.text(min_size=10, max_size=100).filter(lambda x: '~' in x or '-' in x),
            st.just("量程0~250ppm"),
            st.just("输出4~20mA"),
            st.just("精度±5%")
        )
    )
    @settings(max_examples=100)
    def test_property_5_parameters_always_have_confidence(self, extractor, param_text):
        """
        属性5：参数提取总是返回置信度
        验证需求：2.2.3
        
        对于任何成功提取的参数，都应该包含置信度评分
        """
        result = extractor.extract(param_text)
        
        # 检查每个提取的参数
        if result.range is not None:
            assert hasattr(result.range, 'confidence'), "量程应该包含confidence字段"
            assert 0 <= result.range.confidence <= 1, f"量程置信度应该在[0, 1]区间内"
        
        if result.output is not None:
            assert hasattr(result.output, 'confidence'), "输出信号应该包含confidence字段"
            assert 0 <= result.output.confidence <= 1, f"输出信号置信度应该在[0, 1]区间内"
        
        if result.accuracy is not None:
            assert hasattr(result.accuracy, 'confidence'), "精度应该包含confidence字段"
            assert 0 <= result.accuracy.confidence <= 1, f"精度置信度应该在[0, 1]区间内"
