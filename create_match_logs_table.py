#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""创建 match_logs 表"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Base, MatchLog
from sqlalchemy import inspect

def create_match_logs_table():
    """创建 match_logs 表"""
    print("=" * 80)
    print("创建 match_logs 表")
    print("=" * 80)
    
    # 初始化数据库
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    
    # 检查表是否已存在
    inspector = inspect(db_manager.engine)
    existing_tables = inspector.get_table_names()
    
    print(f"\n当前数据库中的表: {existing_tables}")
    
    if 'match_logs' in existing_tables:
        print("\n✅ match_logs 表已存在，无需创建")
        return True
    
    print("\n⚠️  match_logs 表不存在，开始创建...")
    
    try:
        # 创建表
        MatchLog.__table__.create(db_manager.engine, checkfirst=True)
        print("✅ match_logs 表创建成功！")
        
        # 验证表是否创建成功
        inspector = inspect(db_manager.engine)
        existing_tables = inspector.get_table_names()
        
        if 'match_logs' in existing_tables:
            print("\n✅ 验证成功：match_logs 表已存在于数据库中")
            
            # 显示表结构
            columns = inspector.get_columns('match_logs')
            print("\n表结构:")
            for col in columns:
                print(f"   - {col['name']}: {col['type']}")
            
            return True
        else:
            print("\n❌ 验证失败：表创建后仍然不存在")
            return False
            
    except Exception as e:
        print(f"\n❌ 创建表失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        success = create_match_logs_table()
        
        if success:
            print("\n" + "=" * 80)
            print("下一步操作:")
            print("=" * 80)
            print("\n1. 重启后端服务:")
            print("   cd backend")
            print("   python app.py")
            print("\n2. 在前端执行设备匹配操作:")
            print("   - 访问 http://localhost:3000/matching")
            print("   - 上传Excel文件并执行匹配")
            print("\n3. 查看统计页面:")
            print("   http://localhost:3000/statistics")
        
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 执行过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
