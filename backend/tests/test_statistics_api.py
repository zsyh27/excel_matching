# -*- coding: utf-8 -*-
"""
统计API测试

测试从规则管理迁移到统计仪表板的API端点
验证需求: Requirements 4.1, 4.2, 5.1, 5.2
"""

import pytest
import json
from datetime import datetime, timedelta


def test_get_statistics_match_logs_basic(client):
    """测试获取匹配日志基本功能"""
    response = client.get('/api/statistics/match-logs')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert 'logs' in data
    assert 'total' in data
    assert 'page' in data
    assert 'page_size' in data
    assert isinstance(data['logs'], list)


def test_get_statistics_match_logs_with_pagination(client):
    """测试匹配日志分页功能"""
    response = client.get('/api/statistics/match-logs?page=1&page_size=10')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert data['page'] == 1
    assert data['page_size'] == 10
    assert len(data['logs']) <= 10


def test_get_statistics_match_logs_with_status_filter(client):
    """测试匹配日志状态筛选"""
    response = client.get('/api/statistics/match-logs?status=success')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    # 如果有日志，验证都是success状态
    for log in data['logs']:
        if 'match_status' in log:
            assert log['match_status'] == 'success'


def test_get_statistics_match_logs_with_date_range(client):
    """测试匹配日志日期范围筛选"""
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    response = client.get(f'/api/statistics/match-logs?start_date={yesterday}&end_date={today}')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert 'logs' in data


def test_get_statistics_rules_basic(client):
    """测试获取规则统计基本功能"""
    response = client.get('/api/statistics/rules')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert 'statistics' in data
    
    stats = data['statistics']
    assert 'total_rules' in stats
    assert 'total_devices' in stats
    assert 'avg_threshold' in stats
    assert 'avg_features' in stats
    assert 'avg_weight' in stats
    assert 'threshold_distribution' in stats
    assert 'weight_distribution' in stats
    assert 'top_brands' in stats


def test_get_statistics_rules_structure(client):
    """测试规则统计数据结构"""
    response = client.get('/api/statistics/rules')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    stats = data['statistics']
    
    # 验证阈值分布结构
    assert 'low' in stats['threshold_distribution']
    assert 'medium' in stats['threshold_distribution']
    assert 'high' in stats['threshold_distribution']
    
    # 验证权重分布结构
    assert 'low' in stats['weight_distribution']
    assert 'medium' in stats['weight_distribution']
    assert 'high' in stats['weight_distribution']
    
    # 验证品牌列表结构
    assert isinstance(stats['top_brands'], list)
    for brand in stats['top_brands']:
        assert 'brand' in brand
        assert 'count' in brand


def test_get_statistics_match_success_rate_basic(client):
    """测试获取匹配成功率基本功能"""
    response = client.get('/api/statistics/match-success-rate')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert 'trend' in data
    assert 'overall' in data
    
    # 验证overall结构
    overall = data['overall']
    assert 'success_rate' in overall
    assert 'total' in overall
    assert 'success' in overall


def test_get_statistics_match_success_rate_with_date_range(client):
    """测试匹配成功率日期范围筛选"""
    today = datetime.now().strftime('%Y-%m-%d')
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    response = client.get(f'/api/statistics/match-success-rate?start_date={week_ago}&end_date={today}')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['success'] is True
    assert 'trend' in data
    assert isinstance(data['trend'], list)


def test_get_statistics_match_success_rate_trend_structure(client):
    """测试匹配成功率趋势数据结构"""
    response = client.get('/api/statistics/match-success-rate')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # 验证趋势数据结构
    for item in data['trend']:
        assert 'date' in item
        assert 'success_rate' in item
        assert 'total' in item
        assert 'success' in item
        
        # 验证成功率在0-1之间
        assert 0 <= item['success_rate'] <= 1


def test_statistics_api_backward_compatibility(client):
    """测试统计API向后兼容性 - 旧API仍然可用"""
    # 测试旧的规则管理统计API仍然可用
    response = client.get('/api/rules/management/statistics')
    assert response.status_code == 200
    
    # 测试旧的匹配日志API仍然可用
    response = client.get('/api/rules/management/logs')
    assert response.status_code == 200


def test_statistics_api_consistency(client):
    """测试新旧API返回数据一致性"""
    # 获取新API的规则统计
    new_response = client.get('/api/statistics/rules')
    new_data = json.loads(new_response.data)
    
    # 获取旧API的规则统计
    old_response = client.get('/api/rules/management/statistics')
    old_data = json.loads(old_response.data)
    
    # 验证关键数据一致
    assert new_data['statistics']['total_rules'] == old_data['statistics']['total_rules']
    assert new_data['statistics']['total_devices'] == old_data['statistics']['total_devices']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
