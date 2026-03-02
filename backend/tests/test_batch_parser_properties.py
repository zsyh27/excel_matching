# -*- coding: utf-8 -*-
"""
批量解析服务属性测试

使用属性测试验证批量解析的通用属性
验证需求: 10.5

Feature: intelligent-device-input
"""

import pytest
import copy
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import Mock, MagicMock, patch

from modules.intelligent_device import (
    BatchParser,
    DeviceDescriptionParser,
    ParseResult
)
from modules.database import DatabaseManager
from modules.models import Device as DeviceModel


# 策略：生成设备数据
@st.composite
def device_data_strategy(draw):
    """生成随机设备数据（不是ORM对象）"""
    return {
        'device_id': draw(st.text(min_size=3, max_size=10, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')),
        'brand': draw(st.sampled_from(['西门子', '霍尼韦尔', '施耐德', '丹佛斯', 'ABB'])),
        'device_name': draw(st.sampled_from(['CO2传感器', '温度传感器', '座阀', '压力传感器', '控制器'])),
        'spec_model': draw(st.text(min_size=3, max_size=10, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')),
        'detailed_params': draw(st.text(min_size=10, max_size=100)),
        'unit_price': draw(st.floats(min_value=100.0, max_value=10000.0, allow_nan=False, allow_infinity=False)),
        'raw_description': draw(st.one_of(st.none(), st.text(min_size=10, max_size=100))),
        'key_params': draw(st.one_of(st.none(), st.just({"量程": {"value": "0-100"}}))),
        'confidence_score': draw(st.one_of(st.none(), st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)))
    }


def create_device_from_data(data):
    """从数据字典创建设备对象"""
    device = DeviceModel()
    for key, value in data.items():
        setattr(device, key, value)
    return device


# Feature: intelligent-device-input, Property 17: 批量解析数据完整性
@given(
    devices_data=st.lists(device_data_strategy(), min_size=1, max_size=5),
    fail_index=st.integers(min_value=0, max_value=4)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_17_batch_parse_data_integrity(devices_data, fail_index):
    """
    属性 17：批量解析数据完整性
    
    对于任意批量解析操作，如果某个设备的解析失败，
    该设备的原始数据应该保持不变，不应该被部分更新或损坏。
    
    **验证：需求 10.5**
    """
    # 确保失败索引在有效范围内
    if fail_index >= len(devices_data):
        fail_index = 0
    
    # 创建设备对象
    devices = [create_device_from_data(data) for data in devices_data]
    
    # 保存设备的初始状态
    initial_states = {}
    for device in devices:
        initial_states[device.device_id] = copy.deepcopy({
            'device_id': device.device_id,
            'brand': device.brand,
            'device_name': device.device_name,
            'spec_model': device.spec_model,
            'detailed_params': device.detailed_params,
            'unit_price': device.unit_price,
            'raw_description': device.raw_description,
            'key_params': copy.deepcopy(device.key_params),
            'confidence_score': device.confidence_score
        })
    
    # 创建模拟对象
    mock_parser = Mock(spec=DeviceDescriptionParser)
    mock_db_manager = Mock(spec=DatabaseManager)
    
    # 模拟数据库查询 - 返回设备列表
    mock_session = MagicMock()
    mock_session.query.return_value.all.return_value = devices
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None
    mock_db_manager.session_scope.return_value = mock_context
    
    # 模拟解析器行为：对于指定索引的设备抛出异常
    parse_call_count = [0]
    
    def parse_side_effect(description):
        current_idx = parse_call_count[0]
        parse_call_count[0] += 1
        
        # 如果是失败索引，抛出异常
        if current_idx == fail_index:
            raise Exception(f"解析失败：设备索引 {current_idx}")
        
        # 否则返回成功的解析结果
        result = ParseResult()
        result.raw_description = description
        result.brand = "西门子"
        result.device_type = "传感器"
        result.model = "TEST123"
        result.key_params = {"量程": {"value": "0-100", "required": True}}
        result.confidence_score = 0.85
        return result
    
    mock_parser.parse.side_effect = parse_side_effect
    
    # 创建批量解析服务
    batch_parser = BatchParser(parser=mock_parser, db_manager=mock_db_manager)
    
    # 执行批量解析（dry_run 模式，不实际更新数据库）
    result = batch_parser.batch_parse(device_ids=None, dry_run=True)
    
    # 验证：至少有一个设备失败
    assert result.failed >= 1
    
    # 验证：所有设备的原始数据应该保持不变（因为是 dry_run 模式）
    for device in devices:
        initial_state = initial_states[device.device_id]
        
        # 验证所有字段都没有被修改
        assert device.device_id == initial_state['device_id']
        assert device.brand == initial_state['brand']
        assert device.device_name == initial_state['device_name']
        assert device.spec_model == initial_state['spec_model']
        assert device.detailed_params == initial_state['detailed_params']
        assert device.unit_price == initial_state['unit_price']
        assert device.raw_description == initial_state['raw_description']
        assert device.key_params == initial_state['key_params']
        assert device.confidence_score == initial_state['confidence_score']


# Feature: intelligent-device-input, Property 17: 批量解析数据完整性（空描述场景）
@given(
    num_devices=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_17_batch_parse_data_integrity_empty_description(num_devices):
    """
    属性 17：批量解析数据完整性（空描述场景）
    
    对于任意批量解析操作，如果设备没有可用的描述文本（解析失败），
    该设备的原始数据应该保持不变，不应该被部分更新或损坏。
    
    **验证：需求 10.5**
    """
    # 创建设备列表，所有设备都没有描述
    devices = []
    for idx in range(num_devices):
        device = DeviceModel()
        device.device_id = f"DEV{idx:03d}"
        device.brand = "测试品牌"
        device.device_name = "测试设备"
        device.spec_model = f"MODEL{idx}"
        device.detailed_params = ""  # 空描述
        device.unit_price = 1000.0
        device.raw_description = None  # 没有原始描述
        device.key_params = None
        device.confidence_score = None
        devices.append(device)
    
    # 保存设备的初始状态
    initial_states = {}
    for device in devices:
        initial_states[device.device_id] = {
            'device_id': device.device_id,
            'brand': device.brand,
            'device_name': device.device_name,
            'spec_model': device.spec_model,
            'detailed_params': device.detailed_params,
            'unit_price': device.unit_price,
            'raw_description': device.raw_description,
            'key_params': device.key_params,
            'confidence_score': device.confidence_score
        }
    
    # 创建模拟对象
    mock_parser = Mock(spec=DeviceDescriptionParser)
    mock_db_manager = Mock(spec=DatabaseManager)
    
    # 模拟数据库查询
    mock_session = MagicMock()
    mock_session.query.return_value.all.return_value = devices
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None
    mock_db_manager.session_scope.return_value = mock_context
    
    # 创建批量解析服务
    batch_parser = BatchParser(parser=mock_parser, db_manager=mock_db_manager)
    
    # 执行批量解析（dry_run 模式）
    result = batch_parser.batch_parse(device_ids=None, dry_run=True)
    
    # 验证：所有设备都应该失败（因为没有描述）
    assert result.failed == num_devices
    assert result.successful == 0
    
    # 验证：所有设备的原始数据应该保持不变
    for device in devices:
        initial_state = initial_states[device.device_id]
        
        # 验证所有字段都没有被修改
        assert device.device_id == initial_state['device_id']
        assert device.brand == initial_state['brand']
        assert device.device_name == initial_state['device_name']
        assert device.spec_model == initial_state['spec_model']
        assert device.detailed_params == initial_state['detailed_params']
        assert device.unit_price == initial_state['unit_price']
        assert device.raw_description == initial_state['raw_description']
        assert device.key_params == initial_state['key_params']
        assert device.confidence_score == initial_state['confidence_score']


# Feature: intelligent-device-input, Property 17: 批量解析数据完整性（解析结果无效场景）
@given(
    devices_data=st.lists(device_data_strategy(), min_size=1, max_size=5)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_17_batch_parse_data_integrity_invalid_parse_result(devices_data):
    """
    属性 17：批量解析数据完整性（解析结果无效场景）
    
    对于任意批量解析操作，如果解析结果无效（没有提取到任何有用信息），
    该设备的原始数据应该保持不变，不应该被部分更新或损坏。
    
    **验证：需求 10.5**
    """
    # 创建设备对象
    devices = [create_device_from_data(data) for data in devices_data]
    
    # 保存设备的初始状态
    initial_states = {}
    for device in devices:
        initial_states[device.device_id] = copy.deepcopy({
            'device_id': device.device_id,
            'brand': device.brand,
            'device_name': device.device_name,
            'spec_model': device.spec_model,
            'detailed_params': device.detailed_params,
            'unit_price': device.unit_price,
            'raw_description': device.raw_description,
            'key_params': copy.deepcopy(device.key_params),
            'confidence_score': device.confidence_score
        })
    
    # 创建模拟对象
    mock_parser = Mock(spec=DeviceDescriptionParser)
    mock_db_manager = Mock(spec=DatabaseManager)
    
    # 模拟数据库查询
    mock_session = MagicMock()
    mock_session.query.return_value.all.return_value = devices
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_session
    mock_context.__exit__.return_value = None
    mock_db_manager.session_scope.return_value = mock_context
    
    # 模拟解析器返回无效结果（所有字段都为空）
    mock_parse_result = ParseResult()
    mock_parse_result.brand = None
    mock_parse_result.device_type = None
    mock_parse_result.model = None
    mock_parse_result.key_params = {}
    mock_parse_result.confidence_score = 0.3
    mock_parser.parse.return_value = mock_parse_result
    
    # 创建批量解析服务
    batch_parser = BatchParser(parser=mock_parser, db_manager=mock_db_manager)
    
    # 执行批量解析（dry_run 模式）
    result = batch_parser.batch_parse(device_ids=None, dry_run=True)
    
    # 验证：所有设备都应该失败（因为解析结果无效）
    assert result.failed == len(devices)
    assert result.successful == 0
    
    # 验证：所有设备的原始数据应该保持不变
    for device in devices:
        initial_state = initial_states[device.device_id]
        
        # 验证所有字段都没有被修改
        assert device.device_id == initial_state['device_id']
        assert device.brand == initial_state['brand']
        assert device.device_name == initial_state['device_name']
        assert device.spec_model == initial_state['spec_model']
        assert device.detailed_params == initial_state['detailed_params']
        assert device.unit_price == initial_state['unit_price']
        assert device.raw_description == initial_state['raw_description']
        assert device.key_params == initial_state['key_params']
        assert device.confidence_score == initial_state['confidence_score']

