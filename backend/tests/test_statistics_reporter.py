"""
统计报告生成器测试

测试 StatisticsReporter 的各种统计功能
验证需求: 17.1-17.6
"""

import pytest
import os
from modules.database import DatabaseManager
from modules.statistics_reporter import StatisticsReporter
from modules.models import Device as DeviceModel, Rule as RuleModel, Config as ConfigModel


@pytest.fixture
def db_manager():
    """创建测试数据库管理器"""
    # 使用内存数据库进行测试
    db_manager = DatabaseManager(database_url='sqlite:///:memory:')
    db_manager.create_tables()
    yield db_manager
    db_manager.close()


@pytest.fixture
def statistics_reporter(db_manager):
    """创建统计报告生成器"""
    return StatisticsReporter(db_manager)


@pytest.fixture
def sample_data(db_manager):
    """创建示例数据"""
    with db_manager.session_scope() as session:
        # 添加设备
        devices = [
            DeviceModel(device_id='D001', brand='华为', device_name='交换机', 
                       spec_model='S5720', detailed_params='24口千兆', unit_price=5000.0),
            DeviceModel(device_id='D002', brand='华为', device_name='路由器', 
                       spec_model='AR2220', detailed_params='企业级', unit_price=8000.0),
            DeviceModel(device_id='D003', brand='思科', device_name='交换机', 
                       spec_model='C2960', detailed_params='48口千兆', unit_price=12000.0),
            DeviceModel(device_id='D004', brand='思科', device_name='防火墙', 
                       spec_model='ASA5506', detailed_params='企业级', unit_price=15000.0),
            DeviceModel(device_id='D005', brand='H3C', device_name='交换机', 
                       spec_model='S5130', detailed_params='24口千兆', unit_price=4500.0),
        ]
        for device in devices:
            session.add(device)
        
        # 添加规则（只为部分设备添加规则）
        rules = [
            RuleModel(rule_id='R001', target_device_id='D001', 
                     auto_extracted_features=['华为', '交换机', 'S5720'],
                     feature_weights=[3.0, 2.5, 3.0], match_threshold=0.7),
            RuleModel(rule_id='R002', target_device_id='D002', 
                     auto_extracted_features=['华为', '路由器', 'AR2220'],
                     feature_weights=[3.0, 2.5, 3.0], match_threshold=0.7),
            RuleModel(rule_id='R003', target_device_id='D003', 
                     auto_extracted_features=['思科', '交换机', 'C2960'],
                     feature_weights=[3.0, 2.5, 3.0], match_threshold=0.7),
        ]
        for rule in rules:
            session.add(rule)
        
        # 添加配置
        configs = [
            ConfigModel(config_key='match_threshold', config_value=0.7, 
                       description='默认匹配阈值'),
            ConfigModel(config_key='batch_size', config_value=100, 
                       description='批量操作大小'),
        ]
        for config in configs:
            session.add(config)


class TestStatisticsReporter:
    """测试统计报告生成器"""
    
    def test_get_table_counts(self, statistics_reporter, sample_data):
        """测试获取表统计信息 - 验证需求 17.1"""
        counts = statistics_reporter.get_table_counts()
        
        assert 'devices' in counts
        assert 'rules' in counts
        assert 'configs' in counts
        assert counts['devices'] == 5
        assert counts['rules'] == 3
        assert counts['configs'] == 2
    
    def test_get_devices_by_brand(self, statistics_reporter, sample_data):
        """测试按品牌统计设备 - 验证需求 17.2"""
        brand_stats = statistics_reporter.get_devices_by_brand()
        
        assert isinstance(brand_stats, list)
        assert len(brand_stats) == 3  # 华为、思科、H3C
        
        # 验证统计结果（按数量降序）
        assert brand_stats[0]['brand'] in ['华为', '思科']
        assert brand_stats[0]['count'] == 2
        
        # 验证所有品牌都被统计
        brands = [stat['brand'] for stat in brand_stats]
        assert '华为' in brands
        assert '思科' in brands
        assert 'H3C' in brands
    
    def test_get_rule_coverage(self, statistics_reporter, sample_data):
        """测试规则覆盖统计 - 验证需求 17.3"""
        coverage = statistics_reporter.get_rule_coverage()
        
        assert 'total_devices' in coverage
        assert 'devices_with_rules' in coverage
        assert 'devices_without_rules' in coverage
        assert 'coverage_percentage' in coverage
        
        assert coverage['total_devices'] == 5
        assert coverage['devices_with_rules'] == 3
        assert coverage['devices_without_rules'] == 2
        assert coverage['coverage_percentage'] == 60.0
    
    def test_get_database_size_sqlite(self, statistics_reporter, sample_data):
        """测试获取数据库大小（SQLite）- 验证需求 17.4"""
        db_size = statistics_reporter.get_database_size()
        
        assert 'database_type' in db_size
        assert db_size['database_type'] == 'sqlite'
        
        # 内存数据库可能没有文件路径
        if 'error' not in db_size:
            assert 'size_bytes' in db_size
            assert 'size_mb' in db_size
            assert 'size_readable' in db_size
    
    def test_get_index_info(self, statistics_reporter, sample_data):
        """测试获取索引信息 - 验证需求 17.5"""
        index_info = statistics_reporter.get_index_info()
        
        assert isinstance(index_info, dict)
        assert 'devices' in index_info
        assert 'rules' in index_info
        assert 'configs' in index_info  # 表名是 configs 而不是 config
        
        # 验证索引信息结构
        for table_name, indexes in index_info.items():
            assert isinstance(indexes, list)
            for index in indexes:
                assert 'name' in index
                assert 'columns' in index
                assert 'unique' in index
    
    def test_generate_report(self, statistics_reporter, sample_data):
        """测试生成统计报告 - 验证需求 17.6"""
        report = statistics_reporter.generate_report()
        
        assert isinstance(report, str)
        assert len(report) > 0
        
        # 验证报告包含关键信息
        assert '数据库统计报告' in report
        assert '表统计信息' in report
        assert '品牌分布' in report
        assert '规则覆盖情况' in report
        assert '数据库大小' in report
        assert '索引信息' in report
        
        # 验证报告包含具体数据
        assert 'devices' in report
        assert 'rules' in report
        assert '华为' in report
        assert '思科' in report
    
    def test_empty_database(self, statistics_reporter):
        """测试空数据库的统计"""
        counts = statistics_reporter.get_table_counts()
        
        assert counts['devices'] == 0
        assert counts['rules'] == 0
        assert counts['configs'] == 0
        
        coverage = statistics_reporter.get_rule_coverage()
        assert coverage['total_devices'] == 0
        assert coverage['devices_with_rules'] == 0
        assert coverage['coverage_percentage'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
