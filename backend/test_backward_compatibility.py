"""
测试向后兼容性 - 确保MatchEngine扩展不影响现有匹配功能
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from modules.match_engine import MatchEngine, MatchResult
from modules.data_loader import Device, Rule


@pytest.fixture
def config():
    """配置fixture"""
    return {
        "global_config": {
            "default_match_threshold": 5.0
        }
    }


@pytest.fixture
def devices():
    """设备数据fixture"""
    return {
        "SENSOR001": Device(
            device_id="SENSOR001",
            brand="霍尼韦尔",
            device_name="CO传感器",
            spec_model="HSCM-R100U",
            detailed_params="0-100PPM,4-20mA",
            unit_price=766.14
        )
    }


@pytest.fixture
def rules():
    """规则数据fixture"""
    return [
        Rule(
            rule_id="R001",
            target_device_id="SENSOR001",
            auto_extracted_features=["霍尼韦尔", "co传感器", "0-100ppm", "4-20ma"],
            feature_weights={"霍尼韦尔": 3.0, "co传感器": 2.0, "0-100ppm": 2.0, "4-20ma": 2.0},
            match_threshold=5.0,
            remark="霍尼韦尔CO传感器"
        )
    ]


def test_match_without_detail_recorder(rules, devices, config):
    """测试不使用detail_recorder的情况（向后兼容）"""
    # 不传递detail_recorder参数
    match_engine = MatchEngine(rules, devices, config)
    
    features = ["霍尼韦尔", "co传感器", "0-100ppm"]
    result, cache_key = match_engine.match(features)
    
    # 应该正常匹配
    assert result.match_status == "success"
    assert result.device_id == "SENSOR001"
    assert result.match_score == 7.0  # 3 + 2 + 2
    # 应该有缓存键（因为默认record_detail=True）
    assert cache_key is not None


def test_match_with_record_detail_false(rules, devices, config):
    """测试record_detail=False的情况"""
    match_engine = MatchEngine(rules, devices, config)
    
    features = ["霍尼韦尔", "co传感器"]
    result, cache_key = match_engine.match(features, record_detail=False)
    
    # 应该正常匹配
    assert result.match_status == "success"
    assert result.device_id == "SENSOR001"
    assert result.match_score == 5.0  # 3 + 2
    # 不应该有缓存键
    assert cache_key is None


def test_match_result_structure_unchanged(rules, devices, config):
    """测试MatchResult结构没有改变"""
    match_engine = MatchEngine(rules, devices, config)
    
    features = ["霍尼韦尔"]
    result, cache_key = match_engine.match(features)
    
    # 验证MatchResult的所有字段都存在
    assert hasattr(result, 'device_id')
    assert hasattr(result, 'matched_device_text')
    assert hasattr(result, 'unit_price')
    assert hasattr(result, 'match_status')
    assert hasattr(result, 'match_score')
    assert hasattr(result, 'match_reason')
    
    # 验证to_dict()方法仍然工作
    result_dict = result.to_dict()
    assert 'device_id' in result_dict
    assert 'match_status' in result_dict
    assert 'match_score' in result_dict


def test_calculate_weight_score_unchanged(rules, devices, config):
    """测试calculate_weight_score方法没有改变"""
    match_engine = MatchEngine(rules, devices, config)
    
    rule = rules[0]
    features = ["霍尼韦尔", "0-100ppm", "不存在的特征"]
    
    score, matched = match_engine.calculate_weight_score(features, rule)
    
    # 验证返回值格式没有改变
    assert isinstance(score, (int, float))
    assert isinstance(matched, list)
    assert score == 5.0  # 3 + 2
    assert len(matched) == 2


def test_empty_features_behavior(rules, devices, config):
    """测试空特征列表的行为没有改变"""
    match_engine = MatchEngine(rules, devices, config)
    
    features = []
    result, cache_key = match_engine.match(features)
    
    assert result.match_status == "failed"
    assert result.device_id is None
    assert "设备描述为空" in result.match_reason


def test_no_match_behavior(rules, devices, config):
    """测试无匹配的行为没有改变"""
    match_engine = MatchEngine(rules, devices, config)
    
    features = ["不存在的特征"]
    result, cache_key = match_engine.match(features)
    
    assert result.match_status == "failed"
    assert result.device_id is None
    assert result.match_score == 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
