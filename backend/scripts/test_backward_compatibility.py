#!/usr/bin/env python3
"""
向后兼容性测试脚本 - 规则管理重构
测试旧API端点仍然可用，URL重定向正常工作
"""

import sys
import os
import requests
import json
from typing import Dict, List

# 测试配置
BASE_URL = "http://localhost:5000"
TEST_RESULTS = []


def test_deprecated_api(endpoint: str, method: str = 'GET', data: Dict = None) -> Dict:
    """测试已弃用的API端点"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=5)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=5)
        else:
            return {
                'endpoint': endpoint,
                'method': method,
                'status': 'ERROR',
                'message': f'不支持的HTTP方法: {method}'
            }
        
        # 检查是否有deprecation警告
        deprecation_header = response.headers.get('Deprecation') or response.headers.get('X-Deprecated')
        
        result = {
            'endpoint': endpoint,
            'method': method,
            'status_code': response.status_code,
            'status': 'PASS' if response.status_code < 500 else 'FAIL',
            'deprecated': deprecation_header is not None,
            'deprecation_header': deprecation_header
        }
        
        # 如果响应是JSON，尝试解析
        try:
            result['response'] = response.json()
        except:
            result['response'] = response.text[:200]
        
        return result
        
    except requests.exceptions.ConnectionError:
        return {
            'endpoint': endpoint,
            'method': method,
            'status': 'ERROR',
            'message': '无法连接到服务器，请确保Flask应用正在运行'
        }
    except Exception as e:
        return {
            'endpoint': endpoint,
            'method': method,
            'status': 'ERROR',
            'message': str(e)
        }


def test_url_redirects():
    """测试URL重定向"""
    print("\n" + "=" * 60)
    print("测试URL重定向")
    print("=" * 60)
    
    # 注意：这些测试需要前端应用运行
    # 这里我们只测试API端点的可用性
    
    redirects = [
        {
            'name': '规则管理页面重定向',
            'old_url': '/rule-management',
            'expected_redirect': '/device-management',
            'note': '需要前端路由测试'
        },
        {
            'name': '匹配日志重定向',
            'old_url': '/rule-management/logs',
            'expected_redirect': '/statistics?tab=logs',
            'note': '需要前端路由测试'
        },
        {
            'name': '规则统计重定向',
            'old_url': '/rule-management/statistics',
            'expected_redirect': '/statistics?tab=rules',
            'note': '需要前端路由测试'
        }
    ]
    
    print("\n前端URL重定向（需要手动测试）:")
    for redirect in redirects:
        print(f"  • {redirect['name']}")
        print(f"    旧URL: {redirect['old_url']}")
        print(f"    新URL: {redirect['expected_redirect']}")
        print(f"    说明: {redirect['note']}")
    
    return True


def test_deprecated_apis():
    """测试已弃用的API端点"""
    print("\n" + "=" * 60)
    print("测试已弃用的API端点")
    print("=" * 60)
    
    # 定义需要测试的已弃用API
    deprecated_apis = [
        {
            'name': '获取规则列表',
            'endpoint': '/api/rules/management/list',
            'method': 'GET'
        },
        {
            'name': '获取规则统计',
            'endpoint': '/api/rules/management/statistics',
            'method': 'GET'
        },
        {
            'name': '获取匹配日志',
            'endpoint': '/api/rules/management/logs',
            'method': 'GET'
        }
    ]
    
    results = []
    
    for api in deprecated_apis:
        print(f"\n测试: {api['name']}")
        print(f"  端点: {api['endpoint']}")
        
        result = test_deprecated_api(api['endpoint'], api['method'])
        results.append(result)
        
        if result['status'] == 'ERROR':
            print(f"  ❌ 错误: {result.get('message', '未知错误')}")
        elif result['status'] == 'FAIL':
            print(f"  ❌ 失败: HTTP {result['status_code']}")
        else:
            print(f"  ✅ 通过: HTTP {result['status_code']}")
            if result.get('deprecated'):
                print(f"  ℹ️  已标记为弃用: {result['deprecation_header']}")
            else:
                print(f"  ⚠️  警告: 未标记为弃用")
    
    return results


def test_new_apis():
    """测试新的API端点"""
    print("\n" + "=" * 60)
    print("测试新的API端点")
    print("=" * 60)
    
    # 定义需要测试的新API
    new_apis = [
        {
            'name': '获取设备列表（含规则摘要）',
            'endpoint': '/api/devices',
            'method': 'GET'
        },
        {
            'name': '获取规则统计（新位置）',
            'endpoint': '/api/statistics/rules',
            'method': 'GET'
        },
        {
            'name': '获取匹配日志（新位置）',
            'endpoint': '/api/statistics/match-logs',
            'method': 'GET'
        }
    ]
    
    results = []
    
    for api in new_apis:
        print(f"\n测试: {api['name']}")
        print(f"  端点: {api['endpoint']}")
        
        result = test_deprecated_api(api['endpoint'], api['method'])
        results.append(result)
        
        if result['status'] == 'ERROR':
            print(f"  ❌ 错误: {result.get('message', '未知错误')}")
        elif result['status'] == 'FAIL':
            print(f"  ❌ 失败: HTTP {result['status_code']}")
        else:
            print(f"  ✅ 通过: HTTP {result['status_code']}")
    
    return results


def test_data_compatibility():
    """测试数据兼容性"""
    print("\n" + "=" * 60)
    print("测试数据兼容性")
    print("=" * 60)
    
    print("\n测试: 现有规则数据可正常读取")
    
    # 测试获取设备列表
    result = test_deprecated_api('/api/devices', 'GET')
    
    if result['status'] == 'ERROR':
        print(f"  ❌ 错误: {result.get('message', '未知错误')}")
        return False
    
    if result['status_code'] == 200:
        response_data = result.get('response', {})
        if isinstance(response_data, dict) and 'devices' in response_data:
            devices = response_data['devices']
            print(f"  ✅ 成功读取 {len(devices)} 个设备")
            
            # 检查是否包含规则摘要
            if devices and 'rule_summary' in devices[0]:
                print(f"  ✅ 设备数据包含规则摘要")
            else:
                print(f"  ⚠️  设备数据不包含规则摘要")
            
            return True
        else:
            print(f"  ❌ 响应格式不正确")
            return False
    else:
        print(f"  ❌ HTTP {result['status_code']}")
        return False


def generate_report(deprecated_results: List[Dict], new_results: List[Dict]):
    """生成测试报告"""
    print("\n" + "=" * 60)
    print("向后兼容性测试报告")
    print("=" * 60)
    
    # 统计结果
    deprecated_pass = sum(1 for r in deprecated_results if r['status'] == 'PASS')
    deprecated_fail = sum(1 for r in deprecated_results if r['status'] == 'FAIL')
    deprecated_error = sum(1 for r in deprecated_results if r['status'] == 'ERROR')
    
    new_pass = sum(1 for r in new_results if r['status'] == 'PASS')
    new_fail = sum(1 for r in new_results if r['status'] == 'FAIL')
    new_error = sum(1 for r in new_results if r['status'] == 'ERROR')
    
    print(f"\n已弃用API测试结果:")
    print(f"  通过: {deprecated_pass}/{len(deprecated_results)}")
    print(f"  失败: {deprecated_fail}/{len(deprecated_results)}")
    print(f"  错误: {deprecated_error}/{len(deprecated_results)}")
    
    print(f"\n新API测试结果:")
    print(f"  通过: {new_pass}/{len(new_results)}")
    print(f"  失败: {new_fail}/{len(new_results)}")
    print(f"  错误: {new_error}/{len(new_results)}")
    
    # 总体评估
    print(f"\n总体评估:")
    if deprecated_error > 0 or new_error > 0:
        print("  ⚠️  无法连接到服务器，请确保Flask应用正在运行")
        print("  运行命令: cd backend && python app.py")
    elif deprecated_fail > 0 or new_fail > 0:
        print("  ❌ 部分API测试失败，需要修复")
    else:
        print("  ✅ 所有API测试通过")
    
    print("\n" + "=" * 60)
    
    # 保存详细报告
    report = {
        'deprecated_apis': deprecated_results,
        'new_apis': new_results,
        'summary': {
            'deprecated': {
                'total': len(deprecated_results),
                'pass': deprecated_pass,
                'fail': deprecated_fail,
                'error': deprecated_error
            },
            'new': {
                'total': len(new_results),
                'pass': new_pass,
                'fail': new_fail,
                'error': new_error
            }
        }
    }
    
    report_file = 'backward_compatibility_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"详细报告已保存到: {report_file}")


def main():
    """主函数"""
    print("=" * 60)
    print("规则管理重构 - 向后兼容性测试")
    print("=" * 60)
    print(f"测试服务器: {BASE_URL}")
    print()
    
    # 1. 测试URL重定向
    test_url_redirects()
    
    # 2. 测试已弃用的API
    deprecated_results = test_deprecated_apis()
    
    # 3. 测试新的API
    new_results = test_new_apis()
    
    # 4. 测试数据兼容性
    test_data_compatibility()
    
    # 5. 生成报告
    generate_report(deprecated_results, new_results)
    
    # 返回退出码
    has_errors = any(r['status'] == 'ERROR' for r in deprecated_results + new_results)
    if has_errors:
        print("\n提示: 请先启动Flask应用，然后重新运行此测试")
        print("命令: cd backend && python app.py")
        sys.exit(2)  # 服务器未运行
    
    has_failures = any(r['status'] == 'FAIL' for r in deprecated_results + new_results)
    if has_failures:
        sys.exit(1)  # 测试失败
    
    sys.exit(0)  # 测试通过


if __name__ == '__main__':
    main()
