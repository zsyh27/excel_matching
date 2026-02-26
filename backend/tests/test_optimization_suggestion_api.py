"""
优化建议管理 API 测试

验证需求: 11.2, 11.3, 11.4, 11.5, 11.6
"""

import pytest
import json
import uuid
from datetime import datetime, timedelta
from modules.models import OptimizationSuggestion, MatchLog


class TestOptimizationSuggestionAPI:
    """优化建议管理 API 测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self, client, db_manager):
        """测试前准备"""
        self.client = client
        self.db_manager = db_manager
        
        # 清理测试数据
        with db_manager.session_scope() as session:
            session.query(OptimizationSuggestion).delete()
            session.query(MatchLog).delete()
            session.commit()
        
        # 创建测试数据
        self._create_test_data()
    
    def _create_test_data(self):
        """创建测试数据"""
        with self.db_manager.session_scope() as session:
            # 创建匹配日志
            for i in range(20):
                log = MatchLog(
                    log_id=f"LOG_{uuid.uuid4().hex[:8]}",
                    timestamp=datetime.utcnow() - timedelta(days=i),
                    input_description=f"测试设备描述 {i}",
                    extracted_features=["4-20ma", "0-10v", "温度传感器"],
                    match_status='failed' if i % 3 == 0 else 'success',
                    matched_device_id=f"DEVICE_{i:03d}" if i % 3 != 0 else None,
                    match_score=2.5 if i % 3 != 0 else 0.0,
                    match_threshold=5.0,
                    match_reason="测试原因"
                )
                session.add(log)
            
            # 创建优化建议
            suggestions = [
                OptimizationSuggestion(
                    suggestion_id=f"SUG_{uuid.uuid4().hex[:8]}",
                    priority="high",
                    type="weight_adjustment",
                    feature="4-20ma",
                    current_value=3.0,
                    suggested_value=1.0,
                    impact_count=15,
                    reason="通用参数权重过高",
                    evidence=["LOG_001", "LOG_002"],
                    status="pending",
                    created_at=datetime.utcnow()
                ),
                OptimizationSuggestion(
                    suggestion_id=f"SUG_{uuid.uuid4().hex[:8]}",
                    priority="medium",
                    type="weight_adjustment",
                    feature="0-10v",
                    current_value=2.5,
                    suggested_value=1.0,
                    impact_count=10,
                    reason="低区分度特征",
                    evidence=[],
                    status="pending",
                    created_at=datetime.utcnow()
                ),
                OptimizationSuggestion(
                    suggestion_id=f"SUG_{uuid.uuid4().hex[:8]}",
                    priority="high",
                    type="threshold_adjustment",
                    feature="global_threshold",
                    current_value=2.0,
                    suggested_value=5.0,
                    impact_count=100,
                    reason="阈值过低",
                    evidence=[],
                    status="applied",
                    created_at=datetime.utcnow() - timedelta(days=1),
                    applied_at=datetime.utcnow() - timedelta(hours=1),
                    applied_by="admin"
                )
            ]
            
            for suggestion in suggestions:
                session.add(suggestion)
            
            session.commit()
    
    def test_get_suggestions_list(self):
        """测试获取优化建议列表"""
        # 测试获取所有待处理建议
        response = self.client.get('/api/optimization/suggestions?status=pending')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['total'] == 2  # 2条待处理建议
        assert len(data['suggestions']) == 2
        
        # 验证建议数据结构
        suggestion = data['suggestions'][0]
        assert 'suggestion_id' in suggestion
        assert 'priority' in suggestion
        assert 'type' in suggestion
        assert 'feature' in suggestion
        assert 'current_value' in suggestion
        assert 'suggested_value' in suggestion
        assert 'impact_count' in suggestion
        assert 'reason' in suggestion
        assert 'status' in suggestion
    
    def test_get_suggestions_by_priority(self):
        """测试按优先级筛选建议"""
        # 测试获取高优先级建议
        response = self.client.get('/api/optimization/suggestions?priority=high&status=pending')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['total'] == 1  # 1条高优先级待处理建议
        assert data['suggestions'][0]['priority'] == 'high'
    
    def test_get_suggestions_pagination(self):
        """测试分页功能"""
        # 测试第一页
        response = self.client.get('/api/optimization/suggestions?page=1&page_size=1')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['page'] == 1
        assert data['page_size'] == 1
        assert len(data['suggestions']) == 1
    
    def test_get_suggestion_detail(self):
        """测试获取建议详情"""
        # 先获取一个建议ID
        response = self.client.get('/api/optimization/suggestions?status=pending')
        data = json.loads(response.data)
        suggestion_id = data['suggestions'][0]['suggestion_id']
        
        # 获取详情
        response = self.client.get(f'/api/optimization/suggestions/{suggestion_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['suggestion']['suggestion_id'] == suggestion_id
        assert 'affected_devices' in data['suggestion']
    
    def test_get_suggestion_detail_not_found(self):
        """测试获取不存在的建议"""
        response = self.client.get('/api/optimization/suggestions/INVALID_ID')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'SUGGESTION_NOT_FOUND'
    
    def test_apply_suggestion(self):
        """测试应用优化建议"""
        # 先获取一个待处理建议
        response = self.client.get('/api/optimization/suggestions?status=pending')
        data = json.loads(response.data)
        suggestion_id = data['suggestions'][0]['suggestion_id']
        
        # 应用建议
        response = self.client.post(
            f'/api/optimization/suggestions/{suggestion_id}/apply',
            json={'applied_by': 'test_user'}
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'affected_rules' in data
        
        # 验证建议状态已更新
        response = self.client.get(f'/api/optimization/suggestions/{suggestion_id}')
        data = json.loads(response.data)
        assert data['suggestion']['status'] == 'applied'
        assert data['suggestion']['applied_by'] == 'test_user'
    
    def test_apply_suggestion_already_processed(self):
        """测试应用已处理的建议"""
        # 获取一个已应用的建议
        response = self.client.get('/api/optimization/suggestions?status=applied')
        data = json.loads(response.data)
        suggestion_id = data['suggestions'][0]['suggestion_id']
        
        # 尝试再次应用
        response = self.client.post(
            f'/api/optimization/suggestions/{suggestion_id}/apply',
            json={'applied_by': 'test_user'}
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'SUGGESTION_ALREADY_PROCESSED'
    
    def test_ignore_suggestion(self):
        """测试忽略优化建议"""
        # 先获取一个待处理建议
        response = self.client.get('/api/optimization/suggestions?status=pending')
        data = json.loads(response.data)
        suggestion_id = data['suggestions'][0]['suggestion_id']
        
        # 忽略建议
        response = self.client.post(f'/api/optimization/suggestions/{suggestion_id}/ignore')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 验证建议状态已更新
        response = self.client.get(f'/api/optimization/suggestions/{suggestion_id}')
        data = json.loads(response.data)
        assert data['suggestion']['status'] == 'ignored'
    
    def test_generate_suggestions(self):
        """测试生成优化建议"""
        # 生成建议
        response = self.client.post(
            '/api/optimization/suggestions/generate',
            json={
                'min_logs': 5
            }
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'analysis_summary' in data
        assert 'suggestions_count' in data
        
        # 验证分析摘要
        summary = data['analysis_summary']
        assert 'total_logs' in summary
        assert 'success_count' in summary
        assert 'failed_count' in summary
        assert 'accuracy_rate' in summary
    
    def test_generate_suggestions_with_date_range(self):
        """测试指定日期范围生成建议"""
        # 指定最近7天
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        response = self.client.post(
            '/api/optimization/suggestions/generate',
            json={
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'min_logs': 5
            }
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_invalid_priority_parameter(self):
        """测试无效的优先级参数"""
        response = self.client.get('/api/optimization/suggestions?priority=invalid')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'INVALID_PARAMETER'
    
    def test_invalid_status_parameter(self):
        """测试无效的状态参数"""
        response = self.client.get('/api/optimization/suggestions?status=invalid')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['error_code'] == 'INVALID_PARAMETER'


class TestOptimizationSuggestionIntegration:
    """优化建议集成测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, client, db_manager):
        """测试前准备"""
        self.client = client
        self.db_manager = db_manager
    
    def test_full_workflow(self):
        """测试完整工作流程：生成 -> 查看 -> 应用"""
        # 1. 生成建议
        response = self.client.post(
            '/api/optimization/suggestions/generate',
            json={'min_logs': 1}
        )
        assert response.status_code == 200
        
        # 2. 获取建议列表
        response = self.client.get('/api/optimization/suggestions?status=pending')
        assert response.status_code == 200
        data = json.loads(response.data)
        
        if data['total'] > 0:
            suggestion_id = data['suggestions'][0]['suggestion_id']
            
            # 3. 查看建议详情
            response = self.client.get(f'/api/optimization/suggestions/{suggestion_id}')
            assert response.status_code == 200
            
            # 4. 应用建议
            response = self.client.post(
                f'/api/optimization/suggestions/{suggestion_id}/apply',
                json={'applied_by': 'integration_test'}
            )
            assert response.status_code == 200
            
            # 5. 验证建议已应用
            response = self.client.get(f'/api/optimization/suggestions/{suggestion_id}')
            data = json.loads(response.data)
            assert data['suggestion']['status'] == 'applied'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
