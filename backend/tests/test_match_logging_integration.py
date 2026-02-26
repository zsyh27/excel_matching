"""
测试匹配日志记录集成

验证匹配引擎与日志记录器的集成
"""

import pytest
from modules.database import DatabaseManager
from modules.match_engine import MatchEngine
from modules.match_logger import MatchLogger
from modules.models import Device, Rule


class TestMatchLoggingIntegration:
    """测试匹配日志记录集成"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建内存数据库
        self.db_manager = DatabaseManager('sqlite:///:memory:')
        self.db_manager.create_tables()
        
        # 创建日志记录器
        self.match_logger = MatchLogger(self.db_manager)
        
        # 创建测试设备
        self.devices = {
            'SENSOR001': Device(
                device_id='SENSOR001',
                brand='霍尼韦尔',
                device_name='温度传感器',
                spec_model='HST-RA',
                detailed_params='0-50℃,4-20mA',
                unit_price=213.0
            )
        }
        
        # 为设备添加 get_display_text 方法
        def get_display_text(self):
            return f"{self.brand} {self.device_name} {self.spec_model} {self.detailed_params}"
        
        Device.get_display_text = get_display_text
        
        # 创建测试规则
        self.rules = [
            Rule(
                rule_id='R_SENSOR001',
                target_device_id='SENSOR001',
                auto_extracted_features=['霍尼韦尔', '温度传感器', 'HST-RA', '0-50℃', '4-20mA'],
                feature_weights={
                    '霍尼韦尔': 3.0,
                    '温度传感器': 5.0,
                    'HST-RA': 3.0,
                    '0-50℃': 2.0,
                    '4-20mA': 1.0
                },
                match_threshold=5.0,
                remark='温度传感器规则'
            )
        ]
        
        # 创建配置
        self.config = {
            'global_config': {
                'default_match_threshold': 5.0
            }
        }
        
        # 创建匹配引擎（带日志记录器）
        self.match_engine = MatchEngine(
            rules=self.rules,
            devices=self.devices,
            config=self.config,
            match_logger=self.match_logger
        )
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        self.db_manager.close()
    
    def test_match_with_logging_success(self):
        """测试成功匹配时自动记录日志"""
        # 执行匹配
        input_description = "温度传感器，0-50℃，4-20mA"
        features = ['温度传感器', '0-50℃', '4-20mA']
        
        result = self.match_engine.match(features, input_description=input_description)
        
        # 验证匹配成功
        assert result.match_status == 'success'
        assert result.device_id == 'SENSOR001'
        
        # 验证日志已记录
        logs_result = self.match_logger.query_logs()
        assert logs_result['success'] is True
        assert logs_result['total'] == 1
        
        # 验证日志内容
        log = logs_result['logs'][0]
        assert log['input_description'] == input_description
        assert log['extracted_features'] == features
        assert log['match_status'] == 'success'
        assert log['matched_device_id'] == 'SENSOR001'
        assert log['match_score'] > 0
    
    def test_match_with_logging_failed(self):
        """测试失败匹配时自动记录日志"""
        # 执行匹配（使用不匹配的特征）
        input_description = "未知设备"
        features = ['未知设备']
        
        result = self.match_engine.match(features, input_description=input_description)
        
        # 验证匹配失败
        assert result.match_status == 'failed'
        assert result.device_id is None
        
        # 验证日志已记录
        logs_result = self.match_logger.query_logs()
        assert logs_result['success'] is True
        assert logs_result['total'] == 1
        
        # 验证日志内容
        log = logs_result['logs'][0]
        assert log['input_description'] == input_description
        assert log['match_status'] == 'failed'
        assert log['matched_device_id'] is None
    
    def test_multiple_matches_with_logging(self):
        """测试多次匹配都会记录日志"""
        # 执行多次匹配
        test_cases = [
            ("温度传感器，0-50℃", ['温度传感器', '0-50℃']),
            ("霍尼韦尔温度传感器", ['霍尼韦尔', '温度传感器']),
            ("未知设备", ['未知设备'])
        ]
        
        for input_desc, features in test_cases:
            self.match_engine.match(features, input_description=input_desc)
        
        # 验证所有匹配都已记录
        logs_result = self.match_logger.query_logs()
        assert logs_result['total'] == 3
        
        # 验证统计信息
        stats = self.match_logger.get_statistics()
        assert stats['total'] == 3
        # 前两个应该成功，最后一个失败
        assert stats['success_count'] == 2
        assert stats['failed_count'] == 1
    
    def test_match_without_logger(self):
        """测试没有日志记录器时匹配仍然正常工作"""
        # 创建没有日志记录器的匹配引擎
        engine_no_logger = MatchEngine(
            rules=self.rules,
            devices=self.devices,
            config=self.config,
            match_logger=None
        )
        
        # 执行匹配
        features = ['温度传感器', '4-20mA']
        result = engine_no_logger.match(features, input_description="温度传感器")
        
        # 验证匹配正常工作
        assert result.match_status == 'success'
        
        # 验证没有日志记录（因为没有传入日志记录器）
        logs_result = self.match_logger.query_logs()
        assert logs_result['total'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
