"""
测试批量操作功能

验证需求: 10.12, 10.13
"""

import pytest
import json
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, data_loader
from modules.data_loader import Rule


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def setup_test_rules():
    """设置测试规则"""
    # 确保使用数据库模式
    if not hasattr(data_loader, 'loader') or not data_loader.loader:
        pytest.skip("需要数据库模式")
    
    # 获取一些测试规则
    rules = data_loader.loader.load_rules()
    if len(rules) < 2:
        pytest.skip("需要至少2条规则进行测试")
    
    return rules[:2]  # 返回前两条规则用于测试


class TestBatchOperations:
    """批量操作测试类"""
    
    def test_batch_update_weights_by_type_all_rules(self, client, setup_test_rules):
        """
        测试按特征类型批量调整所有规则的权重
        验证需求: 10.12
        """
        # 准备请求数据
        batch_data = {
            'operation': 'update_weights_by_type',
            'feature_type': 'parameter',
            'new_weight': 1.5,
            'rule_ids': []  # 空列表表示应用到所有规则
        }
        
        # 发送请求
        response = client.post(
            '/api/rules/management/batch-update',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'updated_count' in data
        assert data['updated_count'] > 0
        print(f"✓ 成功更新 {data['updated_count']} 条规则的参数权重")
    
    def test_batch_update_weights_by_type_selected_rules(self, client, setup_test_rules):
        """
        测试按特征类型批量调整选中规则的权重
        验证需求: 10.12
        """
        test_rules = setup_test_rules
        rule_ids = [rule.rule_id for rule in test_rules]
        
        # 准备请求数据
        batch_data = {
            'operation': 'update_weights_by_type',
            'feature_type': 'brand',
            'new_weight': 5.0,
            'rule_ids': rule_ids
        }
        
        # 发送请求
        response = client.post(
            '/api/rules/management/batch-update',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['updated_count'] <= len(rule_ids)
        print(f"✓ 成功更新 {data['updated_count']} 条选中规则的品牌权重")
    
    def test_batch_update_threshold_all_rules(self, client, setup_test_rules):
        """
        测试批量调整所有规则的阈值
        验证需求: 10.12
        """
        # 准备请求数据
        batch_data = {
            'operation': 'update_threshold',
            'new_threshold': 6.0,
            'rule_ids': []  # 空列表表示应用到所有规则
        }
        
        # 发送请求
        response = client.post(
            '/api/rules/management/batch-update',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'updated_count' in data
        assert data['updated_count'] > 0
        print(f"✓ 成功更新 {data['updated_count']} 条规则的阈值")
    
    def test_batch_update_threshold_selected_rules(self, client, setup_test_rules):
        """
        测试批量调整选中规则的阈值
        验证需求: 10.12
        """
        test_rules = setup_test_rules
        rule_ids = [rule.rule_id for rule in test_rules]
        
        # 准备请求数据
        batch_data = {
            'operation': 'update_threshold',
            'new_threshold': 4.5,
            'rule_ids': rule_ids
        }
        
        # 发送请求
        response = client.post(
            '/api/rules/management/batch-update',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['updated_count'] == len(rule_ids)
        print(f"✓ 成功更新 {data['updated_count']} 条选中规则的阈值")
    
    def test_batch_reset_rules_selected(self, client, setup_test_rules):
        """
        测试批量重置选中的规则
        验证需求: 10.13
        """
        test_rules = setup_test_rules
        rule_ids = [rule.rule_id for rule in test_rules]
        
        # 准备请求数据
        batch_data = {
            'operation': 'reset_rules',
            'rule_ids': rule_ids
        }
        
        # 发送请求
        response = client.post(
            '/api/rules/management/batch-update',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['updated_count'] == len(rule_ids)
        print(f"✓ 成功重置 {data['updated_count']} 条规则")
    
    def test_batch_operation_missing_operation(self, client):
        """
        测试缺少 operation 参数的情况
        """
        # 准备请求数据（缺少 operation）
        batch_data = {
            'new_weight': 2.0
        }
        
        # 发送请求
        response = client.post(
            '/api/rules/management/batch-update',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'operation' in data['error_message'].lower()
        print("✓ 正确处理缺少 operation 参数的情况")
    
    def test_batch_operation_invalid_operation(self, client):
        """
        测试无效的 operation 类型
        """
        # 准备请求数据（无效的 operation）
        batch_data = {
            'operation': 'invalid_operation',
            'new_weight': 2.0
        }
        
        # 发送请求
        response = client.post(
            '/api/rules/management/batch-update',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        print("✓ 正确处理无效的 operation 类型")
    
    def test_batch_update_weights_different_types(self, client, setup_test_rules):
        """
        测试不同特征类型的权重调整
        验证需求: 10.12
        """
        feature_types = ['brand', 'device_type', 'model', 'parameter']
        
        for feature_type in feature_types:
            # 准备请求数据
            batch_data = {
                'operation': 'update_weights_by_type',
                'feature_type': feature_type,
                'new_weight': 2.0,
                'rule_ids': []
            }
            
            # 发送请求
            response = client.post(
                '/api/rules/management/batch-update',
                data=json.dumps(batch_data),
                content_type='application/json'
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            print(f"✓ 成功调整 {feature_type} 类型的权重")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
