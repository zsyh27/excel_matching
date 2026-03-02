"""
测试MatchDetailRecorder类的功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.match_detail import MatchDetailRecorder, CandidateDetail, FeatureMatch


def test_basic_record_and_retrieve():
    """测试基本的记录和检索功能"""
    print("测试基本记录和检索...")
    
    # 创建记录器
    recorder = MatchDetailRecorder(config={})
    
    # 准备测试数据
    original_text = "霍尼韦尔 温度传感器 T7350A1008"
    preprocessing_result = {
        "original": original_text,
        "cleaned": "霍尼韦尔 温度传感器 T7350A1008",
        "normalized": "霍尼韦尔温度传感器t7350a1008",
        "features": ["霍尼韦尔", "温度传感器", "t7350a1008"]
    }
    
    candidates = [
        CandidateDetail(
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
            unmatched_features=[],
            score_breakdown={"霍尼韦尔": 3.0, "温度传感器": 2.5},
            total_possible_score=10.0
        )
    ]
    
    final_result = {
        "device_id": "device_001",
        "matched_device_text": "霍尼韦尔 温度传感器 T7350A1008",
        "unit_price": 1200.00,
        "match_status": "success",
        "match_score": 8.5,
        "threshold": 5.0,
        "match_reason": "匹配成功"
    }
    
    # 记录匹配详情
    cache_key = recorder.record_match(
        original_text=original_text,
        preprocessing_result=preprocessing_result,
        candidates=candidates,
        final_result=final_result,
        selected_candidate_id="rule_001",
        match_duration_ms=15.5
    )
    
    print(f"  生成的缓存键: {cache_key}")
    assert cache_key is not None
    assert len(cache_key) == 36  # UUID格式
    
    # 检索匹配详情
    detail = recorder.get_detail(cache_key)
    assert detail is not None
    assert detail.original_text == original_text
    assert len(detail.candidates) == 1
    assert detail.final_result['match_status'] == "success"
    assert detail.selected_candidate_id == "rule_001"
    assert detail.match_duration_ms == 15.5
    
    print("  ✓ 基本记录和检索测试通过\n")


def test_cache_key_uniqueness():
    """测试缓存键的唯一性"""
    print("测试缓存键唯一性...")
    
    recorder = MatchDetailRecorder(config={})
    
    # 记录多次相同的匹配
    keys = []
    for i in range(10):
        cache_key = recorder.record_match(
            original_text=f"测试文本 {i}",
            preprocessing_result={"features": []},
            candidates=[],
            final_result={"match_status": "failed"},
            selected_candidate_id=None
        )
        keys.append(cache_key)
    
    # 验证所有键都是唯一的
    assert len(keys) == len(set(keys))
    print(f"  生成了 {len(keys)} 个唯一的缓存键")
    print("  ✓ 缓存键唯一性测试通过\n")


def test_nonexistent_cache_key():
    """测试获取不存在的缓存键"""
    print("测试不存在的缓存键...")
    
    recorder = MatchDetailRecorder(config={})
    
    # 尝试获取不存在的键
    detail = recorder.get_detail("nonexistent-key-12345")
    assert detail is None
    
    print("  ✓ 不存在的缓存键测试通过\n")


def test_decision_reason_success():
    """测试成功匹配的决策原因生成"""
    print("测试成功匹配的决策原因...")
    
    recorder = MatchDetailRecorder(config={})
    
    candidates = [
        CandidateDetail(
            rule_id="rule_001",
            target_device_id="device_001",
            device_info={"brand": "霍尼韦尔"},
            weight_score=8.5,
            match_threshold=5.0,
            threshold_type="rule",
            is_qualified=True
        )
    ]
    
    final_result = {
        "match_status": "success",
        "match_score": 8.5,
        "threshold": 5.0,
        "matched_device_text": "霍尼韦尔 温度传感器"
    }
    
    cache_key = recorder.record_match(
        original_text="test",
        preprocessing_result={"features": ["霍尼韦尔"]},
        candidates=candidates,
        final_result=final_result,
        selected_candidate_id="rule_001"
    )
    
    detail = recorder.get_detail(cache_key)
    print(f"  决策原因: {detail.decision_reason}")
    assert "匹配成功" in detail.decision_reason
    assert "8.5" in detail.decision_reason or "8.50" in detail.decision_reason
    
    print("  ✓ 成功匹配决策原因测试通过\n")


def test_decision_reason_no_candidates():
    """测试无候选规则的决策原因生成"""
    print("测试无候选规则的决策原因...")
    
    recorder = MatchDetailRecorder(config={})
    
    final_result = {
        "match_status": "failed",
        "match_score": 0,
        "match_reason": "无候选规则"
    }
    
    cache_key = recorder.record_match(
        original_text="test",
        preprocessing_result={"features": []},
        candidates=[],
        final_result=final_result,
        selected_candidate_id=None
    )
    
    detail = recorder.get_detail(cache_key)
    print(f"  决策原因: {detail.decision_reason}")
    assert "未找到任何候选规则" in detail.decision_reason
    
    print("  ✓ 无候选规则决策原因测试通过\n")


def test_decision_reason_score_insufficient():
    """测试得分不足的决策原因生成"""
    print("测试得分不足的决策原因...")
    
    recorder = MatchDetailRecorder(config={})
    
    candidates = [
        CandidateDetail(
            rule_id="rule_001",
            target_device_id="device_001",
            device_info={"brand": "霍尼韦尔"},
            weight_score=4.5,
            match_threshold=5.0,
            threshold_type="rule",
            is_qualified=False
        )
    ]
    
    final_result = {
        "match_status": "failed",
        "match_score": 4.5,
        "match_reason": "得分不足"
    }
    
    cache_key = recorder.record_match(
        original_text="test",
        preprocessing_result={"features": ["霍尼韦尔"]},
        candidates=candidates,
        final_result=final_result,
        selected_candidate_id=None
    )
    
    detail = recorder.get_detail(cache_key)
    print(f"  决策原因: {detail.decision_reason}")
    assert "匹配失败" in detail.decision_reason
    assert "4.5" in detail.decision_reason or "4.50" in detail.decision_reason
    assert "差距" in detail.decision_reason
    
    print("  ✓ 得分不足决策原因测试通过\n")


def test_suggestions_no_features():
    """测试无特征提取的优化建议"""
    print("测试无特征提取的优化建议...")
    
    recorder = MatchDetailRecorder(config={})
    
    final_result = {"match_status": "failed"}
    preprocessing_result = {"features": []}
    
    cache_key = recorder.record_match(
        original_text="test",
        preprocessing_result=preprocessing_result,
        candidates=[],
        final_result=final_result,
        selected_candidate_id=None
    )
    
    detail = recorder.get_detail(cache_key)
    print(f"  优化建议: {detail.optimization_suggestions}")
    assert len(detail.optimization_suggestions) > 0
    assert any("特征" in s for s in detail.optimization_suggestions)
    
    print("  ✓ 无特征提取优化建议测试通过\n")


def test_suggestions_no_candidates():
    """测试无候选规则的优化建议"""
    print("测试无候选规则的优化建议...")
    
    recorder = MatchDetailRecorder(config={})
    
    final_result = {"match_status": "failed"}
    preprocessing_result = {"features": ["霍尼韦尔", "温度传感器"]}
    
    cache_key = recorder.record_match(
        original_text="test",
        preprocessing_result=preprocessing_result,
        candidates=[],
        final_result=final_result,
        selected_candidate_id=None
    )
    
    detail = recorder.get_detail(cache_key)
    print(f"  优化建议: {detail.optimization_suggestions}")
    assert len(detail.optimization_suggestions) > 0
    assert any("候选规则" in s or "规则库" in s for s in detail.optimization_suggestions)
    
    print("  ✓ 无候选规则优化建议测试通过\n")


def test_suggestions_close_to_threshold():
    """测试得分接近阈值的优化建议"""
    print("测试得分接近阈值的优化建议...")
    
    recorder = MatchDetailRecorder(config={})
    
    candidates = [
        CandidateDetail(
            rule_id="rule_001",
            target_device_id="device_001",
            device_info={"brand": "霍尼韦尔"},
            weight_score=4.5,
            match_threshold=5.0,
            threshold_type="rule",
            is_qualified=False,
            unmatched_features=[]
        )
    ]
    
    final_result = {"match_status": "failed", "match_score": 4.5}
    preprocessing_result = {"features": ["霍尼韦尔"]}
    
    cache_key = recorder.record_match(
        original_text="test",
        preprocessing_result=preprocessing_result,
        candidates=candidates,
        final_result=final_result,
        selected_candidate_id=None
    )
    
    detail = recorder.get_detail(cache_key)
    print(f"  优化建议: {detail.optimization_suggestions}")
    assert len(detail.optimization_suggestions) > 0
    assert any("阈值" in s for s in detail.optimization_suggestions)
    
    print("  ✓ 得分接近阈值优化建议测试通过\n")


def test_suggestions_success():
    """测试成功匹配的优化建议"""
    print("测试成功匹配的优化建议...")
    
    recorder = MatchDetailRecorder(config={})
    
    candidates = [
        CandidateDetail(
            rule_id="rule_001",
            target_device_id="device_001",
            device_info={"brand": "霍尼韦尔"},
            weight_score=8.5,
            match_threshold=5.0,
            threshold_type="rule",
            is_qualified=True
        )
    ]
    
    final_result = {"match_status": "success", "match_score": 8.5}
    preprocessing_result = {"features": ["霍尼韦尔"]}
    
    cache_key = recorder.record_match(
        original_text="test",
        preprocessing_result=preprocessing_result,
        candidates=candidates,
        final_result=final_result,
        selected_candidate_id="rule_001"
    )
    
    detail = recorder.get_detail(cache_key)
    print(f"  优化建议: {detail.optimization_suggestions}")
    assert len(detail.optimization_suggestions) > 0
    
    print("  ✓ 成功匹配优化建议测试通过\n")


def test_cache_size_limit():
    """测试缓存大小限制"""
    print("测试缓存大小限制...")
    
    recorder = MatchDetailRecorder(config={})
    recorder.max_cache_size = 10  # 设置较小的限制便于测试
    
    # 添加超过限制的记录
    keys = []
    for i in range(15):
        cache_key = recorder.record_match(
            original_text=f"测试文本 {i}",
            preprocessing_result={"features": []},
            candidates=[],
            final_result={"match_status": "failed"},
            selected_candidate_id=None
        )
        keys.append(cache_key)
    
    # 验证缓存大小被限制
    print(f"  缓存大小: {len(recorder.cache)} (限制: {recorder.max_cache_size})")
    assert len(recorder.cache) <= recorder.max_cache_size
    
    # 验证最新的记录仍然存在
    latest_key = keys[-1]
    assert recorder.get_detail(latest_key) is not None
    
    print("  ✓ 缓存大小限制测试通过\n")


def test_match_detail_completeness():
    """测试MatchDetail的完整性"""
    print("测试MatchDetail完整性...")
    
    recorder = MatchDetailRecorder(config={})
    
    cache_key = recorder.record_match(
        original_text="test",
        preprocessing_result={"features": ["test"]},
        candidates=[],
        final_result={"match_status": "failed"},
        selected_candidate_id=None,
        match_duration_ms=25.5
    )
    
    detail = recorder.get_detail(cache_key)
    
    # 验证所有必需字段都存在
    assert detail.original_text is not None
    assert detail.preprocessing is not None
    assert detail.candidates is not None
    assert detail.final_result is not None
    assert detail.decision_reason is not None
    assert detail.optimization_suggestions is not None
    assert detail.timestamp is not None
    assert detail.match_duration_ms == 25.5
    
    print("  ✓ MatchDetail完整性测试通过\n")


def test_suggestions_unmatched_features():
    """测试有未匹配特征的优化建议"""
    print("测试有未匹配特征的优化建议...")
    
    recorder = MatchDetailRecorder(config={})
    
    candidates = [
        CandidateDetail(
            rule_id="rule_001",
            target_device_id="device_001",
            device_info={"brand": "霍尼韦尔"},
            weight_score=4.0,
            match_threshold=5.0,
            threshold_type="rule",
            is_qualified=False,
            unmatched_features=["型号", "参数1", "参数2"]
        )
    ]
    
    final_result = {"match_status": "failed", "match_score": 4.0}
    preprocessing_result = {"features": ["霍尼韦尔"]}
    
    cache_key = recorder.record_match(
        original_text="test",
        preprocessing_result=preprocessing_result,
        candidates=candidates,
        final_result=final_result,
        selected_candidate_id=None
    )
    
    detail = recorder.get_detail(cache_key)
    print(f"  优化建议: {detail.optimization_suggestions}")
    assert len(detail.optimization_suggestions) > 0
    # 应该包含关于未匹配特征的建议
    assert any("未匹配" in s or "特征" in s for s in detail.optimization_suggestions)
    
    print("  ✓ 有未匹配特征优化建议测试通过\n")


def test_suggestions_low_average_score():
    """测试候选规则得分普遍较低的优化建议"""
    print("测试候选规则得分普遍较低的优化建议...")
    
    recorder = MatchDetailRecorder(config={})
    
    # 创建3个得分都很低的候选
    candidates = [
        CandidateDetail(
            rule_id=f"rule_{i:03d}",
            target_device_id=f"device_{i:03d}",
            device_info={"brand": "品牌"},
            weight_score=2.0 + i * 0.1,
            match_threshold=8.0,
            threshold_type="rule",
            is_qualified=False,
            unmatched_features=[]
        )
        for i in range(3)
    ]
    
    final_result = {"match_status": "failed", "match_score": 2.2}
    preprocessing_result = {"features": ["品牌"]}
    
    cache_key = recorder.record_match(
        original_text="test",
        preprocessing_result=preprocessing_result,
        candidates=candidates,
        final_result=final_result,
        selected_candidate_id=None
    )
    
    detail = recorder.get_detail(cache_key)
    print(f"  优化建议: {detail.optimization_suggestions}")
    assert len(detail.optimization_suggestions) > 0
    # 应该包含关于得分普遍较低的建议
    assert any("普遍较低" in s or "权重配置" in s for s in detail.optimization_suggestions)
    
    print("  ✓ 候选规则得分普遍较低优化建议测试通过\n")


def test_suggestions_close_scores():
    """测试最高分和第二高分接近的优化建议"""
    print("测试最高分和第二高分接近的优化建议...")
    
    recorder = MatchDetailRecorder(config={})
    
    candidates = [
        CandidateDetail(
            rule_id="rule_001",
            target_device_id="device_001",
            device_info={"brand": "霍尼韦尔"},
            weight_score=8.5,
            match_threshold=5.0,
            threshold_type="rule",
            is_qualified=True
        ),
        CandidateDetail(
            rule_id="rule_002",
            target_device_id="device_002",
            device_info={"brand": "西门子"},
            weight_score=8.2,  # 与第一名差距很小
            match_threshold=5.0,
            threshold_type="rule",
            is_qualified=True
        )
    ]
    
    final_result = {"match_status": "success", "match_score": 8.5}
    preprocessing_result = {"features": ["霍尼韦尔"]}
    
    cache_key = recorder.record_match(
        original_text="test",
        preprocessing_result=preprocessing_result,
        candidates=candidates,
        final_result=final_result,
        selected_candidate_id="rule_001"
    )
    
    detail = recorder.get_detail(cache_key)
    print(f"  优化建议: {detail.optimization_suggestions}")
    assert len(detail.optimization_suggestions) > 0
    # 应该包含关于得分差距小的建议
    assert any("差距较小" in s or "区分度" in s for s in detail.optimization_suggestions)
    
    print("  ✓ 最高分和第二高分接近优化建议测试通过\n")


def test_suggestions_all_scenarios():
    """测试综合场景的优化建议"""
    print("测试综合场景的优化建议...")
    
    recorder = MatchDetailRecorder(config={})
    
    # 场景：得分接近阈值 + 有未匹配特征
    candidates = [
        CandidateDetail(
            rule_id="rule_001",
            target_device_id="device_001",
            device_info={"brand": "霍尼韦尔"},
            weight_score=4.8,
            match_threshold=5.0,
            threshold_type="rule",
            is_qualified=False,
            unmatched_features=["型号", "参数"]
        )
    ]
    
    final_result = {"match_status": "failed", "match_score": 4.8}
    preprocessing_result = {"features": ["霍尼韦尔", "温度传感器"]}
    
    cache_key = recorder.record_match(
        original_text="test",
        preprocessing_result=preprocessing_result,
        candidates=candidates,
        final_result=final_result,
        selected_candidate_id=None
    )
    
    detail = recorder.get_detail(cache_key)
    print(f"  优化建议数量: {len(detail.optimization_suggestions)}")
    print(f"  优化建议: {detail.optimization_suggestions}")
    
    # 应该包含多个建议
    assert len(detail.optimization_suggestions) >= 2
    # 应该包含阈值建议
    assert any("阈值" in s for s in detail.optimization_suggestions)
    # 应该包含未匹配特征建议
    assert any("未匹配" in s for s in detail.optimization_suggestions)
    
    print("  ✓ 综合场景优化建议测试通过\n")


if __name__ == "__main__":
    print("=" * 60)
    print("MatchDetailRecorder 测试")
    print("=" * 60 + "\n")
    
    try:
        test_basic_record_and_retrieve()
        test_cache_key_uniqueness()
        test_nonexistent_cache_key()
        test_decision_reason_success()
        test_decision_reason_no_candidates()
        test_decision_reason_score_insufficient()
        test_suggestions_no_features()
        test_suggestions_no_candidates()
        test_suggestions_close_to_threshold()
        test_suggestions_success()
        test_cache_size_limit()
        test_match_detail_completeness()
        test_suggestions_unmatched_features()
        test_suggestions_low_average_score()
        test_suggestions_close_scores()
        test_suggestions_all_scenarios()
        
        print("=" * 60)
        print("✓ 所有测试通过!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
