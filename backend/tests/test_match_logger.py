"""
测试匹配日志记录器

验证需求: 10.9, 10.10, 10.11
"""

import pytest
from datetime import datetime, timedelta
from modules.database import DatabaseManager
from modules.match_logger import MatchLogger


class TestMatchLogger:
    """测试匹配日志记录器"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建内存数据库
        self.db_manager = DatabaseManager('sqlite:///:memory:')
        self.db_manager.create_tables()
        
        # 创建日志记录器
        self.match_logger = MatchLogger(self.db_manager)
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        self.db_manager.close()
    
    def test_log_match_success(self):
        """测试记录成功匹配 - 验证需求 10.9"""
        # 准备测试数据
        input_description = "温度传感器，0-50℃，4-20mA"
        extracted_features = ["温度传感器", "0-50摄氏度", "4-20ma"]
        match_result = {
            'device_id': 'SENSOR001',
            'match_status': 'success',
            'match_score': 8.5,
            'match_threshold': 5.0,
            'match_reason': '权重得分 8.5 超过阈值 5.0'
        }
        
        # 记录日志
        log_id = self.match_logger.log_match(
            input_description=input_description,
            extracted_features=extracted_features,
            match_result=match_result
        )
        
        # 验证日志ID已生成
        assert log_id is not None
        assert log_id.startswith('LOG_')
        
        # 验证可以查询到日志
        log = self.match_logger.get_log_by_id(log_id)
        assert log is not None
        assert log['input_description'] == input_description
        assert log['extracted_features'] == extracted_features
        assert log['match_status'] == 'success'
        assert log['matched_device_id'] == 'SENSOR001'
        assert log['match_score'] == 8.5
    
    def test_log_match_failed(self):
        """测试记录失败匹配 - 验证需求 10.9"""
        # 准备测试数据
        input_description = "未知设备"
        extracted_features = ["未知设备"]
        match_result = {
            'device_id': None,
            'match_status': 'failed',
            'match_score': 0.0,
            'match_threshold': 5.0,
            'match_reason': '未找到匹配的设备'
        }
        
        # 记录日志
        log_id = self.match_logger.log_match(
            input_description=input_description,
            extracted_features=extracted_features,
            match_result=match_result
        )
        
        # 验证日志ID已生成
        assert log_id is not None
        
        # 验证可以查询到日志
        log = self.match_logger.get_log_by_id(log_id)
        assert log is not None
        assert log['match_status'] == 'failed'
        assert log['matched_device_id'] is None
    
    def test_query_logs_all(self):
        """测试查询所有日志 - 验证需求 10.10"""
        # 记录多条日志
        for i in range(5):
            self.match_logger.log_match(
                input_description=f"设备{i}",
                extracted_features=[f"特征{i}"],
                match_result={
                    'device_id': f'DEV{i}',
                    'match_status': 'success' if i % 2 == 0 else 'failed',
                    'match_score': float(i),
                    'match_threshold': 5.0,
                    'match_reason': f'原因{i}'
                }
            )
        
        # 查询所有日志
        result = self.match_logger.query_logs()
        
        assert result['success'] is True
        assert result['total'] == 5
        assert len(result['logs']) == 5
    
    def test_query_logs_by_status(self):
        """测试按状态筛选日志 - 验证需求 10.10"""
        # 记录成功和失败的日志
        for i in range(6):
            self.match_logger.log_match(
                input_description=f"设备{i}",
                extracted_features=[f"特征{i}"],
                match_result={
                    'device_id': f'DEV{i}' if i < 4 else None,
                    'match_status': 'success' if i < 4 else 'failed',
                    'match_score': float(i),
                    'match_threshold': 5.0,
                    'match_reason': f'原因{i}'
                }
            )
        
        # 查询成功的日志
        result_success = self.match_logger.query_logs(status='success')
        assert result_success['total'] == 4
        
        # 查询失败的日志
        result_failed = self.match_logger.query_logs(status='failed')
        assert result_failed['total'] == 2
    
    def test_query_logs_by_date_range(self):
        """测试按日期范围筛选日志 - 验证需求 10.10"""
        # 记录日志
        now = datetime.utcnow()
        self.match_logger.log_match(
            input_description="设备1",
            extracted_features=["特征1"],
            match_result={
                'device_id': 'DEV1',
                'match_status': 'success',
                'match_score': 5.0,
                'match_threshold': 5.0,
                'match_reason': '原因1'
            }
        )
        
        # 查询今天的日志
        start_date = now - timedelta(hours=1)
        end_date = now + timedelta(hours=1)
        result = self.match_logger.query_logs(start_date=start_date, end_date=end_date)
        
        assert result['total'] >= 1
    
    def test_query_logs_pagination(self):
        """测试分页查询 - 验证需求 10.10"""
        # 记录10条日志
        for i in range(10):
            self.match_logger.log_match(
                input_description=f"设备{i}",
                extracted_features=[f"特征{i}"],
                match_result={
                    'device_id': f'DEV{i}',
                    'match_status': 'success',
                    'match_score': float(i),
                    'match_threshold': 5.0,
                    'match_reason': f'原因{i}'
                }
            )
        
        # 第一页（每页3条）
        result_page1 = self.match_logger.query_logs(page=1, page_size=3)
        assert result_page1['total'] == 10
        assert len(result_page1['logs']) == 3
        assert result_page1['page'] == 1
        
        # 第二页
        result_page2 = self.match_logger.query_logs(page=2, page_size=3)
        assert len(result_page2['logs']) == 3
        assert result_page2['page'] == 2
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        # 记录成功和失败的日志
        for i in range(10):
            self.match_logger.log_match(
                input_description=f"设备{i}",
                extracted_features=[f"特征{i}"],
                match_result={
                    'device_id': f'DEV{i}' if i < 7 else None,
                    'match_status': 'success' if i < 7 else 'failed',
                    'match_score': float(i),
                    'match_threshold': 5.0,
                    'match_reason': f'原因{i}'
                }
            )
        
        # 获取统计信息
        stats = self.match_logger.get_statistics()
        
        assert stats['success'] is True
        assert stats['total'] == 10
        assert stats['success_count'] == 7
        assert stats['failed_count'] == 3
        assert stats['accuracy_rate'] == 70.0
    
    def test_log_match_with_empty_features(self):
        """测试记录空特征的匹配"""
        # 准备测试数据
        input_description = ""
        extracted_features = []
        match_result = {
            'device_id': None,
            'match_status': 'failed',
            'match_score': 0.0,
            'match_threshold': 5.0,
            'match_reason': '设备描述为空'
        }
        
        # 记录日志
        log_id = self.match_logger.log_match(
            input_description=input_description,
            extracted_features=extracted_features,
            match_result=match_result
        )
        
        # 验证日志已记录
        assert log_id is not None
        log = self.match_logger.get_log_by_id(log_id)
        assert log is not None
        assert log['extracted_features'] == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
