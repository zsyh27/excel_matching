"""
规则管理 API 集成测试
测试 Flask API 的规则管理端点

验证需求: 22.1, 22.2, 22.3, 22.4, 22.5, 22.6, 22.7
"""

import os
import sys
import pytest
import json

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.data_loader import Device, Rule
from modules.text_preprocessor import TextPreprocessor


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def setup_database():
    """设置测试数据库"""
    # 创建内存数据库
    db_manager = DatabaseManager('sqlite:///:memory:')
    db_manager.create_tables()
    
    # 创建数据库加载器
    config = {
        'text_preprocessing': {
            'feature_split_chars': [',', '，', ' '],
            'normalize_chars': {'（': '(', '）': ')'}
        }
    }
    preprocessor = TextPreprocessor(config)
    db_loader = DatabaseLoader(db_manager, preprocessor)
    
    # 添加测试设备
    test_devices = [
        Device(
            device_id='TEST_DEVICE_001',
            brand='霍尼韦尔',
            device_name='温度传感器',
            spec_model='T7350A1008',
            detailed_params='测量范围: -40~120℃',
            unit_price=450.0
        ),
        Device(
            device_id='TEST_DEVICE_002',
            brand='西门子',
            device_name='压力传感器',
            spec_model='QBE2003-P25',
            detailed_params='测量范围: 0-25bar',
            unit_price=680.0
        )
    ]
    
    for device in test_devices:
        db_loader.add_device(device, auto_generate_rule=False)
    
    # 添加测试规则
    test_rule = Rule(
        rule_id='R_TEST_DEVICE_001',  # 使用规则生成器的 ID 格式
        target_device_id='TEST_DEVICE_001',
        auto_extracted_features=['霍尼韦尔', '温度传感器', 'T7350A1008'],
        feature_weights={'霍尼韦尔': 3.0, '温度传感器': 2.5, 'T7350A1008': 3.0},
        match_threshold=2.0,
        remark='测试规则'
    )
    db_loader.add_rule(test_rule)
    
    # 将数据库加载器注入到 app 的 data_loader
    from app import data_loader
    data_loader.loader = db_loader
    
    yield db_loader
    
    # 清理
    db_manager.close()


class TestGetRules:
    """测试 GET /api/rules 端点 - 验证需求 22.1, 22.3"""
    
    def test_get_all_rules(self, client, setup_database):
        """测试获取所有规则"""
        response = client.get('/api/rules')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'rules' in data['data']
        assert 'total' in data['data']
        assert data['data']['total'] >= 1
        
        # 验证规则包含必要字段
        rule = data['data']['rules'][0]
        assert 'rule_id' in rule
        assert 'target_device_id' in rule
        assert 'auto_extracted_features' in rule
        assert 'feature_weights' in rule
        assert 'match_threshold' in rule
        assert 'device_name' in rule
    
    def test_get_rules_by_device_id(self, client, setup_database):
        """测试按设备 ID 过滤规则 - 验证需求 22.3"""
        response = client.get('/api/rules?device_id=TEST_DEVICE_001')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['total'] >= 1
        
        # 验证所有规则都属于指定设备
        for rule in data['data']['rules']:
            assert rule['target_device_id'] == 'TEST_DEVICE_001'
    
    def test_get_rules_by_nonexistent_device(self, client, setup_database):
        """测试查询不存在设备的规则"""
        response = client.get('/api/rules?device_id=NONEXISTENT_DEVICE')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['total'] == 0
        assert data['data']['rules'] == []


class TestGetRuleById:
    """测试 GET /api/rules/:id 端点 - 验证需求 22.2"""
    
    def test_get_rule_by_id_success(self, client, setup_database):
        """测试成功获取规则详情"""
        response = client.get('/api/rules/R_TEST_DEVICE_001')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        
        # 验证规则详情
        rule = data['data']
        assert rule['rule_id'] == 'R_TEST_DEVICE_001'
        assert rule['target_device_id'] == 'TEST_DEVICE_001'
        assert 'device' in rule
        assert rule['device']['device_id'] == 'TEST_DEVICE_001'
        assert rule['device']['device_name'] == '温度传感器'
        assert rule['device']['brand'] == '霍尼韦尔'
    
    def test_get_nonexistent_rule(self, client, setup_database):
        """测试获取不存在的规则"""
        response = client.get('/api/rules/NONEXISTENT_RULE')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'RULE_NOT_FOUND'


class TestCreateRule:
    """测试 POST /api/rules 端点 - 验证需求 22.4"""
    
    def test_create_rule_success(self, client, setup_database):
        """测试成功创建规则"""
        new_rule = {
            'rule_id': 'TEST_RULE_002',
            'target_device_id': 'TEST_DEVICE_002',
            'auto_extracted_features': ['西门子', '压力传感器', 'QBE2003-P25'],
            'feature_weights': {'西门子': 3.0, '压力传感器': 2.5, 'QBE2003-P25': 3.0},
            'match_threshold': 2.0,
            'remark': '新创建的规则'
        }
        
        response = client.post(
            '/api/rules',
            data=json.dumps(new_rule),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['rule_id'] == 'TEST_RULE_002'
        assert '规则创建成功' in data['message']
        
        # 验证规则已保存
        verify_response = client.get('/api/rules/TEST_RULE_002')
        assert verify_response.status_code == 200
    
    def test_create_rule_with_nonexistent_device(self, client, setup_database):
        """测试创建规则时设备不存在"""
        new_rule = {
            'rule_id': 'TEST_RULE_003',
            'target_device_id': 'NONEXISTENT_DEVICE',
            'auto_extracted_features': ['测试'],
            'feature_weights': {'测试': 1.0},
            'match_threshold': 2.0
        }
        
        response = client.post(
            '/api/rules',
            data=json.dumps(new_rule),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'DEVICE_NOT_FOUND'
    
    def test_create_duplicate_rule(self, client, setup_database):
        """测试创建重复规则"""
        duplicate_rule = {
            'rule_id': 'R_TEST_DEVICE_001',  # 已存在的规则 ID
            'target_device_id': 'TEST_DEVICE_001',
            'auto_extracted_features': ['测试'],
            'feature_weights': {'测试': 1.0},
            'match_threshold': 2.0
        }
        
        response = client.post(
            '/api/rules',
            data=json.dumps(duplicate_rule),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'RULE_ALREADY_EXISTS'
    
    def test_create_rule_missing_fields(self, client, setup_database):
        """测试创建规则时缺少必需字段"""
        incomplete_rule = {
            'rule_id': 'TEST_RULE_004',
            'target_device_id': 'TEST_DEVICE_001'
            # 缺少其他必需字段
        }
        
        response = client.post(
            '/api/rules',
            data=json.dumps(incomplete_rule),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'VALIDATION_ERROR'


class TestUpdateRule:
    """测试 PUT /api/rules/:id 端点 - 验证需求 22.5"""
    
    def test_update_rule_success(self, client, setup_database):
        """测试成功更新规则"""
        updated_data = {
            'auto_extracted_features': ['霍尼韦尔', '温度传感器', 'T7350A1008', '新特征'],
            'feature_weights': {'霍尼韦尔': 3.0, '温度传感器': 2.5, 'T7350A1008': 3.0, '新特征': 2.0},
            'match_threshold': 2.5,
            'remark': '更新后的规则'
        }
        
        response = client.put(
            '/api/rules/R_TEST_DEVICE_001',
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['rule_id'] == 'R_TEST_DEVICE_001'
        assert '规则更新成功' in data['message']
        
        # 验证规则已更新
        verify_response = client.get('/api/rules/R_TEST_DEVICE_001')
        verify_data = json.loads(verify_response.data)
        assert verify_data['data']['match_threshold'] == 2.5
        assert verify_data['data']['remark'] == '更新后的规则'
    
    def test_update_nonexistent_rule(self, client, setup_database):
        """测试更新不存在的规则"""
        updated_data = {
            'match_threshold': 3.0
        }
        
        response = client.put(
            '/api/rules/NONEXISTENT_RULE',
            data=json.dumps(updated_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'RULE_NOT_FOUND'


class TestDeleteRule:
    """测试 DELETE /api/rules/:id 端点 - 验证需求 22.6"""
    
    def test_delete_rule_success(self, client, setup_database):
        """测试成功删除规则"""
        response = client.delete('/api/rules/R_TEST_DEVICE_001')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['rule_id'] == 'R_TEST_DEVICE_001'
        assert '规则删除成功' in data['message']
        
        # 验证规则已删除
        verify_response = client.get('/api/rules/R_TEST_DEVICE_001')
        assert verify_response.status_code == 404
    
    def test_delete_nonexistent_rule(self, client, setup_database):
        """测试删除不存在的规则"""
        response = client.delete('/api/rules/NONEXISTENT_RULE')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'RULE_NOT_FOUND'


class TestGenerateRules:
    """测试 POST /api/rules/generate 端点 - 验证需求 22.7"""
    
    def test_generate_rules_success(self, client, setup_database):
        """测试成功批量生成规则"""
        request_data = {
            'device_ids': ['TEST_DEVICE_002'],
            'force_regenerate': False
        }
        
        response = client.post(
            '/api/rules/generate',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['generated'] >= 1
        assert len(data['data']['details']) == 1
        assert data['data']['details'][0]['device_id'] == 'TEST_DEVICE_002'
        assert data['data']['details'][0]['status'] == 'generated'
    
    def test_generate_rules_force_regenerate(self, client, setup_database):
        """测试强制重新生成规则"""
        request_data = {
            'device_ids': ['TEST_DEVICE_001'],
            'force_regenerate': True
        }
        
        response = client.post(
            '/api/rules/generate',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['updated'] >= 1
        assert data['data']['details'][0]['status'] == 'updated'
    
    def test_generate_rules_skip_existing(self, client, setup_database):
        """测试跳过已有规则的设备"""
        request_data = {
            'device_ids': ['TEST_DEVICE_001'],
            'force_regenerate': False
        }
        
        response = client.post(
            '/api/rules/generate',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['details'][0]['status'] == 'skipped'
    
    def test_generate_rules_nonexistent_device(self, client, setup_database):
        """测试为不存在的设备生成规则"""
        request_data = {
            'device_ids': ['NONEXISTENT_DEVICE'],
            'force_regenerate': False
        }
        
        response = client.post(
            '/api/rules/generate',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['failed'] == 1
        assert data['data']['details'][0]['status'] == 'failed'
        assert '设备不存在' in data['data']['details'][0]['reason']
    
    def test_generate_rules_missing_device_ids(self, client, setup_database):
        """测试缺少 device_ids 参数"""
        request_data = {
            'force_regenerate': False
        }
        
        response = client.post(
            '/api/rules/generate',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'VALIDATION_ERROR'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
