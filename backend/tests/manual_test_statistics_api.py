# -*- coding: utf-8 -*-
"""
手动测试统计API

简单的脚本来验证统计API端点是否正常工作
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_statistics_match_logs():
    """测试匹配日志API"""
    print("\n=== 测试 GET /api/statistics/match-logs ===")
    response = requests.get(f"{BASE_URL}/api/statistics/match-logs")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    assert response.status_code == 200
    assert response.json()['success'] is True
    print("✓ 匹配日志API测试通过")


def test_statistics_rules():
    """测试规则统计API"""
    print("\n=== 测试 GET /api/statistics/rules ===")
    response = requests.get(f"{BASE_URL}/api/statistics/rules")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    assert response.status_code == 200
    assert data['success'] is True
    assert 'statistics' in data
    print("✓ 规则统计API测试通过")


def test_statistics_match_success_rate():
    """测试匹配成功率API"""
    print("\n=== 测试 GET /api/statistics/match-success-rate ===")
    response = requests.get(f"{BASE_URL}/api/statistics/match-success-rate")
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    assert response.status_code == 200
    assert data['success'] is True
    assert 'trend' in data
    assert 'overall' in data
    print("✓ 匹配成功率API测试通过")


def test_backward_compatibility():
    """测试向后兼容性 - 旧API仍然可用"""
    print("\n=== 测试向后兼容性 ===")
    
    # 测试旧的规则统计API
    print("测试旧API: /api/rules/management/statistics")
    response = requests.get(f"{BASE_URL}/api/rules/management/statistics")
    print(f"状态码: {response.status_code}")
    assert response.status_code == 200
    print("✓ 旧规则统计API仍然可用")
    
    # 测试旧的匹配日志API
    print("测试旧API: /api/rules/management/logs")
    response = requests.get(f"{BASE_URL}/api/rules/management/logs")
    print(f"状态码: {response.status_code}")
    assert response.status_code == 200
    print("✓ 旧匹配日志API仍然可用")


def test_with_filters():
    """测试带筛选参数的API"""
    print("\n=== 测试带筛选参数的API ===")
    
    # 测试分页
    print("测试分页参数")
    response = requests.get(f"{BASE_URL}/api/statistics/match-logs?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data['page'] == 1
    assert data['page_size'] == 10
    print("✓ 分页参数测试通过")
    
    # 测试状态筛选
    print("测试状态筛选")
    response = requests.get(f"{BASE_URL}/api/statistics/match-logs?status=success")
    assert response.status_code == 200
    print("✓ 状态筛选测试通过")
    
    # 测试日期范围
    print("测试日期范围筛选")
    response = requests.get(f"{BASE_URL}/api/statistics/match-success-rate?start_date=2024-01-01&end_date=2024-12-31")
    assert response.status_code == 200
    print("✓ 日期范围筛选测试通过")


if __name__ == '__main__':
    print("=" * 60)
    print("统计API手动测试")
    print("=" * 60)
    print("\n注意: 请确保后端服务器正在运行 (python backend/app.py)")
    print("如果服务器未运行，测试将失败\n")
    
    try:
        # 检查服务器是否运行
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if response.status_code != 200:
            print("❌ 服务器未正常运行")
            exit(1)
        print("✓ 服务器正在运行\n")
        
        # 运行测试
        test_statistics_match_logs()
        test_statistics_rules()
        test_statistics_match_success_rate()
        test_backward_compatibility()
        test_with_filters()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
        print("请确保后端服务器正在运行: python backend/app.py")
        exit(1)
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
