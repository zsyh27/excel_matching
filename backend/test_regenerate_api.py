#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试规则重新生成API
"""

import requests
import json

def test_regenerate_rules_api():
    """测试规则重新生成API"""
    
    print("=" * 80)
    print("测试规则重新生成API")
    print("=" * 80)
    
    # 1. 先获取当前配置
    print("\n步骤1: 获取当前配置")
    response = requests.get('http://localhost:5000/api/config')
    
    if response.status_code != 200:
        print(f"  ✗ 获取配置失败: {response.status_code}")
        print(f"  响应: {response.text}")
        return False
    
    response_data = response.json()
    print(f"  响应结构: {list(response_data.keys())}")
    
    # 检查响应格式
    if 'data' in response_data:
        config = response_data['data']
    elif 'config' in response_data:
        config = response_data['config']
    else:
        # 可能整个响应就是配置
        config = response_data
    
    print(f"  ✓ 配置获取成功")
    
    # 2. 调用规则重新生成API
    print("\n步骤2: 调用规则重新生成API")
    response = requests.post(
        'http://localhost:5000/api/rules/regenerate',
        json={'config': config},
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"  状态码: {response.status_code}")
    print(f"  响应: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            data = result.get('data', {})
            print(f"\n  ✓ 规则重新生成成功!")
            print(f"  总设备数: {data.get('total')}")
            print(f"  成功生成: {data.get('generated')}")
            print(f"  生成失败: {data.get('failed')}")
            return True
        else:
            print(f"  ✗ 规则重新生成失败: {result.get('message')}")
            return False
    else:
        print(f"  ✗ API调用失败")
        return False

if __name__ == '__main__':
    try:
        success = test_regenerate_rules_api()
        
        if success:
            print("\n" + "=" * 80)
            print("✓ 测试通过!")
            print("=" * 80)
        else:
            print("\n" + "=" * 80)
            print("✗ 测试失败!")
            print("=" * 80)
    
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
