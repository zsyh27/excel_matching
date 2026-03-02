"""
测试匹配详情API接口

验证需求: Requirements 1.2, 1.3, 6.5
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, match_engine
from modules.match_detail import MatchDetail, CandidateDetail, FeatureMatch
import json


def test_get_match_detail_success():
    """测试成功获取匹配详情"""
    print("\n=== 测试1: 成功获取匹配详情 ===")
    
    # 创建测试数据
    test_detail = MatchDetail(
        original_text="测试设备描述",
        preprocessing={
            'original': '测试设备描述',
            'cleaned': '测试设备描述',
            'normalized': '测试设备描述',
            'features': ['测试', '设备']
        },
        candidates=[],
        final_result={
            'match_status': 'success',
            'device_id': 'TEST001',
            'matched_device_text': '测试设备',
            'match_score': 10.0
        },
        selected_candidate_id='TEST001',
        decision_reason='测试决策原因',
        optimization_suggestions=['测试建议'],
        timestamp='2024-01-01T00:00:00',
        match_duration_ms=100.0
    )
    
    # 手动添加到缓存
    test_cache_key = 'test-cache-key-123'
    match_engine.detail_recorder.cache[test_cache_key] = test_detail
    
    # 测试API
    with app.test_client() as client:
        response = client.get(f'/api/match/detail/{test_cache_key}')
        
        assert response.status_code == 200, f"期望状态码200，实际: {response.status_code}"
        
        data = json.loads(response.data)
        assert data['success'] is True, "期望success为True"
        assert 'detail' in data, "响应应包含detail字段"
        
        detail = data['detail']
        assert detail['original_text'] == '测试设备描述', "原始文本不匹配"
        assert detail['decision_reason'] == '测试决策原因', "决策原因不匹配"
        assert len(detail['optimization_suggestions']) == 1, "优化建议数量不匹配"
        
        print("✓ 成功获取匹配详情")
        print(f"  - 原始文本: {detail['original_text']}")
        print(f"  - 决策原因: {detail['decision_reason']}")
        print(f"  - 优化建议: {detail['optimization_suggestions']}")


def test_get_match_detail_not_found():
    """测试缓存键不存在的情况"""
    print("\n=== 测试2: 缓存键不存在 ===")
    
    with app.test_client() as client:
        response = client.get('/api/match/detail/non-existent-key')
        
        assert response.status_code == 404, f"期望状态码404，实际: {response.status_code}"
        
        data = json.loads(response.data)
        assert data['success'] is False, "期望success为False"
        assert data['error_code'] == 'DETAIL_NOT_FOUND', "错误码不匹配"
        assert '不存在或已过期' in data['error_message'], "错误消息不匹配"
        
        print("✓ 正确处理缓存键不存在的情况")
        print(f"  - 错误码: {data['error_code']}")
        print(f"  - 错误消息: {data['error_message']}")


def test_get_match_detail_with_candidates():
    """测试包含候选规则的匹配详情"""
    print("\n=== 测试3: 包含候选规则的匹配详情 ===")
    
    # 创建候选规则
    candidate = CandidateDetail(
        rule_id='RULE001',
        target_device_id='DEV001',
        device_info={
            'device_id': 'DEV001',
            'brand': '测试品牌',
            'device_name': '测试设备',
            'spec_model': 'TEST-MODEL',
            'unit_price': 1000.0
        },
        weight_score=8.5,
        match_threshold=5.0,
        threshold_type='rule',
        is_qualified=True,
        matched_features=[
            FeatureMatch(
                feature='测试',
                weight=5.0,
                feature_type='brand',
                contribution_percentage=58.82
            ),
            FeatureMatch(
                feature='设备',
                weight=3.5,
                feature_type='device_type',
                contribution_percentage=41.18
            )
        ],
        unmatched_features=['参数1', '参数2'],
        score_breakdown={'测试': 5.0, '设备': 3.5},
        total_possible_score=10.0
    )
    
    test_detail = MatchDetail(
        original_text="测试设备描述",
        preprocessing={
            'original': '测试设备描述',
            'cleaned': '测试设备描述',
            'normalized': '测试设备描述',
            'features': ['测试', '设备']
        },
        candidates=[candidate],
        final_result={
            'match_status': 'success',
            'device_id': 'DEV001',
            'matched_device_text': '测试品牌 测试设备',
            'match_score': 8.5,
            'threshold': 5.0
        },
        selected_candidate_id='RULE001',
        decision_reason='匹配成功：设备得分8.5超过阈值5.0',
        optimization_suggestions=[],
        timestamp='2024-01-01T00:00:00',
        match_duration_ms=150.0
    )
    
    # 添加到缓存
    test_cache_key = 'test-cache-key-with-candidates'
    match_engine.detail_recorder.cache[test_cache_key] = test_detail
    
    # 测试API
    with app.test_client() as client:
        response = client.get(f'/api/match/detail/{test_cache_key}')
        
        assert response.status_code == 200, f"期望状态码200，实际: {response.status_code}"
        
        data = json.loads(response.data)
        assert data['success'] is True, "期望success为True"
        
        detail = data['detail']
        assert len(detail['candidates']) == 1, "候选规则数量不匹配"
        
        candidate_data = detail['candidates'][0]
        assert candidate_data['rule_id'] == 'RULE001', "规则ID不匹配"
        assert candidate_data['weight_score'] == 8.5, "权重得分不匹配"
        assert candidate_data['is_qualified'] is True, "合格标志不匹配"
        assert len(candidate_data['matched_features']) == 2, "匹配特征数量不匹配"
        assert len(candidate_data['unmatched_features']) == 2, "未匹配特征数量不匹配"
        
        print("✓ 成功获取包含候选规则的匹配详情")
        print(f"  - 候选规则数: {len(detail['candidates'])}")
        print(f"  - 规则ID: {candidate_data['rule_id']}")
        print(f"  - 权重得分: {candidate_data['weight_score']}")
        print(f"  - 匹配特征数: {len(candidate_data['matched_features'])}")
        print(f"  - 未匹配特征数: {len(candidate_data['unmatched_features'])}")


def test_response_structure():
    """测试响应数据结构的完整性"""
    print("\n=== 测试4: 响应数据结构完整性 ===")
    
    # 创建完整的测试数据
    test_detail = MatchDetail(
        original_text="完整测试",
        preprocessing={
            'original': '完整测试',
            'cleaned': '完整测试',
            'normalized': '完整测试',
            'features': ['完整', '测试']
        },
        candidates=[],
        final_result={
            'match_status': 'failed',
            'device_id': None,
            'matched_device_text': None,
            'match_score': 0.0
        },
        selected_candidate_id=None,
        decision_reason='匹配失败：未找到候选规则',
        optimization_suggestions=['建议1', '建议2', '建议3'],
        timestamp='2024-01-01T12:00:00',
        match_duration_ms=200.5
    )
    
    test_cache_key = 'test-structure-key'
    match_engine.detail_recorder.cache[test_cache_key] = test_detail
    
    with app.test_client() as client:
        response = client.get(f'/api/match/detail/{test_cache_key}')
        data = json.loads(response.data)
        detail = data['detail']
        
        # 验证所有必需字段
        required_fields = [
            'original_text', 'preprocessing', 'candidates', 'final_result',
            'selected_candidate_id', 'decision_reason', 'optimization_suggestions',
            'timestamp', 'match_duration_ms'
        ]
        
        for field in required_fields:
            assert field in detail, f"缺少必需字段: {field}"
        
        # 验证preprocessing结构
        preprocessing_fields = ['original', 'cleaned', 'normalized', 'features']
        for field in preprocessing_fields:
            assert field in detail['preprocessing'], f"preprocessing缺少字段: {field}"
        
        # 验证final_result结构
        assert 'match_status' in detail['final_result'], "final_result缺少match_status"
        
        print("✓ 响应数据结构完整")
        print(f"  - 包含所有必需字段: {', '.join(required_fields)}")
        print(f"  - preprocessing字段完整")
        print(f"  - final_result字段完整")


if __name__ == '__main__':
    print("开始测试匹配详情API接口...")
    
    try:
        test_get_match_detail_success()
        test_get_match_detail_not_found()
        test_get_match_detail_with_candidates()
        test_response_structure()
        
        print("\n" + "="*50)
        print("✓ 所有测试通过！")
        print("="*50)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
