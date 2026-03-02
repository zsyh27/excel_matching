"""
Excel数据范围选择API测试

测试预览和范围解析API端点
"""

import pytest
import json
import os
from backend.app import app, excel_analysis_cache


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def uploaded_file_id(client):
    """上传测试文件并返回file_id"""
    test_file = 'data/示例设备清单.xlsx'
    
    if not os.path.exists(test_file):
        pytest.skip(f"测试文件不存在: {test_file}")
    
    with open(test_file, 'rb') as f:
        data = {
            'file': (f, os.path.basename(test_file), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        response = client.post(
            '/api/upload',
            data=data,
            content_type='multipart/form-data'
        )
    
    assert response.status_code == 200, f"Upload failed: {response.data}"
    data = json.loads(response.data)
    assert data['success'] is True
    
    return data['file_id']


class TestPreviewAPI:
    """测试预览API"""
    
    def test_preview_success(self, client, uploaded_file_id):
        """测试成功获取预览"""
        response = client.post(
            '/api/excel/preview',
            json={'file_id': uploaded_file_id},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # 验证响应结构
        assert data['success'] is True
        assert 'data' in data
        
        preview_data = data['data']
        assert 'sheets' in preview_data
        assert 'preview_data' in preview_data
        assert 'total_rows' in preview_data
        assert 'total_cols' in preview_data
        assert 'column_letters' in preview_data
        
        # 验证sheets结构
        assert isinstance(preview_data['sheets'], list)
        assert len(preview_data['sheets']) > 0
        
        first_sheet = preview_data['sheets'][0]
        assert 'index' in first_sheet
        assert 'name' in first_sheet
        assert 'rows' in first_sheet
        assert 'cols' in first_sheet
        
        # 验证预览数据
        assert isinstance(preview_data['preview_data'], list)
        assert len(preview_data['preview_data']) <= 10  # 默认最多10行
        
        # 验证列字母
        assert isinstance(preview_data['column_letters'], list)
        assert len(preview_data['column_letters']) == preview_data['total_cols']
    
    def test_preview_with_sheet_index(self, client, uploaded_file_id):
        """测试指定工作表索引"""
        response = client.post(
            '/api/excel/preview',
            json={'file_id': uploaded_file_id, 'sheet_index': 0},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_preview_missing_file_id(self, client):
        """测试缺少file_id参数"""
        response = client.post(
            '/api/excel/preview',
            json={},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'MISSING_FILE_ID'
    
    def test_preview_file_not_found(self, client):
        """测试文件不存在"""
        response = client.post(
            '/api/excel/preview',
            json={'file_id': 'nonexistent-file-id'},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'FILE_NOT_FOUND'
    
    def test_preview_invalid_sheet_index(self, client, uploaded_file_id):
        """测试无效的工作表索引"""
        response = client.post(
            '/api/excel/preview',
            json={'file_id': uploaded_file_id, 'sheet_index': 999},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'INVALID_PARAMETER'


class TestParseRangeAPI:
    """测试范围解析API"""
    
    def test_parse_range_success(self, client, uploaded_file_id):
        """测试成功解析范围"""
        response = client.post(
            '/api/excel/parse_range',
            json={
                'file_id': uploaded_file_id,
                'start_row': 1,
                'end_row': 10,
                'start_col': 1,
                'end_col': 4  # 修改为4列，因为测试文件只有4列
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # 验证响应结构
        assert data['success'] is True
        assert 'file_id' in data
        assert 'parse_result' in data
        
        parse_result = data['parse_result']
        assert 'rows' in parse_result
        assert 'total_rows' in parse_result
        assert 'filtered_rows' in parse_result
        assert 'format' in parse_result
        
        # 验证行数
        assert parse_result['total_rows'] <= 10
        
        # 验证每行的列数
        for row in parse_result['rows']:
            assert len(row['raw_data']) == 4  # 修改为4列
    
    def test_parse_range_default_values(self, client, uploaded_file_id):
        """测试使用默认参数"""
        response = client.post(
            '/api/excel/parse_range',
            json={'file_id': uploaded_file_id},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 应该解析全部数据
        parse_result = data['parse_result']
        assert parse_result['total_rows'] > 0
    
    def test_parse_range_with_none_end(self, client, uploaded_file_id):
        """测试end_row和end_col为None"""
        response = client.post(
            '/api/excel/parse_range',
            json={
                'file_id': uploaded_file_id,
                'start_row': 2,
                'end_row': None,
                'start_col': 1,
                'end_col': None
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_parse_range_missing_file_id(self, client):
        """测试缺少file_id参数"""
        response = client.post(
            '/api/excel/parse_range',
            json={},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'MISSING_FILE_ID'
    
    def test_parse_range_file_not_found(self, client):
        """测试文件不存在"""
        response = client.post(
            '/api/excel/parse_range',
            json={'file_id': 'nonexistent-file-id'},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'FILE_NOT_FOUND'
    
    def test_parse_range_invalid_start_row(self, client, uploaded_file_id):
        """测试无效的起始行号"""
        response = client.post(
            '/api/excel/parse_range',
            json={'file_id': uploaded_file_id, 'start_row': 0},
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'INVALID_RANGE'
    
    def test_parse_range_end_before_start(self, client, uploaded_file_id):
        """测试结束行小于起始行"""
        response = client.post(
            '/api/excel/parse_range',
            json={
                'file_id': uploaded_file_id,
                'start_row': 10,
                'end_row': 5
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'INVALID_RANGE'
    
    def test_parse_range_caches_result(self, client, uploaded_file_id):
        """测试解析结果被缓存"""
        # 清空缓存
        excel_analysis_cache.clear()
        
        response = client.post(
            '/api/excel/parse_range',
            json={'file_id': uploaded_file_id},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # 验证缓存中有数据
        assert uploaded_file_id in excel_analysis_cache
        cache_entry = excel_analysis_cache[uploaded_file_id]
        assert 'filename' in cache_entry
        assert 'file_path' in cache_entry
        assert 'parse_result' in cache_entry


class TestBackwardCompatibility:
    """测试向后兼容性"""
    
    def test_parse_api_still_works(self, client, uploaded_file_id):
        """测试原有的/api/parse端点仍然工作"""
        response = client.post(
            '/api/parse',
            json={'file_id': uploaded_file_id},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # 验证响应结构与之前一致
        assert data['success'] is True
        assert 'file_id' in data
        assert 'parse_result' in data
        
        parse_result = data['parse_result']
        assert 'rows' in parse_result
        assert 'total_rows' in parse_result
        assert 'filtered_rows' in parse_result
        assert 'format' in parse_result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
