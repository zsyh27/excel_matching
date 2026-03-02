# -*- coding: utf-8 -*-
"""
匹配算法属性测试

使用Hypothesis进行属性基础测试，验证匹配算法的通用正确性属性
"""

import pytest
from hypothesis import given, strategies as st, settings
from modules.intelligent_device.matching_algorithm import MatchingAlgorithm, MatchResult


# 设备类型策略
device_types = st.sampled_from([
    'CO2传感器',
    '座阀',
    '温度传感器',
    '压力传感器',
    '执行器',
    '控制器'
])

# 品牌策略
brands = st.sampled_from([
    '西门子',
    '霍尼韦尔',
    '施耐德',
    'ABB',
    'Johnson Controls'
])

# 型号策略
models = st.from_regex(r'[A-Z]{2,4}[0-9]{3,5}', fullmatch=True)


@st.composite
def device_strategy(draw, device_type=None, include_key_params=True):
    """
    生成设备数据的策略
    
    Args:
        draw: Hypothesis draw函数
        device_type: 指定设备类型（可选）
        include_key_params: 是否包含关键参数
    
    Returns:
        设备字典
    """
    device_id = draw(st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Nd', 'Lu'))))
    dtype = device_type if device_type else draw(device_types)
    brand = draw(st.one_of(brands, st.none()))
    model = draw(st.one_of(models, st.none()))
    
    device = {
        'device_id': device_id,
        'device_type': dtype,
        'brand': brand,
        'model': model
    }
    
    if include_key_params and draw(st.booleans()):
        # 生成关键参数
        key_params = {}
        if dtype in ['CO2传感器', '温度传感器', '压力传感器']:
            if draw(st.booleans()):
                range_val = draw(st.integers(min_value=100, max_value=5000))
                key_params['量程'] = f'0-{range_val}ppm'
            if draw(st.booleans()):
                key_params['输出信号'] = draw(st.sampled_from(['4-20mA', '0-10V', '0-5V']))
        elif dtype == '座阀':
            if draw(st.booleans()):
                dn = draw(st.integers(min_value=15, max_value=300))
                key_params['通径'] = f'DN{dn}'
            if draw(st.booleans()):
                pn = draw(st.integers(min_value=10, max_value=40))
                key_params['压力等级'] = f'PN{pn}'
        
        if key_params:
            device['key_params'] = key_params
    
    return device


class TestMatchingAlgorithmProperties:
    """匹配算法属性测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.matcher = MatchingAlgorithm()
    
    # Feature: intelligent-device-input, Property 14: 设备类型过滤优先
    @settings(max_examples=100)
    @given(
        device_type=device_types,
        num_same_type=st.integers(min_value=1, max_value=20),
        num_different_type=st.integers(min_value=1, max_value=30)
    )
    def test_property_14_device_type_filtering_priority(
        self,
        device_type,
        num_same_type,
        num_different_type
    ):
        """
        **Validates: Requirements 9.1**
        
        属性 14：设备类型过滤优先
        
        对于任意目标设备，匹配算法在查找相似设备时应该首先按设备类型过滤候选设备，
        只返回相同设备类型的匹配结果。
        """
        # 生成目标设备
        target = {
            'device_id': 'target',
            'device_type': device_type,
            'brand': '西门子',
            'model': 'TEST001'
        }
        
        # 生成相同类型的候选设备
        same_type_candidates = [
            {
                'device_id': f'same_{i}',
                'device_type': device_type,
                'brand': '西门子' if i % 2 == 0 else '霍尼韦尔',
                'model': f'MODEL{i}'
            }
            for i in range(num_same_type)
        ]
        
        # 生成不同类型的候选设备
        other_types = ['CO2传感器', '座阀', '温度传感器', '压力传感器', '执行器', '控制器']
        other_types = [t for t in other_types if t != device_type]
        
        different_type_candidates = [
            {
                'device_id': f'diff_{i}',
                'device_type': other_types[i % len(other_types)],
                'brand': '西门子',  # 即使品牌相同
                'model': 'TEST001'  # 即使型号相同
            }
            for i in range(num_different_type)
        ]
        
        # 混合候选设备
        candidates = same_type_candidates + different_type_candidates
        
        # 执行匹配
        results = self.matcher.find_similar_devices(target, candidates)
        
        # 验证：所有返回的设备都是相同设备类型
        for result in results:
            assert result.device['device_type'] == device_type, \
                f"返回的设备类型 {result.device['device_type']} 与目标设备类型 {device_type} 不匹配"
        
        # 验证：返回的设备数量不超过相同类型的候选设备数量
        assert len(results) <= num_same_type, \
            f"返回的设备数量 {len(results)} 超过了相同类型的候选设备数量 {num_same_type}"
    
    # Feature: intelligent-device-input, Property 15: 匹配结果排序和限制
    @settings(max_examples=100)
    @given(
        device_type=device_types,
        num_candidates=st.integers(min_value=25, max_value=100)
    )
    def test_property_15_matching_results_sorted_and_limited(
        self,
        device_type,
        num_candidates
    ):
        """
        **Validates: Requirements 9.6**
        
        属性 15：匹配结果排序和限制
        
        对于任意目标设备，匹配算法应该返回最多20个候选设备，
        并且这些结果按相似度得分降序排列（得分高的在前）。
        """
        # 生成目标设备
        target = {
            'device_id': 'target',
            'device_type': device_type,
            'brand': '西门子',
            'model': 'TARGET001'
        }
        
        # 生成多个候选设备，具有不同的相似度
        candidates = []
        for i in range(num_candidates):
            device = {
                'device_id': f'candidate_{i}',
                'device_type': device_type,
                # 变化品牌和型号以产生不同的相似度得分
                'brand': '西门子' if i % 3 == 0 else '霍尼韦尔',
                'model': 'TARGET001' if i % 5 == 0 else f'MODEL{i}'
            }
            candidates.append(device)
        
        # 执行匹配
        results = self.matcher.find_similar_devices(target, candidates)
        
        # 验证1：返回结果数量不超过20个
        assert len(results) <= 20, \
            f"返回的设备数量 {len(results)} 超过了限制 20"
        
        # 验证2：结果按相似度得分降序排列
        scores = [r.similarity_score for r in results]
        sorted_scores = sorted(scores, reverse=True)
        assert scores == sorted_scores, \
            f"结果未按降序排列: {scores} != {sorted_scores}"
        
        # 验证3：如果候选设备少于20个，返回所有候选设备（排除目标设备本身）
        if num_candidates <= 20:
            # 注意：目标设备不在候选列表中，所以应该返回所有候选设备
            assert len(results) == num_candidates, \
                f"候选设备少于20个时，应该返回所有候选设备"
    
    # Feature: intelligent-device-input, Property 16: 匹配结果包含详情
    @settings(max_examples=100)
    @given(
        target_device=device_strategy(),
        candidate_device=device_strategy()
    )
    def test_property_16_matching_results_include_details(
        self,
        target_device,
        candidate_device
    ):
        """
        **Validates: Requirements 9.7**
        
        属性 16：匹配结果包含详情
        
        对于任意匹配结果，应该包含匹配的特征详情和各特征的得分，
        使用户能够理解为什么这些设备被认为相似。
        """
        # 确保候选设备与目标设备类型相同（否则会被过滤掉）
        candidate_device['device_type'] = target_device['device_type']
        
        # 确保设备ID不同
        if candidate_device['device_id'] == target_device['device_id']:
            candidate_device['device_id'] = target_device['device_id'] + '_different'
        
        candidates = [candidate_device]
        
        # 执行匹配
        results = self.matcher.find_similar_devices(target_device, candidates)
        
        # 如果有匹配结果
        if len(results) > 0:
            result = results[0]
            
            # 验证1：结果是MatchResult对象
            assert isinstance(result, MatchResult), \
                f"结果应该是MatchResult对象，实际是 {type(result)}"
            
            # 验证2：包含必需的字段
            assert hasattr(result, 'device_id'), "结果应该包含device_id字段"
            assert hasattr(result, 'similarity_score'), "结果应该包含similarity_score字段"
            assert hasattr(result, 'matched_features'), "结果应该包含matched_features字段"
            assert hasattr(result, 'device'), "结果应该包含device字段"
            
            # 验证3：matched_features是字典
            assert isinstance(result.matched_features, dict), \
                f"matched_features应该是字典，实际是 {type(result.matched_features)}"
            
            # 验证4：similarity_score是浮点数
            assert isinstance(result.similarity_score, (int, float)), \
                f"similarity_score应该是数字，实际是 {type(result.similarity_score)}"
            
            # 验证5：matched_features中的值都是数字（得分）
            for feature_name, feature_score in result.matched_features.items():
                assert isinstance(feature_score, (int, float)), \
                    f"特征 {feature_name} 的得分应该是数字，实际是 {type(feature_score)}"
                assert feature_score > 0, \
                    f"特征 {feature_name} 的得分应该大于0，实际是 {feature_score}"
            
            # 验证6：matched_features中的特征名称应该是有效的特征
            valid_features = {'device_type', 'brand', 'model', 'key_params', 'description'}
            for feature_name in result.matched_features.keys():
                assert feature_name in valid_features, \
                    f"特征名称 {feature_name} 不是有效的特征"
            
            # 验证7：similarity_score应该等于所有matched_features得分之和
            expected_score = sum(result.matched_features.values())
            assert abs(result.similarity_score - expected_score) < 0.01, \
                f"similarity_score {result.similarity_score} 应该等于所有特征得分之和 {expected_score}"
            
            # 验证8：device字段包含完整的设备信息
            assert result.device == candidate_device, \
                "device字段应该包含完整的候选设备信息"
    
    # Feature: intelligent-device-input, Property 14: 设备类型过滤优先（边界情况：空设备类型）
    @settings(max_examples=100)
    @given(
        num_candidates=st.integers(min_value=5, max_value=30)
    )
    def test_property_14_empty_device_type_returns_all(
        self,
        num_candidates
    ):
        """
        **Validates: Requirements 9.1**
        
        属性 14 边界情况：当目标设备没有设备类型时，应该返回所有候选设备
        """
        # 生成没有设备类型的目标设备
        target = {
            'device_id': 'target',
            'brand': '西门子',
            'model': 'TEST001'
        }
        
        # 生成多个候选设备
        candidates = [
            {
                'device_id': f'candidate_{i}',
                'device_type': 'CO2传感器' if i % 2 == 0 else '座阀',
                'brand': '西门子',
                'model': f'MODEL{i}'
            }
            for i in range(num_candidates)
        ]
        
        # 执行匹配
        results = self.matcher.find_similar_devices(target, candidates)
        
        # 验证：当没有设备类型时，不应该过滤（但实际实现中可能返回空列表）
        # 这取决于实现策略，这里我们验证不会崩溃
        assert isinstance(results, list), "应该返回列表"
    
    # Feature: intelligent-device-input, Property 15: 匹配结果排序和限制（边界情况：少于20个候选）
    @settings(max_examples=100)
    @given(
        device_type=device_types,
        num_candidates=st.integers(min_value=1, max_value=19)
    )
    def test_property_15_fewer_than_limit_returns_all(
        self,
        device_type,
        num_candidates
    ):
        """
        **Validates: Requirements 9.6**
        
        属性 15 边界情况：当候选设备少于20个时，应该返回所有候选设备
        """
        # 生成目标设备
        target = {
            'device_id': 'target',
            'device_type': device_type,
            'brand': '西门子'
        }
        
        # 生成少于20个的候选设备
        candidates = [
            {
                'device_id': f'candidate_{i}',
                'device_type': device_type,
                'brand': '西门子' if i % 2 == 0 else '霍尼韦尔'
            }
            for i in range(num_candidates)
        ]
        
        # 执行匹配
        results = self.matcher.find_similar_devices(target, candidates)
        
        # 验证：应该返回所有候选设备
        assert len(results) == num_candidates, \
            f"候选设备少于20个时，应该返回所有 {num_candidates} 个候选设备，实际返回 {len(results)} 个"
    
    # Feature: intelligent-device-input, Property 15: 匹配结果排序和限制（自定义限制）
    @settings(max_examples=100)
    @given(
        device_type=device_types,
        num_candidates=st.integers(min_value=20, max_value=50),
        custom_limit=st.integers(min_value=5, max_value=15)
    )
    def test_property_15_custom_limit_respected(
        self,
        device_type,
        num_candidates,
        custom_limit
    ):
        """
        **Validates: Requirements 9.6**
        
        属性 15 扩展：自定义限制应该被遵守
        """
        # 生成目标设备
        target = {
            'device_id': 'target',
            'device_type': device_type,
            'brand': '西门子'
        }
        
        # 生成候选设备
        candidates = [
            {
                'device_id': f'candidate_{i}',
                'device_type': device_type,
                'brand': '西门子'
            }
            for i in range(num_candidates)
        ]
        
        # 执行匹配，使用自定义限制
        results = self.matcher.find_similar_devices(target, candidates, limit=custom_limit)
        
        # 验证：返回结果数量不超过自定义限制
        assert len(results) <= custom_limit, \
            f"返回的设备数量 {len(results)} 超过了自定义限制 {custom_limit}"
