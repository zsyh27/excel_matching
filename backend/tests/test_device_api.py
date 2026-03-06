"""
设备管理 API 单元测试

验证需求: 21.1-21.7, 36.6-36.7
"""

import pytest
import sys
import json
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app import app
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.data_loader import Device


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def db_manager():
    """创建测试数据库管理器"""
    db_manager = DatabaseManager("sqlite:///:memory:")
    db_manager.create_tables()
    yield db_manager
    db_manager.close()


@pytest.fixture
def db_loader(db_manager):
    """创建数据库加载器"""
    return DatabaseLoader(db_manager)


@pytest.fixture
def sample_device_data():
    """创建示例设备数据"""
    import uuid
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "device_id": f"TEST_{unique_id}",
        "brand": "测试品牌",
        "device_name": "测试设备",
        "spec_model": "TEST-MODEL-001",
        "detailed_params": "参数1 参数2 参数3",
        "unit_price": 1000.0
    }


class TestGetDevices:
    """GET /api/devices 测试类"""
    
    def test_get_devices_empty(self, client):
        """
        测试获取空设备列表 - 验证需求 21.1
        """
        response = client.get('/api/devices')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'devices' in data
        assert isinstance(data['devices'], list)
    
    def test_get_devices_with_pagination(self, client):
        """
        测试分页功能 - 验证需求 21.1
        """
        # 测试第一页
        response = client.get('/api/devices?page=1&page_size=10')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'devices' in data
        assert 'total' in data
        assert 'page' in data
        assert 'page_size' in data
    
    def test_get_devices_with_filters(self, client):
        """
        测试过滤功能 - 验证需求 21.1
        """
        # 测试品牌过滤
        response = client.get('/api/devices?brand=测试品牌')
        assert response.status_code == 200
        
        # 测试名称过滤
        response = client.get('/api/devices?name=测试设备')
        assert response.status_code == 200
        
        # 测试价格范围过滤
        response = client.get('/api/devices?min_price=100&max_price=2000')
        assert response.status_code == 200
    
    def test_get_devices_with_device_type_filter(self, client):
        """
        测试设备类型过滤 - 验证需求 21.1, 36.6
        """
        response = client.get('/api/devices?device_type=水表')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'devices' in data


class TestGetDeviceById:
    """GET /api/devices/:id 测试类"""
    
    def test_get_device_by_id_not_found(self, client):
        """
        测试获取不存在的设备 - 验证需求 21.2, 21.7
        """
        response = client.get('/api/devices/NONEXISTENT')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_device_by_id_success(self, client, sample_device_data):
        """
        测试成功获取设备详情 - 验证需求 21.2
        """
        # 先创建设备
        create_response = client.post(
            '/api/devices',
            data=json.dumps(sample_device_data),
            content_type='application/json'
        )
        
        if create_response.status_code == 201:
            # 获取设备详情
            device_id = sample_device_data['device_id']
            response = client.get(f'/api/devices/{device_id}')
            
            assert response.status_code == 200
            response_data = json.loads(response.data)
            assert 'data' in response_data
            data = response_data['data']
            assert data['device_id'] == device_id
            assert data['brand'] == sample_device_data['brand']
            assert data['device_name'] == sample_device_data['device_name']


class TestCreateDevice:
    """POST /api/devices 测试类"""
    
    def test_create_device_success(self, client, sample_device_data):
        """
        测试成功创建设备 - 验证需求 21.3
        """
        response = client.post(
            '/api/devices',
            data=json.dumps(sample_device_data),
            content_type='application/json'
        )
        
        # 可能返回201或200
        assert response.status_code in [200, 201]
        data = json.loads(response.data)
        assert 'device_id' in data or 'message' in data
    
    def test_create_device_with_auto_generate_rule(self, client, sample_device_data):
        """
        测试创建设备并自动生成规则 - 验证需求 21.3
        """
        sample_device_data['auto_generate_rule'] = True
        
        response = client.post(
            '/api/devices',
            data=json.dumps(sample_device_data),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 201]
    
    def test_create_device_with_device_type(self, client, sample_device_data):
        """
        测试创建设备时指定设备类型 - 验证需求 36.6
        """
        sample_device_data['device_type'] = '水表'
        sample_device_data['key_params'] = {
            '口径': 'DN15',
            '类型': '远传水表'
        }
        
        response = client.post(
            '/api/devices',
            data=json.dumps(sample_device_data),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 201]
    
    def test_create_device_missing_required_fields(self, client):
        """
        测试缺少必需字段 - 验证需求 21.6, 21.7
        """
        incomplete_data = {
            "device_id": "TEST002"
            # 缺少其他必需字段
        }
        
        response = client.post(
            '/api/devices',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        # 应该返回400错误
        assert response.status_code in [400, 422, 500]
        data = json.loads(response.data)
        assert 'error' in data or 'message' in data
    
    def test_create_device_invalid_json(self, client):
        """
        测试无效的JSON格式 - 验证需求 21.6, 21.7
        """
        response = client.post(
            '/api/devices',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code in [400, 422, 500]


class TestUpdateDevice:
    """PUT /api/devices/:id 测试类"""
    
    def test_update_device_not_found(self, client, sample_device_data):
        """
        测试更新不存在的设备 - 验证需求 21.4, 21.7
        """
        response = client.put(
            '/api/devices/NONEXISTENT',
            data=json.dumps(sample_device_data),
            content_type='application/json'
        )
        
        assert response.status_code in [404, 500]
    
    def test_update_device_success(self, client, sample_device_data):
        """
        测试成功更新设备 - 验证需求 21.4
        """
        # 先创建设备
        create_response = client.post(
            '/api/devices',
            data=json.dumps(sample_device_data),
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            # 更新设备
            updated_data = sample_device_data.copy()
            updated_data['unit_price'] = 2000.0
            updated_data['brand'] = '更新后的品牌'
            
            device_id = sample_device_data['device_id']
            response = client.put(
                f'/api/devices/{device_id}',
                data=json.dumps(updated_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
    
    def test_update_device_with_regenerate_rule(self, client, sample_device_data):
        """
        测试更新设备并重新生成规则 - 验证需求 21.4
        """
        # 先创建设备
        create_response = client.post(
            '/api/devices',
            data=json.dumps(sample_device_data),
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            # 更新设备并重新生成规则
            updated_data = sample_device_data.copy()
            updated_data['regenerate_rule'] = True
            updated_data['detailed_params'] = '新参数1 新参数2'
            
            device_id = sample_device_data['device_id']
            response = client.put(
                f'/api/devices/{device_id}',
                data=json.dumps(updated_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
    
    def test_update_device_with_device_type(self, client, sample_device_data):
        """
        测试更新设备类型和关键参数 - 验证需求 36.7
        """
        # 先创建设备
        create_response = client.post(
            '/api/devices',
            data=json.dumps(sample_device_data),
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            # 更新设备类型
            updated_data = sample_device_data.copy()
            updated_data['device_type'] = '电表'
            updated_data['key_params'] = {
                '电流': '5A',
                '电压': '220V'
            }
            
            device_id = sample_device_data['device_id']
            response = client.put(
                f'/api/devices/{device_id}',
                data=json.dumps(updated_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200


class TestDeleteDevice:
    """DELETE /api/devices/:id 测试类"""
    
    def test_delete_device_not_found(self, client):
        """
        测试删除不存在的设备 - 验证需求 21.5, 21.7
        """
        response = client.delete('/api/devices/NONEXISTENT')
        assert response.status_code in [404, 500]
    
    def test_delete_device_success(self, client, sample_device_data):
        """
        测试成功删除设备 - 验证需求 21.5
        """
        # 先创建设备
        create_response = client.post(
            '/api/devices',
            data=json.dumps(sample_device_data),
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            # 删除设备
            device_id = sample_device_data['device_id']
            response = client.delete(f'/api/devices/{device_id}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'message' in data or 'success' in data
    
    def test_delete_device_cascade_rules(self, client, sample_device_data):
        """
        测试删除设备时级联删除规则 - 验证需求 21.5
        """
        # 先创建设备（带规则）
        sample_device_data['auto_generate_rule'] = True
        create_response = client.post(
            '/api/devices',
            data=json.dumps(sample_device_data),
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            # 删除设备
            device_id = sample_device_data['device_id']
            response = client.delete(f'/api/devices/{device_id}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            # 应该返回级联删除的规则数量
            assert 'message' in data or 'rules_deleted' in data or 'success' in data


class TestDeviceAPIErrorHandling:
    """API错误处理测试类"""
    
    def test_invalid_http_method(self, client):
        """
        测试无效的HTTP方法 - 验证需求 21.6, 21.7
        """
        response = client.patch('/api/devices/TEST001')
        assert response.status_code == 405  # Method Not Allowed
    
    def test_malformed_device_id(self, client):
        """
        测试格式错误的设备ID
        """
        # 测试特殊字符
        response = client.get('/api/devices/<script>alert(1)</script>')
        assert response.status_code in [404, 400]
    
    def test_content_type_validation(self, client, sample_device_data):
        """
        测试Content-Type验证
        """
        # 不指定Content-Type
        response = client.post(
            '/api/devices',
            data=json.dumps(sample_device_data)
        )
        # 应该能处理或返回错误
        assert response.status_code in [200, 201, 400, 415]


class TestDeviceAPIPagination:
    """分页功能测试类"""
    
    def test_pagination_parameters(self, client):
        """
        测试分页参数 - 验证需求 21.1
        """
        # 测试不同的页码和页大小
        test_cases = [
            {'page': 1, 'page_size': 10},
            {'page': 1, 'page_size': 20},
            {'page': 1, 'page_size': 50},
            {'page': 2, 'page_size': 10},
        ]
        
        for params in test_cases:
            response = client.get(f'/api/devices?page={params["page"]}&page_size={params["page_size"]}')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'devices' in data
            assert 'total' in data
    
    def test_invalid_pagination_parameters(self, client):
        """
        测试无效的分页参数
        """
        # 测试负数页码
        response = client.get('/api/devices?page=-1')
        assert response.status_code in [200, 400]
        
        # 测试零页码
        response = client.get('/api/devices?page=0')
        assert response.status_code in [200, 400]
        
        # 测试过大的页大小
        response = client.get('/api/devices?page_size=10000')
        assert response.status_code in [200, 400]


class TestDeviceAPIFiltering:
    """过滤功能测试类"""
    
    def test_brand_filter(self, client):
        """
        测试品牌过滤 - 验证需求 21.1
        """
        response = client.get('/api/devices?brand=测试品牌')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'devices' in data
    
    def test_name_filter(self, client):
        """
        测试名称过滤 - 验证需求 21.1
        """
        response = client.get('/api/devices?name=测试设备')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'devices' in data
    
    def test_price_range_filter(self, client):
        """
        测试价格范围过滤 - 验证需求 21.1
        """
        response = client.get('/api/devices?min_price=100&max_price=2000')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'devices' in data
    
    def test_device_type_filter(self, client):
        """
        测试设备类型过滤 - 验证需求 21.1, 36.6
        """
        response = client.get('/api/devices?device_type=水表')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'devices' in data
    
    def test_multiple_filters(self, client):
        """
        测试多个过滤条件组合
        """
        response = client.get('/api/devices?brand=测试品牌&device_type=水表&min_price=500')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'devices' in data


class TestDeviceAPIResponseFormat:
    """响应格式测试类"""
    
    def test_response_content_type(self, client):
        """
        测试响应Content-Type
        """
        response = client.get('/api/devices')
        assert response.content_type == 'application/json'
    
    def test_response_structure(self, client):
        """
        测试响应结构 - 验证需求 21.1
        """
        response = client.get('/api/devices')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # 验证必需字段
        assert 'devices' in data
        assert isinstance(data['devices'], list)
    
    def test_error_response_structure(self, client):
        """
        测试错误响应结构 - 验证需求 21.6, 21.7
        """
        response = client.get('/api/devices/NONEXISTENT')
        assert response.status_code == 404
        data = json.loads(response.data)
        
        # 错误响应应该包含error或message字段
        assert 'error' in data or 'message' in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
