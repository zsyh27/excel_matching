# -*- coding: utf-8 -*-
"""
设备描述解析器品牌识别属性测试

使用 Hypothesis 进行基于属性的测试，验证品牌识别的通用属性
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from modules.intelligent_device import (
    DeviceDescriptionParser,
    ConfigurationManager
)


@pytest.fixture(scope="module")
def parser(tmp_path_factory):
    """创建带有品牌配置的解析器实例（模块级别）"""
    tmp_path = tmp_path_factory.mktemp("config")
    config_file = tmp_path / "device_params.yaml"
    config_file.write_text("""
brands:
  西门子:
    keywords: ["西门子", "SIEMENS", "siemens", "Siemens"]
  霍尼韦尔:
    keywords: ["霍尼韦尔", "HONEYWELL", "honeywell", "Honeywell"]
  施耐德:
    keywords: ["施耐德", "SCHNEIDER", "schneider", "Schneider"]
  江森自控:
    keywords: ["江森自控", "江森", "JOHNSON", "johnson", "Johnson"]

device_types: {}
""", encoding='utf-8')
    
    config_manager = ConfigurationManager(str(config_file))
    return DeviceDescriptionParser(config_manager)


# 定义品牌和关键词的策略
BRANDS = {
    '西门子': ['西门子', 'SIEMENS', 'siemens', 'Siemens'],
    '霍尼韦尔': ['霍尼韦尔', 'HONEYWELL', 'honeywell', 'Honeywell'],
    '施耐德': ['施耐德', 'SCHNEIDER', 'schneider', 'Schneider'],
    '江森自控': ['江森自控', '江森', 'JOHNSON', 'johnson', 'Johnson']
}

# 品牌名称策略
brand_name_strategy = st.sampled_from(list(BRANDS.keys()))

# 品牌关键词策略（从所有品牌的关键词中选择）
def brand_keyword_strategy(brand_name):
    """为指定品牌生成关键词策略"""
    return st.sampled_from(BRANDS[brand_name])

# 随机文本策略（不包含品牌关键词）
def text_without_brands():
    """生成不包含任何品牌关键词的文本"""
    # 使用常见的设备描述词汇
    words = st.sampled_from([
        'CO2传感器', '温度传感器', '压力传感器', '座阀', '调节阀',
        'QAA2061', 'T5100', 'VVF53', 'DN50', 'PN16',
        '量程', '输出', '通径', '压力', '0-2000ppm', '4-20mA',
        '测量', '控制', '设备', '型号', '参数'
    ])
    return st.lists(words, min_size=1, max_size=10).map(lambda w: ' '.join(w))


class TestBrandRecognitionProperties:
    """品牌识别属性测试"""
    
    # Feature: intelligent-device-input, Property 1: 品牌识别一致性
    @settings(max_examples=100)
    @given(
        brand_name=brand_name_strategy,
        prefix_text=text_without_brands(),
        suffix_text=text_without_brands(),
        data=st.data()
    )
    def test_brand_recognition_consistency(self, parser, brand_name, prefix_text, suffix_text, data):
        """
        **Validates: Requirements 1.1, 2.1, 2.4**
        
        属性 1：品牌识别一致性
        
        对于任意包含配置中品牌关键词的设备描述文本，
        解析器应该能够识别出正确的品牌名称，并且支持品牌别名和拼写变体。
        """
        # 为该品牌随机选择一个关键词
        keyword = data.draw(st.sampled_from(BRANDS[brand_name]))
        
        # 确保前缀和后缀文本不包含任何品牌关键词
        all_keywords = [kw for keywords in BRANDS.values() for kw in keywords]
        assume(not any(kw.lower() in prefix_text.lower() for kw in all_keywords))
        assume(not any(kw.lower() in suffix_text.lower() for kw in all_keywords))
        
        # 构造包含品牌关键词的文本（品牌关键词在中间）
        text_with_brand = f"{prefix_text} {keyword} {suffix_text}"
        
        # 执行品牌识别
        result = parser.extract_brand(text_with_brand)
        
        # 验证：应该识别出正确的品牌名称
        assert result == brand_name, (
            f"期望识别出品牌 '{brand_name}'，但得到 '{result}'\n"
            f"关键词: '{keyword}'\n"
            f"文本: '{text_with_brand}'"
        )
    
    # Feature: intelligent-device-input, Property 1: 品牌识别一致性（关键词变体）
    @settings(max_examples=100)
    @given(
        brand_name=brand_name_strategy,
        surrounding_text=text_without_brands()
    )
    def test_brand_recognition_with_all_keyword_variants(self, parser, brand_name, surrounding_text):
        """
        **Validates: Requirements 1.1, 2.1, 2.4**
        
        属性 1：品牌识别一致性（测试所有关键词变体）
        
        对于任意品牌的任意关键词变体（包括别名和拼写变体），
        解析器都应该能够识别出正确的品牌名称。
        """
        # 确保周围文本不包含任何品牌关键词
        all_keywords = [kw for keywords in BRANDS.values() for kw in keywords]
        assume(not any(kw.lower() in surrounding_text.lower() for kw in all_keywords))
        
        # 测试该品牌的所有关键词变体
        for keyword in BRANDS[brand_name]:
            text_with_brand = f"{surrounding_text} {keyword}"
            result = parser.extract_brand(text_with_brand)
            
            assert result == brand_name, (
                f"期望识别出品牌 '{brand_name}'，但得到 '{result}'\n"
                f"关键词变体: '{keyword}'\n"
                f"文本: '{text_with_brand}'"
            )
    
    # Feature: intelligent-device-input, Property 1: 品牌识别一致性（位置无关性）
    @settings(max_examples=100)
    @given(
        brand_name=brand_name_strategy,
        text_parts=st.lists(text_without_brands(), min_size=2, max_size=5),
        position=st.integers(min_value=0, max_value=4),
        data=st.data()
    )
    def test_brand_recognition_position_independence(self, parser, brand_name, text_parts, position, data):
        """
        **Validates: Requirements 1.1, 2.1, 2.4**
        
        属性 1：品牌识别一致性（位置无关性）
        
        无论品牌关键词出现在文本的哪个位置（开头、中间、结尾），
        解析器都应该能够识别出正确的品牌名称。
        """
        # 确保所有文本部分不包含品牌关键词
        all_keywords = [kw for keywords in BRANDS.values() for kw in keywords]
        for part in text_parts:
            assume(not any(kw.lower() in part.lower() for kw in all_keywords))
        
        # 选择一个关键词
        keyword = data.draw(st.sampled_from(BRANDS[brand_name]))
        
        # 将品牌关键词插入到指定位置
        position = min(position, len(text_parts))
        text_parts_with_brand = text_parts[:position] + [keyword] + text_parts[position:]
        text_with_brand = ' '.join(text_parts_with_brand)
        
        # 执行品牌识别
        result = parser.extract_brand(text_with_brand)
        
        # 验证：应该识别出正确的品牌名称
        assert result == brand_name, (
            f"期望识别出品牌 '{brand_name}'，但得到 '{result}'\n"
            f"关键词: '{keyword}' 在位置 {position}\n"
            f"文本: '{text_with_brand}'"
        )
    
    # Feature: intelligent-device-input, Property 1: 品牌识别一致性（空白字符容忍）
    @settings(max_examples=100)
    @given(
        brand_name=brand_name_strategy,
        whitespace_before=st.sampled_from(['', ' ', '  ', '\t', '\n', ' \t ']),
        whitespace_after=st.sampled_from(['', ' ', '  ', '\t', '\n', ' \t ']),
        surrounding_text=text_without_brands(),
        data=st.data()
    )
    def test_brand_recognition_whitespace_tolerance(
        self, parser, brand_name, whitespace_before, whitespace_after, surrounding_text, data
    ):
        """
        **Validates: Requirements 1.1, 2.1, 2.4**
        
        属性 1：品牌识别一致性（空白字符容忍）
        
        品牌关键词周围的空白字符（空格、制表符、换行符）不应影响品牌识别。
        """
        # 确保周围文本不包含品牌关键词
        all_keywords = [kw for keywords in BRANDS.values() for kw in keywords]
        assume(not any(kw.lower() in surrounding_text.lower() for kw in all_keywords))
        
        # 选择一个关键词
        keyword = data.draw(st.sampled_from(BRANDS[brand_name]))
        
        # 构造包含不同空白字符的文本
        text_with_brand = f"{surrounding_text}{whitespace_before}{keyword}{whitespace_after}"
        
        # 执行品牌识别
        result = parser.extract_brand(text_with_brand)
        
        # 验证：应该识别出正确的品牌名称
        assert result == brand_name, (
            f"期望识别出品牌 '{brand_name}'，但得到 '{result}'\n"
            f"关键词: '{keyword}'\n"
            f"空白字符前: {repr(whitespace_before)}\n"
            f"空白字符后: {repr(whitespace_after)}\n"
            f"文本: {repr(text_with_brand)}"
        )


    # Feature: intelligent-device-input, Property 8: 多品牌选择一致性
    @settings(max_examples=100)
    @given(
        brand1=brand_name_strategy,
        brand2=brand_name_strategy,
        surrounding_text=text_without_brands(),
        data=st.data()
    )
    def test_multi_brand_selection_consistency(self, parser, brand1, brand2, surrounding_text, data):
        """
        **Validates: Requirements 2.2**
        
        属性 8：多品牌选择一致性
        
        对于任意包含多个品牌关键词的设备描述文本，
        解析器应该选择一个最匹配的品牌（不返回多个品牌）。
        """
        # 确保两个品牌不同
        assume(brand1 != brand2)
        
        # 确保周围文本不包含品牌关键词
        all_keywords = [kw for keywords in BRANDS.values() for kw in keywords]
        assume(not any(kw.lower() in surrounding_text.lower() for kw in all_keywords))
        
        # 为每个品牌选择一个关键词
        keyword1 = data.draw(st.sampled_from(BRANDS[brand1]))
        keyword2 = data.draw(st.sampled_from(BRANDS[brand2]))
        
        # 构造包含两个品牌关键词的文本
        text_with_two_brands = f"{keyword1} {surrounding_text} {keyword2}"
        
        # 执行品牌识别
        result = parser.extract_brand(text_with_two_brands)
        
        # 验证：应该只返回一个品牌（不是None，不是多个品牌）
        assert result is not None, (
            f"期望识别出一个品牌，但得到 None\n"
            f"文本: '{text_with_two_brands}'"
        )
        
        # 验证：返回的品牌应该是两个品牌之一
        assert result in [brand1, brand2], (
            f"期望识别出 '{brand1}' 或 '{brand2}'，但得到 '{result}'\n"
            f"文本: '{text_with_two_brands}'"
        )
        
        # 验证：返回的应该是首次出现的品牌（根据设计文档）
        # 由于keyword1在前，应该返回brand1
        assert result == brand1, (
            f"期望识别出首次出现的品牌 '{brand1}'，但得到 '{result}'\n"
            f"关键词1: '{keyword1}' (品牌: {brand1})\n"
            f"关键词2: '{keyword2}' (品牌: {brand2})\n"
            f"文本: '{text_with_two_brands}'"
        )
    
    # Feature: intelligent-device-input, Property 10: 无品牌文本处理
    @settings(max_examples=100)
    @given(text=text_without_brands())
    def test_no_brand_text_handling(self, parser, text):
        """
        **Validates: Requirements 2.3**
        
        属性 10：无品牌文本处理
        
        对于任意不包含任何配置品牌关键词的设备描述文本，
        解析器应该返回 None 作为品牌值。
        """
        # 确保文本不包含任何品牌关键词
        all_keywords = [kw for keywords in BRANDS.values() for kw in keywords]
        assume(not any(kw.lower() in text.lower() for kw in all_keywords))
        
        # 执行品牌识别
        result = parser.extract_brand(text)
        
        # 验证：应该返回 None
        assert result is None, (
            f"期望返回 None，但得到 '{result}'\n"
            f"文本: '{text}'"
        )


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
