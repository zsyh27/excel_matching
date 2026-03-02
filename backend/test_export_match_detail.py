"""
测试匹配详情导出功能

验证 task 7.1 的实现
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.match_detail import MatchDetail, CandidateDetail, FeatureMatch
from datetime import datetime


def test_export_route_basic():
    """测试导出路由的基本功能"""
    print("测试 1: 验证导出路由函数存在")
    
    # 导入 app
    from app import app, export_match_detail
    
    # 验证路由函数存在
    assert export_match_detail is not None
    print("✓ export_match_detail 函数存在")
    
    # 验证路由已注册
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    export_route = '/api/match/detail/export/<cache_key>'
    
    found = False
    for route in routes:
        if 'export' in route and 'cache_key' in route:
            found = True
            print(f"✓ 找到导出路由: {route}")
            break
    
    assert found, "导出路由未正确注册"
    print("✓ 导出路由已正确注册")


def test_format_text_function():
    """测试文本格式化函数"""
    print("\n测试 2: 验证文本格式化函数")
    
    from app import _format_match_detail_as_text
    
    # 创建测试数据
    test_detail = MatchDetail(
        original_text="测试设备描述",
        preprocessing={
            'original': '测试设备描述',
            'cleaned': '测试设备描述',
            'normalized': '测试设备描述',
            'features': ['测试', '设备']
        },
        candidates=[
            CandidateDetail(
                rule_id='test_rule_1',
                target_device_id='test_device_1',
                device_info={
                    'brand': '测试品牌',
                    'device_name': '测试设备',
                    'spec_model': 'TEST-001',
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
                        contribution_percentage=58.8
                    )
                ],
                unmatched_features=['其他特征'],
                score_breakdown={'测试': 5.0},
                total_possible_score=10.0
            )
        ],
        final_result={
            'match_status': 'success',
            'device_id': 'test_device_1',
            'matched_device_text': '测试品牌 测试设备',
            'unit_price': 1000.0,
            'match_score': 8.5,
            'threshold': 5.0,
            'match_reason': '匹配成功'
        },
        selected_candidate_id='test_rule_1',
        decision_reason='测试决策原因',
        optimization_suggestions=['建议1', '建议2'],
        timestamp=datetime.now().isoformat(),
        match_duration_ms=50.0
    )
    
    # 调用格式化函数
    text_output = _format_match_detail_as_text(test_detail)
    
    # 验证输出包含关键信息
    assert '匹配详情报告' in text_output
    assert '测试设备描述' in text_output
    assert '测试品牌' in text_output
    assert '匹配状态: success' in text_output
    assert '决策原因' in text_output
    assert '优化建议' in text_output
    assert '建议1' in text_output
    
    print("✓ 文本格式化函数工作正常")
    print(f"✓ 生成的文本长度: {len(text_output)} 字符")


def test_export_with_mock_request():
    """测试导出功能（使用模拟请求）"""
    print("\n测试 3: 测试导出功能（模拟请求）")
    
    from app import app, match_engine
    from modules.match_detail import MatchDetail, CandidateDetail, FeatureMatch
    
    # 创建测试详情并添加到缓存
    test_detail = MatchDetail(
        original_text="测试导出功能",
        preprocessing={
            'original': '测试导出功能',
            'cleaned': '测试导出功能',
            'normalized': '测试导出功能',
            'features': ['测试', '导出']
        },
        candidates=[],
        final_result={
            'match_status': 'failed',
            'match_score': 0.0,
            'match_reason': '测试失败场景'
        },
        selected_candidate_id=None,
        decision_reason='测试决策',
        optimization_suggestions=['测试建议'],
        timestamp=datetime.now().isoformat(),
        match_duration_ms=10.0
    )
    
    # 手动添加到缓存
    test_cache_key = 'test_export_key_12345'
    match_engine.detail_recorder.cache[test_cache_key] = test_detail
    
    # 使用测试客户端
    with app.test_client() as client:
        # 测试 JSON 格式导出
        print("  测试 JSON 格式导出...")
        response = client.get(f'/api/match/detail/export/{test_cache_key}?format=json')
        assert response.status_code == 200
        assert response.mimetype == 'application/json'
        print("  ✓ JSON 格式导出成功")
        
        # 测试 TXT 格式导出
        print("  测试 TXT 格式导出...")
        response = client.get(f'/api/match/detail/export/{test_cache_key}?format=txt')
        assert response.status_code == 200
        assert 'text/plain' in response.mimetype
        print("  ✓ TXT 格式导出成功")
        
        # 测试默认格式（应该是 JSON）
        print("  测试默认格式...")
        response = client.get(f'/api/match/detail/export/{test_cache_key}')
        assert response.status_code == 200
        assert response.mimetype == 'application/json'
        print("  ✓ 默认格式导出成功（JSON）")
        
        # 测试不支持的格式
        print("  测试不支持的格式...")
        response = client.get(f'/api/match/detail/export/{test_cache_key}?format=xml')
        assert response.status_code == 400
        data = response.get_json()
        assert data['error_code'] == 'UNSUPPORTED_FORMAT'
        print("  ✓ 正确拒绝不支持的格式")
        
        # 测试不存在的缓存键
        print("  测试不存在的缓存键...")
        response = client.get('/api/match/detail/export/nonexistent_key?format=json')
        assert response.status_code == 404
        data = response.get_json()
        assert data['error_code'] == 'DETAIL_NOT_FOUND'
        print("  ✓ 正确处理不存在的缓存键")
    
    # 清理测试数据
    del match_engine.detail_recorder.cache[test_cache_key]
    
    print("✓ 所有导出功能测试通过")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("匹配详情导出功能测试")
    print("=" * 60)
    
    try:
        test_export_route_basic()
        test_format_text_function()
        test_export_with_mock_request()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        print("\n任务 7.1 实现验证成功：")
        print("  ✓ 创建了 /api/match/detail/export/<cache_key> 路由")
        print("  ✓ 支持 format 参数（json 和 txt）")
        print("  ✓ 从 match_engine.detail_recorder 获取匹配详情")
        print("  ✓ 生成对应格式的文件内容")
        print("  ✓ 返回文件下载响应")
        print("  ✓ 处理缓存键不存在、格式不支持等错误情况")
        
        return 0
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
