"""
匹配引擎模块测试

测试匹配引擎的核心功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from modules.match_engine import MatchEngine, MatchResult, MatchCandidate
from modules.data_loader import DataLoader, Device, Rule
from modules.text_preprocessor import TextPreprocessor


@pytest.fixture
def config():
    """配置fixture"""
    return {
        "normalization_map": {
            "~": "-",
            "℃": "摄氏度",
            "PPM": "ppm"
        },
        "feature_split_chars": [",", ";", "，"],
        "ignore_keywords": ["施工要求"],
        "global_config": {
            "default_match_threshold": 5.0,
            "unify_lowercase": True,
            "remove_whitespace": True,
            "fullwidth_to_halfwidth": True
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
            detailed_params="0-100PPM,4-20mA/0-10V/2-10V信号,无显示,无继电器输出",
            unit_price=766.14
        ),
        "SENSOR002": Device(
            device_id="SENSOR002",
            brand="西门子",
            device_name="温度传感器",
            spec_model="QAA2061",
            detailed_params="0-50摄氏度,4-20mA输出,壁挂式",
            unit_price=320.50
        )
    }


@pytest.fixture
def rules():
    """规则数据fixture"""
    return [
        Rule(
            rule_id="R001",
            target_device_id="SENSOR001",
            auto_extracted_features=["霍尼韦尔", "co传感器", "hscm-r100u", "0-100ppm", "4-20ma"],
            feature_weights={"霍尼韦尔": 3.0, "hscm-r100u": 3.0, "0-100ppm": 2.0, "4-20ma": 2.0},
            match_threshold=3.0,
            remark="霍尼韦尔CO传感器"
        ),
        Rule(
            rule_id="R002",
            target_device_id="SENSOR002",
            auto_extracted_features=["西门子", "温度传感器", "qaa2061", "0-50摄氏度", "4-20ma"],
            feature_weights={"西门子": 3.0, "qaa2061": 3.0, "0-50摄氏度": 2.0, "4-20ma": 2.0},
            match_threshold=3.0,
            remark="西门子温度传感器"
        )
    ]


@pytest.fixture
def match_engine(rules, devices, config):
    """匹配引擎fixture"""
    return MatchEngine(rules, devices, config)


class TestMatchEngine:
    """匹配引擎测试类"""
    
    def test_successful_match_with_high_score(self, match_engine):
        """测试成功匹配 - 高权重得分"""
        # 特征包含品牌和型号，应该匹配成功
        features = ["霍尼韦尔", "co传感器", "hscm-r100u", "0-100ppm"]
        result = match_engine.match(features)
        
        assert result.match_status == "success"
        assert result.device_id == "SENSOR001"
        assert result.unit_price == 766.14
        assert result.match_score >= 3.0
        assert "霍尼韦尔" in result.matched_device_text
    
    def test_successful_match_with_threshold(self, match_engine):
        """测试成功匹配 - 刚好达到阈值"""
        # 包含品牌和型号，权重为3+3=6，超过阈值5
        features = ["霍尼韦尔", "hscm-r100u"]
        result = match_engine.match(features)
        
        assert result.match_status == "success"
        assert result.device_id == "SENSOR001"
        assert result.match_score == 6.0
    
    def test_best_match_selection(self, match_engine):
        """测试最佳匹配选择 - 多个规则匹配时选择得分最高的"""
        # 包含两个设备都有的特征，但霍尼韦尔的得分更高
        features = ["霍尼韦尔", "hscm-r100u", "4-20ma"]
        result = match_engine.match(features)
        
        assert result.match_status == "success"
        assert result.device_id == "SENSOR001"  # 霍尼韦尔得分 3+3+2=8
        assert result.match_score == 8.0
    
    def test_fallback_to_default_threshold(self, match_engine):
        """测试兜底机制 - 使用 default_match_threshold"""
        # 得分为6，未达到规则阈值3，但达到默认阈值5
        features = ["霍尼韦尔", "hscm-r100u"]  # 权重为3+3=6
        
        # 临时修改规则阈值为更高的值，使其不满足规则阈值但满足默认阈值
        original_threshold = match_engine.rules[0].match_threshold
        match_engine.rules[0].match_threshold = 10.0  # 设置为10，使得6分不满足
        
        result = match_engine.match(features)
        
        # 应该匹配成功（使用兜底阈值5.0）
        assert result.match_status == "success"
        assert result.match_score == 6.0
        assert "兜底阈值" in result.match_reason
        
        # 恢复原始阈值
        match_engine.rules[0].match_threshold = original_threshold
    
    def test_failed_match_below_threshold(self, match_engine):
        """测试匹配失败 - 得分低于所有阈值"""
        # 不存在的特征
        features = ["不存在的特征"]
        result = match_engine.match(features)
        
        assert result.match_status == "failed"
        assert result.device_id is None
        assert result.matched_device_text is None
        assert result.unit_price == 0.00
        assert result.match_score == 0.0
    
    def test_empty_features(self, match_engine):
        """测试空特征列表"""
        features = []
        result = match_engine.match(features)
        
        assert result.match_status == "failed"
        assert result.device_id is None
        assert "设备描述为空" in result.match_reason
    
    def test_calculate_weight_score(self, match_engine, rules):
        """测试权重得分计算"""
        rule = rules[0]  # 霍尼韦尔规则
        features = ["霍尼韦尔", "0-100ppm", "不存在的特征"]
        
        score, matched = match_engine.calculate_weight_score(features, rule)
        
        assert score == 5.0  # 3 + 2
        assert len(matched) == 2
        assert "霍尼韦尔" in matched
        assert "0-100ppm" in matched
    
    def test_match_result_to_dict(self):
        """测试匹配结果转换为字典"""
        result = MatchResult(
            device_id="SENSOR001",
            matched_device_text="霍尼韦尔 CO传感器 HSCM-R100U",
            unit_price=766.14,
            match_status="success",
            match_score=8.5,
            match_reason="匹配成功"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict['device_id'] == "SENSOR001"
        assert result_dict['unit_price'] == 766.14  # 保留两位小数
        assert result_dict['match_status'] == "success"
        assert result_dict['match_score'] == 8.5
    
    def test_device_not_found_in_table(self, match_engine, rules):
        """测试设备在设备表中不存在的情况"""
        # 创建一个指向不存在设备的规则
        bad_rule = Rule(
            rule_id="R999",
            target_device_id="NONEXISTENT",
            auto_extracted_features=["测试特征"],
            feature_weights={"测试特征": 10.0},
            match_threshold=5.0,
            remark="测试规则"
        )
        match_engine.rules.append(bad_rule)
        
        features = ["测试特征"]
        result = match_engine.match(features)
        
        assert result.match_status == "failed"
        assert "不存在" in result.match_reason


class TestMatchEngineIntegration:
    """匹配引擎集成测试"""
    
    def test_end_to_end_matching(self):
        """端到端匹配测试 - 从文本预处理到匹配结果"""
        # 加载真实数据
        data_loader = DataLoader(
            device_file='data/static_device.json',
            rule_file='data/static_rule.json',
            config_file='data/static_config.json'
        )
        
        devices = data_loader.load_devices()
        rules = data_loader.load_rules()
        config = data_loader.load_config()
        
        # 创建预处理器和匹配引擎
        preprocessor = TextPreprocessor(config)
        match_engine = MatchEngine(rules, devices, config)
        
        # 测试用例1: 标准格式的CO传感器描述
        text1 = "CO浓度探测器，霍尼韦尔，0~100PPM，4~20mA"
        result1 = preprocessor.preprocess(text1)
        match_result1 = match_engine.match(result1.features)
        
        assert match_result1.match_status == "success"
        assert "霍尼韦尔" in match_result1.matched_device_text
        
        # 测试用例2: 非标准格式的温度传感器描述
        text2 = "西门子 温度传感器 QAA2061 0-50℃"
        result2 = preprocessor.preprocess(text2)
        match_result2 = match_engine.match(result2.features)
        
        assert match_result2.match_status == "success"
        assert "西门子" in match_result2.matched_device_text


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
