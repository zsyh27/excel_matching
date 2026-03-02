# -*- coding: utf-8 -*-
"""
智能设备错误处理边界情况测试

测试错误处理的边界情况和特殊场景
验证需求: 14.2, 14.3
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def client():
    """创建测试客户端"""
    from backend.app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_empty_input_error_handling(client):
    """
    测试空输入错误处理
    
    验证需求: 14.2
    """
    # 测试完全空的描述
    response = client.post(
        '/api/devices/parse',
        data=json.dumps({'description': ''}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['error_code'] == 'EMPTY_DESCRIPTION'
    assert '不能为空' in data['error_message']


def test_whitespace_only_input(client):
    """测试只包含空白字符的输入"""
    response = client.post(
        '/api/devices/parse',
        data=json.dumps({'description': '   \t\n  '}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['error_code'] == 'EMPTY_DESCRIPTION'


def test_null_description(client):
    """测试null描述"""
    response = client.post(
        '/api/devices/parse',
        data=json.dumps({'description': None}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['error_code'] in ['EMPTY_DESCRIPTION', 'MISSING_DESCRIPTION']


def test_database_connection_failure(client):
    """
    测试数据库连接失败处理
    
    验证需求: 14.3
    """
    with patch('backend.app.data_loader') as mock_loader:
        mock_loader.loader = Mock()
        # 模拟数据库连接失败
        mock_loader.loader.add_device = Mock(
            side_effect=Exception("Connection to database failed")
        )
        
        test_data = {
            'raw_description': '西门子 CO2传感器',
            'price': 1000.00
        }
        
        response = client.post(
            '/api/devices/intelligent',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # 应该返回500错误
        assert response.status_code == 500
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'error_code' in data
        assert 'error_message' in data
        # 错误消息应该是友好的，不暴露内部细节
        assert 'Connection to database failed' not in data['error_message']


def test_database_timeout(client):
    """测试数据库超时"""
    with patch('backend.app.data_loader') as mock_loader:
        mock_loader.loader = Mock()
        # 模拟数据库超时
        mock_loader.loader.add_device = Mock(
            side_effect=TimeoutError("Database operation timed out")
        )
        
        test_data = {
            'raw_description': '设备描述',
            'price': 1000.00
        }
        
        response = client.post(
            '/api/devices/intelligent',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        
        assert data['success'] is False


def test_very_long_description(client):
    """测试非常长的描述文本"""
    # 创建一个10000字符的描述
    long_description = '西门子 CO2传感器 ' * 1000
    
    test_data = {
        'description': long_description,
        'price': 1000.00
    }
    
    response = client.post(
        '/api/devices/parse',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # 应该能够处理，即使可能解析效果不好
    assert response.status_code in [200, 400, 500]
    data = json.loads(response.data)
    
    # 验证响应结构完整
    assert 'success' in data


def test_special_characters_in_description(client):
    """测试包含特殊字符的描述"""
    test_data = {
        'description': '西门子 CO2传感器 <script>alert("test")</script> @#$%^&*()',
        'price': 1000.00
    }
    
    response = client.post(
        '/api/devices/parse',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # 应该能够处理特殊字符
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True


def test_unicode_characters(client):
    """测试Unicode字符"""
    test_data = {
        'description': '西门子 CO2传感器 🔥 测试 ñ ü ö',
        'price': 1000.00
    }
    
    response = client.post(
        '/api/devices/parse',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True


def test_zero_price(client):
    """测试零价格"""
    test_data = {
        'description': '西门子 CO2传感器',
        'price': 0.0
    }
    
    response = client.post(
        '/api/devices/parse',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # 零价格应该是有效的
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert data['data']['price'] == 0.0


def test_very_large_price(client):
    """测试非常大的价格"""
    test_data = {
        'description': '西门子 CO2传感器',
        'price': 999999999.99
    }
    
    response = client.post(
        '/api/devices/parse',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert data['data']['price'] == 999999999.99


def test_price_with_many_decimals(client):
    """测试有很多小数位的价格"""
    test_data = {
        'description': '西门子 CO2传感器',
        'price': 1234.56789012345
    }
    
    response = client.post(
        '/api/devices/parse',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True


def test_confidence_score_boundary_values(client):
    """测试置信度边界值"""
    with patch('backend.app.data_loader') as mock_loader:
        mock_loader.loader = Mock()
        mock_loader.loader.add_device = Mock(return_value=True)
        
        # 测试0.0
        test_data = {
            'raw_description': '设备描述',
            'confidence_score': 0.0
        }
        
        response = client.post(
            '/api/devices/intelligent',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        
        # 测试1.0
        test_data['confidence_score'] = 1.0
        response = client.post(
            '/api/devices/intelligent',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201


def test_malformed_json(client):
    """测试格式错误的JSON"""
    response = client.post(
        '/api/devices/parse',
        data='{"description": "test"',  # 缺少结束括号
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['error_code'] in ['INVALID_JSON', 'MISSING_DATA']


def test_wrong_content_type(client):
    """测试错误的Content-Type"""
    response = client.post(
        '/api/devices/parse',
        data='description=test&price=100',
        content_type='application/x-www-form-urlencoded'
    )
    
    # Flask会尝试解析，但应该失败
    assert response.status_code in [400, 500]


def test_missing_content_type(client):
    """测试缺少Content-Type"""
    response = client.post(
        '/api/devices/parse',
        data=json.dumps({'description': '测试'}),
        # 不设置content_type
    )
    
    # 应该能够处理或返回错误
    assert response.status_code in [200, 400, 415]


def test_concurrent_requests_data_integrity(client):
    """测试并发请求的数据完整性"""
    import threading
    
    results = []
    
    def make_request():
        test_data = {
            'description': '西门子 CO2传感器',
            'price': 1000.00
        }
        response = client.post(
            '/api/devices/parse',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        results.append(response.status_code)
    
    # 创建10个并发请求
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 验证所有请求都成功
    assert all(status == 200 for status in results)


def test_parser_not_initialized(client):
    """测试解析器未初始化的情况"""
    with patch('backend.app.intelligent_parser', None):
        test_data = {
            'description': '西门子 CO2传感器',
            'price': 1000.00
        }
        
        response = client.post(
            '/api/devices/parse',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 503
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert data['error_code'] == 'CONFIG_ERROR'


def test_empty_key_params(client):
    """测试空的关键参数"""
    with patch('backend.app.data_loader') as mock_loader:
        mock_loader.loader = Mock()
        mock_loader.loader.add_device = Mock(return_value=True)
        
        test_data = {
            'raw_description': '设备描述',
            'key_params': {}  # 空字典
        }
        
        response = client.post(
            '/api/devices/intelligent',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        assert data['success'] is True


def test_null_optional_fields(client):
    """测试可选字段为null"""
    with patch('backend.app.data_loader') as mock_loader:
        mock_loader.loader = Mock()
        mock_loader.loader.add_device = Mock(return_value=True)
        
        test_data = {
            'raw_description': '设备描述',
            'brand': None,
            'device_type': None,
            'model': None,
            'price': None
        }
        
        response = client.post(
            '/api/devices/intelligent',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        assert data['success'] is True
