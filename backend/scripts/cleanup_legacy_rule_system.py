#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理数据库中的旧规则系统数据

任务 8.1: 删除 feature_weight_config 配置和 rules 表
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from sqlalchemy import text

def cleanup_legacy_rule_system():
    """清理数据库中的旧规则系统数据"""
    
    print("=" * 80)
    print("清理数据库中的旧规则系统数据")
    print("=" * 80)
    print()
    
    # 初始化数据库管理器
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    
    try:
        with db_manager.session_scope() as session:
            # 1. 删除 feature_weight_config 配置
            print("步骤 1: 删除 feature_weight_config 配置...")
            
            try:
                result = session.execute(
                    text("DELETE FROM configs WHERE config_key = 'feature_weight_config'")
                )
                deleted_count = result.rowcount
                
                if deleted_count > 0:
                    print(f"  ✓ 删除了 {deleted_count} 条 feature_weight_config 配置")
                else:
                    print("  ℹ feature_weight_config 配置不存在（可能已被删除）")
            
            except Exception as e:
                print(f"  ⚠ 删除 feature_weight_config 配置时出错: {e}")
                print("  ℹ 继续执行后续步骤...")
            
            # 2. 删除 rules 表
            print()
            print("步骤 2: 删除 rules 表...")
            
            try:
                # 检查表是否存在
                result = session.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table' AND name='rules'")
                )
                table_exists = result.fetchone() is not None
                
                if table_exists:
                    # 删除表
                    session.execute(text("DROP TABLE IF EXISTS rules"))
                    print("  ✓ 成功删除 rules 表")
                else:
                    print("  ℹ rules 表不存在（可能已被删除）")
            
            except Exception as e:
                print(f"  ⚠ 删除 rules 表时出错: {e}")
                print("  ℹ 继续执行后续步骤...")
            
            # 提交事务
            session.commit()
        
        print()
        print("=" * 80)
        print("✅ 数据库清理完成!")
        print("=" * 80)
        print()
        print("已完成的操作:")
        print("  ✓ 删除 feature_weight_config 配置")
        print("  ✓ 删除 rules 表")
        print()
        print("注意事项:")
        print("  - rules 表已被彻底删除，无法恢复")
        print("  - 新系统使用 intelligent_extraction 配置，不受影响")
        print("  - 建议重启后端服务以确保更改生效")
        
        return 0
    
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ 数据库清理失败!")
        print("=" * 80)
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(cleanup_legacy_rule_system())
