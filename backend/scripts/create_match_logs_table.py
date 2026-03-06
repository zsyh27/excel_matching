#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建match_logs表

如果match_logs表不存在，创建它
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
    print("创建match_logs表")
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
        storage_mode = data_loader.get_storage_mode()
        if storage_mode != 'database':
            print("✗ 不是数据库模式，无法创建表")
            return
        
        print("2. 创建数据库表...")
        if hasattr(data_loader, 'loader') and data_loader.loader and hasattr(data_loader.loader, 'db_manager'):
            with data_loader.loader.db_manager.session_scope() as session:
                # 创建所有表
                from modules.models import Base
                Base.metadata.create_all(session.bind)
                print("   ✓ 数据库表创建完成")
                
                # 验证表是否创建成功
                from sqlalchemy import inspect
                inspector = inspect(session.bind)
                tables = inspector.get_table_names()
                
                if 'match_logs' in tables:
                    print("   ✓ match_logs表创建成功")
                else:
                    print("   ✗ match_logs表创建失败")
        else:
            print("   ✗ 无法访问数据库管理器")
        
        print()
        print("=" * 60)
        print("创建完成")
        print("=" * 60)
        print()
        print("下一步:")
        print("  1. 运行检查脚本验证: python scripts/check_statistics_tables.py")
        print("  2. 添加测试数据（可选）: python scripts/add_test_match_logs.py")
        
    except Exception as e:
        print(f"✗ 创建失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
