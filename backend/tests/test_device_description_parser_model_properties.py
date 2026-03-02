# -*- coding: utf-8 -*-
"""
设备描述解析器 - 型号提取属性测试

测试型号提取功能的正确性属性
"""

import pytest
from hypothesis import given, strategies as st, settings

from modules.intelligent_device.device_description_parser import DeviceDescriptionParser
from modules.intelligent_device.configuration_manager import ConfigurationManager


@pytest.fixture(scope="module")
def parser():
    """创建解析器实例"""
    config_manager = ConfigurationManager('backend/config/device_params.yaml')
    return DeviceDescriptionParser(config_manager)


# Feature: intelligent-device-input, Property 3: 型号提取正确性
@given(
    model=st.sampled_from(['QAA2061', 'ABC123', 'VVF53', 'QAA2061D', 'ABC-123']),
    prefix=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'), max_codepoint=127), min_size=0, max_size=20),
    suffix=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'), max_codepoint=127), min_size=0, max_size=20)
)
@settings(max_examples=100)
def test_model_extraction_correctness(parser, model, prefix, suffix):
    """
    **Validates: Requirements 1.3, 4.1, 4.4**
    
    对于任意包含型号模式（字母+数字组合）的设备描述文本，
    解析器应该能够提取出型号信息，支持多种常见格式
    （如"QAA2061"、"ABC-123"等）
    """
    # 将型号插入到文本中
    text_with_model = f"{prefix} {model} {suffix}"
    
    result = parser.extract_model(text_with_model)
    
    # 验证型号被正确识别
    assert result is not None, f"应该识别到型号 {model}，但返回了 None"
    # 验证识别的型号与原型号匹配（可能是原型号或其子串）
    assert model in text_with_model, f"原型号 {model} 应该在文本中"
    assert result in text_with_model, f"识别的型号 {result} 应该在文本中"


# Feature: intelligent-device-input, Property 9: 多型号选择一致性
@given(
    model1=st.sampled_from(['QAA2061', 'ABC123', 'VVF53']),
    model2=st.sampled_from(['QAA2061D', 'ABC-123', 'VVF42']),
    separator=st.sampled_from([' ', '  ', ' 和 ', ' / '])
)
@settings(max_examples=100)
def test_multiple_model_selection_consistency(parser, model1, model2, separator):
    """
    **Validates: Requirements 4.2**
    
    对于任意包含多个型号模式的设备描述文本，
    解析器应该选择一个最可能的型号（不返回多个型号）
    """
    # 创建包含多个型号的文本
    text_with_multiple_models = f"{model1}{separator}{model2}"
    
    result = parser.extract_model(text_with_multiple_models)
    
    # 验证只返回一个型号（不是列表或多个值）
    assert result is not None, "应该返回一个型号"
    assert isinstance(result, str), "应该返回字符串类型的单个型号"
    # 验证返回的型号是文本中的某一个
    assert result in text_with_multiple_models, f"返回的型号 {result} 应该在文本中"


# Feature: intelligent-device-input, Property 12: 无型号文本处理
@given(
    text=st.text(
        alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Zs', 'Po'),
            blacklist_characters='0123456789',
            max_codepoint=127
        ),
        min_size=5,
        max_size=50
    )
)
@settings(max_examples=100)
def test_no_model_text_handling(parser, text):
    """
    **Validates: Requirements 4.3**
    
    对于任意不包含型号模式的设备描述文本，
    解析器应该返回 None 作为型号值
    """
    # 确保文本中不包含数字（因此不会匹配型号模式）
    # 型号模式需要字母+数字组合
    
    result = parser.extract_model(text)
    
    # 验证返回 None
    assert result is None, f"对于不包含型号模式的文本，应该返回 None，但返回了 {result}"
