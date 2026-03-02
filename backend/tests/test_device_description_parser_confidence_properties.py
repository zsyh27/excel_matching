# -*- coding: utf-8 -*-
"""
设备描述解析器 - 置信度计算属性测试

测试置信度计算功能的正确性属性
"""

import pytest
from hypothesis import given, strategies as st, settings

from modules.intelligent_device.device_description_parser import (
    DeviceDescriptionParser,
    ParseResult
)
from modules.intelligent_device.configuration_manager import ConfigurationManager


@pytest.fixture(scope="module")
def parser():
    """创建解析器实例"""
    config_manager = ConfigurationManager('backend/config/device_params.yaml')
    return DeviceDescriptionParser(config_manager)


# Feature: intelligent-device-input, Property 6: 置信度范围约束
@given(
    brand=st.one_of(st.none(), st.sampled_from(['西门子', '霍尼韦尔', '施耐德'])),
    device_type=st.one_of(st.none(), st.sampled_from(['CO2传感器', '座阀', '温度传感器'])),
    model=st.one_of(st.none(), st.sampled_from(['QAA2061', 'ABC123', 'VVF53'])),
    num_required_params=st.integers(min_value=0, max_value=5)
)
@settings(max_examples=100)
def test_confidence_score_range(parser, brand, device_type, model, num_required_params):
    """
    **Validates: Requirements 1.5**
    
    对于任意解析结果，计算的置信度评分应该在 0.0 到 1.0 之间（包含边界值）
    """
    # 构建解析结果
    key_params = {}
    for i in range(num_required_params):
        key_params[f'param_{i}'] = {
            'value': f'value_{i}',
            'required': True,
            'data_type': 'string'
        }
    
    parse_result = ParseResult(
        brand=brand,
        device_type=device_type,
        model=model,
        key_params=key_params
    )
    
    confidence = parser.calculate_confidence(parse_result)
    
    # 验证置信度在0.0到1.0之间
    assert 0.0 <= confidence <= 1.0, f"置信度 {confidence} 应该在 0.0 到 1.0 之间"
    assert isinstance(confidence, float), "置信度应该是浮点数类型"


# Feature: intelligent-device-input, Property 7: 置信度与解析完整性相关性
@given(
    has_brand=st.booleans(),
    has_device_type=st.booleans(),
    has_model=st.booleans(),
    num_required_params=st.integers(min_value=0, max_value=3)
)
@settings(max_examples=100)
def test_confidence_completeness_correlation(parser, has_brand, has_device_type, has_model, num_required_params):
    """
    **Validates: Requirements 2.3, 3.3, 5.6, 7.7**
    
    对于任意解析结果，当缺少品牌、设备类型或必填参数时，
    置信度评分应该低于包含所有这些信息的解析结果的置信度评分
    """
    # 构建不完整的解析结果
    incomplete_result = ParseResult(
        brand='西门子' if has_brand else None,
        device_type='CO2传感器' if has_device_type else None,
        model='QAA2061' if has_model else None,
        key_params={
            f'param_{i}': {
                'value': f'value_{i}',
                'required': True,
                'data_type': 'string'
            }
            for i in range(num_required_params)
        }
    )
    
    # 构建完整的解析结果
    complete_result = ParseResult(
        brand='西门子',
        device_type='CO2传感器',
        model='QAA2061',
        key_params={
            f'param_{i}': {
                'value': f'value_{i}',
                'required': True,
                'data_type': 'string'
            }
            for i in range(3)  # 3个必填参数
        }
    )
    
    incomplete_confidence = parser.calculate_confidence(incomplete_result)
    complete_confidence = parser.calculate_confidence(complete_result)
    
    # 如果不完整的结果缺少任何信息，其置信度应该低于或等于完整结果
    # （注意：由于置信度上限为1.0，某些情况下可能相等）
    is_incomplete = (not has_brand) or (not has_device_type) or (num_required_params < 3)
    
    if is_incomplete:
        assert incomplete_confidence <= complete_confidence, \
            f"不完整结果的置信度 {incomplete_confidence} 应该低于或等于完整结果的置信度 {complete_confidence}"
        
        # 如果缺少品牌或设备类型（高权重项），置信度应该严格小于
        if (not has_brand) or (not has_device_type):
            assert incomplete_confidence < complete_confidence, \
                f"缺少品牌或设备类型时，置信度 {incomplete_confidence} 应该严格低于完整结果 {complete_confidence}"
    else:
        # 如果两者都完整，置信度应该相等
        assert incomplete_confidence == complete_confidence, \
            f"两个完整结果的置信度应该相等"
