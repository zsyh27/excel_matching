#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查统计功能所需的数据库表

检查match_logs表是否存在，以及记录数量
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_loader import DataLoader
from config import Config
from modules.text_preprocessor import TextPreprocessor
from modules.data_loader import ConfigManager

def main():
    print("=" * 60)
    print("统计功能数据库表检查")
    print("=" * 60)
    print()
    
    try:
        # 初始化
        print("1. 初始化数据加载器...")
        temp_config_manager = ConfigManager(Config.CONFIG_FILE)
        config = temp_config_manager.get_config()
        preprocessor = TextPreprocessor(config)
        data_loader = DataLoader(config=Config, preprocessor=preprocessor)
        print("   ✓ 初始化完成")
        print()
        
        # 检查数据库模式
        print("2. 检查存储模式...")
        storage_mode = data_loader.get_storage_mode()
        print(f"   存储模式: {storage_mode}")
        
        if storage_mode != 'database':
            print("   ✗ 不是数据库模式")
            print("   统计功能需要数据库模式才能工作")
            print()
            print("解决方案:")
            print("  1. 确保数据库文件存在: data/devices.db")
            print("  2. 确保系统配置使用数据库模式")
            return
        
        print("   ✓ 使用数据库模式")
        print()
        
        # 检查表是否存在
        print("3. 检查数据库表...")
        if hasattr(data_loader, 'loader') and data_loader.loader and hasattr(data_loader.loader, 'db_manager'):
            with data_loader.loader.db_manager.session_scope() as session:
                from sqlalchemy import inspect
                inspector = inspect(session.bind)
                tables = inspector.get_table_names()
                
                print(f"   数据库中的表: {', '.join(tables)}")
                print()
                
                # 检查match_logs表
                print("4. 检查match_logs表...")
                if 'match_logs' in tables:
                    print("   ✓ match_logs表存在")
                    
                    # 检查记录数
                    from modules.models import MatchLog
                    count = session.query(MatchLog).count()
                    print(f"   记录数: {count}")
                    
                    if count == 0:
                        print("   ⚠ 表中没有数据")
                        print("   这就是为什么匹配日志Tab显示为空")
                        print()
                        print("解决方案:")
                        print("  1. 执行一些匹配操作来生成日志")
                        print("  2. 或运行测试数据脚本: python scripts/add_test_match_logs.py")
                    else:
                        print("   ✓ 表中有数据")
                        
                        # 显示最近的几条记录
                        recent_logs = session.query(MatchLog).order_by(MatchLog.created_at.desc()).limit(5).all()
                        print()
                        print("   最近的5条记录:")
                        for log in recent_logs:
                            status_icon = "✓" if log.match_status == 'success' else "✗"
                            print(f"     {status_icon} {log.created_at} - {log.input_description[:50]}...")
                else:
                    print("   ✗ match_logs表不存在")
                    print("   这就是为什么匹配日志Tab显示为空")
                    print()
                    print("解决方案:")
                    print("  运行创建表脚本: python scripts/create_match_logs_table.py")
                
                print()
                
                # 检查其他相关表
                print("5. 检查其他相关表...")
                required_tables = ['devices', 'rules']
                for table in required_tables:
                    if table in tables:
                        print(f"   ✓ {table}表存在")
                    else:
                        print(f"   ✗ {table}表不存在")
        else:
            print("   ✗ 无法访问数据库管理器")
        
        print()
        print("=" * 60)
        print("检查完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
