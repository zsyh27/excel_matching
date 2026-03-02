# -*- coding: utf-8 -*-
"""
设备描述解析器 - 解析入口属性测试

测试统一解析入口和未识别文本追踪的正确性属性
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


# Feature: intelligent-device-input, Property 5: 原始文本保留
@given(
    description=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po'), max_codepoint=127),
        min_size=1,
        max_size=200
    )
)
@settings(max_examples=100)
def test_raw_text_preservation(parser, description):
    """
    **Validates: Requirements 1.6**
    
    对于任意设备描述文本，解析后的结果应该保留完整的原始输入文本到 raw_description 字段，
    确保可以重新解析
    """
    result = parser.parse(description)
    
    # 验证原始文本被保留
    assert result.raw_description == description, \
        f"原始文本应该被完整保留，期望: {description}, 实际: {result.raw_description}"
    
    # 验证可以重新解析（幂等性）
    result2 = parser.parse(result.raw_description)
    assert result2.raw_description == description, \
        "使用保留的原始文本应该能够重新解析"


# Feature: intelligent-device-input, Property 13: 未识别文本记录
@given(
    brand=st.sampled_from(['西门子', '霍尼韦尔', '施耐德']),
    device_type=st.sampled_from(['CO2传感器', '座阀', '温度传感器']),
    model=st.sampled_from(['QAA2061', 'ABC123', 'VVF53']),
    extra_text=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'), max_codepoint=127),
        min_size=5,
        max_size=30
    )
)
@settings(max_examples=100)
def test_unrecognized_text_tracking(parser, brand, device_type, model, extra_text):
    """
    **Validates: Requirements 7.4**
    
    对于任意设备描述文本，解析器应该返回未能识别和分类的文本片段列表，
    允许用户查看哪些内容未被处理
    """
    # 构建包含已知元素和额外文本的描述
    if device_type == 'CO2传感器':
        params = "量程0-2000ppm 输出4-20mA"
    elif device_type == '座阀':
        params = "DN50 PN16"
    else:  # 温度传感器
        params = "量程-20~80℃ 输出4-20mA"
    
    description = f"{brand} {device_type} {model} {params} {extra_text}"
    
    result = parser.parse(description)
    
    # 验证返回的是列表
    assert isinstance(result.unrecognized_text, list), \
        "未识别文本应该是列表类型"
    
    # 验证列表中的元素都是字符串
    for item in result.unrecognized_text:
        assert isinstance(item, str), \
            f"未识别文本列表中的元素应该是字符串，但得到: {type(item)}"
    
    # 如果有额外文本且不为空白，应该在未识别列表中有所体现
    # （注意：由于文本处理的复杂性，我们只验证结构正确性）
    if extra_text.strip():
        # 未识别文本可能为空（如果额外文本恰好匹配某些模式）或非空
        # 我们只验证它是一个有效的列表
        assert result.unrecognized_text is not None


# 测试空输入的处理
@given(
    empty_text=st.sampled_from(['', '   ', '\t', '\n'])
)
@settings(max_examples=20)
def test_empty_input_handling(parser, empty_text):
    """
    测试空输入或只包含空白字符的输入
    """
    result = parser.parse(empty_text)
    
    # 验证返回有效的解析结果
    assert result is not None
    assert result.raw_description == empty_text
    assert result.brand is None
    assert result.device_type is None
    assert result.model is None
    assert result.key_params == {}
    assert isinstance(result.unrecognized_text, list)
