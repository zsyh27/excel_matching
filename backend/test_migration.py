# -*- coding: utf-8 -*-
"""单元测试脚本"""
import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_single_device_match():
    print('=== 测试1：单个设备匹配 ===')
    response = requests.post(f'{BASE_URL}/api/match', 
        json={'rows': [{'row_number': 1, 'row_type': 'device', 'device_description': 'CO浓度探测器 量程0~250ppm 输出4~20mA'}]})
    result = response.json()
    print(f'成功: {result.get("success")}')
    print(f'匹配状态: {result["matched_rows"][0]["match_result"]["match_status"]}')
    print(f'候选数量: {len(result["matched_rows"][0]["candidates"])}')
    return result

def test_return_format(result):
    print('\n=== 测试2：返回格式验证 ===')
    candidate = result['matched_rows'][0]['candidates'][0] if result['matched_rows'][0]['candidates'] else {}
    required_fields = ['device_id', 'matched_device_text', 'unit_price', 'match_score', 'brand', 'device_name', 'spec_model']
    for field in required_fields:
        status = '存在' if field in candidate else '缺失'
        print(f'{field}: {status}')
    return all(field in candidate for field in required_fields)

def test_empty_text():
    print('\n=== 测试3：边界情况 - 空文本 ===')
    response = requests.post(f'{BASE_URL}/api/match', 
        json={'rows': [{'row_number': 1, 'row_type': 'device', 'device_description': ''}]})
    result = response.json()
    print(f'成功: {result.get("success")}')
    print(f'匹配状态: {result["matched_rows"][0]["match_result"]["match_status"]}')
    return result

def test_special_chars():
    print('\n=== 测试4：边界情况 - 特殊字符 ===')
    response = requests.post(f'{BASE_URL}/api/match', 
        json={'rows': [{'row_number': 1, 'row_type': 'device', 'device_description': '@#$%^&*()温度传感器'}]})
    result = response.json()
    print(f'成功: {result.get("success")}')
    print(f'匹配状态: {result["matched_rows"][0]["match_result"]["match_status"]}')
    return result

def test_batch_match():
    print('\n=== 测试5：批量匹配 ===')
    response = requests.post(f'{BASE_URL}/api/match', 
        json={'rows': [
            {'row_number': 1, 'row_type': 'device', 'device_description': '温度传感器'},
            {'row_number': 2, 'row_type': 'device', 'device_description': '压力变送器'},
            {'row_number': 3, 'row_type': 'device', 'device_description': '流量计'}
        ]})
    result = response.json()
    print(f'成功: {result.get("success")}')
    print(f'统计: {result["statistics"]}')
    return result

if __name__ == '__main__':
    result1 = test_single_device_match()
    format_ok = test_return_format(result1)
    test_empty_text()
    test_special_chars()
    test_batch_match()
    print('\n所有单元测试完成!')
