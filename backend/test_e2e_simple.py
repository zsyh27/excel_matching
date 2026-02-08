"""简化的端到端测试"""
import pytest
import os
import json
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import app


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """测试健康检查API"""
    response = client.get('/api/health')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['success'] is True
    assert result['status'] == 'healthy'
    print("✓ 健康检查API测试通过")


def test_get_devices_api(client):
    """测试获取设备列表API"""
    response = client.get('/api/devices')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['success'] is True
    assert 'devices' in result
    assert len(result['devices']) > 0
    print("✓ 获取设备列表API测试通过")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
