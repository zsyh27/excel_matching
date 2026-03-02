"""
增强MatchEngine的单元测试

测试任务3.4: 测试增强MatchEngine的详情记录功能
- 测试详情记录功能
- 测试record_detail=False时不记录
- 测试候选规则评估逻辑
- 测试得分计算和排序

验证需求: 3.2, 6.1-6.4, 7.2, 7.3
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from modules.match_engine import MatchEngine, MatchResult
from modules.match_detail import MatchDetailRecorder, CandidateDetail, FeatureMatch
from modules.data_loader import Device, Rule


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
        },
        "brand_keywords": ["霍尼韦尔", "西门子", "江森", "施耐德"],
        "device_type_keywords": ["传感器", "控制器", "阀门", "探测器"],
        "max_cache_size": 100
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
        ),
        "SENSOR003": Device(
            device_id="SENSOR003",
            brand="江森",
            device_name="压力传感器",
            spec_model="P499VCP-401C",
            detailed_params="0-10bar,4-20mA输出",
            unit_price=450.00
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
            feature_weights={"霍尼韦尔": 3.0, "co传感器": 2.0, "hscm-r100u": 3.0, "0-100ppm": 2.0, "4-20ma": 2.0},
            match_threshold=5.0,
            remark="霍尼韦尔CO传感器"
        ),
        Rule(
            rule_id="R002",
            target_device_id="SENSOR002",
            auto_extracted_features=["西门子", "温度传感器", "qaa2061", "0-50摄氏度", "4-20ma"],
            feature_weights={"西门子": 3.0, "温度传感器": 2.0, "qaa2061": 3.0, "0-50摄氏度": 2.0, "4-20ma": 2.0},
            match_threshold=5.0,
            remark="西门子温度传感器"
        ),
        Rule(
            rule_id="R003",
            target_device_id="SENSOR003",
            auto_extracted_features=["江森", "压力传感器", "p499vcp-401c", "0-10bar", "4-20ma"],
            feature_weights={"江森": 3.0, "压力传感器": 2.0, "p499vcp-401c": 3.0, "0-10bar": 2.0, "4-20ma": 2.0},
            match_threshold=5.0,
            remark="江森压力传感器"
        )
    ]


@pytest.fixture
def detail_recorder(config):
    """详情记录器fixture"""
    return MatchDetailRecorder(config)


@pytest.fixture
def match_engine(rules, devices, config, detail_recorder):
    """匹配引擎fixture"""
    return MatchEngine(rules, devices, config, detail_recorder=detail_recorder)


class TestMatchEngineDetailRecording:
    """测试MatchEngine的详情记录功能"""
    
    def test_match_with_detail_recording_enabled(self, match_engine, detail_recorder):
        """测试启用详情记录时正确记录匹配详情"""
        # 准备测试数据
        features = ["霍尼韦尔", "co传感器", "hscm-r100u", "0-100ppm"]
        input_description = "霍尼韦尔 CO传感器 HSCM-R100U 0-100PPM"
        
        # 执行匹配（默认record_detail=True）
        result, cache_key = match_engine.match(features, input_description, record_detail=True)
        
        # 验证返回结果
        assert result.match_status == "success"
        assert cache_key is not None, "应该返回缓存键"
        
        # 验证详情已记录
        detail = detail_recorder.get_detail(cache_key)
        assert detail is not None, "应该能够获取匹配详情"
        assert detail.original_text == input_description
        assert detail.preprocessing is not None
        assert detail.candidates is not None
        assert len(detail.candidates) > 0, "应该有候选规则"
        assert detail.final_result is not None
        assert detail.decision_reason is not None
    
    def test_match_with_detail_recording_disabled(self, match_engine, detail_recorder):
        """测试禁用详情记录时不记录匹配详情"""
        # 准备测试数据
        features = ["西门子", "温度传感器", "qaa2061"]
        input_description = "西门子 温度传感器 QAA2061"
        
        # 执行匹配（record_detail=False）
        result, cache_key = match_engine.match(features, input_description, record_detail=False)
        
        # 验证返回结果
        assert result.match_status == "success"
        assert cache_key is None, "禁用详情记录时应该返回None"
        
        # 验证缓存中没有新增记录
        # 由于cache_key为None，无法验证缓存，但可以检查缓存大小
        initial_cache_size = len(detail_recorder.cache)
        # 再次执行不记录的匹配
        result2, cache_key2 = match_engine.match(features, input_description, record_detail=False)
        assert cache_key2 is None
        assert len(detail_recorder.cache) == initial_cache_size, "缓存大小不应该增加"
    
    def test_match_detail_contains_preprocessing_result(self, match_engine, detail_recorder):
        """测试匹配详情包含预处理结果"""
        features = ["霍尼韦尔", "co传感器"]
        input_description = "霍尼韦尔 CO传感器"
        
        result, cache_key = match_engine.match(features, input_description)
        
        detail = detail_recorder.get_detail(cache_key)
        assert detail is not None
        
        # 验证预处理结果结构
        preprocessing = detail.preprocessing
        assert 'original' in preprocessing
        assert 'cleaned' in preprocessing
        assert 'normalized' in preprocessing
        assert 'features' in preprocessing
        assert preprocessing['features'] == features
    
    def test_match_detail_contains_candidates(self, match_engine, detail_recorder):
        """测试匹配详情包含候选规则列表"""
        features = ["霍尼韦尔", "co传感器", "4-20ma"]
        input_description = "霍尼韦尔 CO传感器 4-20mA"
        
        result, cache_key = match_engine.match(features, input_description)
        
        detail = detail_recorder.get_detail(cache_key)
        assert detail is not None
        assert len(detail.candidates) > 0, "应该有候选规则"
        
        # 验证候选规则结构
        candidate = detail.candidates[0]
        assert hasattr(candidate, 'rule_id')
        assert hasattr(candidate, 'target_device_id')
        assert hasattr(candidate, 'device_info')
        assert hasattr(candidate, 'weight_score')
        assert hasattr(candidate, 'match_threshold')
        assert hasattr(candidate, 'matched_features')
        assert hasattr(candidate, 'unmatched_features')
    
    def test_match_detail_contains_final_result(self, match_engine, detail_recorder):
        """测试匹配详情包含最终结果"""
        features = ["西门子", "温度传感器"]
        input_description = "西门子 温度传感器"
        
        result, cache_key = match_engine.match(features, input_description)
        
        detail = detail_recorder.get_detail(cache_key)
        assert detail is not None
        
        # 验证最终结果
        final_result = detail.final_result
        assert 'match_status' in final_result
        assert 'device_id' in final_result
        assert 'match_score' in final_result
        assert final_result['match_status'] == result.match_status
        assert final_result['device_id'] == result.device_id
    
    def test_match_detail_with_failed_match(self, match_engine, detail_recorder):
        """测试匹配失败时的详情记录"""
        features = ["不存在的特征"]
        input_description = "不存在的设备"
        
        result, cache_key = match_engine.match(features, input_description)
        
        assert result.match_status == "failed"
        assert cache_key is not None, "失败的匹配也应该记录详情"
        
        detail = detail_recorder.get_detail(cache_key)
        assert detail is not None
        assert detail.final_result['match_status'] == "failed"
        assert len(detail.optimization_suggestions) > 0, "失败时应该有优化建议"


class TestEvaluateAllCandidates:
    """测试_evaluate_all_candidates方法"""
    
    def test_evaluate_all_candidates_returns_sorted_list(self, match_engine):
        """测试候选规则按得分排序（需求3.2）"""
        # 准备特征，让不同规则有不同得分
        features = ["霍尼韦尔", "co传感器", "hscm-r100u", "4-20ma"]  # 霍尼韦尔得分最高
        
        candidates = match_engine._evaluate_all_candidates(features)
        
        assert len(candidates) > 0, "应该有候选规则"
        
        # 验证排序：得分从高到低
        for i in range(len(candidates) - 1):
            assert candidates[i].weight_score >= candidates[i+1].weight_score, \
                f"候选规则应该按得分降序排列，但 {candidates[i].weight_score} < {candidates[i+1].weight_score}"
    
    def test_evaluate_all_candidates_calculates_scores_correctly(self, match_engine):
        """测试候选规则得分计算正确"""
        features = ["霍尼韦尔", "co传感器", "4-20ma"]
        
        candidates = match_engine._evaluate_all_candidates(features)
        
        # 找到霍尼韦尔的候选
        honeywell_candidate = next((c for c in candidates if c.rule_id == "R001"), None)
        assert honeywell_candidate is not None
        
        # 验证得分：霍尼韦尔(3) + co传感器(2) + 4-20ma(2) = 7
        expected_score = 3.0 + 2.0 + 2.0
        assert honeywell_candidate.weight_score == expected_score
    
    def test_evaluate_all_candidates_includes_device_info(self, match_engine):
        """测试候选规则包含设备信息"""
        features = ["西门子", "温度传感器"]
        
        candidates = match_engine._evaluate_all_candidates(features)
        
        # 找到西门子的候选
        siemens_candidate = next((c for c in candidates if c.rule_id == "R002"), None)
        assert siemens_candidate is not None
        
        # 验证设备信息
        device_info = siemens_candidate.device_info
        assert 'device_id' in device_info
        assert 'brand' in device_info
        assert 'device_name' in device_info
        assert device_info['brand'] == "西门子"
        assert device_info['device_name'] == "温度传感器"
    
    def test_evaluate_all_candidates_identifies_matched_features(self, match_engine):
        """测试候选规则正确识别匹配的特征"""
        features = ["霍尼韦尔", "hscm-r100u", "0-100ppm"]
        
        candidates = match_engine._evaluate_all_candidates(features)
        
        honeywell_candidate = next((c for c in candidates if c.rule_id == "R001"), None)
        assert honeywell_candidate is not None
        
        # 验证匹配的特征
        matched_feature_names = [f.feature for f in honeywell_candidate.matched_features]
        assert "霍尼韦尔" in matched_feature_names
        assert "hscm-r100u" in matched_feature_names
        assert "0-100ppm" in matched_feature_names
    
    def test_evaluate_all_candidates_identifies_unmatched_features(self, match_engine):
        """测试候选规则正确识别未匹配的特征"""
        features = ["霍尼韦尔"]  # 只有一个特征匹配
        
        candidates = match_engine._evaluate_all_candidates(features)
        
        honeywell_candidate = next((c for c in candidates if c.rule_id == "R001"), None)
        assert honeywell_candidate is not None
        
        # 验证未匹配的特征
        unmatched = honeywell_candidate.unmatched_features
        assert len(unmatched) > 0, "应该有未匹配的特征"
        # 规则中的其他特征应该在未匹配列表中
        assert "co传感器" in unmatched or "hscm-r100u" in unmatched
    
    def test_evaluate_all_candidates_with_empty_features(self, match_engine):
        """测试空特征列表"""
        features = []
        
        candidates = match_engine._evaluate_all_candidates(features)
        
        # 空特征应该返回空候选列表
        assert len(candidates) == 0
    
    def test_evaluate_all_candidates_threshold_type(self, match_engine):
        """测试候选规则的阈值类型判断"""
        # 测试满足规则阈值的情况
        features = ["霍尼韦尔", "co传感器", "hscm-r100u"]  # 得分 3+2+3=8，超过规则阈值5
        
        candidates = match_engine._evaluate_all_candidates(features)
        
        honeywell_candidate = next((c for c in candidates if c.rule_id == "R001"), None)
        assert honeywell_candidate is not None
        assert honeywell_candidate.threshold_type == "rule"
        assert honeywell_candidate.is_qualified is True
    
    def test_evaluate_all_candidates_handles_missing_device(self, match_engine):
        """测试处理设备不存在的情况"""
        # 添加一个指向不存在设备的规则
        bad_rule = Rule(
            rule_id="R999",
            target_device_id="NONEXISTENT",
            auto_extracted_features=["测试特征"],
            feature_weights={"测试特征": 10.0},
            match_threshold=5.0,
            remark="测试规则"
        )
        match_engine.rules.append(bad_rule)
        
        features = ["测试特征", "霍尼韦尔"]
        
        # 应该不会抛出异常，而是跳过不存在的设备
        candidates = match_engine._evaluate_all_candidates(features)
        
        # 验证不存在的设备被跳过
        bad_candidate = next((c for c in candidates if c.rule_id == "R999"), None)
        assert bad_candidate is None, "不存在的设备应该被跳过"


class TestMatchedFeaturesOrdering:
    """测试匹配特征的排序（需求7.2）"""
    
    def test_matched_features_sorted_by_weight(self, match_engine):
        """测试匹配特征按权重降序排列"""
        features = ["霍尼韦尔", "co传感器", "hscm-r100u", "0-100ppm", "4-20ma"]
        
        candidates = match_engine._evaluate_all_candidates(features)
        
        honeywell_candidate = next((c for c in candidates if c.rule_id == "R001"), None)
        assert honeywell_candidate is not None
        
        matched_features = honeywell_candidate.matched_features
        assert len(matched_features) > 0
        
        # 验证排序：权重从高到低
        for i in range(len(matched_features) - 1):
            assert matched_features[i].weight >= matched_features[i+1].weight, \
                f"匹配特征应该按权重降序排列，但 {matched_features[i].weight} < {matched_features[i+1].weight}"
    
    def test_matched_features_weight_values(self, match_engine):
        """测试匹配特征的权重值正确"""
        features = ["霍尼韦尔", "hscm-r100u"]
        
        candidates = match_engine._evaluate_all_candidates(features)
        
        honeywell_candidate = next((c for c in candidates if c.rule_id == "R001"), None)
        assert honeywell_candidate is not None
        
        # 验证权重值
        for feature_match in honeywell_candidate.matched_features:
            if feature_match.feature == "霍尼韦尔":
                assert feature_match.weight == 3.0
            elif feature_match.feature == "hscm-r100u":
                assert feature_match.weight == 3.0


class TestFeatureContributionCalculation:
    """测试特征贡献值计算（需求7.3）"""
    
    def test_contribution_percentage_calculation(self, match_engine):
        """测试特征贡献百分比计算正确"""
        features = ["霍尼韦尔", "co传感器"]  # 权重 3 + 2 = 5
        
        candidates = match_engine._evaluate_all_candidates(features)
        
        honeywell_candidate = next((c for c in candidates if c.rule_id == "R001"), None)
        assert honeywell_candidate is not None
        
        total_score = honeywell_candidate.weight_score
        assert total_score == 5.0
        
        # 验证贡献百分比
        for feature_match in honeywell_candidate.matched_features:
            expected_contribution = (feature_match.weight / total_score) * 100
            assert abs(feature_match.contribution_percentage - expected_contribution) < 0.01, \
                f"特征 {feature_match.feature} 的贡献百分比计算错误"
    
    def test_contribution_percentages_sum_to_100(self, match_engine):
        """测试所有特征的贡献百分比之和为100%"""
        features = ["西门子", "温度传感器", "qaa2061"]
        
        candidates = match_engine._evaluate_all_candidates(features)
        
        siemens_candidate = next((c for c in candidates if c.rule_id == "R002"), None)
        assert siemens_candidate is not None
        
        # 计算贡献百分比之和
        total_contribution = sum(f.contribution_percentage for f in siemens_candidate.matched_features)
        
        # 允许小的浮点误差
        assert abs(total_contribution - 100.0) < 0.1, \
            f"贡献百分比之和应该为100%，实际为 {total_contribution}%"
    
    def test_contribution_with_single_feature(self, match_engine):
        """测试单个特征的贡献百分比为100%"""
        features = ["江森"]
        
        candidates = match_engine._evaluate_all_candidates(features)
        
        johnson_candidate = next((c for c in candidates if c.rule_id == "R003"), None)
        assert johnson_candidate is not None
        
        assert len(johnson_candidate.matched_features) == 1
        assert johnson_candidate.matched_features[0].contribution_percentage == 100.0


class TestScoreBreakdown:
    """测试得分分解"""
    
    def test_score_breakdown_contains_all_matched_features(self, match_engine):
        """测试得分分解包含所有匹配的特征"""
        features = ["霍尼韦尔", "co传感器", "4-20ma"]
        
        candidates = match_engine._evaluate_all_candidates(features)
        
        honeywell_candidate = next((c for c in candidates if c.rule_id == "R001"), None)
        assert honeywell_candidate is not None
        
        score_breakdown = honeywell_candidate.score_breakdown
        
        # 验证所有匹配的特征都在得分分解中
        for feature_match in honeywell_candidate.matched_features:
            assert feature_match.feature in score_breakdown
            assert score_breakdown[feature_match.feature] == feature_match.weight
    
    def test_score_breakdown_sum_equals_total_score(self, match_engine):
        """测试得分分解的总和等于总得分"""
        features = ["西门子", "温度传感器", "qaa2061", "4-20ma"]
        
        candidates = match_engine._evaluate_all_candidates(features)
        
        siemens_candidate = next((c for c in candidates if c.rule_id == "R002"), None)
        assert siemens_candidate is not None
        
        score_breakdown = siemens_candidate.score_breakdown
        breakdown_sum = sum(score_breakdown.values())
        
        assert breakdown_sum == siemens_candidate.weight_score


class TestTotalPossibleScore:
    """测试最大可能得分计算"""
    
    def test_total_possible_score_calculation(self, match_engine):
        """测试最大可能得分计算正确"""
        features = ["霍尼韦尔"]
        
        candidates = match_engine._evaluate_all_candidates(features)
        
        honeywell_candidate = next((c for c in candidates if c.rule_id == "R001"), None)
        assert honeywell_candidate is not None
        
        # 霍尼韦尔规则的所有特征权重之和：3+2+3+2+2=12
        expected_total = 3.0 + 2.0 + 3.0 + 2.0 + 2.0
        assert honeywell_candidate.total_possible_score == expected_total
    
    def test_total_possible_score_greater_than_actual_score(self, match_engine):
        """测试最大可能得分大于等于实际得分"""
        features = ["西门子", "温度传感器"]
        
        candidates = match_engine._evaluate_all_candidates(features)
        
        for candidate in candidates:
            assert candidate.total_possible_score >= candidate.weight_score, \
                f"最大可能得分 {candidate.total_possible_score} 应该大于等于实际得分 {candidate.weight_score}"


class TestFeatureTypeClassification:
    """测试特征类型分类"""
    
    def test_classify_brand_feature(self, match_engine):
        """测试品牌特征分类"""
        feature_type = match_engine._classify_feature_type("霍尼韦尔")
        assert feature_type == "brand"
    
    def test_classify_device_type_feature(self, match_engine):
        """测试设备类型特征分类"""
        feature_type = match_engine._classify_feature_type("传感器")
        assert feature_type == "device_type"
        
        feature_type2 = match_engine._classify_feature_type("co传感器")
        assert feature_type2 == "device_type"
    
    def test_classify_model_feature(self, match_engine):
        """测试型号特征分类（包含字母和数字）"""
        feature_type = match_engine._classify_feature_type("hscm-r100u")
        assert feature_type == "model"
        
        feature_type2 = match_engine._classify_feature_type("qaa2061")
        assert feature_type2 == "model"
    
    def test_classify_parameter_feature(self, match_engine):
        """测试参数特征分类"""
        feature_type = match_engine._classify_feature_type("0-100ppm")
        # 包含字母和数字，可能被分类为model，但如果没有字母则为parameter
        # 这个测试验证默认分类
        assert feature_type in ["model", "parameter"]


class TestMatchEngineIntegration:
    """集成测试：测试完整的匹配流程"""
    
    def test_complete_match_flow_with_detail_recording(self, match_engine, detail_recorder):
        """测试完整的匹配流程包含详情记录"""
        features = ["霍尼韦尔", "co传感器", "hscm-r100u", "0-100ppm", "4-20ma"]
        input_description = "霍尼韦尔 CO传感器 HSCM-R100U 0-100PPM 4-20mA"
        
        # 执行匹配
        result, cache_key = match_engine.match(features, input_description)
        
        # 验证匹配结果
        assert result.match_status == "success"
        assert result.device_id == "SENSOR001"
        assert cache_key is not None
        
        # 验证详情记录
        detail = detail_recorder.get_detail(cache_key)
        assert detail is not None
        
        # 验证详情完整性
        assert detail.original_text == input_description
        assert len(detail.candidates) > 0
        assert detail.candidates[0].rule_id == "R001"  # 霍尼韦尔应该是最高分
        assert detail.final_result['match_status'] == "success"
        assert detail.final_result['device_id'] == "SENSOR001"
        
        # 验证候选规则排序
        for i in range(len(detail.candidates) - 1):
            assert detail.candidates[i].weight_score >= detail.candidates[i+1].weight_score
        
        # 验证匹配特征排序
        best_candidate = detail.candidates[0]
        for i in range(len(best_candidate.matched_features) - 1):
            assert best_candidate.matched_features[i].weight >= best_candidate.matched_features[i+1].weight
    
    def test_multiple_matches_with_different_scores(self, match_engine, detail_recorder):
        """测试多个匹配，验证不同得分的候选规则"""
        # 第一次匹配：霍尼韦尔
        features1 = ["霍尼韦尔", "co传感器"]
        result1, cache_key1 = match_engine.match(features1, "霍尼韦尔 CO传感器")
        
        # 第二次匹配：西门子
        features2 = ["西门子", "温度传感器"]
        result2, cache_key2 = match_engine.match(features2, "西门子 温度传感器")
        
        # 验证两次匹配都成功
        assert result1.match_status == "success"
        assert result2.match_status == "success"
        assert cache_key1 != cache_key2, "不同的匹配应该有不同的缓存键"
        
        # 验证详情独立存储
        detail1 = detail_recorder.get_detail(cache_key1)
        detail2 = detail_recorder.get_detail(cache_key2)
        
        assert detail1.final_result['device_id'] == "SENSOR001"
        assert detail2.final_result['device_id'] == "SENSOR002"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
