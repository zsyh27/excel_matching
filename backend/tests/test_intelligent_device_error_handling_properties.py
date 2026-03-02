# -*- coding: utf-8 -*-
"""
智能设备错误处理属性测试

使用属性测试验证错误处理的通用属性
验证需求: 11.7, 14.1, 14.4, 14.5

Feature: intelligent-device-input
"""

import pytest
import json
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import Mock, patch


@pytest.fixture
def client():
    """创建测试客户端"""
    from backend.app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# Feature: intelligent-device-input, Property 18: 错误信息具体性
@given(
    error_type=st.sampled_from([
        'missing_description',
        'empty_description',
        'invalid_price_negative',
        'invalid_price_format',
        'missing_raw_description',
        'empty_raw_description',
        'invalid_confidence'
    ])
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_18_error_message_specificity(client, error_type):
    """
    属性 18：错误信息具体性
    
    对于任意导致解析失败或API调用失败的输入，
    系统应该返回具体的错误信息，明确指出失败的原因
    
    验证：需求 11.7, 14.1
    """
    # 根据错误类型构造测试数据
    if error_type == 'missing_description':
        test_data = {'price': 1000.00}
        endpoint = '/api/devices/parse'
    elif error_type == 'empty_description':
        test_data = {'description': '   ', 'price': 1000.00}
        endpoint = '/api/devices/parse'
    elif error_type == 'invalid_price_negative':
        test_data = {'description': '设备描述', 'price': -100.00}
        endpoint = '/api/devices/parse'
    elif error_type == 'invalid_price_format':
        test_data = {'description': '设备描述', 'price': 'invalid'}
        endpoint = '/api/devices/parse'
    elif error_type == 'missing_raw_description':
        test_data = {'brand': '西门子'}
        endpoint = '/api/devices/intelligent'
    elif error_type == 'empty_raw_description':
        test_data = {'raw_description': '   '}
        endpoint = '/api/devices/intelligent'
    else:  # invalid_confidence
        test_data = {'raw_description': '设备描述', 'confidence_score': 1.5}
        endpoint = '/api/devices/intelligent'
    
    # 发送请求
    response = client.post(
        endpoint,
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # 验证返回错误响应
    assert response.status_code in [400, 500, 503]
    data = json.loads(response.data)
    
    # 验证错误响应包含具体信息
    assert data['success'] is False
    assert 'error_code' in data
    assert 'error_message' in data
    
    # 验证错误码不是通用的
    assert data['error_code'] != ''
    assert data['error_code'] != 'ERROR'
    
    # 验证错误消息不是通用的
    assert data['error_message'] != ''
    assert data['error_message'] != '错误'
    assert data['error_message'] != '失败'
    
    # 验证错误消息长度合理（至少5个字符）
    assert len(data['error_message']) >= 5


# Feature: intelligent-device-input, Property 19: 错误分类正确性
@given(
    error_scenario=st.sampled_from([
        ('validation', 'missing_description', 400),
        ('validation', 'invalid_price', 400),
        ('config', 'parser_not_initialized', 503),
        ('database', 'not_database_mode', 400)
    ])
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_19_error_classification_correctness(client, error_scenario):
    """
    属性 19：错误分类正确性
    
    对于任意系统错误，应该被正确分类为可恢复错误或不可恢复错误，
    以便采取适当的处理策略
    
    验证：需求 14.4
    """
    error_category, error_type, expected_status = error_scenario
    
    # 根据错误类型构造测试场景
    if error_type == 'missing_description':
        test_data = {'price': 1000.00}
        endpoint = '/api/devices/parse'
        mock_context = None
    elif error_type == 'invalid_price':
        test_data = {'description': '设备', 'price': -100}
        endpoint = '/api/devices/parse'
        mock_context = None
    elif error_type == 'parser_not_initialized':
        test_data = {'description': '设备'}
        endpoint = '/api/devices/parse'
        # 模拟解析器未初始化
        mock_context = patch('backend.app.intelligent_parser', None)
    elif error_type == 'not_database_mode':
        test_data = {'raw_description': '设备'}
        endpoint = '/api/devices/intelligent'
        # 模拟非数据库模式
        mock_context = patch('backend.app.data_loader.loader', None)
    else:
        return
    
    # 执行测试
    if mock_context:
        with mock_context:
            response = client.post(
                endpoint,
                data=json.dumps(test_data),
                content_type='application/json'
            )
    else:
        response = client.post(
            endpoint,
            data=json.dumps(test_data),
            content_type='application/json'
        )
    
    # 验证响应状态码
    assert response.status_code == expected_status
    data = json.loads(response.data)
    
    # 验证错误响应结构
    assert data['success'] is False
    assert 'error_code' in data
    assert 'error_message' in data
    
    # 验证错误分类
    if error_category == 'validation':
        # 验证错误应该是可恢复的
        assert response.status_code == 400
    elif error_category == 'config':
        # 配置错误应该返回503（服务不可用）
        assert response.status_code == 503
    elif error_category == 'database':
        # 数据库错误可能是400或500
        assert response.status_code in [400, 500, 503]


# Feature: intelligent-device-input, Property 20: 错误时数据完整性保护
@given(
    description=st.text(min_size=1, max_size=100),
    price=st.one_of(
        st.floats(min_value=-1000, max_value=-0.01),  # 负数价格（会导致错误）
        st.just('invalid')  # 无效格式（会导致错误）
    )
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_20_data_integrity_on_error(client, description, price):
    """
    属性 20：错误时数据完整性保护
    
    对于任意操作过程中发生的错误，
    系统应该确保现有数据不被破坏或部分修改，保持数据的完整性和一致性
    
    验证：需求 14.5
    
    注意：此测试验证API层面的数据完整性，即错误发生时不会返回部分数据或损坏的响应
    """
    # 构造会导致错误的请求
    test_data = {
        'description': description,
        'price': price
    }
    
    # 发送请求
    response = client.post(
        '/api/devices/parse',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # 验证响应
    data = json.loads(response.data)
    
    # 如果发生错误，验证响应结构完整
    if not data.get('success', False):
        # 验证错误响应包含必需字段
        assert 'success' in data
        assert 'error_code' in data
        assert 'error_message' in data
        
        # 验证不会返回部分数据
        # 如果success为False，不应该有data字段，或者data字段应该为None/空
        if 'data' in data:
            assert data['data'] is None or data['data'] == {}
        
        # 验证错误码和错误消息都有值
        assert data['error_code'] != ''
        assert data['error_message'] != ''
    else:
        # 如果成功，验证数据完整性
        assert 'data' in data
        result = data['data']
        
        # 验证所有必需字段都存在
        required_fields = ['brand', 'device_type', 'model', 'key_params', 
                          'confidence_score', 'unrecognized_text']
        for field in required_fields:
            assert field in result


# 边界情况测试：空输入
def test_error_handling_empty_input(client):
    """测试空输入错误处理"""
    response = client.post(
        '/api/devices/parse',
        data=json.dumps({'description': ''}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    
    assert data['success'] is False
    assert 'error_code' in data
    assert 'error_message' in data


# 边界情况测试：数据库连接失败
def test_error_handling_database_connection_failure(client):
    """测试数据库连接失败处理"""
    with patch('backend.app.data_loader') as mock_loader:
        mock_loader.loader = Mock()
        # 模拟数据库操作抛出异常
        mock_loader.loader.add_device = Mock(side_effect=Exception("Database connection failed"))
        
        test_data = {
            'raw_description': '设备描述',
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
