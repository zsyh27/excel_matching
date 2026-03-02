# -*- coding: utf-8 -*-
"""
相似设备查询API测试

验证需求: 9.7
"""

import pytest
import json
from app import app
from modules.data_loader import Device


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_devices():
    """创建示例设备数据"""
    return {
        'DEVICE001': Device(
            device_id='DEVICE001',
            brand='西门子',
            device_name='CO2传感器',
            spec_model='QAA2061',
            detailed_params='量程0-2000ppm 输出4-20mA',
            unit_price=1250.0
        ),
        'DEVICE002': Device(
            device_id='DEVICE002',
            brand='西门子',
            device_name='CO2传感器',
            spec_model='QAA2062',
            detailed_params='量程0-5000ppm 输出4-20mA',
            unit_price=1350.0
        ),
        'DEVICE003': Device(
            device_id='DEVICE003',
            brand='霍尼韦尔',
            device_name='CO2传感器',
            spec_model='T7350A',
            detailed_params='量程0-2000ppm 输出0-10V',
            unit_price=1180.0
        ),
        'DEVICE004': Device(
            device_id='DEVICE004',
            brand='西门子',
            device_name='温度传感器',
            spec_model='QAA2012',
            detailed_params='量程0-50℃ 输出4-20mA',
            unit_price=850.0
        ),
        'DEVICE005': Device(
            device_id='DEVICE005',
            brand='施耐德',
            device_name='座阀',
            spec_model='VVF53',
            detailed_params='DN25 PN16',
            unit_price=2200.0
        )
    }


class TestSimilarDevicesAPI:
    """相似设备查询API测试类"""
    
    def test_get_similar_devices_success(self, client, sample_devices, monkeypatch):
        """
        测试成功查询相似设备
        
        验证需求: 9.7
        """
        # Mock data_loader
        class MockDataLoader:
            def get_all_devices(self):
                return sample_devices
        
        # 替换全局data_loader
        import app as app_module
        monkeypatch.setattr(app_module, 'data_loader', MockDataLoader())
        
        # 发送请求
        response = client.get('/api/devices/DEVICE001/similar')
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        
        # 验证返回的相似设备
        similar_devices = data['data']
        assert isinstance(similar_devices, list)
        
        # 应该返回相同设备类型的设备（CO2传感器）
        # 不应该包含目标设备本身
        device_ids = [d['device_id'] for d in similar_devices]
        assert 'DEVICE001' not in device_ids  # 不包含自己
        
        # 验证每个结果包含必需字段
        for device in similar_devices:
            assert 'device_id' in device
            assert 'similarity_score' in device
            assert 'matched_features' in device
            assert 'device' in device
            
            # 验证设备信息
            device_info = device['device']
            assert 'brand' in device_info
            assert 'device_name' in device_info
            assert 'device_type' in device_info
    
    def test_get_similar_devices_with_limit(self, client, sample_devices, monkeypatch):
        """
        测试带limit参数的相似设备查询
        
        验证需求: 9.6
        """
        # Mock data_loader
        class MockDataLoader:
            def get_all_devices(self):
                return sample_devices
        
        import app as app_module
        monkeypatch.setattr(app_module, 'data_loader', MockDataLoader())
        
        # 发送请求，限制返回2个结果
        response = client.get('/api/devices/DEVICE001/similar?limit=2')
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 验证返回数量不超过limit
        similar_devices = data['data']
        assert len(similar_devices) <= 2
    
    def test_get_similar_devices_device_not_found(self, client, sample_devices, monkeypatch):
        """
        测试查询不存在的设备
        
        验证需求: 9.7
        """
        # Mock data_loader
        class MockDataLoader:
            def get_all_devices(self):
                return sample_devices
        
        import app as app_module
        monkeypatch.setattr(app_module, 'data_loader', MockDataLoader())
        
        # 发送请求查询不存在的设备
        response = client.get('/api/devices/NONEXISTENT/similar')
        
        # 验证响应
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error_code' in data
        assert data['error_code'] == 'DEVICE_NOT_FOUND'
    
    def test_get_similar_devices_invalid_limit(self, client, sample_devices, monkeypatch):
        """
        测试无效的limit参数
        
        验证需求: 9.6
        """
        # Mock data_loader
        class MockDataLoader:
            def get_all_devices(self):
                return sample_devices
        
        import app as app_module
        monkeypatch.setattr(app_module, 'data_loader', MockDataLoader())
        
        # 测试limit太小
        response = client.get('/api/devices/DEVICE001/similar?limit=0')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'INVALID_LIMIT' in data['error_code']
        
        # 测试limit太大
        response = client.get('/api/devices/DEVICE001/similar?limit=101')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'INVALID_LIMIT' in data['error_code']
    
    def test_get_similar_devices_sorted_by_score(self, client, sample_devices, monkeypatch):
        """
        测试相似设备按得分降序排列
        
        验证需求: 9.6
        """
        # Mock data_loader
        class MockDataLoader:
            def get_all_devices(self):
                return sample_devices
        
        import app as app_module
        monkeypatch.setattr(app_module, 'data_loader', MockDataLoader())
        
        # 发送请求
        response = client.get('/api/devices/DEVICE001/similar')
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 验证结果按得分降序排列
        similar_devices = data['data']
        if len(similar_devices) > 1:
            scores = [d['similarity_score'] for d in similar_devices]
            assert scores == sorted(scores, reverse=True)
    
    def test_get_similar_devices_includes_matched_features(self, client, sample_devices, monkeypatch):
        """
        测试相似设备结果包含匹配特征详情
        
        验证需求: 9.7
        """
        # Mock data_loader
        class MockDataLoader:
            def get_all_devices(self):
                return sample_devices
        
        import app as app_module
        monkeypatch.setattr(app_module, 'data_loader', MockDataLoader())
        
        # 发送请求
        response = client.get('/api/devices/DEVICE001/similar')
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 验证每个结果包含匹配特征详情
        similar_devices = data['data']
        for device in similar_devices:
            assert 'matched_features' in device
            assert isinstance(device['matched_features'], dict)
            
            # 如果有匹配特征，验证特征权重
            if device['matched_features']:
                for feature_name, weight in device['matched_features'].items():
                    assert isinstance(weight, (int, float))
                    assert weight >= 0
    
    def test_get_similar_devices_filters_by_device_type(self, client, sample_devices, monkeypatch):
        """
        测试相似设备查询按设备类型过滤
        
        验证需求: 9.1
        """
        # Mock data_loader
        class MockDataLoader:
            def get_all_devices(self):
                return sample_devices
        
        import app as app_module
        monkeypatch.setattr(app_module, 'data_loader', MockDataLoader())
        
        # 发送请求查询CO2传感器的相似设备
        response = client.get('/api/devices/DEVICE001/similar')
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 验证所有返回的设备都是相同设备类型
        similar_devices = data['data']
        target_device_type = 'CO2传感器'
        
        for device in similar_devices:
            device_info = device['device']
            # 设备类型应该与目标设备相同
            assert device_info['device_type'] == target_device_type or device_info['device_name'] == target_device_type
            
            # 不应该包含其他类型的设备（如温度传感器、座阀）
            assert device_info['device_type'] not in ['温度传感器', '座阀']
            assert device_info['device_name'] not in ['温度传感器', '座阀']
    
    def test_get_similar_devices_response_format(self, client, sample_devices, monkeypatch):
        """
        测试相似设备查询返回数据格式
        
        验证需求: 9.7
        """
        # Mock data_loader
        class MockDataLoader:
            def get_all_devices(self):
                return sample_devices
        
        import app as app_module
        monkeypatch.setattr(app_module, 'data_loader', MockDataLoader())
        
        # 发送请求
        response = client.get('/api/devices/DEVICE001/similar')
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # 验证顶层结构
        assert 'success' in data
        assert data['success'] is True
        assert 'data' in data
        assert isinstance(data['data'], list)
        
        # 验证每个相似设备的数据格式
        similar_devices = data['data']
        for device in similar_devices:
            # 必需字段
            assert 'device_id' in device
            assert 'similarity_score' in device
            assert 'matched_features' in device
            assert 'device' in device
            
            # 验证字段类型
            assert isinstance(device['device_id'], str)
            assert isinstance(device['similarity_score'], (int, float))
            assert isinstance(device['matched_features'], dict)
            assert isinstance(device['device'], dict)
            
            # 验证设备信息字段
            device_info = device['device']
            assert 'brand' in device_info
            assert 'device_name' in device_info
            assert 'model' in device_info
            assert 'device_type' in device_info
            assert 'spec_model' in device_info
            assert 'unit_price' in device_info
            
            # 验证设备信息字段类型
            assert isinstance(device_info['brand'], str)
            assert isinstance(device_info['device_name'], str)
            assert isinstance(device_info['device_type'], str)
            assert isinstance(device_info['unit_price'], (int, float))
    
    def test_get_similar_devices_empty_result(self, client, monkeypatch):
        """
        测试查询没有相似设备的情况
        
        验证需求: 9.1, 9.6
        """
        # 创建只有一个设备的数据集
        single_device = {
            'DEVICE001': Device(
                device_id='DEVICE001',
                brand='西门子',
                device_name='CO2传感器',
                spec_model='QAA2061',
                detailed_params='量程0-2000ppm 输出4-20mA',
                unit_price=1250.0
            )
        }
        
        # Mock data_loader
        class MockDataLoader:
            def get_all_devices(self):
                return single_device
        
        import app as app_module
        monkeypatch.setattr(app_module, 'data_loader', MockDataLoader())
        
        # 发送请求
        response = client.get('/api/devices/DEVICE001/similar')
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 应该返回空列表（因为只有目标设备本身）
        similar_devices = data['data']
        assert isinstance(similar_devices, list)
        assert len(similar_devices) == 0
    
    def test_get_similar_devices_default_limit(self, client, monkeypatch):
        """
        测试默认limit为20
        
        验证需求: 9.6
        """
        # 创建30个相同类型的设备
        many_devices = {
            'DEVICE001': Device(
                device_id='DEVICE001',
                brand='西门子',
                device_name='CO2传感器',
                spec_model='QAA2061',
                detailed_params='量程0-2000ppm 输出4-20mA',
                unit_price=1250.0
            )
        }
        
        # 添加29个相似设备
        for i in range(2, 31):
            device_id = f'DEVICE{i:03d}'
            many_devices[device_id] = Device(
                device_id=device_id,
                brand='西门子' if i % 2 == 0 else '霍尼韦尔',
                device_name='CO2传感器',
                spec_model=f'MODEL{i}',
                detailed_params=f'量程0-{i*1000}ppm 输出4-20mA',
                unit_price=1000.0 + i * 10
            )
        
        # Mock data_loader
        class MockDataLoader:
            def get_all_devices(self):
                return many_devices
        
        import app as app_module
        monkeypatch.setattr(app_module, 'data_loader', MockDataLoader())
        
        # 发送请求（不指定limit）
        response = client.get('/api/devices/DEVICE001/similar')
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 应该最多返回20个结果
        similar_devices = data['data']
        assert len(similar_devices) <= 20
