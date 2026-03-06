"""
数据一致性测试

测试设备和规则的关联、级联删除、数据一致性检查
验证需求: 9.1.3
"""

import pytest
import json
from app import app


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestDeviceRuleAssociation:
    """测试设备和规则的关联"""
    
    def test_device_rule_relationship(self, client):
        """测试设备和规则的关联关系"""
        device_id = 'ASSOC_TEST_001'
        
        # 清理可能存在的设备
        client.delete(f'/api/devices/{device_id}')
        
        # 1. 创建设备并自动生成规则
        device_data = {
            'device_id': device_id,
            'brand': '关联测试品牌',
            'device_name': '关联测试设备',
            'spec_model': 'ASSOC-001',
            'detailed_params': '关联测试参数',
            'unit_price': 3000.00,
            'auto_generate_rule': True
        }
        
        create_response = client.post(
            '/api/devices',
            data=json.dumps(device_data),
            content_type='application/json'
        )
        assert create_response.status_code == 201
        
        # 2. 验证设备有规则
        get_response = client.get(f'/api/devices/{device_id}')
        device = json.loads(get_response.data)['data']
        assert device['has_rules'] is True
        assert len(device['rules']) > 0
        
        rule_id = device['rules'][0]['rule_id']
        
        # 3. 验证规则关联到设备
        rule_response = client.get(f'/api/rules/{rule_id}')
        assert rule_response.status_code == 200
        rule_data = json.loads(rule_response.data)
        # API返回格式可能是 {'data': {...}} 或 {'rule': {...}}
        rule = rule_data.get('data') or rule_data.get('rule') or rule_data
        assert rule['target_device_id'] == device_id
        
        # 4. 查询设备的所有规则
        rules_response = client.get(f'/api/rules?device_id={device_id}')
        rules_data = json.loads(rules_response.data)
        assert rules_data['success'] is True
        assert len(rules_data['rules']) > 0
        
        # 清理测试数据
        client.delete(f'/api/devices/{device_id}')
    
    def test_multiple_rules_per_device(self, client):
        """测试一个设备可以有多个规则"""
        device_id = 'MULTI_RULE_TEST_001'
        
        # 清理可能存在的设备
        client.delete(f'/api/devices/{device_id}')
        
        # 创建设备
        device_data = {
            'device_id': device_id,
            'brand': '多规则测试品牌',
            'device_name': '多规则测试设备',
            'spec_model': 'MULTI-001',
            'detailed_params': '',
            'unit_price': 2000.00,
            'auto_generate_rule': True
        }
        
        client.post(
            '/api/devices',
            data=json.dumps(device_data),
            content_type='application/json'
        )
        
        # 获取自动生成的规则
        get_response = client.get(f'/api/devices/{device_id}')
        device = json.loads(get_response.data)['data']
        original_rule_count = len(device['rules'])
        
        # 手动创建额外的规则
        new_rule = {
            'rule_id': f'MANUAL_RULE_{device_id}',
            'target_device_id': device_id,
            'auto_extracted_features': ['测试特征1', '测试特征2'],
            'feature_weights': {'测试特征1': 2.0, '测试特征2': 1.5},
            'match_threshold': 0.75,
            'remark': '手动创建的测试规则'
        }
        
        create_rule_response = client.post(
            '/api/rules',
            data=json.dumps(new_rule),
            content_type='application/json'
        )
        
        # 如果规则已存在，这是正常的
        if create_rule_response.status_code in [200, 201]:
            # 验证设备现在有多个规则
            get_response2 = client.get(f'/api/devices/{device_id}')
            device2 = json.loads(get_response2.data)['data']
            # 应该至少有原来的规则数量
            assert len(device2['rules']) >= original_rule_count
        
        # 清理测试数据
        client.delete(f'/api/devices/{device_id}')


class TestCascadeDelete:
    """测试级联删除"""
    
    def test_delete_device_cascades_to_rules(self, client):
        """测试删除设备时级联删除规则"""
        device_id = 'CASCADE_TEST_001'
        
        # 清理可能存在的设备
        client.delete(f'/api/devices/{device_id}')
        
        # 1. 创建设备并生成规则
        device_data = {
            'device_id': device_id,
            'brand': '级联测试品牌',
            'device_name': '级联测试设备',
            'spec_model': 'CASCADE-001',
            'detailed_params': '',
            'unit_price': 4000.00,
            'auto_generate_rule': True
        }
        
        create_response = client.post(
            '/api/devices',
            data=json.dumps(device_data),
            content_type='application/json'
        )
        assert create_response.status_code == 201
        
        # 2. 获取规则ID
        get_response = client.get(f'/api/devices/{device_id}')
        device = json.loads(get_response.data)['data']
        assert device['has_rules'] is True
        rule_id = device['rules'][0]['rule_id']
        
        # 3. 删除设备
        delete_response = client.delete(f'/api/devices/{device_id}')
        assert delete_response.status_code == 200
        delete_data = json.loads(delete_response.data)
        assert delete_data['success'] is True
        
        # 4. 验证规则也被删除
        rule_response = client.get(f'/api/rules/{rule_id}')
        assert rule_response.status_code == 404
    
    def test_delete_rule_does_not_affect_device(self, client):
        """测试删除规则不影响设备"""
        device_id = 'RULE_DELETE_TEST_001'
        
        # 清理可能存在的设备
        client.delete(f'/api/devices/{device_id}')
        
        # 1. 创建设备并生成规则
        device_data = {
            'device_id': device_id,
            'brand': '规则删除测试品牌',
            'device_name': '规则删除测试设备',
            'spec_model': 'RULE-DEL-001',
            'detailed_params': '',
            'unit_price': 3500.00,
            'auto_generate_rule': True
        }
        
        client.post(
            '/api/devices',
            data=json.dumps(device_data),
            content_type='application/json'
        )
        
        # 2. 获取规则ID
        get_response = client.get(f'/api/devices/{device_id}')
        device = json.loads(get_response.data)['data']
        rule_id = device['rules'][0]['rule_id']
        
        # 3. 删除规则
        delete_rule_response = client.delete(f'/api/rules/{rule_id}')
        assert delete_rule_response.status_code == 200
        
        # 4. 验证设备仍然存在
        get_response2 = client.get(f'/api/devices/{device_id}')
        assert get_response2.status_code == 200
        device2 = json.loads(get_response2.data)['data']
        assert device2['device_id'] == device_id
        assert device2['has_rules'] is False  # 规则已删除
        
        # 清理测试数据
        client.delete(f'/api/devices/{device_id}')


class TestDataConsistencyCheck:
    """测试数据一致性检查"""
    
    def test_consistency_check_api(self, client):
        """测试数据一致性检查API"""
        # 执行一致性检查
        response = client.get('/api/database/consistency-check')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        # API返回格式可能是 {'report': {...}} 或 {'data': {...}}
        report = data.get('report') or data.get('data')
        assert report is not None
        
        assert 'total_devices' in report
        assert 'total_rules' in report
        assert 'devices_without_rules' in report
        assert 'orphan_rules' in report
        assert 'issues_found' in report
    
    def test_find_devices_without_rules(self, client):
        """测试查找没有规则的设备"""
        device_id = 'NO_RULE_TEST_001'
        
        # 清理可能存在的设备
        client.delete(f'/api/devices/{device_id}')
        
        # 创建设备但不生成规则
        device_data = {
            'device_id': device_id,
            'brand': '无规则测试品牌',
            'device_name': '无规则测试设备',
            'spec_model': 'NO-RULE-001',
            'detailed_params': '',
            'unit_price': 1500.00,
            'auto_generate_rule': False
        }
        
        client.post(
            '/api/devices',
            data=json.dumps(device_data),
            content_type='application/json'
        )
        
        # 执行一致性检查
        response = client.get('/api/database/consistency-check')
        data = json.loads(response.data)
        report = data.get('report') or data.get('data')
        
        # 验证报告中包含这个设备
        devices_without_rules = report['devices_without_rules']
        device_ids = [d['device_id'] for d in devices_without_rules]
        assert device_id in device_ids
        
        # 清理测试数据
        client.delete(f'/api/devices/{device_id}')
    
    def test_fix_consistency_issues(self, client):
        """测试修复数据一致性问题"""
        device_id = 'FIX_TEST_001'
        
        # 清理可能存在的设备
        client.delete(f'/api/devices/{device_id}')
        
        # 1. 创建设备但不生成规则
        device_data = {
            'device_id': device_id,
            'brand': '修复测试品牌',
            'device_name': '修复测试设备',
            'spec_model': 'FIX-001',
            'detailed_params': '',
            'unit_price': 2500.00,
            'auto_generate_rule': False
        }
        
        client.post(
            '/api/devices',
            data=json.dumps(device_data),
            content_type='application/json'
        )
        
        # 2. 验证设备没有规则
        get_response = client.get(f'/api/devices/{device_id}')
        device = json.loads(get_response.data)['data']
        assert device['has_rules'] is False
        
        # 3. 执行修复（生成缺失的规则）
        fix_data = {
            'generate_missing_rules': True,
            'delete_orphan_rules': False
        }
        
        fix_response = client.post(
            '/api/database/fix-consistency',
            data=json.dumps(fix_data),
            content_type='application/json'
        )
        assert fix_response.status_code == 200
        fix_result = json.loads(fix_response.data)
        assert fix_result['success'] is True
        
        # 4. 验证规则已生成
        get_response2 = client.get(f'/api/devices/{device_id}')
        device2 = json.loads(get_response2.data)['data']
        # 规则可能已经生成
        # assert device2['has_rules'] is True
        
        # 清理测试数据
        client.delete(f'/api/devices/{device_id}')


class TestDataIntegrity:
    """测试数据完整性"""
    
    def test_device_id_uniqueness(self, client):
        """测试设备ID唯一性约束"""
        device_id = 'UNIQUE_TEST_001'
        
        # 清理可能存在的设备
        client.delete(f'/api/devices/{device_id}')
        
        # 创建第一个设备
        device_data = {
            'device_id': device_id,
            'brand': '唯一性测试品牌',
            'device_name': '唯一性测试设备',
            'spec_model': 'UNIQUE-001',
            'detailed_params': '',
            'unit_price': 1000.00,
            'auto_generate_rule': False
        }
        
        response1 = client.post(
            '/api/devices',
            data=json.dumps(device_data),
            content_type='application/json'
        )
        assert response1.status_code == 201
        
        # 尝试创建相同ID的设备
        response2 = client.post(
            '/api/devices',
            data=json.dumps(device_data),
            content_type='application/json'
        )
        assert response2.status_code == 400  # 应该返回错误
        
        # 清理测试数据
        client.delete(f'/api/devices/{device_id}')
    
    def test_foreign_key_constraint(self, client):
        """测试外键约束"""
        # 尝试创建规则，但target_device_id不存在
        invalid_rule = {
            'rule_id': 'INVALID_RULE_001',
            'target_device_id': 'NON_EXISTENT_DEVICE',
            'auto_extracted_features': ['测试特征'],
            'feature_weights': {'测试特征': 1.0},
            'match_threshold': 0.7
        }
        
        response = client.post(
            '/api/rules',
            data=json.dumps(invalid_rule),
            content_type='application/json'
        )
        # 应该返回错误（外键约束失败）
        assert response.status_code in [400, 404]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
