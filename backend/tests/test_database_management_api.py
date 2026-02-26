"""
数据库管理 API 测试

测试批量导入、数据一致性检查和统计信息 API
验证需求: 25.1-25.7, 27.1-27.7, 28.1-28.7
"""

import pytest
import json
import os
from io import BytesIO
from app import app, data_loader


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_excel_file():
    """创建示例 Excel 文件"""
    # 这里应该创建一个真实的 Excel 文件用于测试
    # 为了简化，我们返回一个文件路径
    return 'data/示例设备清单.xlsx'


class TestBatchImportAPI:
    """测试批量导入 API - 验证需求: 25.1-25.7"""
    
    def test_batch_import_no_file(self, client):
        """测试没有文件的情况"""
        response = client.post('/api/devices/batch')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        # 如果不是数据库模式，跳过测试
        if data.get('error_code') == 'DATABASE_MODE_REQUIRED':
            pytest.skip("需要数据库模式")
        assert data['error_code'] == 'NO_FILE'
    
    def test_batch_import_empty_filename(self, client):
        """测试空文件名的情况"""
        data = {'file': (BytesIO(b''), '')}
        response = client.post('/api/devices/batch', data=data)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        # 如果不是数据库模式，跳过测试
        if data.get('error_code') == 'DATABASE_MODE_REQUIRED':
            pytest.skip("需要数据库模式")
        assert data['error_code'] == 'EMPTY_FILENAME'
    
    def test_batch_import_invalid_format(self, client):
        """测试无效文件格式"""
        data = {'file': (BytesIO(b'test'), 'test.txt')}
        response = client.post('/api/devices/batch', data=data)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        # 如果不是数据库模式，跳过测试
        if data.get('error_code') == 'DATABASE_MODE_REQUIRED':
            pytest.skip("需要数据库模式")
        assert data['error_code'] == 'INVALID_FORMAT'
    
    @pytest.mark.skipif(not os.path.exists('data/示例设备清单.xlsx'), 
                       reason="示例文件不存在")
    def test_batch_import_success(self, client, sample_excel_file):
        """测试成功批量导入"""
        with open(sample_excel_file, 'rb') as f:
            data = {
                'file': (f, '示例设备清单.xlsx'),
                'auto_generate_rules': 'true'
            }
            response = client.post('/api/devices/batch', 
                                  data=data,
                                  content_type='multipart/form-data')
            
            # 如果不是数据库模式，跳过测试
            if response.status_code == 400:
                result = json.loads(response.data)
                if result.get('error_code') == 'DATABASE_MODE_REQUIRED':
                    pytest.skip("需要数据库模式")
            
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['success'] is True
            assert 'inserted' in result['data']
            assert 'updated' in result['data']
            assert 'failed' in result['data']
            assert 'rules_generated' in result['data']


class TestConsistencyCheckAPI:
    """测试数据一致性检查 API - 验证需求: 28.1-28.7"""
    
    def test_consistency_check(self, client):
        """测试数据一致性检查"""
        response = client.get('/api/database/consistency-check')
        
        if response.status_code == 400:
            # 如果不是数据库模式，跳过测试
            data = json.loads(response.data)
            if data.get('error_code') == 'DATABASE_MODE_REQUIRED':
                pytest.skip("需要数据库模式")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'total_devices' in data['data']
        assert 'total_rules' in data['data']
        assert 'devices_without_rules' in data['data']
        assert 'orphan_rules' in data['data']
        assert 'issues_found' in data['data']
    
    def test_fix_consistency_generate_rules(self, client):
        """测试修复一致性问题 - 生成规则"""
        request_data = {
            'generate_missing_rules': True,
            'delete_orphan_rules': False
        }
        response = client.post('/api/database/fix-consistency',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            if data.get('error_code') == 'DATABASE_MODE_REQUIRED':
                pytest.skip("需要数据库模式")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'rules_generated' in data['data']
        assert 'rules_deleted' in data['data']
    
    def test_fix_consistency_delete_orphans(self, client):
        """测试修复一致性问题 - 删除孤立规则"""
        request_data = {
            'generate_missing_rules': False,
            'delete_orphan_rules': True
        }
        response = client.post('/api/database/fix-consistency',
                              data=json.dumps(request_data),
                              content_type='application/json')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            if data.get('error_code') == 'DATABASE_MODE_REQUIRED':
                pytest.skip("需要数据库模式")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True


class TestStatisticsAPI:
    """测试统计信息 API - 验证需求: 27.1-27.7"""
    
    def test_get_statistics(self, client):
        """测试获取概览统计"""
        response = client.get('/api/database/statistics')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            if data.get('error_code') == 'DATABASE_MODE_REQUIRED':
                pytest.skip("需要数据库模式")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'total_devices' in data['data']
        assert 'total_rules' in data['data']
        assert 'total_brands' in data['data']
        assert 'rule_coverage' in data['data']
    
    def test_get_brand_statistics(self, client):
        """测试获取品牌分布统计"""
        response = client.get('/api/database/statistics/brands')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            if data.get('error_code') == 'DATABASE_MODE_REQUIRED':
                pytest.skip("需要数据库模式")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'brands' in data['data']
        assert 'total_brands' in data['data']
        assert isinstance(data['data']['brands'], list)
    
    def test_get_price_statistics(self, client):
        """测试获取价格分布统计"""
        response = client.get('/api/database/statistics/prices')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            if data.get('error_code') == 'DATABASE_MODE_REQUIRED':
                pytest.skip("需要数据库模式")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'price_ranges' in data['data']
        assert isinstance(data['data']['price_ranges'], list)
    
    def test_get_recent_devices(self, client):
        """测试获取最近添加的设备"""
        response = client.get('/api/database/statistics/recent')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            if data.get('error_code') == 'DATABASE_MODE_REQUIRED':
                pytest.skip("需要数据库模式")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'devices' in data['data']
        assert 'count' in data['data']
        assert isinstance(data['data']['devices'], list)
    
    def test_get_devices_without_rules(self, client):
        """测试获取没有规则的设备"""
        response = client.get('/api/database/statistics/without-rules')
        
        if response.status_code == 400:
            data = json.loads(response.data)
            if data.get('error_code') == 'DATABASE_MODE_REQUIRED':
                pytest.skip("需要数据库模式")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'devices' in data['data']
        assert 'count' in data['data']
        assert isinstance(data['data']['devices'], list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
