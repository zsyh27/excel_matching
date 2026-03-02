"""
集成测试: /api/match 接口增强功能

验证任务 5.2: 编写API扩展的集成测试
- 测试/api/match返回cache_key
- 测试record_detail=False时不返回cache_key
- 测试响应数据结构

验证需求: Requirements 1.1, 6.5
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


class TestMatchAPIIntegration:
    """测试 /api/match 接口的集成功能"""
    
    def test_match_returns_cache_key_when_record_detail_true(self, client):
        """
        测试: 当record_detail=True时，/api/match应返回cache_key
        
        验证需求: 1.1, 6.5
        """
        # 准备测试数据
        test_data = {
            "rows": [
                {
                    "row_number": 1,
                    "row_type": "device",
                    "raw_data": ["西门子", "DDC控制器", "RWD68"],
                    "device_description": "西门子 DDC控制器 RWD68"
                }
            ],
            "record_detail": True
        }
        
        # 发送请求
        response = client.post('/api/match', 
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        # 验证响应状态码
        assert response.status_code == 200, f"期望状态码200，实际: {response.status_code}"
        
        # 解析响应数据
        data = response.get_json()
        
        # 验证基本响应结构
        assert data is not None, "响应数据不应为None"
        assert data['success'] is True, "期望success为True"
        assert 'matched_rows' in data, "响应应包含matched_rows字段"
        assert len(data['matched_rows']) > 0, "matched_rows不应为空"
        
        # 验证detail_cache_key字段存在
        first_row = data['matched_rows'][0]
        assert 'detail_cache_key' in first_row, "匹配行应包含detail_cache_key字段"
        
        # 验证cache_key不为None（无论匹配成功或失败，只要record_detail=True就应该有）
        cache_key = first_row['detail_cache_key']
        assert cache_key is not None, "detail_cache_key不应为None"
        assert isinstance(cache_key, str), "detail_cache_key应为字符串类型"
        assert len(cache_key) > 0, "detail_cache_key不应为空字符串"
        
        # 验证cache_key格式（应该是UUID格式）
        assert len(cache_key) >= 32, "cache_key长度应至少为32个字符（UUID格式）"
    
    def test_match_no_cache_key_when_record_detail_false(self, client):
        """
        测试: 当record_detail=False时，/api/match不应返回cache_key或返回None
        
        验证需求: 1.1, 6.5
        """
        # 准备测试数据
        test_data = {
            "rows": [
                {
                    "row_number": 1,
                    "row_type": "device",
                    "raw_data": ["西门子", "DDC控制器", "RWD68"],
                    "device_description": "西门子 DDC控制器 RWD68"
                }
            ],
            "record_detail": False
        }
        
        # 发送请求
        response = client.post('/api/match',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        # 验证响应状态码
        assert response.status_code == 200, f"期望状态码200，实际: {response.status_code}"
        
        # 解析响应数据
        data = response.get_json()
        
        # 验证基本响应结构
        assert data is not None, "响应数据不应为None"
        assert data['success'] is True, "期望success为True"
        assert 'matched_rows' in data, "响应应包含matched_rows字段"
        
        # 验证detail_cache_key不存在或为None
        first_row = data['matched_rows'][0]
        if 'detail_cache_key' in first_row:
            assert first_row['detail_cache_key'] is None, \
                "record_detail=False时，detail_cache_key应为None"
    
    def test_match_default_record_detail_behavior(self, client):
        """
        测试: 默认行为（不传record_detail参数），应默认为True并返回cache_key
        
        验证需求: 1.1, 6.5
        """
        # 准备测试数据（不包含record_detail参数）
        test_data = {
            "rows": [
                {
                    "row_number": 1,
                    "row_type": "device",
                    "raw_data": ["西门子", "DDC控制器", "RWD68"],
                    "device_description": "西门子 DDC控制器 RWD68"
                }
            ]
            # 不传record_detail参数，应默认为True
        }
        
        # 发送请求
        response = client.post('/api/match',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        # 验证响应状态码
        assert response.status_code == 200, f"期望状态码200，实际: {response.status_code}"
        
        # 解析响应数据
        data = response.get_json()
        
        # 验证基本响应结构
        assert data is not None, "响应数据不应为None"
        assert data['success'] is True, "期望success为True"
        
        # 默认应该记录详情，因此应该有cache_key
        first_row = data['matched_rows'][0]
        assert 'detail_cache_key' in first_row, \
            "默认行为应包含detail_cache_key字段"
        
        cache_key = first_row['detail_cache_key']
        assert cache_key is not None, \
            "默认行为的detail_cache_key不应为None"
    
    def test_match_response_data_structure(self, client):
        """
        测试: 验证/api/match响应的完整数据结构
        
        验证需求: 1.1, 6.5
        """
        # 准备测试数据
        test_data = {
            "rows": [
                {
                    "row_number": 1,
                    "row_type": "device",
                    "raw_data": ["西门子", "DDC控制器", "RWD68"],
                    "device_description": "西门子 DDC控制器 RWD68"
                },
                {
                    "row_number": 2,
                    "row_type": "device",
                    "raw_data": ["霍尼韦尔", "温度传感器"],
                    "device_description": "霍尼韦尔 温度传感器"
                }
            ],
            "record_detail": True
        }
        
        # 发送请求
        response = client.post('/api/match',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        # 验证响应状态码
        assert response.status_code == 200, f"期望状态码200，实际: {response.status_code}"
        
        # 解析响应数据
        data = response.get_json()
        
        # 验证顶层结构
        assert 'success' in data, "响应应包含success字段"
        assert 'matched_rows' in data, "响应应包含matched_rows字段"
        assert 'statistics' in data, "响应应包含statistics字段"
        assert 'message' in data, "响应应包含message字段"
        
        # 验证matched_rows结构
        assert isinstance(data['matched_rows'], list), "matched_rows应为列表"
        assert len(data['matched_rows']) == 2, "应返回2个匹配行"
        
        # 验证每个匹配行的结构
        for row in data['matched_rows']:
            assert 'row_number' in row, "匹配行应包含row_number字段"
            assert 'row_type' in row, "匹配行应包含row_type字段"
            assert 'device_description' in row, "匹配行应包含device_description字段"
            assert 'match_result' in row, "匹配行应包含match_result字段"
            
            # 对于设备行，应该有detail_cache_key
            if row['row_type'] == 'device':
                assert 'detail_cache_key' in row, "设备行应包含detail_cache_key字段"
                
                # 验证match_result结构
                match_result = row['match_result']
                assert isinstance(match_result, dict), "match_result应为字典"
                assert 'match_status' in match_result, "match_result应包含match_status字段"
                assert 'match_score' in match_result, "match_result应包含match_score字段"
                assert 'match_reason' in match_result, "match_result应包含match_reason字段"
        
        # 验证statistics结构
        statistics = data['statistics']
        assert 'total_devices' in statistics, "statistics应包含total_devices字段"
        assert 'matched' in statistics, "statistics应包含matched字段"
        assert 'unmatched' in statistics, "statistics应包含unmatched字段"
        assert 'accuracy_rate' in statistics, "statistics应包含accuracy_rate字段"
        
        # 验证统计数据的正确性
        assert statistics['total_devices'] == 2, "总设备数应为2"
        assert statistics['matched'] + statistics['unmatched'] == 2, \
            "匹配数+未匹配数应等于总设备数"
    
    def test_match_with_multiple_devices(self, client):
        """
        测试: 多个设备匹配时，每个设备都应有独立的cache_key
        
        验证需求: 1.1, 6.5
        """
        # 准备测试数据（多个设备）
        test_data = {
            "rows": [
                {
                    "row_number": 1,
                    "row_type": "device",
                    "raw_data": ["西门子", "DDC控制器", "RWD68"],
                    "device_description": "西门子 DDC控制器 RWD68"
                },
                {
                    "row_number": 2,
                    "row_type": "device",
                    "raw_data": ["霍尼韦尔", "温度传感器", "T7350"],
                    "device_description": "霍尼韦尔 温度传感器 T7350"
                },
                {
                    "row_number": 3,
                    "row_type": "device",
                    "raw_data": ["江森", "压力传感器"],
                    "device_description": "江森 压力传感器"
                }
            ],
            "record_detail": True
        }
        
        # 发送请求
        response = client.post('/api/match',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        # 验证响应状态码
        assert response.status_code == 200, f"期望状态码200，实际: {response.status_code}"
        
        # 解析响应数据
        data = response.get_json()
        
        # 收集所有cache_key
        cache_keys = []
        for row in data['matched_rows']:
            if row['row_type'] == 'device' and 'detail_cache_key' in row:
                cache_key = row['detail_cache_key']
                if cache_key is not None:
                    cache_keys.append(cache_key)
        
        # 验证每个设备都有cache_key
        assert len(cache_keys) == 3, "应该有3个cache_key"
        
        # 验证所有cache_key都是唯一的
        assert len(cache_keys) == len(set(cache_keys)), \
            "所有cache_key应该是唯一的，不应有重复"
    
    def test_match_with_non_device_rows(self, client):
        """
        测试: 非设备行（如标题行）不应有cache_key
        
        验证需求: 1.1, 6.5
        """
        # 准备测试数据（包含非设备行）
        test_data = {
            "rows": [
                {
                    "row_number": 1,
                    "row_type": "title",
                    "device_description": "设备清单"
                },
                {
                    "row_number": 2,
                    "row_type": "device",
                    "raw_data": ["西门子", "DDC控制器", "RWD68"],
                    "device_description": "西门子 DDC控制器 RWD68"
                }
            ],
            "record_detail": True
        }
        
        # 发送请求
        response = client.post('/api/match',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        # 验证响应状态码
        assert response.status_code == 200, f"期望状态码200，实际: {response.status_code}"
        
        # 解析响应数据
        data = response.get_json()
        
        # 验证非设备行没有cache_key
        title_row = data['matched_rows'][0]
        assert title_row['row_type'] == 'title', "第一行应为标题行"
        assert 'detail_cache_key' not in title_row or title_row.get('detail_cache_key') is None, \
            "非设备行不应有detail_cache_key"
        
        # 验证设备行有cache_key
        device_row = data['matched_rows'][1]
        assert device_row['row_type'] == 'device', "第二行应为设备行"
        assert 'detail_cache_key' in device_row, "设备行应有detail_cache_key"
    
    def test_match_backward_compatibility(self, client):
        """
        测试: 向后兼容性 - 旧的API调用方式仍然工作
        
        验证需求: 1.1, 6.5
        """
        # 使用旧的API调用方式（不包含record_detail参数）
        test_data = {
            "rows": [
                {
                    "row_number": 1,
                    "row_type": "device",
                    "raw_data": ["西门子", "DDC控制器"],
                }
            ]
        }
        
        # 发送请求
        response = client.post('/api/match',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        # 验证响应状态码
        assert response.status_code == 200, f"期望状态码200，实际: {response.status_code}"
        
        # 解析响应数据
        data = response.get_json()
        
        # 验证基本响应结构（向后兼容）
        assert data['success'] is True, "期望success为True"
        assert 'matched_rows' in data, "响应应包含matched_rows"
        assert 'statistics' in data, "响应应包含statistics"
        
        # 新增的detail_cache_key字段不应破坏旧的功能
        first_row = data['matched_rows'][0]
        assert 'match_result' in first_row, "应包含match_result字段"
    
    def test_match_with_empty_rows(self, client):
        """
        测试: 空rows列表的错误处理
        
        验证需求: 1.1, 6.5
        """
        # 准备测试数据（空rows）
        test_data = {
            "rows": [],
            "record_detail": True
        }
        
        # 发送请求
        response = client.post('/api/match',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        # 验证响应状态码
        assert response.status_code == 200, f"期望状态码200，实际: {response.status_code}"
        
        # 解析响应数据
        data = response.get_json()
        
        # 验证响应结构
        assert data['success'] is True, "空rows应该成功处理"
        assert 'matched_rows' in data, "响应应包含matched_rows"
        assert len(data['matched_rows']) == 0, "matched_rows应为空列表"
        assert data['statistics']['total_devices'] == 0, "总设备数应为0"
    
    def test_match_with_missing_rows_parameter(self, client):
        """
        测试: 缺少rows参数的错误处理
        
        验证需求: 1.1, 6.5
        """
        # 准备测试数据（缺少rows参数）
        test_data = {
            "record_detail": True
        }
        
        # 发送请求
        response = client.post('/api/match',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        # 验证响应状态码（应该返回错误）
        assert response.status_code == 400, f"期望状态码400，实际: {response.status_code}"
        
        # 解析响应数据
        data = response.get_json()
        
        # 验证错误响应结构
        assert data['success'] is False, "期望success为False"
        assert 'error_code' in data, "错误响应应包含error_code"
        assert 'error_message' in data, "错误响应应包含error_message"
        assert data['error_code'] == 'MISSING_ROWS', "错误代码应为MISSING_ROWS"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
