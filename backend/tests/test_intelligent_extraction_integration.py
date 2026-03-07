"""
智能提取系统集成测试

测试完整的提取和匹配流程
Feature: intelligent-feature-extraction
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.intelligent_extraction.api_handler import IntelligentExtractionAPI
from .test_intelligent_extraction_config import FULL_CONFIG


class MockDeviceLoader:
    """模拟设备加载器"""
    def get_all_devices(self):
        return [
            {
                'device_id': 'honeywell_co_001',
                'device_name': 'CO浓度探测器',
                'device_type': 'CO浓度探测器',
                'brand': '霍尼韦尔',
                'spec_model': 'CO-100',
                'raw_description': 'CO浓度探测器 量程0-250ppm 输出4-20mA',
                'key_params': '{"量程": "0-250ppm", "输出": "4-20mA", "精度": "±5%"}'
            },
            {
                'device_id': 'siemens_temp_001',
                'device_name': '温度传感器',
                'device_type': '温度传感器',
                'brand': '西门子',
                'spec_model': 'T-200',
                'raw_description': '温度传感器 量程-40~80℃ 输出4-20mA',
                'key_params': '{"量程": "-40~80℃", "输出": "4-20mA"}'
            }
        ]
    
    def get_devices_by_type(self, device_type):
        return [d for d in self.get_all_devices() if d['device_type'] == device_type]


class TestIntelligentExtractionIntegration:
    """智能提取系统集成测试"""
    
    @pytest.fixture
    def api(self):
        """创建API实例"""
        return IntelligentExtractionAPI(FULL_CONFIG, MockDeviceLoader())
    
    def test_extract_api(self, api):
        """测试提取API"""
        text = "CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%"
        result = api.extract(text)
        
        assert result['success'] is True
        assert 'data' in result
        
        # 验证设备类型提取
        device_type = result['data']['device_type']
        assert device_type['sub_type'] == 'CO浓度探测器' or 'CO' in device_type['sub_type']
        assert device_type['confidence'] > 0.7
        
        # 验证参数提取
        parameters = result['data']['parameters']
        assert parameters['range'] is not None
        assert parameters['output'] is not None
        assert parameters['accuracy'] is not None
    
    def test_match_api(self, api):
        """测试匹配API"""
        text = "CO浓度探测器 量程0~250ppm 输出4~20mA"
        result = api.match(text, top_k=5)
        
        assert result['success'] is True
        assert 'data' in result
        
        # 验证候选设备
        candidates = result['data']['candidates']
        assert len(candidates) > 0
        assert len(candidates) <= 5
        
        # 验证第一个候选设备
        top_candidate = candidates[0]
        assert 'device_id' in top_candidate
        assert 'total_score' in top_candidate
        assert top_candidate['total_score'] > 0
    
    def test_preview_api(self, api):
        """测试预览API"""
        text = "CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%"
        result = api.preview(text)
        
        assert result['success'] is True
        assert 'data' in result
        
        data = result['data']
        
        # 验证五步流程
        assert 'step1_device_type' in data
        assert 'step2_parameters' in data
        assert 'step3_auxiliary' in data
        assert 'step4_matching' in data
        assert 'step5_ui_preview' in data
        
        # 验证调试信息
        assert 'debug_info' in data
        assert 'performance' in data['debug_info']
    
    def test_batch_match_api(self, api):
        """测试批量匹配API"""
        items = [
            {'text': 'CO浓度探测器 量程0~250ppm'},
            {'text': '温度传感器 量程-40~80℃'}
        ]
        
        result = api.match_batch(items, top_k=3)
        
        assert result['success'] is True
        assert 'data' in result
        assert len(result['data']) == 2
    
    def test_empty_input_error(self, api):
        """测试空输入错误处理"""
        result = api.extract("")
        
        assert result['success'] is False
        assert 'error' in result
        assert result['error']['code'] == 'EMPTY_INPUT'
    
    def test_performance(self, api):
        """测试性能要求"""
        text = "CO浓度探测器 量程0~250ppm 输出4~20mA"
        result = api.match(text)
        
        assert result['success'] is True
        
        # 验证响应时间 <500ms
        total_time = result['performance']['total_time_ms']
        assert total_time < 500, f"响应时间应该 <500ms，实际：{total_time}ms"
