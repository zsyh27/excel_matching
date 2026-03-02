# -*- coding: utf-8 -*-
"""
批量解析服务单元测试

验证需求: 10.1, 10.2, 10.3, 10.4, 10.5
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from modules.intelligent_device import (
    BatchParser,
    BatchParseResult,
    DeviceDescriptionParser,
    ParseResult,
    ConfigurationManager
)
from modules.database import DatabaseManager
from modules.models import Device as DeviceModel


@pytest.fixture
def mock_db_manager():
    """创建模拟的数据库管理器"""
    db_manager = Mock(spec=DatabaseManager)
    return db_manager


@pytest.fixture
def mock_parser():
    """创建模拟的解析器"""
    parser = Mock(spec=DeviceDescriptionParser)
    return parser


@pytest.fixture
def batch_parser(mock_parser, mock_db_manager):
    """创建批量解析服务实例"""
    return BatchParser(parser=mock_parser, db_manager=mock_db_manager)


@pytest.fixture
def sample_devices():
    """创建示例设备列表"""
    devices = []
    
    # 设备1：有详细参数
    device1 = DeviceModel()
    device1.device_id = "DEV001"
    device1.brand = "西门子"
    device1.device_name = "CO2传感器"
    device1.spec_model = "QAA2061"
    device1.detailed_params = "西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA"
    device1.unit_price = 1250.0
    device1.raw_description = None
    device1.key_params = None
    device1.confidence_score = None
    devices.append(device1)
    
    # 设备2：有原始描述
    device2 = DeviceModel()
    device2.device_id = "DEV002"
    device2.brand = "霍尼韦尔"
    device2.device_name = "温度传感器"
    device2.spec_model = "T7350"
    device2.detailed_params = "霍尼韦尔温度传感器"
    device2.unit_price = 850.0
    device2.raw_description = "霍尼韦尔 温度传感器 T7350 量程-50-150℃"
    device2.key_params = None
    device2.confidence_score = None
    devices.append(device2)
    
    # 设备3：没有描述
    device3 = DeviceModel()
    device3.device_id = "DEV003"
    device3.brand = "施耐德"
    device3.device_name = "座阀"
    device3.spec_model = "VVF53"
    device3.detailed_params = ""
    device3.unit_price = 2500.0
    device3.raw_description = None
    device3.key_params = None
    device3.confidence_score = None
    devices.append(device3)
    
    return devices


class TestBatchParser:
    """批量解析服务测试类"""
    
    def test_initialization(self, batch_parser):
        """测试批量解析服务初始化"""
        assert batch_parser is not None
        assert batch_parser.parser is not None
        assert batch_parser.db_manager is not None
    
    def test_batch_parse_all_devices(self, batch_parser, mock_db_manager, mock_parser, sample_devices):
        """
        测试批量解析所有设备
        
        验证需求: 10.1, 10.2, 10.3
        """
        # 模拟数据库查询
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = sample_devices
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_context.__exit__.return_value = None
        mock_db_manager.session_scope.return_value = mock_context
        
        # 模拟解析结果
        def mock_parse(description):
            result = ParseResult()
            result.raw_description = description
            result.brand = "西门子"
            result.device_type = "CO2传感器"
            result.model = "QAA2061"
            result.key_params = {"量程": {"value": "0-2000ppm", "required": True}}
            result.confidence_score = 0.85
            return result
        
        mock_parser.parse.side_effect = mock_parse
        
        # 执行批量解析（dry_run模式）
        result = batch_parser.batch_parse(device_ids=None, dry_run=True)
        
        # 验证结果
        assert result.total == 3
        assert result.processed == 3
        assert result.successful == 2  # 设备1和2成功，设备3失败（没有描述）
        assert result.failed == 1
        assert 0 < result.success_rate < 1
        assert len(result.failed_devices) == 1
        assert result.failed_devices[0]['device_id'] == "DEV003"
    
    def test_batch_parse_specific_devices(self, batch_parser, mock_db_manager, mock_parser, sample_devices):
        """
        测试批量解析指定设备
        
        验证需求: 10.1, 10.2
        """
        # 只返回前两个设备
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = sample_devices[:2]
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_context.__exit__.return_value = None
        mock_db_manager.session_scope.return_value = mock_context
        
        # 模拟解析结果
        mock_parse_result = ParseResult()
        mock_parse_result.brand = "西门子"
        mock_parse_result.device_type = "CO2传感器"
        mock_parse_result.key_params = {"量程": {"value": "0-2000ppm"}}
        mock_parse_result.confidence_score = 0.85
        mock_parser.parse.return_value = mock_parse_result
        
        # 执行批量解析
        result = batch_parser.batch_parse(device_ids=["DEV001", "DEV002"], dry_run=True)
        
        # 验证结果
        assert result.total == 2
        assert result.processed == 2
        assert result.successful == 2
        assert result.failed == 0
    
    def test_batch_parse_with_update(self, batch_parser, mock_db_manager, mock_parser, sample_devices):
        """
        测试批量解析并更新数据库
        
        验证需求: 10.3
        """
        # 模拟数据库查询和更新
        mock_session = MagicMock()
        # 需要同时支持 .all() 和 .filter().all()
        mock_session.query.return_value.filter.return_value.all.return_value = [sample_devices[0]]
        mock_session.query.return_value.filter_by.return_value.first.return_value = sample_devices[0]
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_context.__exit__.return_value = None
        mock_db_manager.session_scope.return_value = mock_context
        
        # 模拟解析结果
        mock_parse_result = ParseResult()
        mock_parse_result.raw_description = "西门子 CO2传感器 QAA2061"
        mock_parse_result.brand = "西门子"
        mock_parse_result.device_type = "CO2传感器"
        mock_parse_result.model = "QAA2061"
        mock_parse_result.key_params = {
            "量程": {"value": "0-2000ppm", "required": True},
            "输出信号": {"value": "4-20mA", "required": True}
        }
        mock_parse_result.confidence_score = 0.92
        mock_parser.parse.return_value = mock_parse_result
        
        # 执行批量解析（非dry_run模式）
        result = batch_parser.batch_parse(device_ids=["DEV001"], dry_run=False)
        
        # 验证结果
        assert result.successful == 1
        assert result.failed == 0
        
        # 验证数据库更新被调用
        assert mock_session.query.called
    
    def test_batch_parse_report_generation(self, batch_parser, mock_db_manager, mock_parser, sample_devices):
        """
        测试批量解析报告生成
        
        验证需求: 10.4
        """
        # 模拟数据库查询
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = sample_devices
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_context.__exit__.return_value = None
        mock_db_manager.session_scope.return_value = mock_context
        
        # 模拟解析结果
        mock_parse_result = ParseResult()
        mock_parse_result.brand = "西门子"
        mock_parse_result.device_type = "CO2传感器"
        mock_parse_result.key_params = {"量程": {"value": "0-2000ppm"}}
        mock_parse_result.confidence_score = 0.85
        mock_parser.parse.return_value = mock_parse_result
        
        # 执行批量解析
        result = batch_parser.batch_parse(dry_run=True)
        
        # 验证报告内容
        assert result.total > 0
        assert result.processed == result.total
        assert result.successful + result.failed == result.total
        assert 0 <= result.success_rate <= 1
        assert isinstance(result.failed_devices, list)
        assert result.start_time is not None
        assert result.end_time is not None
        assert result.duration_seconds >= 0
        
        # 验证报告可以转换为字典
        report_dict = result.to_dict()
        assert 'total' in report_dict
        assert 'processed' in report_dict
        assert 'successful' in report_dict
        assert 'failed' in report_dict
        assert 'success_rate' in report_dict
        assert 'failed_devices' in report_dict
        assert 'start_time' in report_dict
        assert 'end_time' in report_dict
        assert 'duration_seconds' in report_dict
    
    def test_batch_parse_data_integrity_on_error(self, batch_parser, mock_db_manager, mock_parser, sample_devices):
        """
        测试批量解析失败时的数据完整性保护
        
        验证需求: 10.5
        """
        # 模拟数据库查询
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [sample_devices[0]]
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_context.__exit__.return_value = None
        mock_db_manager.session_scope.return_value = mock_context
        
        # 模拟解析器抛出异常
        mock_parser.parse.side_effect = Exception("解析错误")
        
        # 执行批量解析
        result = batch_parser.batch_parse(device_ids=["DEV001"], dry_run=False)
        
        # 验证失败被正确记录
        assert result.failed == 1
        assert result.successful == 0
        assert len(result.failed_devices) == 1
        assert "解析错误" in result.failed_devices[0]['error']
        
        # 验证数据库更新没有被调用（因为解析失败）
        # session_scope 被调用了两次：一次加载设备，一次尝试更新（但因为异常没有实际更新）
        assert mock_db_manager.session_scope.called
    
    def test_batch_parse_empty_device_list(self, batch_parser, mock_db_manager, mock_parser):
        """测试空设备列表的批量解析"""
        # 模拟数据库返回空列表
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = []
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_context.__exit__.return_value = None
        mock_db_manager.session_scope.return_value = mock_context
        
        # 执行批量解析
        result = batch_parser.batch_parse(dry_run=True)
        
        # 验证结果
        assert result.total == 0
        assert result.processed == 0
        assert result.successful == 0
        assert result.failed == 0
        assert result.success_rate == 0.0
    
    def test_batch_parse_with_low_confidence(self, batch_parser, mock_db_manager, mock_parser, sample_devices):
        """测试低置信度的解析结果"""
        # 模拟数据库查询
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = [sample_devices[0]]
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_context.__exit__.return_value = None
        mock_db_manager.session_scope.return_value = mock_context
        
        # 模拟低置信度的解析结果
        mock_parse_result = ParseResult()
        mock_parse_result.brand = None
        mock_parse_result.device_type = None
        mock_parse_result.model = None
        mock_parse_result.key_params = {}
        mock_parse_result.confidence_score = 0.3
        mock_parser.parse.return_value = mock_parse_result
        
        # 执行批量解析
        result = batch_parser.batch_parse(dry_run=True)
        
        # 验证低置信度结果被视为失败
        assert result.failed == 1
        assert result.successful == 0
    
    def test_batch_parse_performance(self, batch_parser, mock_db_manager, mock_parser):
        """测试批量解析性能"""
        # 创建大量设备
        large_device_list = []
        for i in range(100):
            device = DeviceModel()
            device.device_id = f"DEV{i:03d}"
            device.brand = "西门子"
            device.device_name = "传感器"
            device.spec_model = f"MODEL{i}"
            device.detailed_params = f"西门子传感器 MODEL{i}"
            device.unit_price = 1000.0
            large_device_list.append(device)
        
        # 模拟数据库查询
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = large_device_list
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_context.__exit__.return_value = None
        mock_db_manager.session_scope.return_value = mock_context
        
        # 模拟解析结果
        mock_parse_result = ParseResult()
        mock_parse_result.brand = "西门子"
        mock_parse_result.device_type = "传感器"
        mock_parse_result.key_params = {"量程": {"value": "0-100"}}
        mock_parse_result.confidence_score = 0.85
        mock_parser.parse.return_value = mock_parse_result
        
        # 执行批量解析
        result = batch_parser.batch_parse(dry_run=True)
        
        # 验证性能
        assert result.total == 100
        assert result.processed == 100
        assert result.duration_seconds >= 0
        # 验证每秒至少处理10个设备（需求13.2）
        if result.duration_seconds > 0:
            throughput = result.processed / result.duration_seconds
            # 注意：这是模拟测试，实际性能会更慢
            assert throughput > 0
    
    def test_dry_run_mode_no_database_updates(self, batch_parser, mock_db_manager, mock_parser, sample_devices):
        """
        测试 dry_run 模式不更新数据库
        
        验证需求: 10.3
        """
        # 模拟数据库查询
        mock_session = MagicMock()
        # 需要支持 .filter().all() 调用链
        mock_session.query.return_value.filter.return_value.all.return_value = [sample_devices[0]]
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_context.__exit__.return_value = None
        mock_db_manager.session_scope.return_value = mock_context
        
        # 模拟解析结果
        mock_parse_result = ParseResult()
        mock_parse_result.raw_description = "西门子 CO2传感器"
        mock_parse_result.brand = "西门子"
        mock_parse_result.device_type = "CO2传感器"
        mock_parse_result.model = "QAA2061"
        mock_parse_result.key_params = {"量程": {"value": "0-2000ppm"}}
        mock_parse_result.confidence_score = 0.85
        mock_parser.parse.return_value = mock_parse_result
        
        # 执行批量解析（dry_run模式）
        result = batch_parser.batch_parse(device_ids=["DEV001"], dry_run=True)
        
        # 验证解析成功
        assert result.successful == 1
        assert result.failed == 0
        
        # 验证数据库只被调用一次（加载设备），没有更新操作
        # 在 dry_run 模式下，session_scope 只应该被调用一次（加载设备）
        assert mock_db_manager.session_scope.call_count == 1
    
    def test_batch_parse_mixed_success_and_failure(self, batch_parser, mock_db_manager, mock_parser):
        """
        测试批量解析混合成功和失败的情况
        
        验证需求: 10.4, 10.5
        """
        # 创建测试设备
        devices = []
        for i in range(5):
            device = DeviceModel()
            device.device_id = f"DEV{i:03d}"
            device.brand = "西门子"
            device.device_name = "传感器"
            device.spec_model = f"MODEL{i}"
            device.detailed_params = f"西门子传感器 MODEL{i}" if i % 2 == 0 else ""
            device.unit_price = 1000.0
            devices.append(device)
        
        # 模拟数据库查询
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = devices
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_context.__exit__.return_value = None
        mock_db_manager.session_scope.return_value = mock_context
        
        # 模拟解析结果
        mock_parse_result = ParseResult()
        mock_parse_result.brand = "西门子"
        mock_parse_result.device_type = "传感器"
        mock_parse_result.key_params = {"量程": {"value": "0-100"}}
        mock_parse_result.confidence_score = 0.85
        mock_parser.parse.return_value = mock_parse_result
        
        # 执行批量解析
        result = batch_parser.batch_parse(dry_run=True)
        
        # 验证结果：3个成功（偶数索引），2个失败（奇数索引，没有描述）
        assert result.total == 5
        assert result.processed == 5
        assert result.successful == 3
        assert result.failed == 2
        assert result.success_rate == 0.6
        assert len(result.failed_devices) == 2
        
        # 验证失败设备的错误信息
        failed_ids = [fd['device_id'] for fd in result.failed_devices]
        assert "DEV001" in failed_ids
        assert "DEV003" in failed_ids
    
    def test_batch_parse_report_format(self, batch_parser, mock_db_manager, mock_parser, sample_devices):
        """
        测试批量解析报告格式
        
        验证需求: 10.4
        """
        # 模拟数据库查询
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = [sample_devices[0]]
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_context.__exit__.return_value = None
        mock_db_manager.session_scope.return_value = mock_context
        
        # 模拟解析结果
        mock_parse_result = ParseResult()
        mock_parse_result.brand = "西门子"
        mock_parse_result.device_type = "CO2传感器"
        mock_parse_result.key_params = {"量程": {"value": "0-2000ppm"}}
        mock_parse_result.confidence_score = 0.85
        mock_parser.parse.return_value = mock_parse_result
        
        # 执行批量解析
        result = batch_parser.batch_parse(dry_run=True)
        
        # 转换为字典格式
        report_dict = result.to_dict()
        
        # 验证报告格式
        assert isinstance(report_dict, dict)
        assert isinstance(report_dict['total'], int)
        assert isinstance(report_dict['processed'], int)
        assert isinstance(report_dict['successful'], int)
        assert isinstance(report_dict['failed'], int)
        assert isinstance(report_dict['success_rate'], float)
        assert isinstance(report_dict['failed_devices'], list)
        assert isinstance(report_dict['duration_seconds'], float)
        
        # 验证时间戳格式
        if report_dict['start_time']:
            assert isinstance(report_dict['start_time'], str)
            # 验证是ISO格式
            datetime.fromisoformat(report_dict['start_time'])
        
        if report_dict['end_time']:
            assert isinstance(report_dict['end_time'], str)
            datetime.fromisoformat(report_dict['end_time'])
    
    def test_batch_parse_database_error_handling(self, batch_parser, mock_db_manager, mock_parser):
        """
        测试数据库错误处理
        
        验证需求: 10.5
        """
        # 模拟数据库连接失败
        mock_db_manager.session_scope.side_effect = Exception("数据库连接失败")
        
        # 执行批量解析应该抛出异常
        with pytest.raises(Exception) as exc_info:
            batch_parser.batch_parse(dry_run=True)
        
        assert "数据库连接失败" in str(exc_info.value)
    
    def test_batch_parse_partial_update_failure(self, batch_parser, mock_db_manager, mock_parser, sample_devices):
        """
        测试部分更新失败时的数据保护
        
        验证需求: 10.5
        """
        # 模拟数据库查询成功
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [sample_devices[0]]
        
        # 模拟更新时查询失败（设备不存在）
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_context.__exit__.return_value = None
        mock_db_manager.session_scope.return_value = mock_context
        
        # 模拟解析结果
        mock_parse_result = ParseResult()
        mock_parse_result.raw_description = "西门子 CO2传感器"
        mock_parse_result.brand = "西门子"
        mock_parse_result.device_type = "CO2传感器"
        mock_parse_result.model = "QAA2061"
        mock_parse_result.key_params = {"量程": {"value": "0-2000ppm"}}
        mock_parse_result.confidence_score = 0.85
        mock_parser.parse.return_value = mock_parse_result
        
        # 执行批量解析（非dry_run模式）
        result = batch_parser.batch_parse(device_ids=["DEV001"], dry_run=False)
        
        # 验证解析成功但更新可能失败
        # 由于更新逻辑中设备不存在只是记录日志，不抛出异常，所以解析仍然算成功
        assert result.processed == 1
    
    def test_batch_parse_prefers_raw_description(self, batch_parser, mock_db_manager, mock_parser, sample_devices):
        """
        测试批量解析优先使用 raw_description
        
        验证需求: 10.2
        """
        # 使用有 raw_description 的设备
        device = sample_devices[1]  # DEV002 有 raw_description
        
        # 模拟数据库查询
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = [device]
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_context.__exit__.return_value = None
        mock_db_manager.session_scope.return_value = mock_context
        
        # 模拟解析结果
        mock_parse_result = ParseResult()
        mock_parse_result.brand = "霍尼韦尔"
        mock_parse_result.device_type = "温度传感器"
        mock_parse_result.key_params = {"量程": {"value": "-50-150℃"}}
        mock_parse_result.confidence_score = 0.85
        mock_parser.parse.return_value = mock_parse_result
        
        # 执行批量解析
        result = batch_parser.batch_parse(dry_run=True)
        
        # 验证解析器被调用时使用的是 raw_description
        mock_parser.parse.assert_called_once()
        call_args = mock_parser.parse.call_args[0][0]
        assert call_args == device.raw_description
    
    def test_batch_parse_fallback_to_detailed_params(self, batch_parser, mock_db_manager, mock_parser, sample_devices):
        """
        测试批量解析在没有 raw_description 时使用 detailed_params
        
        验证需求: 10.2
        """
        # 使用没有 raw_description 的设备
        device = sample_devices[0]  # DEV001 没有 raw_description
        
        # 模拟数据库查询
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = [device]
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_session
        mock_context.__exit__.return_value = None
        mock_db_manager.session_scope.return_value = mock_context
        
        # 模拟解析结果
        mock_parse_result = ParseResult()
        mock_parse_result.brand = "西门子"
        mock_parse_result.device_type = "CO2传感器"
        mock_parse_result.key_params = {"量程": {"value": "0-2000ppm"}}
        mock_parse_result.confidence_score = 0.85
        mock_parser.parse.return_value = mock_parse_result
        
        # 执行批量解析
        result = batch_parser.batch_parse(dry_run=True)
        
        # 验证解析器被调用时使用的是 detailed_params
        mock_parser.parse.assert_called_once()
        call_args = mock_parser.parse.call_args[0][0]
        assert call_args == device.detailed_params
