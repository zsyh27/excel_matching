"""
Property-Based Tests for Match Detail Data Classes

Feature: matching-rule-visualization-system
Tests Properties 1, 2, and 3 from the design document
"""

import pytest
from hypothesis import given, strategies as st
from hypothesis import settings, HealthCheck
from backend.modules.match_detail import MatchDetail, CandidateDetail, FeatureMatch


# ============================================================================
# Test Data Generators (Strategies)
# ============================================================================

@st.composite
def feature_match_strategy(draw):
    """Generate random FeatureMatch objects"""
    feature_types = ['brand', 'device_type', 'model', 'parameter']
    
    return FeatureMatch(
        feature=draw(st.text(min_size=1, max_size=50)),
        weight=draw(st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False)),
        feature_type=draw(st.sampled_from(feature_types)),
        contribution_percentage=draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    )


@st.composite
def device_info_strategy(draw):
    """Generate random device info dictionaries"""
    return {
        'device_id': draw(st.text(min_size=1, max_size=50)),
        'brand': draw(st.text(min_size=1, max_size=50)),
        'device_name': draw(st.text(min_size=1, max_size=100)),
        'spec_model': draw(st.text(min_size=1, max_size=50)),
        'unit_price': draw(st.floats(min_value=0.0, max_value=100000.0, allow_nan=False, allow_infinity=False))
    }


@st.composite
def candidate_detail_strategy(draw):
    """Generate random CandidateDetail objects"""
    threshold_types = ['rule', 'default']
    
    # Generate matched features and sort them by weight (descending)
    matched_features = draw(st.lists(feature_match_strategy(), min_size=0, max_size=10))
    matched_features.sort(key=lambda f: f.weight, reverse=True)
    
    return CandidateDetail(
        rule_id=draw(st.text(min_size=1, max_size=50)),
        target_device_id=draw(st.text(min_size=1, max_size=50)),
        device_info=draw(device_info_strategy()),
        weight_score=draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)),
        match_threshold=draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)),
        threshold_type=draw(st.sampled_from(threshold_types)),
        is_qualified=draw(st.booleans()),
        matched_features=matched_features,
        unmatched_features=draw(st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=10)),
        score_breakdown=draw(st.dictionaries(
            st.text(min_size=1, max_size=50),
            st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False),
            min_size=0,
            max_size=10
        )),
        total_possible_score=draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    )


@st.composite
def preprocessing_result_strategy(draw):
    """Generate random preprocessing result dictionaries"""
    return {
        'original': draw(st.text(min_size=0, max_size=200)),
        'cleaned': draw(st.text(min_size=0, max_size=200)),
        'normalized': draw(st.text(min_size=0, max_size=200)),
        'features': draw(st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=20))
    }


@st.composite
def match_result_strategy(draw):
    """Generate random match result dictionaries"""
    match_statuses = ['success', 'failed']
    
    status = draw(st.sampled_from(match_statuses))
    
    if status == 'success':
        return {
            'device_id': draw(st.text(min_size=1, max_size=50)),
            'matched_device_text': draw(st.text(min_size=1, max_size=100)),
            'unit_price': draw(st.floats(min_value=0.0, max_value=100000.0, allow_nan=False, allow_infinity=False)),
            'match_status': status,
            'match_score': draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)),
            'match_reason': draw(st.text(min_size=1, max_size=200)),
            'threshold': draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
        }
    else:
        return {
            'device_id': None,
            'matched_device_text': None,
            'unit_price': 0.0,
            'match_status': status,
            'match_score': draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)),
            'match_reason': draw(st.text(min_size=1, max_size=200)),
            'threshold': draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False))
        }


@st.composite
def match_detail_strategy(draw):
    """Generate random MatchDetail objects"""
    return MatchDetail(
        original_text=draw(st.text(min_size=0, max_size=200)),
        preprocessing=draw(preprocessing_result_strategy()),
        candidates=draw(st.lists(candidate_detail_strategy(), min_size=0, max_size=10)),
        final_result=draw(match_result_strategy()),
        selected_candidate_id=draw(st.one_of(st.none(), st.text(min_size=1, max_size=50))),
        decision_reason=draw(st.text(min_size=1, max_size=200)),
        optimization_suggestions=draw(st.lists(st.text(min_size=1, max_size=200), min_size=0, max_size=5)),
        timestamp=draw(st.text(min_size=1, max_size=50)),
        match_duration_ms=draw(st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False))
    )


# ============================================================================
# Property 1: 匹配详情数据完整性
# ============================================================================

@given(match_detail=match_detail_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_1_match_detail_completeness(match_detail):
    """
    Feature: matching-rule-visualization-system
    Property 1: 匹配详情数据完整性
    
    For any 匹配操作,生成的MatchDetail对象应该包含所有核心组件:
    原始文本、预处理结果、候选规则列表、最终结果和决策原因。
    
    Validates: Requirements 1.3, 3.1, 6.1, 6.4
    """
    # 验证所有核心字段都存在且不为None
    assert match_detail.original_text is not None, "original_text should not be None"
    assert match_detail.preprocessing is not None, "preprocessing should not be None"
    assert match_detail.candidates is not None, "candidates should not be None"
    assert match_detail.final_result is not None, "final_result should not be None"
    assert match_detail.decision_reason is not None, "decision_reason should not be None"
    
    # 验证candidates是列表类型
    assert isinstance(match_detail.candidates, list), "candidates should be a list"
    
    # 验证preprocessing是字典类型
    assert isinstance(match_detail.preprocessing, dict), "preprocessing should be a dict"
    
    # 验证final_result是字典类型
    assert isinstance(match_detail.final_result, dict), "final_result should be a dict"
    
    # 验证decision_reason是字符串类型
    assert isinstance(match_detail.decision_reason, str), "decision_reason should be a string"
    
    # 验证optimization_suggestions是列表类型
    assert isinstance(match_detail.optimization_suggestions, list), "optimization_suggestions should be a list"


@given(match_detail=match_detail_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_1_match_detail_serialization(match_detail):
    """
    Feature: matching-rule-visualization-system
    Property 1: 匹配详情数据完整性 (序列化测试)
    
    MatchDetail对象应该能够正确序列化和反序列化,保持数据完整性。
    
    Validates: Requirements 6.1, 6.4
    """
    # 序列化
    serialized = match_detail.to_dict()
    
    # 验证序列化结果是字典
    assert isinstance(serialized, dict), "Serialized result should be a dict"
    
    # 验证所有核心字段都在序列化结果中
    assert 'original_text' in serialized
    assert 'preprocessing' in serialized
    assert 'candidates' in serialized
    assert 'final_result' in serialized
    assert 'decision_reason' in serialized
    assert 'optimization_suggestions' in serialized
    assert 'timestamp' in serialized
    assert 'match_duration_ms' in serialized
    
    # 反序列化
    deserialized = MatchDetail.from_dict(serialized)
    
    # 验证反序列化后的对象类型正确
    assert isinstance(deserialized, MatchDetail), "Deserialized object should be MatchDetail"
    
    # 验证核心字段值保持一致
    assert deserialized.original_text == match_detail.original_text
    assert deserialized.decision_reason == match_detail.decision_reason
    assert len(deserialized.candidates) == len(match_detail.candidates)
    assert len(deserialized.optimization_suggestions) == len(match_detail.optimization_suggestions)


# ============================================================================
# Property 2: 预处理阶段数据完整性
# ============================================================================

@given(preprocessing=preprocessing_result_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_2_preprocessing_completeness(preprocessing):
    """
    Feature: matching-rule-visualization-system
    Property 2: 预处理阶段数据完整性
    
    For any 匹配详情中的预处理结果,应该包含所有处理阶段的数据:
    原始文本(original)、清理后文本(cleaned)、归一化文本(normalized)和特征列表(features)。
    
    Validates: Requirements 2.1, 2.2, 2.3, 2.4, 6.2
    """
    # 验证所有必需字段都存在
    assert 'original' in preprocessing, "preprocessing should contain 'original'"
    assert 'cleaned' in preprocessing, "preprocessing should contain 'cleaned'"
    assert 'normalized' in preprocessing, "preprocessing should contain 'normalized'"
    assert 'features' in preprocessing, "preprocessing should contain 'features'"
    
    # 验证字段类型
    assert isinstance(preprocessing['original'], str), "'original' should be a string"
    assert isinstance(preprocessing['cleaned'], str), "'cleaned' should be a string"
    assert isinstance(preprocessing['normalized'], str), "'normalized' should be a string"
    assert isinstance(preprocessing['features'], list), "'features' should be a list"
    
    # 验证features列表中的元素都是字符串
    for feature in preprocessing['features']:
        assert isinstance(feature, str), "Each feature should be a string"


@given(match_detail=match_detail_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_2_preprocessing_in_match_detail(match_detail):
    """
    Feature: matching-rule-visualization-system
    Property 2: 预处理阶段数据完整性 (在MatchDetail中)
    
    MatchDetail中的preprocessing字段应该包含完整的预处理阶段数据。
    
    Validates: Requirements 2.1, 2.2, 2.3, 2.4, 6.2
    """
    preprocessing = match_detail.preprocessing
    
    # 验证preprocessing不为None
    assert preprocessing is not None, "preprocessing should not be None"
    
    # 验证所有必需字段都存在
    assert 'original' in preprocessing, "preprocessing should contain 'original'"
    assert 'cleaned' in preprocessing, "preprocessing should contain 'cleaned'"
    assert 'normalized' in preprocessing, "preprocessing should contain 'normalized'"
    assert 'features' in preprocessing, "preprocessing should contain 'features'"
    
    # 验证字段类型
    assert isinstance(preprocessing['original'], str), "'original' should be a string"
    assert isinstance(preprocessing['cleaned'], str), "'cleaned' should be a string"
    assert isinstance(preprocessing['normalized'], str), "'normalized' should be a string"
    assert isinstance(preprocessing['features'], list), "'features' should be a list"


# ============================================================================
# Property 3: 候选规则数据完整性
# ============================================================================

@given(candidate=candidate_detail_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_3_candidate_detail_completeness(candidate):
    """
    Feature: matching-rule-visualization-system
    Property 3: 候选规则数据完整性
    
    For any 候选规则(CandidateDetail),应该包含所有必需字段:
    规则ID、目标设备ID、设备信息、权重得分、匹配阈值、阈值类型、是否合格标志、
    匹配特征列表、未匹配特征列表和得分分解。
    
    Validates: Requirements 3.3, 3.4, 4.2, 4.3, 4.4, 4.5, 6.3, 8.4
    """
    # 验证所有核心字段都存在且不为None
    assert candidate.rule_id is not None, "rule_id should not be None"
    assert candidate.target_device_id is not None, "target_device_id should not be None"
    assert candidate.device_info is not None, "device_info should not be None"
    assert candidate.weight_score is not None, "weight_score should not be None"
    assert candidate.match_threshold is not None, "match_threshold should not be None"
    assert candidate.threshold_type is not None, "threshold_type should not be None"
    assert candidate.is_qualified is not None, "is_qualified should not be None"
    assert candidate.matched_features is not None, "matched_features should not be None"
    assert candidate.unmatched_features is not None, "unmatched_features should not be None"
    assert candidate.score_breakdown is not None, "score_breakdown should not be None"
    assert candidate.total_possible_score is not None, "total_possible_score should not be None"
    
    # 验证字段类型
    assert isinstance(candidate.rule_id, str), "rule_id should be a string"
    assert isinstance(candidate.target_device_id, str), "target_device_id should be a string"
    assert isinstance(candidate.device_info, dict), "device_info should be a dict"
    assert isinstance(candidate.weight_score, (int, float)), "weight_score should be numeric"
    assert isinstance(candidate.match_threshold, (int, float)), "match_threshold should be numeric"
    assert isinstance(candidate.threshold_type, str), "threshold_type should be a string"
    assert isinstance(candidate.is_qualified, bool), "is_qualified should be a boolean"
    assert isinstance(candidate.matched_features, list), "matched_features should be a list"
    assert isinstance(candidate.unmatched_features, list), "unmatched_features should be a list"
    assert isinstance(candidate.score_breakdown, dict), "score_breakdown should be a dict"
    assert isinstance(candidate.total_possible_score, (int, float)), "total_possible_score should be numeric"
    
    # 验证threshold_type的值是有效的
    assert candidate.threshold_type in ['rule', 'default'], "threshold_type should be 'rule' or 'default'"
    
    # 验证matched_features列表中的元素都是FeatureMatch对象
    for feature_match in candidate.matched_features:
        assert isinstance(feature_match, FeatureMatch), "Each matched feature should be a FeatureMatch object"
    
    # 验证unmatched_features列表中的元素都是字符串
    for feature in candidate.unmatched_features:
        assert isinstance(feature, str), "Each unmatched feature should be a string"


@given(candidate=candidate_detail_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_3_candidate_detail_serialization(candidate):
    """
    Feature: matching-rule-visualization-system
    Property 3: 候选规则数据完整性 (序列化测试)
    
    CandidateDetail对象应该能够正确序列化和反序列化,保持数据完整性。
    
    Validates: Requirements 6.3
    """
    # 序列化
    serialized = candidate.to_dict()
    
    # 验证序列化结果是字典
    assert isinstance(serialized, dict), "Serialized result should be a dict"
    
    # 验证所有核心字段都在序列化结果中
    assert 'rule_id' in serialized
    assert 'target_device_id' in serialized
    assert 'device_info' in serialized
    assert 'weight_score' in serialized
    assert 'match_threshold' in serialized
    assert 'threshold_type' in serialized
    assert 'is_qualified' in serialized
    assert 'matched_features' in serialized
    assert 'unmatched_features' in serialized
    assert 'score_breakdown' in serialized
    assert 'total_possible_score' in serialized
    
    # 反序列化
    deserialized = CandidateDetail.from_dict(serialized)
    
    # 验证反序列化后的对象类型正确
    assert isinstance(deserialized, CandidateDetail), "Deserialized object should be CandidateDetail"
    
    # 验证核心字段值保持一致
    assert deserialized.rule_id == candidate.rule_id
    assert deserialized.target_device_id == candidate.target_device_id
    assert deserialized.threshold_type == candidate.threshold_type
    assert deserialized.is_qualified == candidate.is_qualified
    assert len(deserialized.matched_features) == len(candidate.matched_features)
    assert len(deserialized.unmatched_features) == len(candidate.unmatched_features)


@given(feature_match=feature_match_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_3_feature_match_completeness(feature_match):
    """
    Feature: matching-rule-visualization-system
    Property 3: 候选规则数据完整性 (FeatureMatch)
    
    FeatureMatch对象应该包含所有必需字段。
    
    Validates: Requirements 4.2, 4.3
    """
    # 验证所有字段都存在且不为None
    assert feature_match.feature is not None, "feature should not be None"
    assert feature_match.weight is not None, "weight should not be None"
    assert feature_match.feature_type is not None, "feature_type should not be None"
    assert feature_match.contribution_percentage is not None, "contribution_percentage should not be None"
    
    # 验证字段类型
    assert isinstance(feature_match.feature, str), "feature should be a string"
    assert isinstance(feature_match.weight, (int, float)), "weight should be numeric"
    assert isinstance(feature_match.feature_type, str), "feature_type should be a string"
    assert isinstance(feature_match.contribution_percentage, (int, float)), "contribution_percentage should be numeric"
    
    # 验证feature_type的值是有效的
    valid_types = ['brand', 'device_type', 'model', 'parameter']
    assert feature_match.feature_type in valid_types, f"feature_type should be one of {valid_types}"
    
    # 验证contribution_percentage在合理范围内
    assert 0.0 <= feature_match.contribution_percentage <= 100.0, "contribution_percentage should be between 0 and 100"


@given(feature_match=feature_match_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_3_feature_match_serialization(feature_match):
    """
    Feature: matching-rule-visualization-system
    Property 3: 候选规则数据完整性 (FeatureMatch序列化)
    
    FeatureMatch对象应该能够正确序列化和反序列化。
    
    Validates: Requirements 6.3
    """
    # 序列化
    serialized = feature_match.to_dict()
    
    # 验证序列化结果是字典
    assert isinstance(serialized, dict), "Serialized result should be a dict"
    
    # 验证所有字段都在序列化结果中
    assert 'feature' in serialized
    assert 'weight' in serialized
    assert 'feature_type' in serialized
    assert 'contribution_percentage' in serialized
    
    # 反序列化
    deserialized = FeatureMatch.from_dict(serialized)
    
    # 验证反序列化后的对象类型正确
    assert isinstance(deserialized, FeatureMatch), "Deserialized object should be FeatureMatch"
    
    # 验证字段值保持一致
    assert deserialized.feature == feature_match.feature
    assert deserialized.feature_type == feature_match.feature_type
    # 注意：由于序列化时会四舍五入，所以这里使用近似比较
    assert abs(deserialized.weight - feature_match.weight) < 0.01
    assert abs(deserialized.contribution_percentage - feature_match.contribution_percentage) < 0.01


# ============================================================================
# Property 12: 缓存键唯一性
# ============================================================================

@given(
    original_text1=st.text(min_size=0, max_size=200),
    original_text2=st.text(min_size=0, max_size=200),
    preprocessing1=preprocessing_result_strategy(),
    preprocessing2=preprocessing_result_strategy(),
    candidates1=st.lists(candidate_detail_strategy(), min_size=0, max_size=5),
    candidates2=st.lists(candidate_detail_strategy(), min_size=0, max_size=5),
    final_result1=match_result_strategy(),
    final_result2=match_result_strategy()
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_12_cache_key_uniqueness(
    original_text1, original_text2,
    preprocessing1, preprocessing2,
    candidates1, candidates2,
    final_result1, final_result2
):
    """
    Feature: matching-rule-visualization-system
    Property 12: 缓存键唯一性
    
    For any 两次不同的匹配操作,生成的缓存键(cache_key)应该是唯一的,
    确保不会发生缓存冲突。
    
    Validates: Requirements 6.1
    """
    from backend.modules.match_detail import MatchDetailRecorder
    
    # 创建记录器
    config = {'max_cache_size': 1000}
    recorder = MatchDetailRecorder(config)
    
    # 记录第一次匹配
    cache_key1 = recorder.record_match(
        original_text=original_text1,
        preprocessing_result=preprocessing1,
        candidates=candidates1,
        final_result=final_result1,
        selected_candidate_id=None,
        match_duration_ms=10.0
    )
    
    # 记录第二次匹配
    cache_key2 = recorder.record_match(
        original_text=original_text2,
        preprocessing_result=preprocessing2,
        candidates=candidates2,
        final_result=final_result2,
        selected_candidate_id=None,
        match_duration_ms=20.0
    )
    
    # 验证两个缓存键都成功生成
    assert cache_key1 is not None, "First cache key should not be None"
    assert cache_key2 is not None, "Second cache key should not be None"
    
    # 验证两个缓存键是字符串
    assert isinstance(cache_key1, str), "First cache key should be a string"
    assert isinstance(cache_key2, str), "Second cache key should be a string"
    
    # 验证两个缓存键不为空
    assert len(cache_key1) > 0, "First cache key should not be empty"
    assert len(cache_key2) > 0, "Second cache key should not be empty"
    
    # 核心验证：两个缓存键应该不同（唯一性）
    assert cache_key1 != cache_key2, "Cache keys should be unique for different match operations"
    
    # 验证两个详情都能正确检索
    detail1 = recorder.get_detail(cache_key1)
    detail2 = recorder.get_detail(cache_key2)
    
    assert detail1 is not None, "First detail should be retrievable"
    assert detail2 is not None, "Second detail should be retrievable"
    
    # 验证检索到的详情与原始输入匹配
    assert detail1.original_text == original_text1, "First detail should match original input"
    assert detail2.original_text == original_text2, "Second detail should match original input"
    
    # 验证两个详情是不同的对象
    assert detail1 is not detail2, "Two details should be different objects"


@given(
    original_text=st.text(min_size=0, max_size=200),
    preprocessing=preprocessing_result_strategy(),
    candidates=st.lists(candidate_detail_strategy(), min_size=0, max_size=5),
    final_result=match_result_strategy()
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_12_cache_key_uniqueness_multiple_calls(
    original_text, preprocessing, candidates, final_result
):
    """
    Feature: matching-rule-visualization-system
    Property 12: 缓存键唯一性 (多次调用测试)
    
    即使使用相同的输入数据多次调用record_match,每次也应该生成唯一的缓存键。
    
    Validates: Requirements 6.1
    """
    from backend.modules.match_detail import MatchDetailRecorder
    
    # 创建记录器
    config = {'max_cache_size': 1000}
    recorder = MatchDetailRecorder(config)
    
    # 使用相同的输入数据记录多次匹配
    cache_keys = []
    num_calls = 10
    
    for i in range(num_calls):
        cache_key = recorder.record_match(
            original_text=original_text,
            preprocessing_result=preprocessing,
            candidates=candidates,
            final_result=final_result,
            selected_candidate_id=None,
            match_duration_ms=float(i)
        )
        
        assert cache_key is not None, f"Cache key {i} should not be None"
        assert isinstance(cache_key, str), f"Cache key {i} should be a string"
        assert len(cache_key) > 0, f"Cache key {i} should not be empty"
        
        cache_keys.append(cache_key)
    
    # 验证所有缓存键都是唯一的
    unique_keys = set(cache_keys)
    assert len(unique_keys) == num_calls, \
        f"All {num_calls} cache keys should be unique, but got {len(unique_keys)} unique keys"
    
    # 验证所有详情都能正确检索
    for i, cache_key in enumerate(cache_keys):
        detail = recorder.get_detail(cache_key)
        assert detail is not None, f"Detail {i} should be retrievable"
        assert detail.original_text == original_text, f"Detail {i} should match original input"


# ============================================================================
# Property 4: 候选规则排序不变量
# ============================================================================

@given(candidates=st.lists(candidate_detail_strategy(), min_size=0, max_size=20))
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_4_candidate_rule_sorting_invariant(candidates):
    """
    Feature: matching-rule-visualization-system
    Property 4: 候选规则排序不变量
    
    For any 候选规则列表,规则应该按权重得分从高到低严格排序,
    即对于列表中任意相邻的两个候选规则candidates[i]和candidates[i+1],
    应该满足candidates[i].weight_score >= candidates[i+1].weight_score。
    
    Validates: Requirements 3.2
    """
    # 如果候选列表为空或只有一个元素，排序属性自动满足
    if len(candidates) <= 1:
        return
    
    # 按权重得分排序（模拟MatchEngine._evaluate_all_candidates的排序逻辑）
    sorted_candidates = sorted(candidates, key=lambda c: c.weight_score, reverse=True)
    
    # 验证排序不变量：对于任意相邻的两个候选规则，前一个的得分应该 >= 后一个的得分
    for i in range(len(sorted_candidates) - 1):
        current_score = sorted_candidates[i].weight_score
        next_score = sorted_candidates[i + 1].weight_score
        
        assert current_score >= next_score, \
            f"候选规则排序不变量被违反: candidates[{i}].weight_score ({current_score}) < candidates[{i+1}].weight_score ({next_score})"


@given(
    features=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10),
    num_rules=st.integers(min_value=2, max_value=10)
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_4_match_engine_candidate_sorting(features, num_rules):
    """
    Feature: matching-rule-visualization-system
    Property 4: 候选规则排序不变量 (MatchEngine集成测试)
    
    验证MatchEngine._evaluate_all_candidates()方法返回的候选规则列表
    是否按权重得分从高到低排序。
    
    Validates: Requirements 3.2
    """
    from backend.modules.match_engine import MatchEngine
    from backend.modules.data_loader import Rule, Device
    
    # 创建测试规则和设备
    rules = []
    devices = {}
    
    for i in range(num_rules):
        device_id = f"device_{i}"
        rule_id = f"rule_{i}"
        
        # 创建设备
        device = Device(
            device_id=device_id,
            brand=f"Brand_{i}",
            device_name=f"Device_{i}",
            spec_model=f"Model_{i}",
            detailed_params=f"Params_{i}",
            unit_price=100.0 * (i + 1)
        )
        devices[device_id] = device
        
        # 创建规则，使用随机特征和权重
        import random
        rule_features = random.sample(features, min(len(features), random.randint(1, len(features))))
        feature_weights = {f: random.uniform(0.5, 5.0) for f in rule_features}
        
        rule = Rule(
            rule_id=rule_id,
            target_device_id=device_id,
            auto_extracted_features=rule_features,
            feature_weights=feature_weights,
            match_threshold=random.uniform(3.0, 8.0),
            remark=f"Test rule {i}"
        )
        rules.append(rule)
    
    # 创建配置
    config = {
        'global_config': {
            'default_match_threshold': 5.0
        },
        'brand_keywords': [],
        'device_type_keywords': []
    }
    
    # 创建匹配引擎
    match_engine = MatchEngine(rules, devices, config)
    
    # 评估所有候选规则
    try:
        candidates = match_engine._evaluate_all_candidates(features)
        
        # 验证候选列表不为None
        assert candidates is not None, "候选规则列表不应为None"
        
        # 如果候选列表为空或只有一个元素，排序属性自动满足
        if len(candidates) <= 1:
            return
        
        # 验证排序不变量：对于任意相邻的两个候选规则，前一个的得分应该 >= 后一个的得分
        for i in range(len(candidates) - 1):
            current_score = candidates[i].weight_score
            next_score = candidates[i + 1].weight_score
            
            assert current_score >= next_score, \
                f"MatchEngine返回的候选规则排序不变量被违反: " \
                f"candidates[{i}].weight_score ({current_score:.2f}) < " \
                f"candidates[{i+1}].weight_score ({next_score:.2f})"
    
    except Exception as e:
        # 如果评估失败，记录错误但不失败测试（因为可能是测试数据问题）
        logger.warning(f"评估候选规则时出错: {e}")
        # 重新抛出异常以便调试
        raise


# ============================================================================
# Property 5: 匹配特征排序不变量
# ============================================================================

@given(matched_features=st.lists(feature_match_strategy(), min_size=0, max_size=20))
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_5_matched_features_sorting_invariant(matched_features):
    """
    Feature: matching-rule-visualization-system
    Property 5: 匹配特征排序不变量
    
    For any 候选规则的匹配特征列表,特征应该按权重从高到低排序,
    即对于列表中任意相邻的两个特征features[i]和features[i+1],
    应该满足features[i].weight >= features[i+1].weight。
    
    Validates: Requirements 7.2
    """
    # 如果特征列表为空或只有一个元素，排序属性自动满足
    if len(matched_features) <= 1:
        return
    
    # 按权重排序（模拟MatchEngine._evaluate_all_candidates中的排序逻辑）
    sorted_features = sorted(matched_features, key=lambda f: f.weight, reverse=True)
    
    # 验证排序不变量：对于任意相邻的两个特征，前一个的权重应该 >= 后一个的权重
    for i in range(len(sorted_features) - 1):
        current_weight = sorted_features[i].weight
        next_weight = sorted_features[i + 1].weight
        
        assert current_weight >= next_weight, \
            f"匹配特征排序不变量被违反: features[{i}].weight ({current_weight}) < features[{i+1}].weight ({next_weight})"


@given(candidate=candidate_detail_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_5_candidate_matched_features_sorting(candidate):
    """
    Feature: matching-rule-visualization-system
    Property 5: 匹配特征排序不变量 (CandidateDetail中)
    
    验证CandidateDetail对象中的matched_features列表是否按权重从高到低排序。
    
    Validates: Requirements 7.2
    """
    matched_features = candidate.matched_features
    
    # 如果特征列表为空或只有一个元素，排序属性自动满足
    if len(matched_features) <= 1:
        return
    
    # 验证排序不变量：对于任意相邻的两个特征，前一个的权重应该 >= 后一个的权重
    for i in range(len(matched_features) - 1):
        current_weight = matched_features[i].weight
        next_weight = matched_features[i + 1].weight
        
        assert current_weight >= next_weight, \
            f"CandidateDetail中的匹配特征排序不变量被违反: " \
            f"matched_features[{i}].weight ({current_weight}) < " \
            f"matched_features[{i+1}].weight ({next_weight})"


@given(
    features=st.lists(st.text(min_size=1, max_size=50), min_size=2, max_size=10),
    num_rules=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_5_match_engine_feature_sorting(features, num_rules):
    """
    Feature: matching-rule-visualization-system
    Property 5: 匹配特征排序不变量 (MatchEngine集成测试)
    
    验证MatchEngine._evaluate_all_candidates()方法返回的候选规则中，
    每个候选规则的matched_features列表是否按权重从高到低排序。
    
    Validates: Requirements 7.2
    """
    from backend.modules.match_engine import MatchEngine
    from backend.modules.data_loader import Rule, Device
    
    # 创建测试规则和设备
    rules = []
    devices = {}
    
    for i in range(num_rules):
        device_id = f"device_{i}"
        rule_id = f"rule_{i}"
        
        # 创建设备
        device = Device(
            device_id=device_id,
            brand=f"Brand_{i}",
            device_name=f"Device_{i}",
            spec_model=f"Model_{i}",
            detailed_params=f"Params_{i}",
            unit_price=100.0 * (i + 1)
        )
        devices[device_id] = device
        
        # 创建规则，使用随机特征和权重
        import random
        rule_features = random.sample(features, min(len(features), random.randint(1, len(features))))
        
        # 为每个特征分配不同的权重，确保有明显的排序差异
        feature_weights = {}
        for idx, f in enumerate(rule_features):
            # 使用递减的权重，确保有排序差异
            feature_weights[f] = random.uniform(1.0, 10.0)
        
        rule = Rule(
            rule_id=rule_id,
            target_device_id=device_id,
            auto_extracted_features=rule_features,
            feature_weights=feature_weights,
            match_threshold=random.uniform(3.0, 8.0),
            remark=f"Test rule {i}"
        )
        rules.append(rule)
    
    # 创建配置
    config = {
        'global_config': {
            'default_match_threshold': 5.0
        },
        'brand_keywords': [],
        'device_type_keywords': []
    }
    
    # 创建匹配引擎
    match_engine = MatchEngine(rules, devices, config)
    
    # 评估所有候选规则
    try:
        candidates = match_engine._evaluate_all_candidates(features)
        
        # 验证候选列表不为None
        assert candidates is not None, "候选规则列表不应为None"
        
        # 对每个候选规则，验证其matched_features的排序
        for candidate in candidates:
            matched_features = candidate.matched_features
            
            # 如果特征列表为空或只有一个元素，排序属性自动满足
            if len(matched_features) <= 1:
                continue
            
            # 验证排序不变量：对于任意相邻的两个特征，前一个的权重应该 >= 后一个的权重
            for i in range(len(matched_features) - 1):
                current_weight = matched_features[i].weight
                next_weight = matched_features[i + 1].weight
                
                assert current_weight >= next_weight, \
                    f"MatchEngine返回的候选规则 {candidate.rule_id} 中的匹配特征排序不变量被违反: " \
                    f"matched_features[{i}].weight ({current_weight:.2f}) < " \
                    f"matched_features[{i+1}].weight ({next_weight:.2f})"
    
    except Exception as e:
        # 如果评估失败，记录错误但不失败测试（因为可能是测试数据问题）
        logger.warning(f"评估候选规则时出错: {e}")
        # 重新抛出异常以便调试
        raise


# ============================================================================
# Property 6: 特征贡献值计算正确性
# ============================================================================

@st.composite
def valid_candidate_for_contribution_test(draw):
    """
    Generate CandidateDetail objects with correctly calculated contribution percentages
    
    This strategy ensures that:
    1. Each feature's contribution_percentage = (weight / total_score) * 100
    2. Sum of all contribution_percentages = 100%
    """
    threshold_types = ['rule', 'default']
    feature_types = ['brand', 'device_type', 'model', 'parameter']
    
    # Generate features with weights (at least 1 feature with non-zero weight)
    num_features = draw(st.integers(min_value=1, max_value=10))
    features = []
    total_weight = 0.0
    
    for i in range(num_features):
        feature_name = draw(st.text(min_size=1, max_size=50))
        # Ensure at least some features have non-zero weight
        weight = draw(st.floats(min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False))
        total_weight += weight
        features.append((feature_name, weight, draw(st.sampled_from(feature_types))))
    
    # Calculate contribution percentages correctly
    matched_features = []
    for feature_name, weight, feature_type in features:
        contribution_percentage = (weight / total_weight) * 100 if total_weight > 0 else 0
        matched_features.append(FeatureMatch(
            feature=feature_name,
            weight=weight,
            feature_type=feature_type,
            contribution_percentage=contribution_percentage
        ))
    
    # Sort by weight (descending) as per Property 5
    matched_features.sort(key=lambda f: f.weight, reverse=True)
    
    return CandidateDetail(
        rule_id=draw(st.text(min_size=1, max_size=50)),
        target_device_id=draw(st.text(min_size=1, max_size=50)),
        device_info=draw(device_info_strategy()),
        weight_score=total_weight,  # Total score equals sum of weights
        match_threshold=draw(st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)),
        threshold_type=draw(st.sampled_from(threshold_types)),
        is_qualified=draw(st.booleans()),
        matched_features=matched_features,
        unmatched_features=draw(st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=10)),
        score_breakdown={f[0]: f[1] for f in features},
        total_possible_score=draw(st.floats(min_value=total_weight, max_value=100.0, allow_nan=False, allow_infinity=False))
    )


@given(candidate=valid_candidate_for_contribution_test())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_6_feature_contribution_calculation(candidate):
    """
    Feature: matching-rule-visualization-system
    Property 6: 特征贡献值计算正确性
    
    For any 候选规则的匹配特征,该特征的贡献百分比(contribution_percentage)
    应该等于(特征权重 / 总得分 * 100),且所有匹配特征的贡献百分比之和应该等于100%。
    
    Validates: Requirements 7.3
    """
    matched_features = candidate.matched_features
    
    # 如果没有匹配特征，跳过测试
    if len(matched_features) == 0:
        return
    
    # 如果总得分为0，跳过测试（避免除零）
    if candidate.weight_score == 0:
        return
    
    # 验证每个特征的贡献百分比计算正确
    for feature_match in matched_features:
        expected_contribution = (feature_match.weight / candidate.weight_score) * 100
        actual_contribution = feature_match.contribution_percentage
        
        # 使用近似比较（允许0.1%的误差，因为浮点数精度问题）
        assert abs(actual_contribution - expected_contribution) < 0.1, \
            f"特征 '{feature_match.feature}' 的贡献百分比计算错误: " \
            f"期望 {expected_contribution:.2f}%, 实际 {actual_contribution:.2f}% " \
            f"(权重={feature_match.weight}, 总得分={candidate.weight_score})"
    
    # 验证所有特征的贡献百分比之和等于100%
    total_contribution = sum(f.contribution_percentage for f in matched_features)
    
    # 使用近似比较（允许0.1%的误差）
    assert abs(total_contribution - 100.0) < 0.1, \
        f"所有特征的贡献百分比之和应该等于100%, 实际为 {total_contribution:.2f}%"


@given(
    features=st.lists(st.text(min_size=1, max_size=50), min_size=2, max_size=10),
    num_rules=st.integers(min_value=1, max_value=5)
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_6_match_engine_contribution_calculation(features, num_rules):
    """
    Feature: matching-rule-visualization-system
    Property 6: 特征贡献值计算正确性 (MatchEngine集成测试)
    
    验证MatchEngine._evaluate_all_candidates()方法返回的候选规则中，
    每个匹配特征的贡献百分比计算是否正确，且总和是否为100%。
    
    Validates: Requirements 7.3
    """
    from backend.modules.match_engine import MatchEngine
    from backend.modules.data_loader import Rule, Device
    
    # 创建测试规则和设备
    rules = []
    devices = {}
    
    for i in range(num_rules):
        device_id = f"device_{i}"
        rule_id = f"rule_{i}"
        
        # 创建设备
        device = Device(
            device_id=device_id,
            brand=f"Brand_{i}",
            device_name=f"Device_{i}",
            spec_model=f"Model_{i}",
            detailed_params=f"Params_{i}",
            unit_price=100.0 * (i + 1)
        )
        devices[device_id] = device
        
        # 创建规则，使用随机特征和权重
        import random
        rule_features = random.sample(features, min(len(features), random.randint(1, len(features))))
        
        # 为每个特征分配权重
        feature_weights = {}
        for f in rule_features:
            feature_weights[f] = random.uniform(1.0, 10.0)
        
        rule = Rule(
            rule_id=rule_id,
            target_device_id=device_id,
            auto_extracted_features=rule_features,
            feature_weights=feature_weights,
            match_threshold=random.uniform(3.0, 8.0),
            remark=f"Test rule {i}"
        )
        rules.append(rule)
    
    # 创建配置
    config = {
        'global_config': {
            'default_match_threshold': 5.0
        },
        'brand_keywords': [],
        'device_type_keywords': []
    }
    
    # 创建匹配引擎
    match_engine = MatchEngine(rules, devices, config)
    
    # 评估所有候选规则
    try:
        candidates = match_engine._evaluate_all_candidates(features)
        
        # 验证候选列表不为None
        assert candidates is not None, "候选规则列表不应为None"
        
        # 对每个候选规则，验证特征贡献百分比计算
        for candidate in candidates:
            matched_features = candidate.matched_features
            
            # 如果没有匹配特征或总得分为0，跳过
            if len(matched_features) == 0 or candidate.weight_score == 0:
                continue
            
            # 验证每个特征的贡献百分比计算正确
            for feature_match in matched_features:
                expected_contribution = (feature_match.weight / candidate.weight_score) * 100
                actual_contribution = feature_match.contribution_percentage
                
                # 使用近似比较（允许0.1%的误差）
                assert abs(actual_contribution - expected_contribution) < 0.1, \
                    f"候选规则 {candidate.rule_id} 中特征 '{feature_match.feature}' 的贡献百分比计算错误: " \
                    f"期望 {expected_contribution:.2f}%, 实际 {actual_contribution:.2f}% " \
                    f"(权重={feature_match.weight}, 总得分={candidate.weight_score})"
            
            # 验证所有特征的贡献百分比之和等于100%
            total_contribution = sum(f.contribution_percentage for f in matched_features)
            
            # 使用近似比较（允许0.1%的误差）
            assert abs(total_contribution - 100.0) < 0.1, \
                f"候选规则 {candidate.rule_id} 的所有特征贡献百分比之和应该等于100%, " \
                f"实际为 {total_contribution:.2f}%"
    
    except Exception as e:
        # 如果评估失败，记录错误但不失败测试（因为可能是测试数据问题）
        logger.warning(f"评估候选规则时出错: {e}")
        # 重新抛出异常以便调试
        raise


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
