# -*- coding: utf-8 -*-
"""性能基准测试脚本"""
import requests
import time
import json

BASE_URL = 'http://127.0.0.1:5000'

def test_single_match_performance():
    """测试单个匹配响应时间"""
    print('=== 测试1：单个匹配响应时间 ===')
    
    test_cases = [
        'CO浓度探测器 量程0~250ppm 输出4~20mA',
        '温度传感器 量程-50~150℃',
        '压力变送器 量程0~10MPa 输出4~20mA',
        '流量计 DN100',
        '蝶阀 DN150 PN16'
    ]
    
    times = []
    for desc in test_cases:
        start = time.time()
        response = requests.post(f'{BASE_URL}/api/match', 
            json={'rows': [{'row_number': 1, 'row_type': 'device', 'device_description': desc}]})
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        print(f'  "{desc[:20]}..." - {elapsed:.2f}ms')
    
    avg_time = sum(times) / len(times)
    print(f'平均响应时间: {avg_time:.2f}ms')
    print(f'目标: <500ms - {"通过" if avg_time < 500 else "失败"}')
    return avg_time

def test_batch_match_performance():
    """测试批量匹配处理速度"""
    print('\n=== 测试2：批量匹配处理速度 ===')
    
    # 生成100条测试数据
    test_descriptions = [
        'CO浓度探测器 量程0~250ppm 输出4~20mA',
        '温度传感器 量程-50~150℃',
        '压力变送器 量程0~10MPa',
        '流量计 DN100',
        '蝶阀 DN150 PN16',
        '球阀 DN50',
        '温度变送器',
        '湿度传感器',
        '液位传感器',
        '压差变送器'
    ]
    
    rows = [{'row_number': i, 'row_type': 'device', 'device_description': test_descriptions[i % 10]} 
            for i in range(100)]
    
    start = time.time()
    response = requests.post(f'{BASE_URL}/api/match', json={'rows': rows})
    elapsed = time.time() - start
    
    result = response.json()
    throughput = 100 / elapsed
    
    print(f'处理100条数据耗时: {elapsed:.2f}s')
    print(f'吞吐量: {throughput:.2f}条/秒')
    print(f'目标: >100条/秒 - {"通过" if throughput > 100 else "失败"}')
    print(f'匹配结果: {result["statistics"]}')
    return throughput

def test_preview_performance():
    """测试预览API性能"""
    print('\n=== 测试3：预览API性能 ===')
    
    test_text = 'CO浓度探测器 量程0~250ppm 输出4~20mA 精度5%'
    
    times = []
    for i in range(5):
        start = time.time()
        response = requests.post(f'{BASE_URL}/api/intelligent-extraction/preview', 
            json={'text': test_text})
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
    
    avg_time = sum(times) / len(times)
    print(f'预览API平均响应时间: {avg_time:.2f}ms')
    return avg_time

if __name__ == '__main__':
    print('开始性能基准测试...\n')
    
    single_time = test_single_match_performance()
    throughput = test_batch_match_performance()
    preview_time = test_preview_performance()
    
    print('\n=== 性能测试总结 ===')
    print(f'单个匹配响应时间: {single_time:.2f}ms (目标<500ms)')
    print(f'批量处理吞吐量: {throughput:.2f}条/秒 (目标>100条/秒)')
    print(f'预览API响应时间: {preview_time:.2f}ms')
    
    all_passed = single_time < 500 and throughput > 100
    print(f'\n总体结果: {"全部通过" if all_passed else "部分未达标"}')
