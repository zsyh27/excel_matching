# -*- coding: utf-8 -*-
"""
匹配算法单元测试
"""

import pytest
from modules.intelligent_device.matching_algorithm import MatchingAlgorithm, MatchResult


class TestMatchingAlgorithmWeights:
    """测试匹配算法权重配置"""
    
    def test_weight_constants_exist(self):
        """验证权重常量存在"""
        assert hasattr(MatchingAlgorithm, 'WEIGHTS')
        assert isinstance(MatchingAlgorithm.WEIGHTS, dict)
    
    def test_device_type_weight(self):
        """验证设备类型权重为30.0"""
        assert MatchingAlgorithm.WEIGHTS['device_type'] == 30.0
    
    def test_key_params_weight(self):
        """验证关键参数权重为15.0"""
        assert MatchingAlgorithm.WEIGHTS['key_params'] == 15.0
    
    def test_brand_weight(self):
        """验证品牌权重为10.0"""
        assert MatchingAlgorithm.WEIGHTS['brand'] == 10.0
    
    def test_model_weight(self):
        """验证型号权重为8.0"""
        assert MatchingAlgorithm.WEIGHTS['model'] == 8.0


class TestFilterByDeviceType:
    """测试按设备类型过滤功能"""
    
    def setup_method(self):
        """设置测试环境"""
        self.matcher = MatchingAlgorithm()
    
    def test_filter_same_device_type(self):
        """测试过滤相同设备类型"""
        candidates = [
            {'device_id': '1', 'device_type': 'CO2传感器', 'brand': '西门子'},
            {'device_id': '2', 'device_type': '座阀', 'brand': '霍尼韦尔'},
            {'device_id': '3', 'device_type': 'CO2传感器', 'brand': '施耐德'},
        ]
        
        result = self.matcher.filter_by_device_type('CO2传感器', candidates)
        
        assert len(result) == 2
        assert all(d['device_type'] == 'CO2传感器' for d in result)
        assert result[0]['device_id'] == '1'
        assert result[1]['device_id'] == '3'
    
    def test_filter_no_matches(self):
        """测试没有匹配的设备类型"""
        candidates = [
            {'device_id': '1', 'device_type': 'CO2传感器', 'brand': '西门子'},
            {'device_id': '2', 'device_type': '座阀', 'brand': '霍尼韦尔'},
        ]
        
        result = self.matcher.filter_by_device_type('温度传感器', candidates)
        
        assert len(result) == 0
    
    def test_filter_empty_candidates(self):
        """测试空候选列表"""
        result = self.matcher.filter_by_device_type('CO2传感器', [])
        
        assert len(result) == 0
    
    def test_filter_empty_device_type(self):
        """测试空设备类型（返回所有候选）"""
        candidates = [
            {'device_id': '1', 'device_type': 'CO2传感器', 'brand': '西门子'},
            {'device_id': '2', 'device_type': '座阀', 'brand': '霍尼韦尔'},
        ]
        
        result = self.matcher.filter_by_device_type('', candidates)
        
        assert len(result) == 2
    
    def test_filter_none_device_type(self):
        """测试None设备类型（返回所有候选）"""
        candidates = [
            {'device_id': '1', 'device_type': 'CO2传感器', 'brand': '西门子'},
            {'device_id': '2', 'device_type': '座阀', 'brand': '霍尼韦尔'},
        ]
        
        result = self.matcher.filter_by_device_type(None, candidates)
        
        assert len(result) == 2
    
    def test_filter_with_device_name_field(self):
        """测试使用device_name字段的设备"""
        candidates = [
            {'device_id': '1', 'device_name': 'CO2传感器', 'brand': '西门子'},
            {'device_id': '2', 'device_name': '座阀', 'brand': '霍尼韦尔'},
            {'device_id': '3', 'device_name': 'CO2传感器', 'brand': '施耐德'},
        ]
        
        result = self.matcher.filter_by_device_type('CO2传感器', candidates)
        
        assert len(result) == 2
        assert all(d['device_name'] == 'CO2传感器' for d in result)
    
    def test_filter_mixed_field_names(self):
        """测试混合使用device_type和device_name字段"""
        candidates = [
            {'device_id': '1', 'device_type': 'CO2传感器', 'brand': '西门子'},
            {'device_id': '2', 'device_name': '座阀', 'brand': '霍尼韦尔'},
            {'device_id': '3', 'device_name': 'CO2传感器', 'brand': '施耐德'},
        ]
        
        result = self.matcher.filter_by_device_type('CO2传感器', candidates)
        
        assert len(result) == 2
        device_ids = [d['device_id'] for d in result]
        assert '1' in device_ids
        assert '3' in device_ids
    
    def test_filter_missing_device_type_field(self):
        """测试缺少设备类型字段的设备"""
        candidates = [
            {'device_id': '1', 'device_type': 'CO2传感器', 'brand': '西门子'},
            {'device_id': '2', 'brand': '霍尼韦尔'},  # 缺少device_type
            {'device_id': '3', 'device_type': 'CO2传感器', 'brand': '施耐德'},
        ]
        
        result = self.matcher.filter_by_device_type('CO2传感器', candidates)
        
        assert len(result) == 2
        assert all('device_type' in d for d in result)


class TestMatchingAlgorithmInitialization:
    """测试匹配算法初始化"""
    
    def test_initialization(self):
        """测试匹配算法可以正常初始化"""
        matcher = MatchingAlgorithm()
        assert matcher is not None
        assert isinstance(matcher, MatchingAlgorithm)


class TestCalculateSimilarity:
    """测试相似度计算功能"""
    
    def setup_method(self):
        """设置测试环境"""
        self.matcher = MatchingAlgorithm()
    
    def test_identical_devices(self):
        """测试完全相同的设备"""
        device1 = {
            'device_id': '1',
            'device_type': 'CO2传感器',
            'brand': '西门子',
            'model': 'QAA2061',
            'key_params': {'量程': '0-2000ppm', '输出信号': '4-20mA'}
        }
        device2 = {
            'device_id': '2',
            'device_type': 'CO2传感器',
            'brand': '西门子',
            'model': 'QAA2061',
            'key_params': {'量程': '0-2000ppm', '输出信号': '4-20mA'}
        }
        
        score, features = self.matcher.calculate_similarity(device1, device2)
        
        # 应该匹配所有特征
        assert 'device_type' in features
        assert 'brand' in features
        assert 'model' in features
        assert 'key_params' in features
        
        # 验证各特征得分
        assert features['device_type'] == 30.0
        assert features['brand'] == 10.0
        assert features['model'] == 8.0
        assert features['key_params'] == 15.0  # 完全匹配
        
        # 总分应该是所有权重之和
        assert score == 63.0
    
    def test_different_device_types(self):
        """测试不同设备类型"""
        device1 = {
            'device_type': 'CO2传感器',
            'brand': '西门子',
            'model': 'QAA2061'
        }
        device2 = {
            'device_type': '座阀',
            'brand': '西门子',
            'model': 'QAA2061'
        }
        
        score, features = self.matcher.calculate_similarity(device1, device2)
        
        # 设备类型不匹配，不应该有device_type得分
        assert 'device_type' not in features
        
        # 但品牌和型号应该匹配
        assert 'brand' in features
        assert 'model' in features
        assert features['brand'] == 10.0
        assert features['model'] == 8.0
        
        assert score == 18.0
    
    def test_same_device_type_only(self):
        """测试只有设备类型相同"""
        device1 = {
            'device_type': 'CO2传感器',
            'brand': '西门子',
            'model': 'QAA2061'
        }
        device2 = {
            'device_type': 'CO2传感器',
            'brand': '霍尼韦尔',
            'model': 'ABC123'
        }
        
        score, features = self.matcher.calculate_similarity(device1, device2)
        
        # 只有设备类型匹配
        assert 'device_type' in features
        assert 'brand' not in features
        assert 'model' not in features
        
        assert features['device_type'] == 30.0
        assert score == 30.0
    
    def test_partial_key_params_match(self):
        """测试关键参数部分匹配"""
        device1 = {
            'device_type': 'CO2传感器',
            'brand': '西门子',
            'key_params': {'量程': '0-2000ppm', '输出信号': '4-20mA', '精度': '±50ppm'}
        }
        device2 = {
            'device_type': 'CO2传感器',
            'brand': '西门子',
            'key_params': {'量程': '0-2000ppm', '输出信号': '0-10V'}
        }
        
        score, features = self.matcher.calculate_similarity(device1, device2)
        
        # 设备类型和品牌匹配
        assert features['device_type'] == 30.0
        assert features['brand'] == 10.0
        
        # 关键参数部分匹配
        # device1有3个参数，device2有2个参数，共同参数2个（量程、输出信号）
        # 只有量程的值匹配（1个匹配）
        # 总共不同的参数键：3个（量程、输出信号、精度）
        # 匹配比例 = 1/3 = 0.333...
        # 得分 = 0.333... * 15.0 = 5.0
        assert 'key_params' in features
        assert features['key_params'] == pytest.approx(5.0)
        
        assert score == pytest.approx(45.0)
    
    def test_no_key_params(self):
        """测试没有关键参数"""
        device1 = {
            'device_type': 'CO2传感器',
            'brand': '西门子',
            'model': 'QAA2061'
        }
        device2 = {
            'device_type': 'CO2传感器',
            'brand': '西门子',
            'model': 'QAA2061'
        }
        
        score, features = self.matcher.calculate_similarity(device1, device2)
        
        # 没有关键参数，不应该有key_params得分
        assert 'key_params' not in features
        
        # 其他特征应该匹配
        assert features['device_type'] == 30.0
        assert features['brand'] == 10.0
        assert features['model'] == 8.0
        
        assert score == 48.0
    
    def test_empty_devices(self):
        """测试空设备"""
        device1 = {}
        device2 = {}
        
        score, features = self.matcher.calculate_similarity(device1, device2)
        
        # 没有任何匹配
        assert len(features) == 0
        assert score == 0.0
    
    def test_one_empty_device(self):
        """测试一个空设备"""
        device1 = {
            'device_type': 'CO2传感器',
            'brand': '西门子',
            'model': 'QAA2061'
        }
        device2 = {}
        
        score, features = self.matcher.calculate_similarity(device1, device2)
        
        # 没有任何匹配
        assert len(features) == 0
        assert score == 0.0
    
    def test_missing_fields(self):
        """测试缺少某些字段"""
        device1 = {
            'device_type': 'CO2传感器',
            'brand': '西门子'
            # 缺少model
        }
        device2 = {
            'device_type': 'CO2传感器',
            'model': 'QAA2061'
            # 缺少brand
        }
        
        score, features = self.matcher.calculate_similarity(device1, device2)
        
        # 只有设备类型匹配
        assert 'device_type' in features
        assert 'brand' not in features
        assert 'model' not in features
        
        assert features['device_type'] == 30.0
        assert score == 30.0
    
    def test_device_name_field(self):
        """测试使用device_name字段"""
        device1 = {
            'device_name': 'CO2传感器',
            'brand': '西门子'
        }
        device2 = {
            'device_name': 'CO2传感器',
            'brand': '西门子'
        }
        
        score, features = self.matcher.calculate_similarity(device1, device2)
        
        # 设备类型和品牌应该匹配
        assert 'device_type' in features
        assert 'brand' in features
        
        assert features['device_type'] == 30.0
        assert features['brand'] == 10.0
        assert score == 40.0
    
    def test_no_common_key_params(self):
        """测试没有共同的关键参数"""
        device1 = {
            'device_type': 'CO2传感器',
            'key_params': {'量程': '0-2000ppm'}
        }
        device2 = {
            'device_type': 'CO2传感器',
            'key_params': {'输出信号': '4-20mA'}
        }
        
        score, features = self.matcher.calculate_similarity(device1, device2)
        
        # 设备类型匹配
        assert features['device_type'] == 30.0
        
        # 没有共同参数，不应该有key_params得分
        assert 'key_params' not in features
        
        assert score == 30.0



class TestFindSimilarDevices:
    """测试相似设备查找功能"""
    
    def setup_method(self):
        """设置测试环境"""
        self.matcher = MatchingAlgorithm()
    
    def test_find_similar_devices_basic(self):
        """测试基本的相似设备查找"""
        target = {
            'device_id': 'target',
            'device_type': 'CO2传感器',
            'brand': '西门子',
            'model': 'QAA2061',
            'key_params': {'量程': '0-2000ppm', '输出信号': '4-20mA'}
        }
        
        candidates = [
            {
                'device_id': '1',
                'device_type': 'CO2传感器',
                'brand': '西门子',
                'model': 'QAA2061',
                'key_params': {'量程': '0-2000ppm', '输出信号': '4-20mA'}
            },
            {
                'device_id': '2',
                'device_type': 'CO2传感器',
                'brand': '霍尼韦尔',
                'model': 'ABC123',
                'key_params': {'量程': '0-2000ppm', '输出信号': '4-20mA'}
            },
            {
                'device_id': '3',
                'device_type': '座阀',  # 不同设备类型，应该被过滤掉
                'brand': '西门子',
                'model': 'VVF53'
            }
        ]
        
        results = self.matcher.find_similar_devices(target, candidates)
        
        # 应该只返回CO2传感器
        assert len(results) == 2
        assert all(r.device['device_type'] == 'CO2传感器' for r in results)
        
        # 验证结果按得分降序排列
        assert results[0].similarity_score >= results[1].similarity_score
        
        # 第一个结果应该是完全匹配的设备
        assert results[0].device_id == '1'
        assert results[0].similarity_score == 63.0
    
    def test_find_similar_devices_sorted_by_score(self):
        """测试结果按得分降序排列"""
        target = {
            'device_id': 'target',
            'device_type': 'CO2传感器',
            'brand': '西门子',
            'model': 'QAA2061'
        }
        
        candidates = [
            {
                'device_id': '1',
                'device_type': 'CO2传感器',
                'brand': '霍尼韦尔',
                'model': 'ABC123'
            },
            {
                'device_id': '2',
                'device_type': 'CO2传感器',
                'brand': '西门子',
                'model': 'QAA2061'
            },
            {
                'device_id': '3',
                'device_type': 'CO2传感器',
                'brand': '西门子',
                'model': 'ABC123'
            }
        ]
        
        results = self.matcher.find_similar_devices(target, candidates)
        
        assert len(results) == 3
        
        # 验证降序排列
        scores = [r.similarity_score for r in results]
        assert scores == sorted(scores, reverse=True)
        
        # 第一个应该是完全匹配的设备（设备类型+品牌+型号）
        assert results[0].device_id == '2'
        assert results[0].similarity_score == 48.0  # 30 + 10 + 8
        
        # 第二个应该是设备类型+品牌匹配
        assert results[1].device_id == '3'
        assert results[1].similarity_score == 40.0  # 30 + 10
        
        # 第三个应该是只有设备类型匹配
        assert results[2].device_id == '1'
        assert results[2].similarity_score == 30.0  # 30
    
    def test_find_similar_devices_limit(self):
        """测试返回结果数量限制"""
        target = {
            'device_id': 'target',
            'device_type': 'CO2传感器',
            'brand': '西门子'
        }
        
        # 创建30个候选设备
        candidates = [
            {
                'device_id': str(i),
                'device_type': 'CO2传感器',
                'brand': '西门子' if i % 2 == 0 else '霍尼韦尔'
            }
            for i in range(30)
        ]
        
        results = self.matcher.find_similar_devices(target, candidates, limit=20)
        
        # 应该最多返回20个结果
        assert len(results) <= 20
    
    def test_find_similar_devices_default_limit(self):
        """测试默认限制为20"""
        target = {
            'device_id': 'target',
            'device_type': 'CO2传感器',
            'brand': '西门子'
        }
        
        # 创建30个候选设备
        candidates = [
            {
                'device_id': str(i),
                'device_type': 'CO2传感器',
                'brand': '西门子'
            }
            for i in range(30)
        ]
        
        results = self.matcher.find_similar_devices(target, candidates)
        
        # 默认应该返回最多20个结果
        assert len(results) == 20
    
    def test_find_similar_devices_filters_by_device_type(self):
        """测试首先按设备类型过滤"""
        target = {
            'device_id': 'target',
            'device_type': 'CO2传感器',
            'brand': '西门子'
        }
        
        candidates = [
            {'device_id': '1', 'device_type': 'CO2传感器', 'brand': '西门子'},
            {'device_id': '2', 'device_type': '座阀', 'brand': '西门子'},
            {'device_id': '3', 'device_type': '温度传感器', 'brand': '西门子'},
            {'device_id': '4', 'device_type': 'CO2传感器', 'brand': '霍尼韦尔'},
        ]
        
        results = self.matcher.find_similar_devices(target, candidates)
        
        # 应该只返回CO2传感器
        assert len(results) == 2
        assert all(r.device['device_type'] == 'CO2传感器' for r in results)
    
    def test_find_similar_devices_includes_matched_features(self):
        """测试返回结果包含匹配特征详情"""
        target = {
            'device_id': 'target',
            'device_type': 'CO2传感器',
            'brand': '西门子',
            'model': 'QAA2061'
        }
        
        candidates = [
            {
                'device_id': '1',
                'device_type': 'CO2传感器',
                'brand': '西门子',
                'model': 'QAA2061'
            }
        ]
        
        results = self.matcher.find_similar_devices(target, candidates)
        
        assert len(results) == 1
        
        # 验证包含匹配特征详情
        assert 'device_type' in results[0].matched_features
        assert 'brand' in results[0].matched_features
        assert 'model' in results[0].matched_features
        
        # 验证特征得分
        assert results[0].matched_features['device_type'] == 30.0
        assert results[0].matched_features['brand'] == 10.0
        assert results[0].matched_features['model'] == 8.0
    
    def test_find_similar_devices_empty_candidates(self):
        """测试空候选列表"""
        target = {
            'device_id': 'target',
            'device_type': 'CO2传感器',
            'brand': '西门子'
        }
        
        results = self.matcher.find_similar_devices(target, [])
        
        assert len(results) == 0
    
    def test_find_similar_devices_no_matching_type(self):
        """测试没有匹配的设备类型"""
        target = {
            'device_id': 'target',
            'device_type': 'CO2传感器',
            'brand': '西门子'
        }
        
        candidates = [
            {'device_id': '1', 'device_type': '座阀', 'brand': '西门子'},
            {'device_id': '2', 'device_type': '温度传感器', 'brand': '西门子'},
        ]
        
        results = self.matcher.find_similar_devices(target, candidates)
        
        assert len(results) == 0
    
    def test_find_similar_devices_excludes_target(self):
        """测试排除目标设备本身"""
        target = {
            'device_id': 'target',
            'device_type': 'CO2传感器',
            'brand': '西门子'
        }
        
        candidates = [
            {'device_id': 'target', 'device_type': 'CO2传感器', 'brand': '西门子'},  # 目标设备本身
            {'device_id': '1', 'device_type': 'CO2传感器', 'brand': '西门子'},
            {'device_id': '2', 'device_type': 'CO2传感器', 'brand': '霍尼韦尔'},
        ]
        
        results = self.matcher.find_similar_devices(target, candidates)
        
        # 应该排除目标设备本身
        assert len(results) == 2
        assert all(r.device_id != 'target' for r in results)
    
    def test_find_similar_devices_custom_limit(self):
        """测试自定义限制数量"""
        target = {
            'device_id': 'target',
            'device_type': 'CO2传感器',
            'brand': '西门子'
        }
        
        candidates = [
            {
                'device_id': str(i),
                'device_type': 'CO2传感器',
                'brand': '西门子'
            }
            for i in range(15)
        ]
        
        results = self.matcher.find_similar_devices(target, candidates, limit=5)
        
        # 应该返回5个结果
        assert len(results) == 5
    
    def test_find_similar_devices_with_key_params(self):
        """测试包含关键参数的相似设备查找"""
        target = {
            'device_id': 'target',
            'device_type': 'CO2传感器',
            'brand': '西门子',
            'key_params': {'量程': '0-2000ppm', '输出信号': '4-20mA'}
        }
        
        candidates = [
            {
                'device_id': '1',
                'device_type': 'CO2传感器',
                'brand': '西门子',
                'key_params': {'量程': '0-2000ppm', '输出信号': '4-20mA'}
            },
            {
                'device_id': '2',
                'device_type': 'CO2传感器',
                'brand': '西门子',
                'key_params': {'量程': '0-2000ppm', '输出信号': '0-10V'}
            },
            {
                'device_id': '3',
                'device_type': 'CO2传感器',
                'brand': '西门子',
                'key_params': {}
            }
        ]
        
        results = self.matcher.find_similar_devices(target, candidates)
        
        assert len(results) == 3
        
        # 第一个应该是关键参数完全匹配的
        assert results[0].device_id == '1'
        assert 'key_params' in results[0].matched_features
        assert results[0].matched_features['key_params'] == 15.0
        
        # 第二个应该是关键参数部分匹配的
        assert results[1].device_id == '2'
        assert 'key_params' in results[1].matched_features
        
        # 第三个没有关键参数
        assert results[2].device_id == '3'
        assert 'key_params' not in results[2].matched_features
    
    def test_find_similar_devices_returns_match_result_objects(self):
        """测试返回MatchResult对象"""
        target = {
            'device_id': 'target',
            'device_type': 'CO2传感器',
            'brand': '西门子'
        }
        
        candidates = [
            {'device_id': '1', 'device_type': 'CO2传感器', 'brand': '西门子'}
        ]
        
        results = self.matcher.find_similar_devices(target, candidates)
        
        assert len(results) == 1
        assert isinstance(results[0], MatchResult)
        assert hasattr(results[0], 'device_id')
        assert hasattr(results[0], 'similarity_score')
        assert hasattr(results[0], 'matched_features')
        assert hasattr(results[0], 'device')
