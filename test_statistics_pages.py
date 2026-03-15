#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试统计页面API"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_match_logs_api():
    """测试匹配日志API"""
    print("\n" + "="*80)
    print("测试匹配日志API")
    print("="*80)
    
    url = f"{BASE_URL}/api/statistics/match-logs"
    print(f"\n请求URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n响应数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            if data.get('success'):
                logs = data.get('logs', [])
                total = data.get('total', 0)
                print(f"\n✅ 成功获取匹配日志")
                print(f"   总数: {total}")
                print(f"   当前页数据: {len(logs)} 条")
                
                if logs:
                    print(f"\n第一条日志示例:")
                    first_log = logs[0]
                    print(f"   日志ID: {first_log.get('log_id')}")
                    print(f"   时间: {first_log.get('timestamp')}")
                    print(f"   输入描述: {first_log.get('input_description')}")
                    print(f"   匹配状态: {first_log.get('match_status')}")
                    print(f"   匹配设备名称: {first_log.get('matched_device_name')}")
                    print(f"   匹配得分: {first_log.get('match_score')}")
                else:
                    print(f"\n⚠️  日志列表为空")
                    print(f"   提示: {data.get('message', '无')}")
            else:
                print(f"\n❌ API返回失败")
                print(f"   消息: {data.get('message')}")
        else:
            print(f"\n❌ HTTP请求失败")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")


def test_match_success_rate_api():
    """测试匹配成功率API"""
    print("\n" + "="*80)
    print("测试匹配成功率API")
    print("="*80)
    
    url = f"{BASE_URL}/api/statistics/match-success-rate"
    print(f"\n请求URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n响应数据:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            
            if data.get('success'):
                trend = data.get('trend', [])
                overall = data.get('overall', {})
                print(f"\n✅ 成功获取匹配成功率")
                print(f"   趋势数据点数: {len(trend)}")
                print(f"   总体成功率: {overall.get('success_rate', 0)*100:.1f}%")
                print(f"   总匹配次数: {overall.get('total', 0)}")
                print(f"   成功次数: {overall.get('success', 0)}")
                
                if trend:
                    print(f"\n最近3天数据:")
                    for item in trend[-3:]:
                        print(f"   {item.get('date')}: 成功率 {item.get('success_rate', 0)*100:.1f}% ({item.get('success')}/{item.get('total')})")
                else:
                    print(f"\n⚠️  趋势数据为空")
                    print(f"   提示: {data.get('message', '无')}")
            else:
                print(f"\n❌ API返回失败")
                print(f"   消息: {data.get('message')}")
        else:
            print(f"\n❌ HTTP请求失败")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")


def check_database_mode():
    """检查数据库模式"""
    print("\n" + "="*80)
    print("检查数据库模式")
    print("="*80)
    
    url = f"{BASE_URL}/api/database/statistics"
    print(f"\n请求URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"\n✅ 数据库模式已启用")
                print(f"   总设备数: {data.get('data', {}).get('total_devices', 0)}")
            else:
                print(f"\n⚠️  数据库模式可能未启用")
        else:
            print(f"\n❌ 无法检查数据库模式")
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("统计页面API测试")
    print("="*80)
    
    # 检查数据库模式
    check_database_mode()
    
    # 测试匹配日志API
    test_match_logs_api()
    
    # 测试匹配成功率API
    test_match_success_rate_api()
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)
