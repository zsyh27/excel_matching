# -*- coding: utf-8 -*-
"""
设备描述解析器设备类型识别属性测试

使用 Hypothesis 进行基于属性的测试，验证设备类型识别的通用属性
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from modules.intelligent_device import (
    DeviceDescriptionParser,
    ConfigurationManager
)


@pytest.fixture(scope="module")
def parser(tmp_path_factory):
    """创建带有设备类型配置的解析器实例（模块级别）"""
    tmp_path = tmp_path_factory.mktemp("config")
    config_file = tmp_path / "device_params.yaml"
    config_file.write_text("""
brands: {}

device_types:
  CO2传感器:
    keywords: ["CO2传感器", "二氧化碳传感器", "CO2 sensor", "co2传感器"]
    params: []
  座阀:
    keywords: ["座阀", "调节阀", "control valve", "座式调节阀"]
    params: []
  温度传感器:
    keywords: ["温度传感器", "温度探头", "temperature sensor", "温感"]
    params: []
  压力传感器:
    keywords: ["压力传感器", "压力变送器", "pressure sensor", "压感"]
    params: []
  执行器:
    keywords: ["执行器", "电动执行器", "actuator", "风阀执行器"]
    params: []
""", encoding='utf-8')
    
    config_manager = ConfigurationManager(str(config_file))
    return DeviceDescriptionParser(config_manager)


# 定义设备类型和关键词的策略
DEVICE_TYPES = {
    'CO2传感器': ['CO2传感器', '二氧化碳传感器', 'CO2 sensor', 'co2传感器'],
    '座阀': ['座阀', '调节阀', 'control valve', '座式调节阀'],
    '温度传感器': ['温度传感器', '温度探头', 'temperature sensor', '温感'],
    '压力传感器': ['压力传感器', '压力变送器', 'pressure sensor', '压感'],
    '执行器': ['执行器', '电动执行器', 'actuator', '风阀执行器']
}

# 设备类型名称策略
device_type_strategy = st.sampled_from(list(DEVICE_TYPES.keys()))

# 随机文本策略（不包含设备类型关键词）
def text_without_device_types():
    """生成不包含任何设备类型关键词的文本"""
    words = st.sampled_from([
        '西门子', '霍尼韦尔', '施耐德', '贝尔莫',
        'QAA2061', 'T5100', 'VVF53', 'DN50', 'PN16',
        '量程', '输出', '通径', '压力', '0-2000ppm', '4-20mA',
        '测量', '控制', '设备', '型号', '参数'
    ])
    return st.lists(words, min_size=1, max_size=10).map(lambda w: ' '.join(w))


class TestDeviceTypeRecognitionProperties:
    """设备类型识别属性测试"""
    
    # Feature: intelligent-device-input, Property 2: 设备类型识别和规则应用
    @settings(max_examples=100)
    @given(
        device_type=device_type_strategy,
        prefix_text=text_without_device_types(),
        suffix_text=text_without_device_types(),
        data=st.data()
    )
    def test_device_type_recognition_consistency(self, parser, device_type, prefix_text, suffix_text, data):
        """
        **Validates: Requirements 1.2, 3.1, 3.2**
        
        属性 2：设备类型识别和规则应用
        
        对于任意包含设备类型关键词的设备描述文本，
        解析器应该能够识别设备类型，并自动应用该类型对应的参数提取规则。
        """
        # 为该设备类型随机选择一个关键词
        keyword = data.draw(st.sampled_from(DEVICE_TYPES[device_type]))
        
        # 确保前缀和后缀文本不包含任何设备类型关键词
        all_keywords = [kw for keywords in DEVICE_TYPES.values() for kw in keywords]
        assume(not any(kw.lower() in prefix_text.lower() for kw in all_keywords))
        assume(not any(kw.lower() in suffix_text.lower() for kw in all_keywords))
        
        # 构造包含设备类型关键词的文本
        text_with_type = f"{prefix_text} {keyword} {suffix_text}"
        
        # 执行设备类型识别
        result = parser.extract_device_type(text_with_type)
        
        # 验证：应该识别出正确的设备类型
        assert result == device_type, (
            f"期望识别出设备类型 '{device_type}'，但得到 '{result}'\n"
            f"关键词: '{keyword}'\n"
            f"文本: '{text_with_type}'"
        )
    
    # Feature: intelligent-device-input, Property 2: 设备类型识别（关键词变体）
    @settings(max_examples=100)
    @given(
        device_type=device_type_strategy,
        surrounding_text=text_without_device_types()
    )
    def test_device_type_recognition_with_all_keyword_variants(self, parser, device_type, surrounding_text):
        """
        **Validates: Requirements 1.2, 3.1, 3.2**
        
        属性 2：设备类型识别和规则应用（测试所有关键词变体）
        
        对于任意设备类型的任意关键词变体，
        解析器都应该能够识别出正确的设备类型。
        """
        # 确保周围文本不包含任何设备类型关键词
        all_keywords = [kw for keywords in DEVICE_TYPES.values() for kw in keywords]
        assume(not any(kw.lower() in surrounding_text.lower() for kw in all_keywords))
        
        # 测试该设备类型的所有关键词变体
        for keyword in DEVICE_TYPES[device_type]:
            text_with_type = f"{surrounding_text} {keyword}"
            result = parser.extract_device_type(text_with_type)
            
            assert result == device_type, (
                f"期望识别出设备类型 '{device_type}'，但得到 '{result}'\n"
                f"关键词变体: '{keyword}'\n"
                f"文本: '{text_with_type}'"
            )
    
    # Feature: intelligent-device-input, Property 2: 设备类型识别（位置无关性）
    @settings(max_examples=100)
    @given(
        device_type=device_type_strategy,
        text_parts=st.lists(text_without_device_types(), min_size=2, max_size=5),
        position=st.integers(min_value=0, max_value=4),
        data=st.data()
    )
    def test_device_type_recognition_position_independence(self, parser, device_type, text_parts, position, data):
        """
        **Validates: Requirements 1.2, 3.1, 3.2**
        
        属性 2：设备类型识别和规则应用（位置无关性）
        
        无论设备类型关键词出现在文本的哪个位置，
        解析器都应该能够识别出正确的设备类型。
        """
        # 确保所有文本部分不包含设备类型关键词
        all_keywords = [kw for keywords in DEVICE_TYPES.values() for kw in keywords]
        for part in text_parts:
            assume(not any(kw.lower() in part.lower() for kw in all_keywords))
        
        # 选择一个关键词
        keyword = data.draw(st.sampled_from(DEVICE_TYPES[device_type]))
        
        # 将设备类型关键词插入到指定位置
        position = min(position, len(text_parts))
        text_parts_with_type = text_parts[:position] + [keyword] + text_parts[position:]
        text_with_type = ' '.join(text_parts_with_type)
        
        # 执行设备类型识别
        result = parser.extract_device_type(text_with_type)
        
        # 验证：应该识别出正确的设备类型
        assert result == device_type, (
            f"期望识别出设备类型 '{device_type}'，但得到 '{result}'\n"
            f"关键词: '{keyword}' 在位置 {position}\n"
            f"文本: '{text_with_type}'"
        )


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
