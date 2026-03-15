#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证新智能提取匹配系统功能

任务 9.1-9.3: 验证新系统功能完整性
- 验证智能提取匹配 API 正常
- 验证 Excel 批量匹配正常
- 验证五步流程预览正常
- 验证设备管理功能正常
"""

import requests
import sys
import io

# 设置标准输出为 UTF-8 编码（Windows 兼容）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 后端服务地址
BASE_URL = 'http://localhost:5000'

def test_intelligent_extraction_match():
    """测试智能提取匹配 API"""
    print("测试 1: 智能提取匹配 API (POST /api/intelligent-extraction/match)")
    
    test_text = "CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/intelligent-extraction/match",
            json={"text": test_text, "top_k": 5},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                candidates = data.get('data', {}).get('candidates', [])
                print(f"  ✓ API 正常响应，返回 {len(candidates)} 个候选设备")
                return True
            else:
                print(f"  ✗ API 返回失败: {data.get('error', {}).get('message', '未知错误')}")
                return False
        else:
            print(f"  ✗ HTTP {response.status_code}")
            return False
    
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        return False

def test_excel_batch_match():
    """测试 Excel 批量匹配 API"""
    print("\n测试 2: Excel 批量匹配 API (POST /api/match)")
    
    test_rows = [
        {
            "row_number": 1,
            "row_type": "device",
            "raw_data": ["霍尼韦尔", "温度传感器", "HST-RA"],
            "device_description": "霍尼韦尔 | 温度传感器 | HST-RA"
        }
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/match",
            json={"rows": test_rows, "record_detail": True},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                matched_rows = data.get('matched_rows', [])
                if matched_rows:
                    candidates = matched_rows[0].get('candidates', [])
                    print(f"  ✓ API 正常响应，返回 {len(candidates)} 个候选设备")
                    return True
                else:
                    print("  ✗ 没有返回匹配结果")
                    return False
            else:
                print(f"  ✗ API 返回失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"  ✗ HTTP {response.status_code}")
            return False
    
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        return False

def test_preview_five_steps():
    """测试五步流程预览 API"""
    print("\n测试 3: 五步流程预览 API (POST /api/intelligent-extraction/preview)")
    
    test_text = "CO浓度探测器 量程0~250ppm"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/intelligent-extraction/preview",
            json={"text": test_text},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result_data = data.get('data', {})
                # 检查是否包含各个步骤的结果
                has_step1 = 'step1_device_type' in result_data
                has_step2 = 'step2_parameters' in result_data
                has_step3 = 'step3_auxiliary' in result_data
                has_step4 = 'step4_matching' in result_data
                
                if has_step1 and has_step2 and has_step3 and has_step4:
                    print(f"  ✓ API 正常响应，包含完整的五步流程结果")
                    return True
                else:
                    missing = []
                    if not has_step1:
                        missing.append('step1_device_type')
                    if not has_step2:
                        missing.append('step2_parameters')
                    if not has_step3:
                        missing.append('step3_auxiliary')
                    if not has_step4:
                        missing.append('step4_matching')
                    print(f"  ✗ 缺少步骤: {', '.join(missing)}")
                    return False
            else:
                print(f"  ✗ API 返回失败: {data.get('error', {}).get('message', '未知错误')}")
                return False
        else:
            print(f"  ✗ HTTP {response.status_code}")
            return False
    
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        return False

def test_device_list():
    """测试设备列表 API"""
    print("\n测试 4: 设备列表 API (GET /api/devices)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/devices",
            params={"page": 1, "page_size": 10},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                devices = data.get('devices', [])
                total = data.get('total', 0)
                print(f"  ✓ API 正常响应，共 {total} 个设备，返回 {len(devices)} 个")
                return True
            else:
                print(f"  ✗ API 返回失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"  ✗ HTTP {response.status_code}")
            return False
    
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        return False

def test_device_detail():
    """测试设备详情 API"""
    print("\n测试 5: 设备详情 API (GET /api/devices/<device_id>)")
    
    try:
        # 先获取一个设备ID
        list_response = requests.get(
            f"{BASE_URL}/api/devices",
            params={"page": 1, "page_size": 1},
            timeout=5
        )
        
        if list_response.status_code != 200:
            print("  ✗ 无法获取设备列表")
            return False
        
        list_data = list_response.json()
        devices = list_data.get('devices', [])
        
        if not devices:
            print("  ✗ 没有设备可供测试")
            return False
        
        device_id = devices[0].get('device_id')
        
        # 获取设备详情
        detail_response = requests.get(
            f"{BASE_URL}/api/devices/{device_id}",
            timeout=5
        )
        
        if detail_response.status_code == 200:
            data = detail_response.json()
            if data.get('success'):
                device = data.get('data', {})
                has_basic_fields = all(field in device for field in ['device_id', 'brand', 'device_name'])
                
                if has_basic_fields:
                    print(f"  ✓ API 正常响应，设备信息完整")
                    return True
                else:
                    print("  ✗ 设备信息不完整")
                    return False
            else:
                print(f"  ✗ API 返回失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"  ✗ HTTP {detail_response.status_code}")
            return False
    
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 80)
    print("验证新智能提取匹配系统功能")
    print("=" * 80)
    print()
    
    tests = [
        ("智能提取匹配", test_intelligent_extraction_match),
        ("Excel批量匹配", test_excel_batch_match),
        ("五步流程预览", test_preview_five_steps),
        ("设备列表", test_device_list),
        ("设备详情", test_device_detail),
    ]
    
    passed = 0
    failed = 0
    
    try:
        for test_name, test_func in tests:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
    
    except requests.exceptions.ConnectionError:
        print("\n✗ 无法连接到服务器")
        print("   提示: 请确保后端服务正在运行 (python backend/app.py)")
        return 1
    
    # 输出测试结果
    print()
    print("=" * 80)
    print("测试结果")
    print("=" * 80)
    print(f"总计: {passed + failed} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    print()
    
    if failed == 0:
        print("✅ 所有测试通过! 新系统功能正常")
        return 0
    else:
        print(f"❌ {failed} 个测试失败")
        return 1

if __name__ == '__main__':
    sys.exit(main())
