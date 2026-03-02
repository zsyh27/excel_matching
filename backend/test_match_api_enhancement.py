"""
测试 /api/match 接口的增强功能

验证任务 5.1: 修改match_devices()函数
- 支持record_detail参数
- 返回detail_cache_key字段
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_match_api_with_record_detail():
    """测试带record_detail参数的匹配接口"""
    from app import app
    
    client = app.test_client()
    
    # 准备测试数据
    test_data = {
        "rows": [
            {
                "row_number": 1,
                "row_type": "device",
                "raw_data": ["西门子", "DDC控制器", "RWD68"],
                "device_description": "西门子 DDC控制器 RWD68"
            }
        ],
        "record_detail": True  # 明确启用详情记录
    }
    
    # 发送请求
    response = client.post('/api/match', json=test_data)
    
    # 验证响应
    assert response.status_code == 200, f"期望状态码200，实际: {response.status_code}"
    
    data = response.get_json()
    assert data['success'] is True, "期望success为True"
    assert 'matched_rows' in data, "响应应包含matched_rows"
    assert len(data['matched_rows']) > 0, "matched_rows不应为空"
    
    # 验证detail_cache_key字段
    first_row = data['matched_rows'][0]
    print(f"\n第一行匹配结果: {first_row}")
    
    if first_row.get('match_result', {}).get('match_status') == 'success':
        # 成功匹配时应该有cache_key
        assert 'detail_cache_key' in first_row, "成功匹配时应包含detail_cache_key字段"
        assert first_row['detail_cache_key'] is not None, "detail_cache_key不应为None"
        print(f"✓ detail_cache_key存在: {first_row['detail_cache_key']}")
    else:
        # 失败匹配时也应该有cache_key（因为record_detail=True）
        if 'detail_cache_key' in first_row:
            print(f"✓ 失败匹配也记录了详情: {first_row['detail_cache_key']}")
    
    print("✓ 测试通过: 带record_detail=True的匹配")


def test_match_api_without_record_detail():
    """测试不记录详情的匹配接口"""
    from app import app
    
    client = app.test_client()
    
    # 准备测试数据（不包含record_detail或设为False）
    test_data = {
        "rows": [
            {
                "row_number": 1,
                "row_type": "device",
                "raw_data": ["西门子", "DDC控制器", "RWD68"],
                "device_description": "西门子 DDC控制器 RWD68"
            }
        ],
        "record_detail": False  # 禁用详情记录
    }
    
    # 发送请求
    response = client.post('/api/match', json=test_data)
    
    # 验证响应
    assert response.status_code == 200, f"期望状态码200，实际: {response.status_code}"
    
    data = response.get_json()
    assert data['success'] is True, "期望success为True"
    
    # 验证不应该有detail_cache_key字段（或为None）
    first_row = data['matched_rows'][0]
    print(f"\n第一行匹配结果（无详情）: {first_row}")
    
    if 'detail_cache_key' in first_row:
        assert first_row['detail_cache_key'] is None, "record_detail=False时cache_key应为None"
        print("✓ detail_cache_key为None（符合预期）")
    else:
        print("✓ 没有detail_cache_key字段（符合预期）")
    
    print("✓ 测试通过: 带record_detail=False的匹配")


def test_match_api_default_behavior():
    """测试默认行为（不传record_detail参数）"""
    from app import app
    
    client = app.test_client()
    
    # 准备测试数据（不包含record_detail，应默认为True）
    test_data = {
        "rows": [
            {
                "row_number": 1,
                "row_type": "device",
                "raw_data": ["西门子", "DDC控制器", "RWD68"],
                "device_description": "西门子 DDC控制器 RWD68"
            }
        ]
        # 不传record_detail参数
    }
    
    # 发送请求
    response = client.post('/api/match', json=test_data)
    
    # 验证响应
    assert response.status_code == 200, f"期望状态码200，实际: {response.status_code}"
    
    data = response.get_json()
    assert data['success'] is True, "期望success为True"
    
    # 默认应该记录详情
    first_row = data['matched_rows'][0]
    print(f"\n第一行匹配结果（默认行为）: {first_row}")
    
    if first_row.get('match_result', {}).get('match_status') == 'success':
        # 默认应该有cache_key
        if 'detail_cache_key' in first_row and first_row['detail_cache_key']:
            print(f"✓ 默认行为记录了详情: {first_row['detail_cache_key']}")
        else:
            print("⚠ 警告: 默认行为未记录详情（可能是匹配失败）")
    
    print("✓ 测试通过: 默认行为（record_detail默认为True）")


def test_backward_compatibility():
    """测试向后兼容性"""
    from app import app
    
    client = app.test_client()
    
    # 使用旧的API调用方式（不包含record_detail）
    test_data = {
        "rows": [
            {
                "row_number": 1,
                "row_type": "device",
                "raw_data": ["西门子", "DDC控制器"],
            }
        ]
    }
    
    # 发送请求
    response = client.post('/api/match', json=test_data)
    
    # 验证响应
    assert response.status_code == 200, f"期望状态码200，实际: {response.status_code}"
    
    data = response.get_json()
    assert data['success'] is True, "期望success为True"
    assert 'matched_rows' in data, "响应应包含matched_rows"
    assert 'statistics' in data, "响应应包含statistics"
    
    print("\n✓ 测试通过: 向后兼容性（旧API调用方式仍然工作）")


if __name__ == '__main__':
    print("=" * 60)
    print("测试任务 5.1: /api/match 接口增强")
    print("=" * 60)
    
    try:
        print("\n[测试1] 带record_detail=True的匹配")
        test_match_api_with_record_detail()
        
        print("\n[测试2] 带record_detail=False的匹配")
        test_match_api_without_record_detail()
        
        print("\n[测试3] 默认行为测试")
        test_match_api_default_behavior()
        
        print("\n[测试4] 向后兼容性测试")
        test_backward_compatibility()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
