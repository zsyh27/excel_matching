"""
测试设备管理 API 端点

验证需求: 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7
"""

import pytest
import json
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, data_loader
from modules.data_loader import Device


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_device():
    """创建示例设备数据"""
    return {
        'device_id': 'TEST_DEVICE_001',
        'brand': '测试品牌',
        'device_name': '测试设备',
        'spec_model': 'TEST-MODEL-001',
        'detailed_params': '测试参数：温度范围 0-100℃',
        'unit_price': 999.99
    }


class TestDeviceAPI:
    """设备管理 API 测试类"""
    
    def test_get_devices_basic(self, client):
        """
        测试 GET /api/devices - 基本功能
        验证需求: 21.1
        """
        response = client.get('/api/devices')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'devices' in data['data']
        assert 'total' in data['data']
        assert 'page' in data['data']
        assert 'page_size' in data['data']
    
    def test_get_devices_with_filters(self, client):
        """
        测试 GET /api/devices - 带过滤参数
        验证需求: 21.1
        """
        # 测试品牌过滤
        response = client.get('/api/devices?brand=霍尼韦尔')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 测试名称搜索
        response = client.get('/api/devices?name=传感器')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 测试价格范围
        response = client.get('/api/devices?min_price=100&max_price=1000')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_get_devices_with_pagination(self, client):
        """
        测试 GET /api/devices - 分页功能
        验证需求: 21.1
        """
        response = client.get('/api/devices?page=1&page_size=10')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['page'] == 1
        assert data['data']['page_size'] == 10
        assert len(data['data']['devices']) <= 10
    
    def test_get_device_by_id_not_found(self, client):
        """
        测试 GET /api/devices/:id - 设备不存在
        验证需求: 21.2
        """
        # 跳过测试如果不是数据库模式
        if not hasattr(data_loader, 'db_loader') or not data_loader.db_loader:
            pytest.skip("需要数据库模式")
        
        response = client.get('/api/devices/NONEXISTENT_DEVICE')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'DEVICE_NOT_FOUND'
    
    def test_create_device_missing_fields(self, client):
        """
        测试 POST /api/devices - 缺少必需字段
        验证需求: 21.3, 21.6, 21.7
        """
        # 跳过测试如果不是数据库模式
        if not hasattr(data_loader, 'db_loader') or not data_loader.db_loader:
            pytest.skip("需要数据库模式")
        
        # 缺少必需字段
        incomplete_device = {
            'device_id': 'TEST_001',
            'brand': '测试品牌'
            # 缺少其他必需字段
        }
        
        response = client.post(
            '/api/devices',
            data=json.dumps(incomplete_device),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'VALIDATION_ERROR'
    
    def test_create_device_empty_body(self, client):
        """
        测试 POST /api/devices - 空请求体
        验证需求: 21.3, 21.6, 21.7
        """
        # 跳过测试如果不是数据库模式
        if not hasattr(data_loader, 'db_loader') or not data_loader.db_loader:
            pytest.skip("需要数据库模式")
        
        response = client.post(
            '/api/devices',
            data='',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'MISSING_DATA'
    
    def test_update_device_not_found(self, client):
        """
        测试 PUT /api/devices/:id - 设备不存在
        验证需求: 21.4, 21.6, 21.7
        """
        # 跳过测试如果不是数据库模式
        if not hasattr(data_loader, 'db_loader') or not data_loader.db_loader:
            pytest.skip("需要数据库模式")
        
        update_data = {
            'brand': '新品牌',
            'unit_price': 1500.00
        }
        
        response = client.put(
            '/api/devices/NONEXISTENT_DEVICE',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'DEVICE_NOT_FOUND'
    
    def test_delete_device_not_found(self, client):
        """
        测试 DELETE /api/devices/:id - 设备不存在
        验证需求: 21.5, 21.6, 21.7
        """
        # 跳过测试如果不是数据库模式
        if not hasattr(data_loader, 'db_loader') or not data_loader.db_loader:
            pytest.skip("需要数据库模式")
        
        response = client.delete('/api/devices/NONEXISTENT_DEVICE')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'DEVICE_NOT_FOUND'
    
    def test_error_response_format(self, client):
        """
        测试错误响应格式的一致性
        验证需求: 21.6, 21.7
        """
        # 跳过测试如果不是数据库模式
        if not hasattr(data_loader, 'db_loader') or not data_loader.db_loader:
            pytest.skip("需要数据库模式")
        
        response = client.get('/api/devices/NONEXISTENT')
        data = json.loads(response.data)
        
        # 验证错误响应包含必需字段
        assert 'success' in data
        assert data['success'] is False
        assert 'error_code' in data
        assert 'error_message' in data
        
        # 验证 HTTP 状态码适当
        assert response.status_code in [400, 404, 500]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
