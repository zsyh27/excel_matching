#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试统计API端点是否正常工作
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoint(endpoint, description):
    """测试单个端点"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n测试: {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
            return True
        else:
            print(f"错误响应: {response.text[:200]}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务器，请确保后端正在运行")
        return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


def main():
    print("=" * 60)
    print("统计API端点测试")
    print("=" * 60)
    
    endpoints = [
        ("/api/database/statistics", "数据库统计"),
        ("/api/database/statistics/brands", "品牌分布"),
        ("/api/database/statistics/prices", "价格分布"),
        ("/api/database/statistics/recent", "最近设备"),
        ("/api/database/statistics/without-rules", "无规则设备"),
        ("/api/statistics/match-logs", "匹配日志"),
        ("/api/statistics/rules", "规则统计"),
        ("/api/statistics/match-success-rate", "匹配成功率"),
    ]
    
    results = []
    for endpoint, description in endpoints:
        success = test_endpoint(endpoint, description)
        results.append((endpoint, success))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for endpoint, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {endpoint}")
    
    success_count = sum(1 for _, success in results if success)
    print(f"\n成功: {success_count}/{len(results)}")


if __name__ == '__main__':
    main()
