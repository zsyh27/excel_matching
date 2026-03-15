#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查后端服务状态和匹配日志功能"""

import requests
import json

def check_backend_status():
    """检查后端服务状态"""
    print("=" * 80)
    print("后端服务状态检查")
    print("=" * 80)
    
    base_url = "http://localhost:5000"
    
    # 1. 检查健康状态
    print("\n1. 检查后端服务健康状态...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ 后端服务正在运行")
            data = response.json()
            print(f"   时间戳: {data.get('timestamp')}")
        else:
            print(f"   ❌ 后端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ 无法连接到后端服务")
        print("   请确认后端服务是否已启动: python backend/app.py")
        return False
    except Exception as e:
        print(f"   ❌ 检查失败: {e}")
        return False
    
    # 2. 测试匹配API
    print("\n2. 测试匹配API...")
    try:
        test_data = {
            "rows": [
                {
                    "row_number": 1,
                    "row_type": "device",
                    "device_description": "霍尼韦尔 温度传感器 HST-RA 测量范围-20~60℃"
                }
            ]
        }
        
        response = requests.post(
            f"{base_url}/api/match",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("   ✅ 匹配API响应正常")
            data = response.json()
            
            if data.get('success'):
                matched_rows = data.get('matched_rows', [])
                if matched_rows:
                    first_match = matched_rows[0]
                    match_result = first_match.get('match_result', {})
                    print(f"   匹配状态: {match_result.get('match_status')}")
                    print(f"   匹配得分: {match_result.get('match_score', 0):.1f}")
                    
                    # 检查是否有候选设备
                    candidates = first_match.get('candidates', [])
                    print(f"   候选设备数: {len(candidates)}")
                else:
                    print("   ⚠️  没有返回匹配结果")
            else:
                print(f"   ❌ 匹配失败: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ 匹配API响应异常: {response.status_code}")
            print(f"   响应内容: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 测试匹配API失败: {e}")
    
    # 3. 检查统计API
    print("\n3. 检查统计API...")
    try:
        response = requests.get(
            f"{base_url}/api/statistics/match-logs",
            params={"page": 1, "page_size": 10},
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ 统计API响应正常")
            data = response.json()
            
            if data.get('success'):
                total = data.get('total', 0)
                logs = data.get('logs', [])
                print(f"   总日志数: {total}")
                print(f"   当前页日志数: {len(logs)}")
                
                if logs:
                    print("\n   最近的日志:")
                    for log in logs[:3]:
                        print(f"   - {log.get('timestamp')}: {log.get('match_status')} - {log.get('input_description', '')[:50]}...")
                else:
                    print("   ⚠️  没有找到任何日志记录")
            else:
                print(f"   ⚠️  API返回失败: {data.get('message', 'Unknown')}")
        else:
            print(f"   ❌ 统计API响应异常: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 检查统计API失败: {e}")
    
    # 4. 再次检查数据库
    print("\n4. 检查数据库中的日志...")
    try:
        import sys
        sys.path.insert(0, 'backend')
        
        from modules.database import DatabaseManager
        from modules.models import MatchLog
        from sqlalchemy import func
        
        db_manager = DatabaseManager("sqlite:///data/devices.db")
        
        with db_manager.session_scope() as session:
            total_logs = session.query(func.count(MatchLog.log_id)).scalar()
            print(f"   数据库中的日志总数: {total_logs}")
            
            if total_logs > 0:
                recent_logs = session.query(MatchLog)\
                    .order_by(MatchLog.timestamp.desc())\
                    .limit(3)\
                    .all()
                
                print("\n   最近的日志:")
                for log in recent_logs:
                    print(f"   - {log.timestamp}: {log.match_status} - {log.input_description[:50]}...")
            else:
                print("   ⚠️  数据库中没有日志记录")
                print("\n   这说明:")
                print("   1. 后端服务可能没有重启")
                print("   2. 或者匹配日志记录器没有正确初始化")
                print("   3. 或者匹配操作没有触发日志记录")
    except Exception as e:
        print(f"   ❌ 检查数据库失败: {e}")
    
    print("\n" + "=" * 80)
    print("诊断结果")
    print("=" * 80)
    
    # 5. 给出诊断结果
    print("\n如果数据库中没有日志，但匹配API正常工作，说明:")
    print("1. ❌ 后端服务可能使用的是旧代码（没有日志记录功能）")
    print("2. ❌ 需要重启后端服务以加载最新代码")
    print("\n解决方法:")
    print("1. 停止当前的后端服务（Ctrl+C）")
    print("2. 重新启动后端服务:")
    print("   cd backend")
    print("   python app.py")
    print("3. 查看启动日志，确认看到:")
    print("   '匹配日志记录器初始化完成'")
    print("4. 再次执行设备匹配操作")
    print("5. 检查统计页面")
    
    return True

if __name__ == '__main__':
    try:
        check_backend_status()
    except Exception as e:
        print(f"\n❌ 检查过程出错: {e}")
        import traceback
        traceback.print_exc()
