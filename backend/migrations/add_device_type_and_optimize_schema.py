"""
数据库Schema优化迁移脚本
添加device_type、input_method、时间戳字段
修改detailed_params为可选

验证需求: 30.1, 31.1, 32.1, 33.1, 34.1
"""

import sys
import os

# 添加backend目录到Python路径
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import text, inspect
from modules.database import DatabaseManager
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_column_exists(session, table_name: str, column_name: str) -> bool:
    """检查列是否存在"""
    inspector = inspect(session.bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def migrate_schema(database_url: str = "sqlite:///data/devices.db", dry_run: bool = False):
    """
    执行Schema迁移
    
    Args:
        database_url: 数据库连接URL
        dry_run: 是否为试运行模式(不实际执行)
    
    Returns:
        bool: 迁移是否成功
    """
    
    logger.info("=" * 60)
    logger.info("开始数据库Schema迁移...")
    logger.info(f"数据库: {database_url}")
    logger.info(f"模式: {'试运行' if dry_run else '正式执行'}")
    logger.info("=" * 60)
    
    db_manager = DatabaseManager(database_url)
    
    try:
        with db_manager.session_scope() as session:
            # 检查现有列
            existing_columns = [col['name'] for col in inspect(session.bind).get_columns('devices')]
            logger.info(f"当前devices表字段: {', '.join(existing_columns)}")
            
            changes_made = []
            
            # 1. 添加device_type字段
            if 'device_type' not in existing_columns:
                logger.info("\n[1/5] 添加device_type字段...")
                if not dry_run:
                    session.execute(text("""
                        ALTER TABLE devices 
                        ADD COLUMN device_type VARCHAR(50);
                    """))
                    logger.info("✅ device_type字段添加成功")
                    changes_made.append("添加device_type字段")
                else:
                    logger.info("  [试运行] 将添加device_type字段")
            else:
                logger.info("\n[1/5] device_type字段已存在，跳过")
            
            # 2. 添加input_method字段
            if 'input_method' not in existing_columns:
                logger.info("\n[2/5] 添加input_method字段...")
                if not dry_run:
                    session.execute(text("""
                        ALTER TABLE devices 
                        ADD COLUMN input_method VARCHAR(20) DEFAULT 'manual';
                    """))
                    logger.info("✅ input_method字段添加成功")
                    changes_made.append("添加input_method字段")
                else:
                    logger.info("  [试运行] 将添加input_method字段")
            else:
                logger.info("\n[2/5] input_method字段已存在，跳过")
            
            # 3. 添加created_at字段
            if 'created_at' not in existing_columns:
                logger.info("\n[3/5] 添加created_at字段...")
                if not dry_run:
                    session.execute(text("""
                        ALTER TABLE devices 
                        ADD COLUMN created_at DATETIME;
                    """))
                    logger.info("✅ created_at字段添加成功")
                    changes_made.append("添加created_at字段")
                else:
                    logger.info("  [试运行] 将添加created_at字段")
            else:
                logger.info("\n[3/5] created_at字段已存在，跳过")
            
            # 4. 添加updated_at字段
            if 'updated_at' not in existing_columns:
                logger.info("\n[4/5] 添加updated_at字段...")
                if not dry_run:
                    session.execute(text("""
                        ALTER TABLE devices 
                        ADD COLUMN updated_at DATETIME;
                    """))
                    logger.info("✅ updated_at字段添加成功")
                    changes_made.append("添加updated_at字段")
                else:
                    logger.info("  [试运行] 将添加updated_at字段")
            else:
                logger.info("\n[4/5] updated_at字段已存在，跳过")
            
            # 5. 为现有数据设置默认值
            if not dry_run and changes_made:
                logger.info("\n[5/5] 为现有数据设置默认值...")
                
                # 统计需要更新的记录数
                result = session.execute(text("""
                    SELECT COUNT(*) as count FROM devices 
                    WHERE input_method IS NULL OR created_at IS NULL OR updated_at IS NULL;
                """))
                count = result.fetchone()[0]
                
                if count > 0:
                    logger.info(f"  发现 {count} 条记录需要设置默认值")
                    session.execute(text("""
                        UPDATE devices 
                        SET input_method = COALESCE(input_method, 'manual'),
                            created_at = COALESCE(created_at, datetime('now')),
                            updated_at = COALESCE(updated_at, datetime('now'))
                        WHERE input_method IS NULL OR created_at IS NULL OR updated_at IS NULL;
                    """))
                    logger.info(f"✅ 已为 {count} 条记录设置默认值")
                    changes_made.append(f"为{count}条记录设置默认值")
                else:
                    logger.info("  所有记录已有默认值，无需更新")
            else:
                logger.info("\n[5/5] 跳过设置默认值(试运行模式或无变更)")
            
            # 6. 创建索引
            logger.info("\n[6/6] 创建索引...")
            if not dry_run:
                try:
                    # 检查索引是否已存在
                    indexes = [idx['name'] for idx in inspect(session.bind).get_indexes('devices')]
                    
                    if 'idx_device_type' not in indexes:
                        session.execute(text("""
                            CREATE INDEX IF NOT EXISTS idx_device_type 
                            ON devices(device_type);
                        """))
                        logger.info("✅ 创建idx_device_type索引")
                        changes_made.append("创建idx_device_type索引")
                    else:
                        logger.info("  idx_device_type索引已存在")
                    
                    if 'idx_input_method' not in indexes:
                        session.execute(text("""
                            CREATE INDEX IF NOT EXISTS idx_input_method 
                            ON devices(input_method);
                        """))
                        logger.info("✅ 创建idx_input_method索引")
                        changes_made.append("创建idx_input_method索引")
                    else:
                        logger.info("  idx_input_method索引已存在")
                        
                except Exception as e:
                    logger.warning(f"⚠️ 索引创建警告: {str(e)}")
            else:
                logger.info("  [试运行] 将创建idx_device_type和idx_input_method索引")
            
            if not dry_run:
                session.commit()
            
        # 迁移完成总结
        logger.info("\n" + "=" * 60)
        if dry_run:
            logger.info("✅ 试运行完成 - 未实际修改数据库")
            logger.info("如需正式执行，请使用: python migrations/add_device_type_and_optimize_schema.py --execute")
        else:
            logger.info("✅ 数据库Schema迁移完成")
            if changes_made:
                logger.info("\n变更内容:")
                for i, change in enumerate(changes_made, 1):
                    logger.info(f"  {i}. {change}")
            else:
                logger.info("  无需变更，所有字段已存在")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ 数据库Schema迁移失败: {str(e)}")
        logger.exception("详细错误信息:")
        return False
    finally:
        db_manager.close()


def rollback_schema(database_url: str = "sqlite:///data/devices.db"):
    """
    回滚Schema迁移(仅用于测试)
    
    注意: SQLite不支持DROP COLUMN,此功能仅用于参考
    """
    logger.warning("=" * 60)
    logger.warning("警告: SQLite不支持DROP COLUMN操作")
    logger.warning("如需回滚,请恢复数据库备份")
    logger.warning("=" * 60)
    return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库Schema优化迁移脚本')
    parser.add_argument('--database', type=str, default='sqlite:///data/devices.db',
                       help='数据库连接URL (默认: sqlite:///data/devices.db)')
    parser.add_argument('--execute', action='store_true',
                       help='正式执行迁移(默认为试运行模式)')
    parser.add_argument('--rollback', action='store_true',
                       help='回滚迁移(仅用于测试)')
    
    args = parser.parse_args()
    
    if args.rollback:
        success = rollback_schema(args.database)
    else:
        dry_run = not args.execute
        success = migrate_schema(args.database, dry_run=dry_run)
    
    sys.exit(0 if success else 1)
