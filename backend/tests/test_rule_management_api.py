"""
规则管理 API 测试

测试规则管理后端 API 的功能
验证需求: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.12, 10.13, 10.14, 10.15
"""

import pytest
import json
from datetime import datetime


class TestRuleManagementAPI:
    """规则管理 API 测试类"""
    
    def test_get_rules_management_list(self, client, db_session):
        """
        测试规则列表接口
        验证需求: 10.1
        """
        # 测试基本查询
        response = client.get('/api/rules/management/list')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'total' in data
        assert 'rules' in data
        assert isinstance(data['rules'], list)
        
        # 测试分页
        response = client.get('/api/rules/management/list?page=1&page_size=10')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['rules']) <= 10
        
        # 测试搜索
        response = client.get('/api/rules/management/list?search=传感器')
        assert response.status_code == 200
        data = json.loads(response.data)
        # 验证搜索结果包含关键词
        for rule in data['rules']:
            assert '传感器' in rule['device_name'] or '传感器' in rule['brand']
        
        # 测试阈值过滤
        response = client.get('/api/rules/management/list?threshold_min=3.0&threshold_max=6.0')
        assert response.status_code == 200
        data = json.loads(response.data)
        for rule in data['rules']:
            assert 3.0 <= rule['match_threshold'] <= 6.0
    
    def test_get_rule_management_detail(self, client, db_session, sample_rule):
        """
        测试规则详情接口
        验证需求: 10.2
        """
        rule_id = sample_rule.rule_id
        
        response = client.get(f'/api/rules/management/{rule_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'rule' in data
        
        rule = data['rule']
        assert rule['rule_id'] == rule_id
        assert 'device_info' in rule
        assert 'features' in rule
        assert 'match_threshold' in rule
        
        # 验证特征列表格式
        features = rule['features']
        assert isinstance(features, list)
        for feature in features:
            assert 'feature' in feature
            assert 'weight' in feature
            assert 'type' in feature
            assert feature['type'] in ['brand', 'device_type', 'model', 'parameter']
        
        # 验证特征按权重降序排序
        weights = [f['weight'] for f in features]
        assert weights == sorted(weights, reverse=True)
    
    def test_get_rule_detail_not_found(self, client, db_session):
        """测试获取不存在的规则"""
        response = client.get('/api/rules/management/NONEXISTENT_RULE')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'RULE_NOT_FOUND'
    
    def test_update_rule_management(self, client, db_session, sample_rule):
        """
        测试规则更新接口
        验证需求: 10.3, 10.4, 10.5
        """
        rule_id = sample_rule.rule_id
        
        # 更新匹配阈值
        update_data = {
            'match_threshold': 8.0
        }
        
        response = client.put(
            f'/api/rules/management/{rule_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 验证更新成功
        response = client.get(f'/api/rules/management/{rule_id}')
        data = json.loads(response.data)
        assert data['rule']['match_threshold'] == 8.0
    
    def test_update_rule_features(self, client, db_session, sample_rule):
        """测试更新规则特征权重"""
        rule_id = sample_rule.rule_id
        
        # 更新特征权重
        update_data = {
            'features': [
                {'feature': '霍尼韦尔', 'weight': 5.0},
                {'feature': '温度传感器', 'weight': 6.0},
                {'feature': '4-20ma', 'weight': 1.0}
            ]
        }
        
        response = client.put(
            f'/api/rules/management/{rule_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # 验证更新成功
        response = client.get(f'/api/rules/management/{rule_id}')
        data = json.loads(response.data)
        features = data['rule']['features']
        
        # 验证权重已更新
        feature_dict = {f['feature']: f['weight'] for f in features}
        assert feature_dict.get('霍尼韦尔') == 5.0
        assert feature_dict.get('温度传感器') == 6.0
    
    def test_test_rule_matching(self, client, db_session):
        """
        测试匹配测试接口
        验证需求: 10.6, 10.7, 10.8
        """
        test_data = {
            'description': '温度传感器，0-50℃，4-20mA'
        }
        
        response = client.post(
            '/api/rules/management/test',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 验证预处理结果
        assert 'preprocessing' in data
        preprocessing = data['preprocessing']
        assert 'original' in preprocessing
        assert 'normalized' in preprocessing
        assert 'features' in preprocessing
        assert isinstance(preprocessing['features'], list)
        
        # 验证候选规则列表
        assert 'candidates' in data
        candidates = data['candidates']
        assert isinstance(candidates, list)
        assert len(candidates) <= 10  # 最多返回10个
        
        # 验证候选规则格式
        for candidate in candidates:
            assert 'rank' in candidate
            assert 'rule_id' in candidate
            assert 'device_id' in candidate
            assert 'device_name' in candidate
            assert 'score' in candidate
            assert 'threshold' in candidate
            assert 'matched_features' in candidate
            assert 'is_match' in candidate
            
            # 验证匹配特征格式
            for feature in candidate['matched_features']:
                assert 'feature' in feature
                assert 'weight' in feature
        
        # 验证候选规则按得分降序排序
        scores = [c['score'] for c in candidates]
        assert scores == sorted(scores, reverse=True)
        
        # 验证最终匹配结果
        assert 'final_match' in data
    
    def test_test_matching_empty_description(self, client, db_session):
        """测试空描述的匹配测试"""
        test_data = {
            'description': ''
        }
        
        response = client.post(
            '/api/rules/management/test',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        # 应该能处理空描述，返回空的匹配结果
        assert response.status_code == 200
    
    def test_batch_update_weights_by_type(self, client, db_session, sample_rules):
        """
        测试按特征类型批量调整权重
        验证需求: 10.12
        """
        # 批量调整参数类型的权重
        batch_data = {
            'operation': 'update_weights_by_type',
            'feature_type': 'parameter',
            'new_weight': 1.5,
            'rule_ids': []  # 空数组表示应用到所有规则
        }
        
        response = client.post(
            '/api/rules/management/batch-update',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['updated_count'] > 0
    
    def test_batch_update_threshold(self, client, db_session, sample_rules):
        """
        测试批量调整阈值
        验证需求: 10.12
        """
        # 获取前两个规则的ID
        rule_ids = [rule.rule_id for rule in sample_rules[:2]]
        
        batch_data = {
            'operation': 'update_threshold',
            'new_threshold': 7.0,
            'rule_ids': rule_ids
        }
        
        response = client.post(
            '/api/rules/management/batch-update',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['updated_count'] == 2
        
        # 验证阈值已更新
        for rule_id in rule_ids:
            response = client.get(f'/api/rules/management/{rule_id}')
            data = json.loads(response.data)
            assert data['rule']['match_threshold'] == 7.0
    
    def test_batch_reset_rules(self, client, db_session, sample_rules):
        """
        测试批量重置规则
        验证需求: 10.13
        """
        rule_ids = [sample_rules[0].rule_id]
        
        batch_data = {
            'operation': 'reset_rules',
            'rule_ids': rule_ids
        }
        
        response = client.post(
            '/api/rules/management/batch-update',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['updated_count'] == 1
    
    def test_batch_update_invalid_operation(self, client, db_session):
        """测试无效的批量操作类型"""
        batch_data = {
            'operation': 'invalid_operation',
            'rule_ids': []
        }
        
        response = client.post(
            '/api/rules/management/batch-update',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'INVALID_OPERATION'
    
    def test_get_rule_statistics(self, client, db_session, sample_rules):
        """
        测试统计分析接口
        验证需求: 10.14, 10.15
        """
        response = client.get('/api/rules/management/statistics')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'statistics' in data
        
        stats = data['statistics']
        
        # 验证统计信息包含所有必需字段
        assert 'total_rules' in stats
        assert 'total_features' in stats
        assert 'avg_weight' in stats
        assert 'avg_threshold' in stats
        assert 'weight_distribution' in stats
        assert 'threshold_distribution' in stats
        
        # 验证权重分布格式
        weight_dist = stats['weight_distribution']
        assert isinstance(weight_dist, dict)
        expected_keys = ['0-1', '1-2', '2-3', '3-4', '4-5', '5+']
        for key in expected_keys:
            assert key in weight_dist
            assert isinstance(weight_dist[key], int)
        
        # 验证阈值分布格式
        threshold_dist = stats['threshold_distribution']
        assert isinstance(threshold_dist, dict)
        
        # 验证统计数据的合理性
        assert stats['total_rules'] > 0
        assert stats['avg_weight'] > 0
        assert stats['avg_threshold'] > 0


# Fixtures

@pytest.fixture
def sample_rule(db_session, sample_device):
    """创建示例规则"""
    from modules.data_loader import Rule
    
    rule = Rule(
        rule_id='R_TEST_001',
        target_device_id=sample_device.device_id,
        auto_extracted_features=['霍尼韦尔', '温度传感器', '4-20ma', '0-10v'],
        feature_weights={
            '霍尼韦尔': 3.0,
            '温度传感器': 5.0,
            '4-20ma': 1.0,
            '0-10v': 1.0
        },
        match_threshold=5.0,
        remark='测试规则'
    )
    
    # 使用 data_loader 添加规则
    from app import data_loader
    data_loader.loader.add_rule(rule)
    
    yield rule
    
    # 清理
    try:
        data_loader.loader.delete_rule(rule.rule_id)
    except:
        pass


@pytest.fixture
def sample_rules(db_session, sample_devices):
    """创建多个示例规则"""
    from modules.data_loader import Rule
    from app import data_loader
    
    rules = []
    for idx, device in enumerate(sample_devices[:3]):
        rule = Rule(
            rule_id=f'R_TEST_{idx:03d}',
            target_device_id=device.device_id,
            auto_extracted_features=[device.brand, device.device_name, '4-20ma'],
            feature_weights={
                device.brand: 3.0,
                device.device_name: 5.0,
                '4-20ma': 1.0
            },
            match_threshold=5.0,
            remark=f'测试规则{idx}'
        )
        data_loader.loader.add_rule(rule)
        rules.append(rule)
    
    yield rules
    
    # 清理
    for rule in rules:
        try:
            data_loader.loader.delete_rule(rule.rule_id)
        except:
            pass


@pytest.fixture
def sample_device(db_session):
    """创建示例设备"""
    from modules.data_loader import Device
    from app import data_loader
    
    device = Device(
        device_id='DEV_TEST_001',
        brand='霍尼韦尔',
        device_name='温度传感器',
        spec_model='HST-RA',
        detailed_params='0-50℃,4-20mA,0-10V',
        unit_price=213.0
    )
    
    data_loader.loader.add_device(device, auto_generate_rule=False)
    
    yield device
    
    # 清理
    try:
        data_loader.loader.delete_device(device.device_id)
    except:
        pass


@pytest.fixture
def sample_devices(db_session):
    """创建多个示例设备"""
    from modules.data_loader import Device
    from app import data_loader
    
    devices = []
    device_data = [
        ('DEV_TEST_001', '霍尼韦尔', '温度传感器', 'HST-RA', '0-50℃,4-20mA', 213.0),
        ('DEV_TEST_002', '西门子', '压力传感器', 'QBE2003-P25', '0-25bar,4-20mA', 450.0),
        ('DEV_TEST_003', '江森', '湿度传感器', 'HT-6700', '0-100%RH,4-20mA', 320.0),
    ]
    
    for device_id, brand, name, model, params, price in device_data:
        device = Device(
            device_id=device_id,
            brand=brand,
            device_name=name,
            spec_model=model,
            detailed_params=params,
            unit_price=price
        )
        data_loader.loader.add_device(device, auto_generate_rule=False)
        devices.append(device)
    
    yield devices
    
    # 清理
    for device in devices:
        try:
            data_loader.loader.delete_device(device.device_id)
        except:
            pass
