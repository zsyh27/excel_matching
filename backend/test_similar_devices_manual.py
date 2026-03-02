#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手动测试相似设备查询API端点

使用方法：
1. 启动后端服务器：python backend/app.py
2. 运行此脚本：python backend/test_similar_devices_manual.py
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:5000"


def test_similar_devices_api():
    """测试相似设备查询API"""
    
    print("=" * 80)
    print("测试相似设备查询API端点")
    print("=" * 80)
    print()
    
    # 测试1: 查询存在的设备的相似设备
    print("测试1: 查询存在的设备的相似设备")
    print("-" * 80)
    
    # 注意：这里使用的设备ID需要在数据库中存在
    # 如果使用JSON模式，设备ID应该在data/devices.json中
    # 如果使用数据库模式，设备ID应该在数据库的devices表中
    device_id = "DEVICE001"  # 替换为实际存在的设备ID
    
    try:
        response = requests.get(f"{BASE_URL}/api/devices/{device_id}/similar")
        print(f"请求URL: {response.url}")
        print(f"状态码: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("响应数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            print()
            
            if data.get('success'):
                similar_devices = data.get('data', [])
                print(f"✓ 找到 {len(similar_devices)} 个相似设备")
                
                # 显示前3个相似设备
                for i, device in enumerate(similar_devices[:3], 1):
                    print(f"\n相似设备 #{i}:")
                    print(f"  设备ID: {device['device_id']}")
                    print(f"  相似度得分: {device['similarity_score']:.2f}")
                    print(f"  品牌: {device['device']['brand']}")
                    print(f"  设备类型: {device['device']['device_type']}")
                    print(f"  匹配特征: {device['matched_features']}")
            else:
                print(f"✗ 查询失败: {data.get('error_message')}")
        else:
            print(f"✗ 请求失败，状态码: {response.status_code}")
            print(f"响应: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器，请确保后端服务器正在运行")
        print("  启动命令: python backend/app.py")
    except Exception as e:
        print(f"✗ 测试失败: {e}")
    
    print()
    print("-" * 80)
    
    # 测试2: 使用limit参数
    print("\n测试2: 使用limit参数限制返回数量")
    print("-" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/devices/{device_id}/similar?limit=5")
        print(f"请求URL: {response.url}")
        print(f"状态码: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                similar_devices = data.get('data', [])
                print(f"✓ 返回 {len(similar_devices)} 个相似设备（限制为5个）")
                assert len(similar_devices) <= 5, "返回数量超过limit"
            else:
                print(f"✗ 查询失败: {data.get('error_message')}")
        else:
            print(f"✗ 请求失败，状态码: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器")
    except Exception as e:
        print(f"✗ 测试失败: {e}")
    
    print()
    print("-" * 80)
    
    # 测试3: 查询不存在的设备
    print("\n测试3: 查询不存在的设备")
    print("-" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/devices/NONEXISTENT_DEVICE/similar")
        print(f"请求URL: {response.url}")
        print(f"状态码: {response.status_code}")
        print()
        
        if response.status_code == 400:
            data = response.json()
            print("✓ 正确返回400错误")
            print(f"  错误码: {data.get('error_code')}")
            print(f"  错误信息: {data.get('error_message')}")
        else:
            print(f"✗ 预期状态码400，实际: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器")
    except Exception as e:
        print(f"✗ 测试失败: {e}")
    
    print()
    print("-" * 80)
    
    # 测试4: 无效的limit参数
    print("\n测试4: 无效的limit参数")
    print("-" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/devices/{device_id}/similar?limit=0")
        print(f"请求URL: {response.url}")
        print(f"状态码: {response.status_code}")
        print()
        
        if response.status_code == 400:
            data = response.json()
            print("✓ 正确返回400错误")
            print(f"  错误码: {data.get('error_code')}")
            print(f"  错误信息: {data.get('error_message')}")
        else:
            print(f"✗ 预期状态码400，实际: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器")
    except Exception as e:
        print(f"✗ 测试失败: {e}")
    
    print()
    print("=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == '__main__':
    test_similar_devices_api()
