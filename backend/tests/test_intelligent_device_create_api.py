# -*- coding: utf-8 -*-
"""
智能设备创建API单元测试

测试设备创建API端点的功能
验证需求: 11.5
"""

import pytest
import json
from unittest.mock import Mock, patch


@pytest.fixture
def client():
    """创建测试客户端"""
    from backend.app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_database_mode():
    """模拟数据库模式"""
    with patch('backend.app.data_loader') as mock_loader:
        mock_loader.loader = Mock()
        mock_loader.loader.add_device = Mock(return_value=True)
        yield mock_loader


def test_create_device_success(client, mock_database_mode):
    """测试设备创建成功流程"""
    test_data = {
        'raw_description': '西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA',
        'brand': '西门子',
        'device_type': 'CO2传感器',
        'model': 'QAA2061',
        'key_params': {
            '量程': {'value': '0-2000ppm', 'required': True, 'data_type': 'range', 'unit': 'ppm'},
            '输出信号': {'value': '4-20mA', 'required': True, 'data_type': 'string', 'unit': 'mA'}
        },
        'price': 1250.00,
        'confidence_score': 0.92
    }
    
    response = client.post(
        '/api/devices/intelligent',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert 'data' in data
    assert 'id' in data['data']
    assert 'created_at' in data['data']


def test_create_device_minimal_fields(client, mock_database_mode):
    """测试只提供必需字段的设备创建"""
    test_data = {
        'raw_description': '某个设备的描述'
    }
    
    response = client.post(
        '/api/devices/intelligent',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    
    assert data['success'] is True


def test_create_device_missing_raw_description(client, mock_database_mode):
    """测试缺少原始描述字段"""
    test_data = {
        'brand': '西门子',
        'price': 1000.00
    }
    
    response = client.post(
        '/api/devices/intelligent',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['error_code'] == 'MISSING_RAW_DESCRIPTION'


def test_create_device_empty_raw_description(client, mock_database_mode):
    """测试空的原始描述"""
    test_data = {
        'raw_description': '   '
    }
    
    response = client.post(
        '/api/devices/intelligent',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['error_code'] == 'EMPTY_RAW_DESCRIPTION'


def test_create_device_invalid_price(client, mock_database_mode):
    """测试无效价格"""
    test_data = {
        'raw_description': '设备描述',
        'price': -100.00
    }
    
    response = client.post(
        '/api/devices/intelligent',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['error_code'] == 'INVALID_PRICE'


def test_create_device_invalid_confidence_score(client, mock_database_mode):
    """测试无效置信度"""
    test_data = {
        'raw_description': '设备描述',
        'confidence_score': 1.5  # 超出范围
    }
    
    response = client.post(
        '/api/devices/intelligent',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert data['error_code'] == 'INVALID_CONFIDENCE'


def test_create_device_database_error(client):
    """测试数据库错误处理"""
    with patch('backend.app.data_loader') as mock_loader:
        mock_loader.loader = Mock()
        mock_loader.loader.add_device = Mock(return_value=False)
        
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


def test_create_device_not_database_mode(client):
    """测试非数据库模式"""
    with patch('backend.app.data_loader') as mock_loader:
        mock_loader.loader = None
        
        test_data = {
            'raw_description': '设备描述'
        }
        
        response = client.post(
            '/api/devices/intelligent',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert data['error_code'] == 'NOT_DATABASE_MODE'


def test_create_device_with_key_params(client, mock_database_mode):
    """测试包含关键参数的设备创建"""
    test_data = {
        'raw_description': '西门子 CO2传感器 QAA2061',
        'brand': '西门子',
        'device_type': 'CO2传感器',
        'model': 'QAA2061',
        'key_params': {
            '量程': {
                'value': '0-2000ppm',
                'required': True,
                'data_type': 'range',
                'unit': 'ppm'
            }
        },
        'price': 1250.00,
        'confidence_score': 0.85
    }
    
    response = client.post(
        '/api/devices/intelligent',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert 'id' in data['data']
