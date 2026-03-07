"""
设备类型识别器属性测试

使用hypothesis进行属性测试
Feature: intelligent-feature-extraction
"""

import pytest
from hypothesis import given, strategies as st, settings
import sys
import os

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.intelligent_extraction.device_type_recognizer import DeviceTypeRecognizer
from .test_intelligent_extraction_config import DEVICE_TYPE_CONFIG


class TestDeviceTypeRecognizerProperties:
    """设备类型识别器属性测试"""
    
    @pytest.fixture
    def recognizer(self):
        """创建识别器实例"""
        return DeviceTypeRecognizer(DEVICE_TYPE_CONFIG)
    
    # Feature: intelligent-feature-extraction, Property 1: 设备类型识别总是返回置信度
    @given(text=st.text(min_size=0, max_size=1000))
    @settings(max_examples=100)
    def test_property_1_always_returns_confidence(self, recognizer, text):
        """
        属性1：设备类型识别总是返回置信度
        验证需求：2.1.3
        
        对于任何输入文本，设备类型识别器都应该返回一个0到1之间的置信度值
        """
        result = recognizer.recognize(text)
        
        # 验证返回结果包含置信度字段
        assert hasattr(result, 'confidence'), "结果应该包含confidence字段"
        
        # 验证置信度在[0, 1]区间内
        assert 0 <= result.confidence <= 1, f"置信度应该在[0, 1]区间内，实际值：{result.confidence}"
    
    # Feature: intelligent-feature-extraction, Property 2: 设备类型识别准确率
    @settings(max_examples=100)
    def test_property_2_recognition_accuracy(self, recognizer):
        """
        属性2：设备类型识别准确率
        验证需求：2.1.1
        
        对于包含已知设备类型的测试集，设备类型识别的准确率应该 >85%
        """
        # 测试用例：从配置中的设备类型生成测试文本
        test_cases = []
        
        # 精确匹配测试
        for device_type in DEVICE_TYPE_CONFIG['device_types']:
            test_cases.append((device_type, device_type))
        
        # 前缀+类型组合测试
        for prefix, types in DEVICE_TYPE_CONFIG['prefix_keywords'].items():
            for dtype in types:
                expected = f"{prefix}{dtype}"
                test_cases.append((f"{prefix}{dtype}", expected))
                test_cases.append((f"{prefix} {dtype}", expected))
        
        # 执行测试
        correct = 0
        total = len(test_cases)
        
        for text, expected in test_cases:
            result = recognizer.recognize(text)
            # 检查是否识别正确（子类型匹配或主类型匹配）
            if result.sub_type == expected or expected in result.sub_type or result.sub_type in expected:
                correct += 1
        
        accuracy = correct / total if total > 0 else 0
        
        # 验证准确率 >85%
        assert accuracy > 0.85, f"识别准确率应该 >85%，实际准确率：{accuracy:.2%} ({correct}/{total})"
    
    # Feature: intelligent-feature-extraction, Property 3: 参数不匹配时设备类型仍然正确
    @given(
        device_type=st.sampled_from(DEVICE_TYPE_CONFIG['device_types']),
        wrong_param=st.text(min_size=5, max_size=50)
    )
    @settings(max_examples=100)
    def test_property_3_device_type_correct_despite_wrong_params(self, recognizer, device_type, wrong_param):
        """
        属性3：参数不匹配时设备类型仍然正确
        验证需求：2.1.4
        
        即使参数信息不完整或不匹配，设备类型识别也应该返回正确的设备类型
        """
        # 构造包含正确设备类型但参数错误的文本
        text = f"{device_type} {wrong_param}"
        
        result = recognizer.recognize(text)
        
        # 验证设备类型识别正确
        assert result.sub_type == device_type or device_type in result.sub_type, \
            f"应该识别出设备类型 {device_type}，实际识别为 {result.sub_type}"
        
        # 验证置信度合理
        assert result.confidence > 0.7, f"置信度应该 >0.7，实际值：{result.confidence}"
