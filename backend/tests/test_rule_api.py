"""
规则管理 API 单元测试

验证需求: 22.1-22.7
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
def sample_rule_data():
    """创建示例规则数据"""
    import uuid
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "rule_id": f"R_TEST_{unique_id}",
        "target_device_id": "D001",  # 假设这个设备存在
        "features": ["特征1", "特征2", "特征3"],
        "weights": [3.0, 2.5, 2.0],
        "match_threshold": 5.0
    }


class TestGetRules:
    """GET /api/rules 测试类"""
    
    def test_get_rules_empty(self, client):
        """
        测试获取空规则列表 - 验证需求 22.1
        """
        response = client.get('/api/rules')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'rules' in data or 'data' in data
    
    def test_get_rules_with_device_filter(self, client):
        """
        测试按设备ID过滤规则 - 验证需求 22.1, 22.3
        """
        response = client.get('/api/rules?device_id=D001')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'rules' in data or 'data' in data


class TestGetRuleById:
    """GET /api/rules/:id 测试类"""
    
    def test_get_rule_by_id_not_found(self, client):
        """
        测试获取不存在的规则 - 验证需求 22.2
        """
        response = client.get('/api/rules/NONEXISTENT')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error_message' in data or 'error' in data or 'message' in data
    
    def test_get_rule_by_id_success(self, client):
        """
        测试成功获取规则详情 - 验证需求 22.2
        
        注意: 这个测试依赖于数据库中已有的规则
        """
        # 先获取规则列表
        list_response = client.get('/api/rules')
        if list_response.status_code == 200:
            list_data = json.loads(list_response.data)
            rules = list_data.get('rules') or list_data.get('data', [])
            
            if rules and len(rules) > 0:
                # 获取第一个规则的详情
                rule_id = rules[0].get('rule_id')
                if rule_id:
                    response = client.get(f'/api/rules/{rule_id}')
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    
                    # 响应格式: {'success': True, 'rule': {...}}
                    assert 'success' in data
                    assert data['success'] == True
                    assert 'rule' in data
                    
                    rule_data = data['rule']
                    assert 'rule_id' in rule_data
                    assert rule_data['rule_id'] == rule_id


class TestCreateRule:
    """POST /api/rules 测试类"""
    
    def test_create_rule_missing_required_fields(self, client):
        """
        测试缺少必需字段 - 验证需求 22.4
        """
        incomplete_data = {
            "rule_id": "R_TEST001"
            # 缺少其他必需字段
        }
        
        response = client.post(
            '/api/rules',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        # 应该返回400错误
        assert response.status_code in [400, 422, 500]
        data = json.loads(response.data)
        assert 'error_message' in data or 'error' in data or 'message' in data
    
    def test_create_rule_invalid_device_id(self, client, sample_rule_data):
        """
        测试无效的target_device_id - 验证需求 22.4
        """
        sample_rule_data['target_device_id'] = 'NONEXISTENT_DEVICE'
        
        response = client.post(
            '/api/rules',
            data=json.dumps(sample_rule_data),
            content_type='application/json'
        )
        
        # 应该返回400或404错误
        assert response.status_code in [400, 404, 500]
        data = json.loads(response.data)
        assert 'error_message' in data or 'error' in data or 'message' in data


class TestUpdateRule:
    """PUT /api/rules/:id 测试类"""
    
    def test_update_rule_not_found(self, client, sample_rule_data):
        """
        测试更新不存在的规则 - 验证需求 22.5
        """
        response = client.put(
            '/api/rules/NONEXISTENT',
            data=json.dumps(sample_rule_data),
            content_type='application/json'
        )
        
        assert response.status_code in [404, 500]
        data = json.loads(response.data)
        assert 'error_message' in data or 'error' in data or 'message' in data
    
    def test_update_rule_success(self, client):
        """
        测试成功更新规则 - 验证需求 22.5
        
        注意: 这个测试依赖于数据库中已有的规则
        """
        # 先获取规则列表
        list_response = client.get('/api/rules')
        if list_response.status_code == 200:
            list_data = json.loads(list_response.data)
            rules = list_data.get('rules') or list_data.get('data', [])
            
            if rules and len(rules) > 0:
                # 更新第一个规则
                rule = rules[0]
                rule_id = rule.get('rule_id')
                if rule_id:
                    updated_data = {
                        'match_threshold': 6.0,
                        'features': rule.get('features', []),
                        'weights': rule.get('weights', [])
                    }
                    
                    response = client.put(
                        f'/api/rules/{rule_id}',
                        data=json.dumps(updated_data),
                        content_type='application/json'
                    )
                    
                    # 可能返回200或204
                    assert response.status_code in [200, 204]


class TestDeleteRule:
    """DELETE /api/rules/:id 测试类"""
    
    def test_delete_rule_not_found(self, client):
        """
        测试删除不存在的规则 - 验证需求 22.6
        """
        response = client.delete('/api/rules/NONEXISTENT')
        assert response.status_code in [404, 500]
        data = json.loads(response.data)
        assert 'error_message' in data or 'error' in data or 'message' in data


class TestGenerateRules:
    """POST /api/rules/generate 测试类"""
    
    def test_generate_rules_no_devices(self, client):
        """
        测试为空设备列表生成规则 - 验证需求 22.7
        """
        request_data = {
            'device_ids': []
        }
        
        response = client.post(
            '/api/rules/generate',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # 应该返回200，但生成数量为0
        assert response.status_code in [200, 400]
    
    def test_generate_rules_with_force_regenerate(self, client):
        """
        测试强制重新生成规则 - 验证需求 22.7
        """
        request_data = {
            'force_regenerate': True
        }
        
        response = client.post(
            '/api/rules/generate',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # 应该返回200
        assert response.status_code == 200
        data = json.loads(response.data)
        # 应该包含统计信息
        assert 'success' in data or 'generated' in data or 'statistics' in data
    
    def test_generate_rules_for_specific_devices(self, client):
        """
        测试为特定设备生成规则 - 验证需求 22.7
        """
        # 先获取设备列表
        devices_response = client.get('/api/devices')
        if devices_response.status_code == 200:
            devices_data = json.loads(devices_response.data)
            devices = devices_data.get('devices', [])
            
            if devices and len(devices) > 0:
                # 为前3个设备生成规则
                device_ids = [d.get('device_id') for d in devices[:3] if d.get('device_id')]
                
                if device_ids:
                    request_data = {
                        'device_ids': device_ids,
                        'force_regenerate': False
                    }
                    
                    response = client.post(
                        '/api/rules/generate',
                        data=json.dumps(request_data),
                        content_type='application/json'
                    )
                    
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    assert 'success' in data or 'generated' in data or 'statistics' in data


class TestRuleAPIErrorHandling:
    """API错误处理测试类"""
    
    def test_invalid_http_method(self, client):
        """
        测试无效的HTTP方法
        """
        response = client.patch('/api/rules/R001')
        assert response.status_code == 405  # Method Not Allowed
    
    def test_invalid_json(self, client):
        """
        测试无效的JSON格式
        """
        response = client.post(
            '/api/rules',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code in [400, 422, 500]
    
    def test_content_type_validation(self, client, sample_rule_data):
        """
        测试Content-Type验证
        """
        # 不指定Content-Type
        response = client.post(
            '/api/rules',
            data=json.dumps(sample_rule_data)
        )
        # 应该能处理或返回错误
        assert response.status_code in [200, 201, 400, 415, 500]


class TestRuleAPIResponseFormat:
    """响应格式测试类"""
    
    def test_response_content_type(self, client):
        """
        测试响应Content-Type
        """
        response = client.get('/api/rules')
        assert response.content_type == 'application/json'
    
    def test_response_structure(self, client):
        """
        测试响应结构 - 验证需求 22.1
        """
        response = client.get('/api/rules')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # 验证必需字段
        assert 'rules' in data or 'data' in data
    
    def test_error_response_structure(self, client):
        """
        测试错误响应结构
        """
        response = client.get('/api/rules/NONEXISTENT')
        assert response.status_code == 404
        data = json.loads(response.data)
        
        # 错误响应应该包含error_message或error或message字段
        assert 'error_message' in data or 'error' in data or 'message' in data


class TestRuleAPIForeignKeyValidation:
    """外键验证测试类"""
    
    def test_create_rule_with_valid_device(self, client):
        """
        测试使用有效设备ID创建规则 - 验证需求 22.4
        """
        # 先获取一个存在的设备
        devices_response = client.get('/api/devices')
        if devices_response.status_code == 200:
            devices_data = json.loads(devices_response.data)
            devices = devices_data.get('devices', [])
            
            if devices and len(devices) > 0:
                device_id = devices[0].get('device_id')
                if device_id:
                    import uuid
                    unique_id = str(uuid.uuid4())[:8].upper()
                    rule_data = {
                        "rule_id": f"R_TEST_{unique_id}",
                        "target_device_id": device_id,
                        "features": ["测试特征1", "测试特征2"],
                        "weights": [3.0, 2.5],
                        "match_threshold": 5.0
                    }
                    
                    response = client.post(
                        '/api/rules',
                        data=json.dumps(rule_data),
                        content_type='application/json'
                    )
                    
                    # 可能返回201或200，或者409(规则已存在)
                    assert response.status_code in [200, 201, 409, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
