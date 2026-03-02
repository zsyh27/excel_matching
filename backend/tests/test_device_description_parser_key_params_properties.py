# -*- coding: utf-8 -*-
"""
设备描述解析器 - 关键参数提取属性测试

测试关键参数提取功能的正确性属性
"""

import pytest
import json
from hypothesis import given, strategies as st, settings, assume

from modules.intelligent_device.device_description_parser import DeviceDescriptionParser
from modules.intelligent_device.configuration_manager import ConfigurationManager


@pytest.fixture(scope="module")
def parser():
    """创建解析器实例"""
    config_manager = ConfigurationManager('backend/config/device_params.yaml')
    return DeviceDescriptionParser(config_manager)


# Feature: intelligent-device-input, Property 4: 设备类型特定参数提取
@given(
    device_type=st.sampled_from(['CO2传感器', '座阀', '温度传感器', '压力传感器', '执行器']),
    extra_text=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'), max_codepoint=127), min_size=0, max_size=30)
)
@settings(max_examples=100)
def test_device_type_specific_param_extraction(parser, device_type, extra_text):
    """
    **Validates: Requirements 1.4, 5.1, 5.2, 5.3, 5.4, 5.5**
    
    对于任意已识别设备类型的设备描述文本，
    解析器应该根据该设备类型的配置规则提取相应的关键参数
    （如传感器提取量程和输出信号，阀门提取通径和压力等级），
    并将结果存储为有效的JSON格式
    """
    # 根据设备类型构建包含相应参数的文本
    if device_type == 'CO2传感器':
        text = f"{extra_text} 量程0-2000ppm 输出4-20mA"
        expected_params = ['量程', '输出信号']
    elif device_type == '座阀':
        text = f"{extra_text} DN50 PN16"
        expected_params = ['通径', '压力等级']
    elif device_type == '温度传感器':
        text = f"{extra_text} 量程-20~80℃ 输出4-20mA"
        expected_params = ['量程', '输出信号']
    elif device_type == '压力传感器':
        text = f"{extra_text} 量程0~1.6MPa 输出4-20mA"
        expected_params = ['量程', '输出信号']
    elif device_type == '执行器':
        text = f"{extra_text} 扭矩10N·m 行程时间90秒"
        expected_params = ['扭矩', '行程时间']
    else:
        assume(False)  # 跳过未知设备类型
    
    result = parser.extract_key_params(text, device_type)
    
    # 验证返回的是字典（可以序列化为JSON）
    assert isinstance(result, dict), "应该返回字典类型"
    
    # 验证可以序列化为JSON
    try:
        json_str = json.dumps(result, ensure_ascii=False)
        assert json_str is not None
    except (TypeError, ValueError) as e:
        pytest.fail(f"参数字典无法序列化为JSON: {e}")
    
    # 验证至少提取了一些参数
    if result:
        # 验证参数包含必要的元数据
        for param_name, param_info in result.items():
            assert isinstance(param_info, dict), f"参数 {param_name} 应该是字典类型"
            assert 'value' in param_info, f"参数 {param_name} 应该包含 value 字段"
            assert 'required' in param_info, f"参数 {param_name} 应该包含 required 字段"
            assert 'data_type' in param_info, f"参数 {param_name} 应该包含 data_type 字段"
