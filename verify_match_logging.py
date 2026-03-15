#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证匹配日志功能是否正常工作"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import MatchLog
from sqlalchemy import func
from datetime import datetime, timedelta

def verify_match_logging():
    """验证匹配日志功能"""
    print("=" * 80)
    print("匹配日志功能验证")
    print("=" * 80)
    
    # 初始化数据库
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    
    with db_manager.session_scope() as session:
        # 1. 检查表是否存在
        try:
            total_logs = session.query(func.count(MatchLog.log_id)).scalar()
            print(f"\n✅ match_logs 表存在")
            print(f"   总日志数: {total_logs}")
        except Exception as e:
            print(f"\n❌ match_logs 表不存在或无法访问: {e}")
            return False
        
        # 2. 检查最近的日志
        recent_logs = session.query(MatchLog)\
            .order_by(MatchLog.timestamp.desc())\
            .limit(5)\
            .all()
        
        if recent_logs:
            print(f"\n✅ 最近的 {len(recent_logs)} 条日志:")
            for log in recent_logs:
                print(f"   - {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}: {log.match_status} - {log.input_description[:50]}...")
        else:
            print("\n⚠️  没有找到任何匹配日志")
            print("   可能原因:")
            print("   1. 后端服务未重启（代码更改后需要重启）")
            print("   2. 尚未执行任何设备匹配操作")
            print("   3. 匹配日志记录功能未正确初始化")
        
        # 3. 统计成功/失败日志
        success_count = session.query(func.count(MatchLog.log_id))\
            .filter(MatchLog.match_status == 'success')\
            .scalar()
        
        failed_count = session.query(func.count(MatchLog.log_id))\
            .filter(MatchLog.match_status == 'failed')\
            .scalar()
        
        print(f"\n📊 日志统计:")
        print(f"   成功: {success_count}")
        print(f"   失败: {failed_count}")
        
        if total_logs > 0:
            success_rate = (success_count / total_logs) * 100
            print(f"   成功率: {success_rate:.1f}%")
        
        # 4. 检查今天的日志
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_logs = session.query(func.count(MatchLog.log_id))\
            .filter(MatchLog.timestamp >= today)\
            .scalar()
        
        print(f"\n📅 今天的日志数: {today_logs}")
        
        # 5. 提供操作建议
        print("\n" + "=" * 80)
        print("操作建议:")
        print("=" * 80)
        
        if total_logs == 0:
            print("\n⚠️  数据库中没有匹配日志，请按以下步骤操作:")
            print("\n1. 重启后端服务（清除Python缓存）:")
            print("   cd backend")
            print("   python app.py")
            print("\n2. 在前端执行一次完整的设备匹配流程:")
            print("   - 访问 http://localhost:3000/matching")
            print("   - 上传Excel文件")
            print("   - 执行设备匹配")
            print("   - 导出结果")
            print("\n3. 再次访问统计页面查看日志:")
            print("   http://localhost:3000/statistics")
        else:
            print("\n✅ 匹配日志功能正常工作！")
            print(f"   已记录 {total_logs} 条匹配日志")
            print("\n如果统计页面仍然显示为空，请:")
            print("1. 刷新浏览器页面（Ctrl+F5 强制刷新）")
            print("2. 检查浏览器控制台是否有错误")
            print("3. 检查后端日志是否有API错误")
        
        return total_logs > 0

if __name__ == '__main__':
    try:
        success = verify_match_logging()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 验证过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
