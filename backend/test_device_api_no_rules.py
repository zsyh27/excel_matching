#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试设备详情 API 不包含规则字段

验证任意设备的详情 API 响应不包含 rule 和 has_rules 字段
Property 2: 设备详情 API 不包含规则字段
Validates: Requirements 5.3
"""

import requests
import sys
import io

# 设置标准输出为 UTF-8 编码（Windows 兼容）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 后端服务地址
BASE_URL = 'http://localhost:5000'

def test_device_detail_no_rule_fields():
    """测试设备详情 API 不包含规则字段"""
    print("=" * 80)
    print("测试设备详情 API 不包含规则字段")
    print("=" * 80)
    print()
    
    try:
        # 1. 获取设备列表
        print("步骤 1: 获取设备列表...")
        response = requests.get(f"{BASE_URL}/api/devices", params={'page_size': 5}, timeout=5)
        
        if response.status_code != 200:
            print(f"✗ 获取设备列表失败: HTTP {response.status_code}")
            return 1
        
        data = response.json()
        if not data.get('success'):
            print(f"✗ 获取设备列表失败: {data.get('message', '未知错误')}")
            return 1
        
        devices = data.get('devices', [])
        if not devices:
            print("✗ 没有找到任何设备，无法测试")
            return 1
        
        print(f"✓ 成功获取 {len(devices)} 个设备")
        print()
        
        # 2. 测试每个设备的详情 API
        print("步骤 2: 测试设备详情 API...")
        passed = 0
        failed = 0
        errors = []
        
        for device in devices:
            device_id = device.get('device_id')
            device_name = device.get('device_name', '未知设备')
            
            try:
                # 获取设备详情
                detail_response = requests.get(f"{BASE_URL}/api/devices/{device_id}", timeout=5)
                
                if detail_response.status_code != 200:
                    print(f"✗ {device_name} ({device_id}) - HTTP {detail_response.status_code}")
                    failed += 1
                    errors.append(f"{device_id}: HTTP {detail_response.status_code}")
                    continue
                
                detail_data = detail_response.json()
                if not detail_data.get('success'):
                    print(f"✗ {device_name} ({device_id}) - API 返回失败")
                    failed += 1
                    errors.append(f"{device_id}: API 返回失败")
                    continue
                
                device_detail = detail_data.get('data', {})
                
                # 检查是否包含 rule 或 has_rules 字段
                has_rule_field = 'rule' in device_detail
                has_has_rules_field = 'has_rules' in device_detail
                
                if has_rule_field or has_has_rules_field:
                    fields = []
                    if has_rule_field:
                        fields.append('rule')
                    if has_has_rules_field:
                        fields.append('has_rules')
                    
                    print(f"✗ {device_name} ({device_id}) - 包含规则字段: {', '.join(fields)}")
                    failed += 1
                    errors.append(f"{device_id}: 包含字段 {', '.join(fields)}")
                else:
                    print(f"✓ {device_name} ({device_id}) - 不包含规则字段")
                    passed += 1
            
            except Exception as e:
                print(f"✗ {device_name} ({device_id}) - 错误: {e}")
                failed += 1
                errors.append(f"{device_id}: {str(e)}")
        
        # 输出测试结果
        print()
        print("=" * 80)
        print("测试结果")
        print("=" * 80)
        print(f"总计: {passed + failed} 个设备")
        print(f"通过: {passed} 个")
        print(f"失败: {failed} 个")
        
        if errors:
            print()
            print("失败详情:")
            for error in errors:
                print(f"  - {error}")
        
        print()
        
        if failed == 0:
            print("✅ 所有测试通过! 设备详情 API 不包含规则字段")
            return 0
        else:
            print(f"❌ {failed} 个测试失败")
            return 1
    
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到服务器")
        print("   提示: 请确保后端服务正在运行 (python backend/app.py)")
        return 1
    
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(test_device_detail_no_rule_fields())
