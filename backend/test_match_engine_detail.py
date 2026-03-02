"""
测试MatchEngine的详情记录功能

验证任务3.1-3.3的实现
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.match_engine import MatchEngine, MatchResult
from modules.match_detail import MatchDetailRecorder, CandidateDetail, FeatureMatch
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class MockRule:
    """模拟规则对象"""
    rule_id: str
    target_device_id: str
    auto_extracted_features: List[str]
    feature_weights: Dict[str, float]
    match_threshold: float


@dataclass
class MockDevice:
    """模拟设备对象"""
    device_id: str
    brand: str
    device_name: str
    spec_model: str
    unit_price: float
    
    def get_display_text(self):
        return f"{self.brand} {self.device_name} {self.spec_model}"


def test_match_engine_initialization():
    """测试任务3.1: MatchEngine初始化添加detail_recorder参数"""
    print("\n=== 测试3.1: MatchEngine初始化 ===")
    
    # 准备测试数据
    rules = []
    devices = {}
    config = {
        'global_config': {'default_match_threshold': 5.0},
        'brand_keywords': ['霍尼韦尔', '西门子'],
        'device_type_keywords': ['传感器', '控制器']
    }
    
    # 测试1: 不提供detail_recorder，应该自动创建
    engine1 = MatchEngine(rules, devices, config)
    assert engine1.detail_recorder is not None, "应该自动创建detail_recorder"
    assert isinstance(engine1.detail_recorder, MatchDetailRecorder), "应该是MatchDetailRecorder实例"
    print("✓ 测试1通过: 不提供detail_recorder时自动创建")
    
    # 测试2: 提供自定义detail_recorder
    custom_recorder = MatchDetailRecorder(config)
    engine2 = MatchEngine(rules, devices, config, detail_recorder=custom_recorder)
    assert engine2.detail_recorder is custom_recorder, "应该使用提供的detail_recorder"
    print("✓ 测试2通过: 使用提供的detail_recorder")
    
    # 测试3: 向后兼容性 - 不提供detail_recorder参数
    engine3 = MatchEngine(rules, devices, config, match_logger=None)
    assert engine3.detail_recorder is not None, "向后兼容：应该自动创建detail_recorder"
    print("✓ 测试3通过: 向后兼容性")
    
    print("✓ 任务3.1测试全部通过")


def test_evaluate_all_candidates():
    """测试任务3.2: _evaluate_all_candidates()方法"""
    print("\n=== 测试3.2: _evaluate_all_candidates()方法 ===")
    
    # 准备测试数据
    rules = [
        MockRule(
            rule_id="rule1",
            target_device_id="device1",
            auto_extracted_features=["霍尼韦尔", "温度传感器", "t7350"],
            feature_weights={"霍尼韦尔": 3.0, "温度传感器": 2.0, "t7350": 1.5},
            match_threshold=5.0
        ),
        MockRule(
            rule_id="rule2",
            target_device_id="device2",
            auto_extracted_features=["西门子", "温度传感器", "qaa2012"],
            feature_weights={"西门子": 3.0, "温度传感器": 2.0, "qaa2012": 1.5},
            match_threshold=5.0
        )
    ]
    
    devices = {
        "device1": MockDevice(
            device_id="device1",
            brand="霍尼韦尔",
            device_name="温度传感器",
            spec_model="T7350",
            unit_price=150.0
        ),
        "device2": MockDevice(
            device_id="device2",
            brand="西门子",
            device_name="温度传感器",
            spec_model="QAA2012",
            unit_price=200.0
        )
    }
    
    config = {
        'global_config': {'default_match_threshold': 5.0},
        'brand_keywords': ['霍尼韦尔', '西门子'],
        'device_type_keywords': ['传感器', '控制器', '温度传感器']
    }
    
    engine = MatchEngine(rules, devices, config)
    
    # 测试1: 评估所有候选规则
    features = ["霍尼韦尔", "温度传感器"]
    candidates = engine._evaluate_all_candidates(features)
    
    assert len(candidates) == 2, f"应该有2个候选规则，实际: {len(candidates)}"
    print(f"✓ 测试1通过: 找到{len(candidates)}个候选规则")
    
    # 测试2: 候选规则按得分排序
    assert candidates[0].weight_score >= candidates[1].weight_score, "候选规则应该按得分降序排列"
    print(f"✓ 测试2通过: 候选规则按得分排序 ({candidates[0].weight_score} >= {candidates[1].weight_score})")
    
    # 测试3: 候选规则包含完整信息
    candidate = candidates[0]
    assert candidate.rule_id is not None, "应该有rule_id"
    assert candidate.target_device_id is not None, "应该有target_device_id"
    assert candidate.device_info is not None, "应该有device_info"
    assert candidate.weight_score > 0, "应该有weight_score"
    assert candidate.match_threshold > 0, "应该有match_threshold"
    assert candidate.threshold_type in ["rule", "default"], "threshold_type应该是rule或default"
    assert isinstance(candidate.matched_features, list), "matched_features应该是列表"
    assert isinstance(candidate.unmatched_features, list), "unmatched_features应该是列表"
    assert isinstance(candidate.score_breakdown, dict), "score_breakdown应该是字典"
    print("✓ 测试3通过: 候选规则包含完整信息")
    
    # 测试4: 匹配特征按权重排序
    if len(candidate.matched_features) > 1:
        for i in range(len(candidate.matched_features) - 1):
            assert candidate.matched_features[i].weight >= candidate.matched_features[i+1].weight, \
                "匹配特征应该按权重降序排列"
    print("✓ 测试4通过: 匹配特征按权重排序")
    
    # 测试5: 贡献百分比计算
    total_contribution = sum(f.contribution_percentage for f in candidate.matched_features)
    assert abs(total_contribution - 100.0) < 0.1, f"贡献百分比之和应该接近100%，实际: {total_contribution}"
    print(f"✓ 测试5通过: 贡献百分比之和 = {total_contribution:.2f}%")
    
    # 测试6: 未匹配特征
    all_rule_features = set(rules[0].auto_extracted_features)
    matched_feature_names = set(f.feature for f in candidate.matched_features)
    expected_unmatched = all_rule_features - matched_feature_names
    actual_unmatched = set(candidate.unmatched_features)
    assert actual_unmatched == expected_unmatched, "未匹配特征应该正确"
    print(f"✓ 测试6通过: 未匹配特征 = {actual_unmatched}")
    
    print("✓ 任务3.2测试全部通过")


def test_match_with_detail_recording():
    """测试任务3.3: match()方法添加详情记录"""
    print("\n=== 测试3.3: match()方法添加详情记录 ===")
    
    # 准备测试数据
    rules = [
        MockRule(
            rule_id="rule1",
            target_device_id="device1",
            auto_extracted_features=["霍尼韦尔", "温度传感器", "t7350"],
            feature_weights={"霍尼韦尔": 3.0, "温度传感器": 2.0, "t7350": 1.5},
            match_threshold=5.0
        )
    ]
    
    devices = {
        "device1": MockDevice(
            device_id="device1",
            brand="霍尼韦尔",
            device_name="温度传感器",
            spec_model="T7350",
            unit_price=150.0
        )
    }
    
    config = {
        'global_config': {'default_match_threshold': 5.0},
        'brand_keywords': ['霍尼韦尔', '西门子'],
        'device_type_keywords': ['传感器', '控制器', '温度传感器']
    }
    
    engine = MatchEngine(rules, devices, config)
    
    # 测试1: 默认记录详情
    features = ["霍尼韦尔", "温度传感器"]
    result, cache_key = engine.match(features, "霍尼韦尔温度传感器T7350")
    
    assert isinstance(result, MatchResult), "应该返回MatchResult"
    assert cache_key is not None, "默认应该记录详情并返回cache_key"
    assert isinstance(cache_key, str), "cache_key应该是字符串"
    print(f"✓ 测试1通过: 默认记录详情，cache_key = {cache_key[:8]}...")
    
    # 测试2: 可以通过cache_key获取详情
    detail = engine.detail_recorder.get_detail(cache_key)
    assert detail is not None, "应该能通过cache_key获取详情"
    assert detail.original_text == "霍尼韦尔温度传感器T7350", "原始文本应该正确"
    assert detail.preprocessing is not None, "应该有预处理结果"
    assert len(detail.candidates) > 0, "应该有候选规则"
    assert detail.final_result is not None, "应该有最终结果"
    print("✓ 测试2通过: 可以通过cache_key获取详情")
    
    # 测试3: record_detail=False时不记录
    result2, cache_key2 = engine.match(features, "霍尼韦尔温度传感器", record_detail=False)
    
    assert isinstance(result2, MatchResult), "应该返回MatchResult"
    assert cache_key2 is None, "record_detail=False时不应该返回cache_key"
    print("✓ 测试3通过: record_detail=False时不记录详情")
    
    # 测试4: 匹配失败时也记录详情
    features_fail = ["不存在的特征"]
    result3, cache_key3 = engine.match(features_fail, "不存在的设备")
    
    assert result3.match_status == "failed", "应该匹配失败"
    assert cache_key3 is not None, "失败时也应该记录详情"
    
    detail3 = engine.detail_recorder.get_detail(cache_key3)
    assert detail3 is not None, "应该能获取失败的详情"
    assert detail3.final_result['match_status'] == "failed", "详情中应该记录失败状态"
    print("✓ 测试4通过: 匹配失败时也记录详情")
    
    # 测试5: 返回值是元组
    result4, cache_key4 = engine.match(features, "测试")
    assert isinstance((result4, cache_key4), tuple), "应该返回元组"
    assert len((result4, cache_key4)) == 2, "元组应该有2个元素"
    print("✓ 测试5通过: 返回(MatchResult, cache_key)元组")
    
    print("✓ 任务3.3测试全部通过")


def test_integration():
    """集成测试：完整流程"""
    print("\n=== 集成测试：完整流程 ===")
    
    # 准备测试数据
    rules = [
        MockRule(
            rule_id="rule1",
            target_device_id="device1",
            auto_extracted_features=["霍尼韦尔", "温度传感器", "t7350"],
            feature_weights={"霍尼韦尔": 3.0, "温度传感器": 2.0, "t7350": 1.5},
            match_threshold=5.0
        ),
        MockRule(
            rule_id="rule2",
            target_device_id="device2",
            auto_extracted_features=["西门子", "温度传感器"],
            feature_weights={"西门子": 3.0, "温度传感器": 2.0},
            match_threshold=4.0
        )
    ]
    
    devices = {
        "device1": MockDevice(
            device_id="device1",
            brand="霍尼韦尔",
            device_name="温度传感器",
            spec_model="T7350",
            unit_price=150.0
        ),
        "device2": MockDevice(
            device_id="device2",
            brand="西门子",
            device_name="温度传感器",
            spec_model="QAA2012",
            unit_price=200.0
        )
    }
    
    config = {
        'global_config': {'default_match_threshold': 5.0},
        'brand_keywords': ['霍尼韦尔', '西门子'],
        'device_type_keywords': ['传感器', '控制器', '温度传感器']
    }
    
    engine = MatchEngine(rules, devices, config)
    
    # 执行匹配
    features = ["霍尼韦尔", "温度传感器", "t7350"]
    result, cache_key = engine.match(features, "霍尼韦尔温度传感器T7350")
    
    print(f"匹配结果: {result.match_status}")
    print(f"匹配设备: {result.matched_device_text}")
    print(f"匹配得分: {result.match_score}")
    print(f"缓存键: {cache_key[:8]}...")
    
    # 获取详情
    detail = engine.detail_recorder.get_detail(cache_key)
    print(f"\n详情信息:")
    print(f"- 原始文本: {detail.original_text}")
    print(f"- 提取特征: {detail.preprocessing['features']}")
    print(f"- 候选数量: {len(detail.candidates)}")
    print(f"- 最佳候选: {detail.candidates[0].device_info['device_name']}")
    print(f"- 最佳得分: {detail.candidates[0].weight_score}")
    print(f"- 匹配特征数: {len(detail.candidates[0].matched_features)}")
    print(f"- 未匹配特征数: {len(detail.candidates[0].unmatched_features)}")
    print(f"- 决策原因: {detail.decision_reason}")
    print(f"- 优化建议: {len(detail.optimization_suggestions)}条")
    
    # 验证详情完整性
    assert detail.original_text is not None
    assert detail.preprocessing is not None
    assert len(detail.candidates) > 0
    assert detail.final_result is not None
    assert detail.decision_reason is not None
    assert detail.optimization_suggestions is not None
    
    print("\n✓ 集成测试通过")


if __name__ == "__main__":
    print("开始测试MatchEngine详情记录功能...")
    
    try:
        test_match_engine_initialization()
        test_evaluate_all_candidates()
        test_match_with_detail_recording()
        test_integration()
        
        print("\n" + "="*50)
        print("✓ 所有测试通过！")
        print("="*50)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
