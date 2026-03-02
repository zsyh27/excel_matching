#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库优化脚本 - 智能设备录入系统

优化数据库查询性能，添加必要的索引
"""

import sys
import os
import logging
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.database import DatabaseManager
from sqlalchemy import text

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """数据库优化器"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        初始化优化器
        
        Args:
            db_manager: 数据库管理器
        """
        self.db_manager = db_manager
        logger.info("数据库优化器初始化完成")
    
    def optimize(self) -> None:
        """执行数据库优化"""
        logger.info("开始数据库优化...")
        
        try:
            # 检查并创建索引
            self._create_indexes()
            
            # 分析表统计信息
            self._analyze_tables()
            
            logger.info("数据库优化完成")
            
        except Exception as e:
            logger.error(f"数据库优化失败: {e}")
            raise
    
    def _create_indexes(self) -> None:
        """创建索引"""
        logger.info("检查并创建索引...")
        
        indexes = [
            # 品牌索引（用于匹配算法）
            {
                'name': 'idx_devices_brand',
                'table': 'devices',
                'column': 'brand',
                'description': '品牌索引，用于设备匹配'
            },
            # 设备类型索引（用于匹配算法）
            {
                'name': 'idx_devices_device_type',
                'table': 'devices',
                'column': 'device_type',
                'description': '设备类型索引，用于设备匹配'
            },
            # 型号索引（用于精确匹配）
            {
                'name': 'idx_devices_model',
                'table': 'devices',
                'column': 'model',
                'description': '型号索引，用于精确匹配'
            },
            # 置信度索引（用于筛选高质量数据）
            {
                'name': 'idx_devices_confidence_score',
                'table': 'devices',
                'column': 'confidence_score',
                'description': '置信度索引，用于筛选高质量数据'
            },
            # 设备ID索引（用于快速查找）
            {
                'name': 'idx_devices_device_id',
                'table': 'devices',
                'column': 'device_id',
                'description': '设备ID索引，用于快速查找'
            }
        ]
        
        with self.db_manager.session_scope() as session:
            for index_info in indexes:
                try:
                    # 检查索引是否存在
                    if self._index_exists(session, index_info['name']):
                        logger.info(f"索引已存在: {index_info['name']}")
                        continue
                    
                    # 创建索引
                    sql = f"CREATE INDEX IF NOT EXISTS {index_info['name']} ON {index_info['table']}({index_info['column']})"
                    session.execute(text(sql))
                    session.commit()
                    
                    logger.info(f"创建索引: {index_info['name']} - {index_info['description']}")
                    
                except Exception as e:
                    logger.error(f"创建索引 {index_info['name']} 失败: {e}")
                    session.rollback()
    
    def _index_exists(self, session, index_name: str) -> bool:
        """
        检查索引是否存在
        
        Args:
            session: 数据库会话
            index_name: 索引名称
            
        Returns:
            索引是否存在
        """
        try:
            # SQLite 查询索引
            result = session.execute(
                text("SELECT name FROM sqlite_master WHERE type='index' AND name=:name"),
                {'name': index_name}
            )
            return result.fetchone() is not None
        except Exception:
            return False
    
    def _analyze_tables(self) -> None:
        """分析表统计信息"""
        logger.info("分析表统计信息...")
        
        try:
            with self.db_manager.session_scope() as session:
                # SQLite 的 ANALYZE 命令
                session.execute(text("ANALYZE"))
                session.commit()
                
                logger.info("表统计信息分析完成")
                
        except Exception as e:
            logger.error(f"分析表统计信息失败: {e}")
    
    def get_index_info(self) -> dict:
        """
        获取索引信息
        
        Returns:
            索引信息字典
        """
        try:
            with self.db_manager.session_scope() as session:
                # 查询所有索引
                result = session.execute(
                    text("SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND tbl_name='devices'")
                )
                
                indexes = []
                for row in result:
                    indexes.append({
                        'name': row[0],
                        'table': row[1]
                    })
                
                return {
                    'total_indexes': len(indexes),
                    'indexes': indexes
                }
                
        except Exception as e:
            logger.error(f"获取索引信息失败: {e}")
            return {}


def main():
    """主函数"""
    try:
        # 初始化数据库管理器
        logger.info("初始化数据库管理器...")
        
        database_url = os.environ.get('DATABASE_URL', 'sqlite:///data/devices.db')
        db_manager = DatabaseManager(database_url)
        
        # 创建优化器
        optimizer = DatabaseOptimizer(db_manager)
        
        # 执行优化
        logger.info("开始数据库优化...")
        optimizer.optimize()
        
        # 获取索引信息
        index_info = optimizer.get_index_info()
        
        # 打印摘要
        print("\n" + "=" * 80)
        print("数据库优化报告")
        print("=" * 80)
        print(f"\n优化时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n索引信息:")
        print(f"  总索引数: {index_info.get('total_indexes', 0)}")
        print(f"\n索引列表:")
        for idx in index_info.get('indexes', []):
            print(f"  - {idx['name']} (表: {idx['table']})")
        print("=" * 80)
        
        logger.info("数据库优化完成")
        
    except Exception as e:
        logger.error(f"数据库优化失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
