"""
测试匹配详情数据类的基本功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.match_detail import FeatureMatch, CandidateDetail, MatchDetail


def test_feature_match():
    """测试FeatureMatch数据类"""
    print("测试 FeatureMatch...")
    
    # 创建实例
    feature = FeatureMatch(
        feature="霍尼韦尔",
        weight=3.0,
        feature_type="brand",
        contribution_percentage=42.857
    )
    
    # 测试to_dict
    feature_dict = feature.to_dict()
    print(f"  to_dict: {feature_dict}")
    assert feature_dict['feature'] == "霍尼韦尔"
    assert feature_dict['weight'] == 3.0
    assert feature_dict['feature_type'] == "brand"
    assert feature_dict['contribution_percentage'] == 42.86  # 四舍五入到2位
    
    # 测试from_dict
    feature2 = FeatureMatch.from_dict(feature_dict)
    print(f"  from_dict: {feature2}")
    assert feature2.feature == feature.feature
    assert feature2.weight == feature.weight
    assert feature2.feature_type == feature.feature_type
    
    print("  ✓ FeatureMatch 测试通过\n")


def test_candidate_detail():
    """测试CandidateDetail数据类"""
    print("测试 CandidateDetail...")
    
    # 创建实例
    candidate = CandidateDetail(
        rule_id="rule_001",
        target_device_id="device_001",
        device_info={
            "brand": "霍尼韦尔",
            "device_name": "温度传感器",
            "spec_model": "T7350A1008"
        },
        weight_score=8.5,
        match_threshold=5.0,
        threshold_type="rule",
        is_qualified=True,
        matched_features=[
            FeatureMatch("霍尼韦尔", 3.0, "brand", 35.29),
            FeatureMatch("温度传感器", 2.5, "device_type", 29.41)
        ],
        unmatched_features=["参数1", "参数2"],
        score_breakdown={"霍尼韦尔": 3.0, "温度传感器": 2.5},
        total_possible_score=10.0
    )
    
    # 测试to_dict
    candidate_dict = candidate.to_dict()
    print(f"  to_dict keys: {list(candidate_dict.keys())}")
    assert candidate_dict['rule_id'] == "rule_001"
    assert candidate_dict['weight_score'] == 8.5
    assert candidate_dict['is_qualified'] is True
    assert len(candidate_dict['matched_features']) == 2
    assert len(candidate_dict['unmatched_features']) == 2
    
    # 测试from_dict
    candidate2 = CandidateDetail.from_dict(candidate_dict)
    print(f"  from_dict: rule_id={candidate2.rule_id}, score={candidate2.weight_score}")
    assert candidate2.rule_id == candidate.rule_id
    assert candidate2.weight_score == candidate.weight_score
    assert len(candidate2.matched_features) == 2
    
    print("  ✓ CandidateDetail 测试通过\n")


def test_match_detail():
    """测试MatchDetail数据类"""
    print("测试 MatchDetail...")
    
    # 创建实例
    match_detail = MatchDetail(
        original_text="霍尼韦尔 温度传感器 T7350A1008",
        preprocessing={
            "original": "霍尼韦尔 温度传感器 T7350A1008",
            "cleaned": "霍尼韦尔 温度传感器 T7350A1008",
            "normalized": "霍尼韦尔温度传感器t7350a1008",
            "features": ["霍尼韦尔", "温度传感器", "t7350a1008"]
        },
        candidates=[
            CandidateDetail(
                rule_id="rule_001",
                target_device_id="device_001",
                device_info={"brand": "霍尼韦尔", "device_name": "温度传感器"},
                weight_score=8.5,
                match_threshold=5.0,
                threshold_type="rule",
                is_qualified=True,
                matched_features=[],
                unmatched_features=[],
                score_breakdown={},
                total_possible_score=10.0
            )
        ],
        final_result={
            "device_id": "device_001",
            "matched_device_text": "霍尼韦尔 温度传感器 T7350A1008",
            "unit_price": 1200.00,
            "match_status": "success",
            "match_score": 8.5,
            "match_reason": "匹配成功"
        },
        selected_candidate_id="rule_001",
        decision_reason="得分最高且超过阈值",
        optimization_suggestions=["配置良好，无需优化"],
        match_duration_ms=15.5
    )
    
    # 测试to_dict
    detail_dict = match_detail.to_dict()
    print(f"  to_dict keys: {list(detail_dict.keys())}")
    assert detail_dict['original_text'] == "霍尼韦尔 温度传感器 T7350A1008"
    assert len(detail_dict['candidates']) == 1
    assert detail_dict['final_result']['match_status'] == "success"
    assert detail_dict['decision_reason'] == "得分最高且超过阈值"
    assert 'timestamp' in detail_dict
    
    # 测试from_dict
    match_detail2 = MatchDetail.from_dict(detail_dict)
    print(f"  from_dict: original_text={match_detail2.original_text[:20]}...")
    assert match_detail2.original_text == match_detail.original_text
    assert len(match_detail2.candidates) == 1
    assert match_detail2.final_result['match_status'] == "success"
    
    print("  ✓ MatchDetail 测试通过\n")


def test_empty_lists():
    """测试空列表的默认值"""
    print("测试空列表默认值...")
    
    # CandidateDetail with empty lists
    candidate = CandidateDetail(
        rule_id="rule_001",
        target_device_id="device_001",
        device_info={},
        weight_score=0.0,
        match_threshold=5.0,
        threshold_type="default",
        is_qualified=False
    )
    
    assert candidate.matched_features == []
    assert candidate.unmatched_features == []
    assert candidate.score_breakdown == {}
    
    # MatchDetail with empty lists
    match_detail = MatchDetail(
        original_text="test",
        preprocessing={},
        candidates=[],
        final_result={},
        selected_candidate_id=None,
        decision_reason="test"
    )
    
    assert match_detail.optimization_suggestions == []
    assert match_detail.timestamp is not None
    
    print("  ✓ 空列表默认值测试通过\n")


if __name__ == "__main__":
    print("=" * 60)
    print("匹配详情数据类测试")
    print("=" * 60 + "\n")
    
    try:
        test_feature_match()
        test_candidate_detail()
        test_match_detail()
        test_empty_lists()
        
        print("=" * 60)
        print("✓ 所有测试通过!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
