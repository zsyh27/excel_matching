# -*- coding: utf-8 -*-
"""
配置管理API集成测试

测试所有配置管理相关的API端点
"""

import pytest
import json
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app


class TestConfigManagementAPI:
    """测试配置管理API"""
    
    @pytest.fixture
    def app(self):
        """创建Flask应用"""
        flask_app.config['TESTING'] = True
        return flask_app
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()
    
    def test_get_config(self, client):
        """测试获取配置 GET /api/config"""
        response = client.get('/api/config')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'config' in data
        
        config = data['config']
        
        # 检查必需的配置项
        required_keys = [
            'synonym_map',
            'brand_keywords',
            'device_type_keywords',
            'normalization_map',
            'feature_split_chars',
            'ignore_keywords',
            'global_config'
        ]
        
        for key in required_keys:
            assert key in config, f"配置中缺少 {key}"
    
    def test_validate_config_valid(self, client):
        """测试验证有效配置 POST /api/config/validate"""
        valid_config = {
            "synonym_map": {"温度传感器": "温传感器"},
            "brand_keywords": ["霍尼韦尔"],
            "device_type_keywords": ["传感器"],
            "normalization_map": {"℃": ""},
            "feature_split_chars": ["+"],
            "ignore_keywords": ["施工"],
            "global_config": {
                "default_match_threshold": 3.0,
                "unify_lowercase": True
            }
        }
        
        response = client.post(
            '/api/config/validate',
            data=json.dumps({'config': valid_config}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['is_valid'] is True
        assert len(data.get('errors', [])) == 0
    
    def test_validate_config_invalid(self, client):
        """测试验证无效配置"""
        invalid_config = {
            "synonym_map": [],  # 错误类型
            "brand_keywords": "not a list"  # 错误类型
        }
        
        response = client.post(
            '/api/config/validate',
            data=json.dumps({'config': invalid_config}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['is_valid'] is False
        assert len(data.get('errors', [])) > 0
    
    def test_test_config(self, client):
        """测试配置效果 POST /api/config/test"""
        # 先获取当前配置
        response = client.get('/api/config')
        current_config = json.loads(response.data)['config']
        
        # 测试配置
        test_data = {
            'test_text': '霍尼韦尔温度传感器',
            'config': current_config
        }
        
        response = client.post(
            '/api/config/test',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'preprocessing' in data
        assert 'match_result' in data
        
        # 检查预处理结果
        preprocessing = data['preprocessing']
        assert 'original' in preprocessing
        assert 'features' in preprocessing
        assert isinstance(preprocessing['features'], list)
    
    def test_get_history(self, client):
        """测试获取配置历史 GET /api/config/history"""
        response = client.get('/api/config/history')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'history' in data
        assert isinstance(data['history'], list)
    
    def test_export_config(self, client):
        """测试导出配置 GET /api/config/export"""
        response = client.get('/api/config/export')
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        # 验证可以解析为JSON
        config = json.loads(response.data)
        assert isinstance(config, dict)
        assert 'synonym_map' in config


class TestConfigManagementAPIErrorHandling:
    """测试配置管理API的错误处理"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        flask_app.config['TESTING'] = True
        return flask_app.test_client()
    
    def test_validate_config_missing_data(self, client):
        """测试验证配置时缺少数据"""
        response = client.post(
            '/api/config/validate',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code in [400, 500]
    
    def test_test_config_missing_text(self, client):
        """测试配置时缺少测试文本"""
        response = client.post(
            '/api/config/test',
            data=json.dumps({'config': {}}),
            content_type='application/json'
        )
        
        assert response.status_code in [400, 500]
    
    def test_save_config_invalid_json(self, client):
        """测试保存配置时提供无效JSON"""
        response = client.post(
            '/api/config/save',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code in [400, 500]


class TestConfigManagementAPIBoundaryConditions:
    """测试配置管理API的边界条件"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        flask_app.config['TESTING'] = True
        return flask_app.test_client()
    
    def test_validate_empty_config(self, client):
        """测试验证空配置"""
        response = client.post(
            '/api/config/validate',
            data=json.dumps({'config': {}}),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        assert data['is_valid'] is False
    
    def test_test_config_empty_text(self, client):
        """测试空文本"""
        response = client.get('/api/config')
        current_config = json.loads(response.data)['config']
        
        test_data = {
            'test_text': '',
            'config': current_config
        }
        
        response = client.post(
            '/api/config/test',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # 应该能处理空文本
        assert response.status_code == 200
    
    def test_test_config_very_long_text(self, client):
        """测试非常长的文本"""
        response = client.get('/api/config')
        current_config = json.loads(response.data)['config']
        
        # 创建一个很长的测试文本
        long_text = '霍尼韦尔温度传感器 ' * 100
        
        test_data = {
            'test_text': long_text,
            'config': current_config
        }
        
        response = client.post(
            '/api/config/test',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # 应该能处理长文本
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
