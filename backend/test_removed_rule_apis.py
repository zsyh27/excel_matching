#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试已移除的规则 API 端点

验证所有已移除的规则 API 端点返回 404
Property 1: 已移除的规则 API 端点返回 404
Validates: Requirements 4.1, 4.2, 4.3
"""

import requests
import sys
import io

# 设置标准输出为 UTF-8 编码（Windows 兼容）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 后端服务地址
BASE_URL = 'http://localhost:5000'

# 所有已移除的规则 API 端点
REMOVED_ENDPOINTS = [
    # 任务 5.1: 规则基础 CRUD API
    ('GET', '/api/rules'),
    ('GET', '/api/rules/test_rule_id'),
    ('POST', '/api/rules'),
    ('PUT', '/api/rules/test_rule_id'),
    ('DELETE', '/api/rules/test_rule_id'),
    
    # 任务 5.2: 规则生成和重新生成 API
    ('POST', '/api/rules/generate'),
    ('POST', '/api/rules/regenerate'),
    ('GET', '/api/rules/regenerate/status'),
    
    # 任务 5.3: DEPRECATED 规则管理 API
    ('GET', '/api/rules/management/test_rule_id'),
    ('PUT', '/api/rules/management/test_rule_id'),
    ('GET', '/api/rules/management/list'),
    ('GET', '/api/rules/management/statistics'),
    ('GET', '/api/rules/management/logs'),
    ('POST', '/api/rules/management/test'),
    
    # 任务 5.4: 设备规则相关 API
    ('PUT', '/api/devices/test_device_id/rule'),
    ('POST', '/api/devices/test_device_id/rule/regenerate'),
]

def test_removed_endpoints():
    """测试所有已移除的端点是否返回 404"""
    print("=" * 80)
    print("测试已移除的规则 API 端点")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    errors = []
    
    for method, endpoint in REMOVED_ENDPOINTS:
        url = f"{BASE_URL}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=5)
            elif method == 'POST':
                response = requests.post(url, json={}, timeout=5)
            elif method == 'PUT':
                response = requests.put(url, json={}, timeout=5)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=5)
            else:
                print(f"✗ {method} {endpoint} - 不支持的方法")
                failed += 1
                continue
            
            if response.status_code == 404:
                print(f"✓ {method} {endpoint} - 正确返回 404")
                passed += 1
            else:
                print(f"✗ {method} {endpoint} - 返回 {response.status_code} (期望 404)")
                failed += 1
                errors.append(f"{method} {endpoint}: 返回 {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            print(f"✗ {method} {endpoint} - 无法连接到服务器")
            print("   提示: 请确保后端服务正在运行 (python backend/app.py)")
            failed += 1
            errors.append(f"{method} {endpoint}: 连接失败")
        
        except Exception as e:
            print(f"✗ {method} {endpoint} - 错误: {e}")
            failed += 1
            errors.append(f"{method} {endpoint}: {str(e)}")
    
    # 输出测试结果
    print()
    print("=" * 80)
    print("测试结果")
    print("=" * 80)
    print(f"总计: {passed + failed} 个端点")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    
    if errors:
        print()
        print("失败详情:")
        for error in errors:
            print(f"  - {error}")
    
    print()
    
    if failed == 0:
        print("✅ 所有测试通过! 所有已移除的规则 API 端点正确返回 404")
        return 0
    else:
        print(f"❌ {failed} 个测试失败")
        return 1

if __name__ == '__main__':
    sys.exit(test_removed_endpoints())
