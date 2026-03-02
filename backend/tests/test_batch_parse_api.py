# -*- coding: utf-8 -*-
"""
批量解析API端点单元测试

验证需求: 10.1, 10.2, 10.3, 10.4
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from app import app
from modules.intelligent_device import BatchParseResult


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_batch_parse_result():
    """创建模拟的批量解析结果"""
    result = BatchParseResult()
    result.total = 10
    result.processed = 10
    result.successful = 8
    result.failed = 2
    result.success_rate = 0.8
    result.failed_devices = [
        {'device_id': 'DEV001', 'brand': '西门子', 'device_name': '传感器', 'error': '无法识别设备类型'},
        {'device_id': 'DEV002', 'brand': '霍尼韦尔', 'device_name': '阀门', 'error': '缺少必填参数'}
    ]
    result.duration_seconds = 5.5
    return result


class TestBatchParseAPI:
    """批量解析API端点测试类"""
    
    @patch('app.intelligent_parser')
    @patch('app.data_loader')
    @patch('modules.intelligent_device.batch_parser.BatchParser')
    def test_batch_parse_all_devices(self, mock_batch_parser_class, mock_data_loader, mock_parser, client, mock_batch_parse_result):
        """
        测试批量解析所有设备
        
        验证需求: 10.1, 10.2, 10.3
        """
        # 模拟组件初始化
        mock_parser.return_value = Mock()
        mock_data_loader.loader = Mock()
        
        # 模拟批量解析服务
        mock_batch_parser = Mock()
        mock_batch_parser.batch_parse.return_value = mock_batch_parse_result
        mock_batch_parser_class.return_value = mock_batch_parser
        
        # 发送请求（不指定device_ids，处理所有设备）
        response = client.post(
            '/api/devices/batch-parse',
            data=json.dumps({'dry_run': True}),
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        
        # 验证返回的数据
        result_data = data['data']
        assert result_data['total'] == 10
        assert result_data['processed'] == 10
        assert result_data['successful'] == 8
        assert result_data['failed'] == 2
        assert result_data['success_rate'] == 0.8
        assert len(result_data['failed_devices']) == 2
        
        # 验证批量解析被调用
        mock_batch_parser.batch_parse.assert_called_once_with(
            device_ids=None,
            dry_run=True
        )
    
    @patch('app.intelligent_parser')
    @patch('app.data_loader')
    @patch('modules.intelligent_device.batch_parser.BatchParser')
    def test_batch_parse_specific_devices(self, mock_batch_parser_class, mock_data_loader, mock_parser, client, mock_batch_parse_result):
        """
        测试批量解析指定设备
        
        验证需求: 10.1, 10.2
        """
        # 模拟组件初始化
        mock_parser.return_value = Mock()
        mock_data_loader.loader = Mock()
        
        # 修改结果为只处理指定设备
        mock_batch_parse_result.total = 3
        mock_batch_parse_result.processed = 3
        mock_batch_parse_result.successful = 3
        mock_batch_parse_result.failed = 0
        mock_batch_parse_result.success_rate = 1.0
        mock_batch_parse_result.failed_devices = []
        
        # 模拟批量解析服务
        mock_batch_parser = Mock()
        mock_batch_parser.batch_parse.return_value = mock_batch_parse_result
        mock_batch_parser_class.return_value = mock_batch_parser
        
        # 发送请求（指定device_ids）
        test_data = {
            'device_ids': ['DEV001', 'DEV002', 'DEV003'],
            'dry_run': False
        }
        
        response = client.post(
            '/api/devices/batch-parse',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 验证返回的数据
        result_data = data['data']
        assert result_data['total'] == 3
        assert result_data['successful'] == 3
        assert result_data['failed'] == 0
        
        # 验证批量解析被调用，并传递了正确的参数
        mock_batch_parser.batch_parse.assert_called_once_with(
            device_ids=['DEV001', 'DEV002', 'DEV003'],
            dry_run=False
        )
    
    @patch('app.intelligent_parser')
    @patch('app.data_loader')
    @patch('modules.intelligent_device.batch_parser.BatchParser')
    def test_batch_parse_dry_run_mode(self, mock_batch_parser_class, mock_data_loader, mock_parser, client, mock_batch_parse_result):
        """
        测试dry_run模式（只测试不更新）
        
        验证需求: 10.2
        """
        # 模拟组件初始化
        mock_parser.return_value = Mock()
        mock_data_loader.loader = Mock()
        
        # 模拟批量解析服务
        mock_batch_parser = Mock()
        mock_batch_parser.batch_parse.return_value = mock_batch_parse_result
        mock_batch_parser_class.return_value = mock_batch_parser
        
        # 发送请求（dry_run=true）
        response = client.post(
            '/api/devices/batch-parse',
            data=json.dumps({'dry_run': True}),
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 验证dry_run参数被正确传递
        mock_batch_parser.batch_parse.assert_called_once()
        call_args = mock_batch_parser.batch_parse.call_args
        assert call_args[1]['dry_run'] is True
    
    @patch('app.intelligent_parser')
    @patch('app.data_loader')
    @patch('modules.intelligent_device.batch_parser.BatchParser')
    def test_batch_parse_report_format(self, mock_batch_parser_class, mock_data_loader, mock_parser, client, mock_batch_parse_result):
        """
        测试批量解析报告格式
        
        验证需求: 10.4
        """
        # 模拟组件初始化
        mock_parser.return_value = Mock()
        mock_data_loader.loader = Mock()
        
        # 模拟批量解析服务
        mock_batch_parser = Mock()
        mock_batch_parser.batch_parse.return_value = mock_batch_parse_result
        mock_batch_parser_class.return_value = mock_batch_parser
        
        # 发送请求
        response = client.post(
            '/api/devices/batch-parse',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 验证报告格式
        result_data = data['data']
        assert 'total' in result_data
        assert 'processed' in result_data
        assert 'successful' in result_data
        assert 'failed' in result_data
        assert 'success_rate' in result_data
        assert 'failed_devices' in result_data
        assert 'duration_seconds' in result_data
        
        # 验证失败设备的格式
        if result_data['failed_devices']:
            failed_device = result_data['failed_devices'][0]
            assert 'device_id' in failed_device
            assert 'error' in failed_device
    
    @patch('app.intelligent_parser', None)
    @patch('app.data_loader')
    def test_batch_parse_parser_not_initialized(self, mock_data_loader, client):
        """测试解析器未初始化的错误处理"""
        # 模拟数据加载器
        mock_data_loader.loader = Mock()
        
        # 发送请求
        response = client.post(
            '/api/devices/batch-parse',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error_code' in data
    
    @patch('app.intelligent_parser')
    @patch('app.data_loader')
    def test_batch_parse_not_database_mode(self, mock_data_loader, mock_parser, client):
        """测试非数据库模式的错误处理"""
        # 模拟解析器
        mock_parser.return_value = Mock()
        
        # 模拟非数据库模式
        mock_data_loader.loader = None
        
        # 发送请求
        response = client.post(
            '/api/devices/batch-parse',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'NOT_DATABASE_MODE'
    
    @patch('app.intelligent_parser')
    @patch('app.data_loader')
    def test_batch_parse_invalid_device_ids(self, mock_data_loader, mock_parser, client):
        """测试无效的device_ids参数"""
        # 模拟组件初始化
        mock_parser.return_value = Mock()
        mock_data_loader.loader = Mock()
        
        # 发送请求（device_ids不是数组）
        response = client.post(
            '/api/devices/batch-parse',
            data=json.dumps({'device_ids': 'invalid'}),
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'INVALID_DEVICE_IDS'
    
    @patch('app.intelligent_parser')
    @patch('app.data_loader')
    def test_batch_parse_invalid_dry_run(self, mock_data_loader, mock_parser, client):
        """测试无效的dry_run参数"""
        # 模拟组件初始化
        mock_parser.return_value = Mock()
        mock_data_loader.loader = Mock()
        
        # 发送请求（dry_run不是布尔值）
        response = client.post(
            '/api/devices/batch-parse',
            data=json.dumps({'dry_run': 'invalid'}),
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'INVALID_DRY_RUN'
    
    @patch('app.intelligent_parser')
    @patch('app.data_loader')
    def test_batch_parse_empty_request(self, mock_data_loader, mock_parser, client, mock_batch_parse_result):
        """测试空请求体（使用默认参数）"""
        # 模拟组件初始化
        mock_parser.return_value = Mock()
        mock_data_loader.loader = Mock()
        
        # 模拟批量解析服务
        with patch('modules.intelligent_device.batch_parser.BatchParser') as mock_batch_parser_class:
            mock_batch_parser = Mock()
            mock_batch_parser.batch_parse.return_value = mock_batch_parse_result
            mock_batch_parser_class.return_value = mock_batch_parser
            
            # 发送空请求
            response = client.post(
                '/api/devices/batch-parse',
                data=json.dumps({}),
                content_type='application/json'
            )
            
            # 验证响应
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            
            # 验证使用默认参数
            mock_batch_parser.batch_parse.assert_called_once_with(
                device_ids=None,
                dry_run=False
            )
    
    @patch('app.intelligent_parser')
    @patch('app.data_loader')
    def test_batch_parse_invalid_json(self, mock_data_loader, mock_parser, client):
        """测试无效的JSON格式"""
        # 模拟组件初始化
        mock_parser.return_value = Mock()
        mock_data_loader.loader = Mock()
        
        # 发送无效的JSON
        response = client.post(
            '/api/devices/batch-parse',
            data='invalid json',
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'INVALID_JSON'
    
    @patch('app.intelligent_parser')
    @patch('app.data_loader')
    @patch('modules.intelligent_device.batch_parser.BatchParser')
    def test_batch_parse_with_numeric_device_ids(self, mock_batch_parser_class, mock_data_loader, mock_parser, client, mock_batch_parse_result):
        """测试数字类型的device_ids（应该被转换为字符串）"""
        # 模拟组件初始化
        mock_parser.return_value = Mock()
        mock_data_loader.loader = Mock()
        
        # 模拟批量解析服务
        mock_batch_parser = Mock()
        mock_batch_parser.batch_parse.return_value = mock_batch_parse_result
        mock_batch_parser_class.return_value = mock_batch_parser
        
        # 发送请求（device_ids包含数字）
        response = client.post(
            '/api/devices/batch-parse',
            data=json.dumps({'device_ids': [1, 2, 3]}),
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 验证device_ids被转换为字符串
        mock_batch_parser.batch_parse.assert_called_once()
        call_args = mock_batch_parser.batch_parse.call_args
        assert call_args[1]['device_ids'] == ['1', '2', '3']
