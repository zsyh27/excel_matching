#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加 optimization_suggestions 表

功能:
添加优化建议表，用于存储智能优化辅助系统生成的优化建议

使用方式:
    python add_optimization_suggestions_table.py
"""

import logging
import sys
import os
from pathlib import Path

# 添加项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.database import DatabaseManager
from modules.models import Base, OptimizationSuggestion
from sqlalchemy import inspect

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_table_exists(db_manager, table_name):
    """
    检查表是否存在
    
    Args:
        db_manager: DatabaseManager实例
        table_name: 表名
    
    Returns:
        bool: 表是否存在
    """
    inspector = inspect(db_manager.engine)
    existing_tables = inspector.get_table_names()
    return table_name in existing_tables


def add_optimization_suggestions_table(db_manager):
    """
    添加 optimization_suggestions 表
    
    Args:
        db_manager: DatabaseManager实例
    """
    logger.info("=" * 60)
    logger.info("添加 optimization_suggestions 表")
    logger.info("=" * 60)
    
    # 检查表是否已存在
    if check_table_exists(db_manager, 'optimization_suggestions'):
        logger.info("✓ optimization_suggestions 表已存在，无需创建")
        return
    
    try:
        # 只创建 OptimizationSuggestion 表
        OptimizationSuggestion.__table__.create(db_manager.engine)
        logger.info("✓ 成功创建 optimization_suggestions 表")
        
        # 检查索引
        inspector = inspect(db_manager.engine)
        indexes = inspector.get_indexes('optimization_suggestions')
        logger.info(f"✓ 创建了 {len(indexes)} 个索引:")
        for idx in indexes:
            logger.info(f"  - {idx['name']}: {idx['column_names']}")
            
    except Exception as e:
        logger.error(f"✗ 创建表失败: {e}")
        raise


def verify_table_structure(db_manager):
    """
    验证表结构
    
    Args:
        db_manager: DatabaseManager实例
    """
    logger.info("=" * 60)
    logger.info("验证表结构")
    logger.info("=" * 60)
    
    try:
        inspector = inspect(db_manager.engine)
        
        # 获取列信息
        columns = inspector.get_columns('optimization_suggestions')
        logger.info(f"✓ 表包含 {len(columns)} 个字段:")
        for col in columns:
            logger.info(f"  - {col['name']}: {col['type']}")
        
        # 获取索引信息
        indexes = inspector.get_indexes('optimization_suggestions')
        logger.info(f"✓ 表包含 {len(indexes)} 个索引:")
        for idx in indexes:
            logger.info(f"  - {idx['name']}: {idx['column_names']}")
            
    except Exception as e:
        logger.error(f"✗ 验证表结构失败: {e}")
        raise


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("数据库迁移 - 添加 optimization_suggestions 表")
    logger.info("=" * 60)
    
    # 使用默认数据库URL
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data'
    db_path = data_dir / 'devices.db'
    database_url = f'sqlite:///{db_path}'
    
    logger.info(f"数据库路径: {db_path}")
    
    # 检查数据库文件是否存在
    if not db_path.exists():
        logger.error(f"✗ 数据库文件不存在: {db_path}")
        logger.error("请先运行 init_database.py 初始化数据库")
        sys.exit(1)
    
    # 初始化数据库管理器
    try:
        db_manager = DatabaseManager(database_url)
    except Exception as e:
        logger.error(f"初始化数据库管理器失败: {e}")
        sys.exit(1)
    
    try:
        # 1. 添加表
        add_optimization_suggestions_table(db_manager)
        
        # 2. 验证表结构
        verify_table_structure(db_manager)
        
        logger.info("=" * 60)
        logger.info("✓ 数据库迁移完成！")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"数据库迁移失败: {e}")
        sys.exit(1)
    finally:
        # 关闭数据库连接
        db_manager.close()


if __name__ == '__main__':
    main()
