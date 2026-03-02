# -*- coding: utf-8 -*-
"""
智能设备解析API单元测试

测试设备描述解析API端点的功能
验证需求: 11.2, 11.3
"""

import pytest
import json
from unittest.mock import Mock, patch
from modules.intelligent_device.device_description_parser import ParseResult


@pytest.fixture
def client():
    """创建测试客户端"""
    from backend.app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_parse_api_success(client):
    """测试正常解析流程"""
    # 准备测试数据
    test_data = {
        'description': '西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA',
        'price': 1250.00
    }
    
    # 发送请求
    response = client.post(
        '/api/devices/parse',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # 验证响应
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert 'data' in data
    
    # 验证解析结果
    result = data['data']
    assert result['brand'] == '西门子'
    assert result['device_type'] == 'CO2传感器'
    assert result['model'] == 'QAA2061'
    assert 'key_params' in result
    assert 'confidence_score' in result
    assert 0.0 <= result['confidence_score'] <= 1.0
    assert result['price'] == 1250.00


def test_parse_api_without_price(client):
    """测试不提供价格的解析"""
    test_data = {
        'description': '霍尼韦尔 温度传感器 T7350A'
    }
    
    response = client.post(
        '/api/devices/parse',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert 'data' in data
    assert 'price' not in data['data']


def test_parse_api_missing_description(client):
    """测试缺少描述字段"""
    test_data = {
        'price': 1000.00
    }
    
    response = client.post(
        '/api/devices/parse',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['error_code'] == 'MISSING_DESCRIPTION'


def test_parse_api_empty_description(client):
    """测试空描述"""
    test_data = {
        'description': '   ',
        'price': 1000.00
    }
    
    response = client.post(
        '/api/devices/parse',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['error_code'] == 'EMPTY_DESCRIPTION'


def test_parse_api_invalid_price_negative(client):
    """测试负数价格"""
    test_data = {
        'description': '西门子 CO2传感器',
        'price': -100.00
    }
    
    response = client.post(
        '/api/devices/parse',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['error_code'] == 'INVALID_PRICE'


def test_parse_api_invalid_price_format(client):
    """测试无效价格格式"""
    test_data = {
        'description': '西门子 CO2传感器',
        'price': 'invalid'
    }
    
    response = client.post(
        '/api/devices/parse',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['error_code'] == 'INVALID_PRICE'


def test_parse_api_missing_data(client):
    """测试缺少请求数据"""
    response = client.post(
        '/api/devices/parse',
        data='',
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['error_code'] in ['INVALID_JSON', 'MISSING_DATA']


def test_parse_api_partial_recognition(client):
    """测试部分识别的情况"""
    test_data = {
        'description': '未知品牌 某种设备 ABC123',
        'price': 500.00
    }
    
    response = client.post(
        '/api/devices/parse',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # 即使部分识别失败，也应该返回成功（但置信度较低）
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert 'data' in data
    
    # 验证置信度较低
    result = data['data']
    assert result['confidence_score'] < 0.8


def test_parse_api_response_format(client):
    """测试返回数据格式"""
    test_data = {
        'description': '西门子 CO2传感器 QAA2061',
        'price': 1000.00
    }
    
    response = client.post(
        '/api/devices/parse',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # 验证响应结构
    assert 'success' in data
    assert 'data' in data
    
    result = data['data']
    # 验证所有必需字段都存在
    required_fields = ['brand', 'device_type', 'model', 'key_params', 
                      'confidence_score', 'unrecognized_text']
    for field in required_fields:
        assert field in result, f"缺少字段: {field}"
    
    # 验证数据类型
    assert isinstance(result['key_params'], dict)
    assert isinstance(result['confidence_score'], (int, float))
    assert isinstance(result['unrecognized_text'], list)


def test_parse_api_unrecognized_text_tracking(client):
    """测试未识别文本追踪"""
    test_data = {
        'description': '西门子 CO2传感器 QAA2061 额外的未知文本',
        'price': 1000.00
    }
    
    response = client.post(
        '/api/devices/parse',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    result = data['data']
    # 应该有未识别的文本
    assert 'unrecognized_text' in result
    assert isinstance(result['unrecognized_text'], list)
