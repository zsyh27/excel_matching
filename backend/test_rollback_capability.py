"""
测试回滚能力
验证可以从备份恢复数据库
"""

import sys
import os
import shutil

# 添加backend目录到Python路径
backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import text, inspect
from modules.database import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_rollback():
    """测试回滚能力"""
    
    logger.info("=" * 60)
    logger.info("测试回滚能力...")
    logger.info("=" * 60)
    
    # 1. 创建测试数据库副本
    test_db_path = "data/devices_test_rollback.db"
    backup_db_path = "data/devices_backup_before_schema_migration.db"
    migrated_db_path = "data/devices.db"
    
    try:
        # 复制迁移后的数据库作为测试
        logger.info("\n[1/3] 创建测试数据库副本...")
        shutil.copy(migrated_db_path, test_db_path)
        logger.info(f"  ✅ 已创建测试数据库: {test_db_path}")
        
        # 2. 验证测试数据库有新字段
        logger.info("\n[2/3] 验证测试数据库有新字段...")
        db_manager = DatabaseManager(f"sqlite:///{test_db_path}")
        
        with db_manager.session_scope() as session:
            inspector = inspect(session.bind)
            columns = [col['name'] for col in inspector.get_columns('devices')]
            
            new_fields = ['device_type', 'input_method', 'created_at', 'updated_at']
            has_new_fields = all(field in columns for field in new_fields)
            
            if has_new_fields:
                logger.info(f"  ✅ 测试数据库包含所有新字段")
            else:
                logger.error(f"  ❌ 测试数据库缺少新字段")
                return False
        
        db_manager.close()
        
        # 3. 模拟回滚：用备份覆盖测试数据库
        logger.info("\n[3/3] 模拟回滚操作...")
        shutil.copy(backup_db_path, test_db_path)
        logger.info(f"  ✅ 已从备份恢复: {backup_db_path} -> {test_db_path}")
        
        # 4. 验证回滚后的数据库没有新字段
        logger.info("\n[4/4] 验证回滚后的数据库...")
        db_manager = DatabaseManager(f"sqlite:///{test_db_path}")
        
        with db_manager.session_scope() as session:
            inspector = inspect(session.bind)
            columns = [col['name'] for col in inspector.get_columns('devices')]
            
            logger.info(f"  回滚后的字段: {', '.join(columns)}")
            
            new_fields = ['device_type', 'input_method', 'created_at', 'updated_at']
            has_new_fields = any(field in columns for field in new_fields)
            
            if not has_new_fields:
                logger.info(f"  ✅ 回滚成功，新字段已移除")
            else:
                logger.error(f"  ❌ 回滚失败，仍包含新字段")
                return False
            
            # 检查数据完整性
            result = session.execute(text("SELECT COUNT(*) as count FROM devices"))
            count = result.fetchone()[0]
            logger.info(f"  设备总数: {count}")
            
            if count > 0:
                logger.info(f"  ✅ 数据完整性保持")
            else:
                logger.error(f"  ❌ 数据丢失")
                return False
        
        db_manager.close()
        
        # 清理测试数据库
        logger.info("\n清理测试文件...")
        os.remove(test_db_path)
        logger.info(f"  ✅ 已删除测试数据库: {test_db_path}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 回滚能力测试通过")
        logger.info("=" * 60)
        logger.info("\n测试结果:")
        logger.info("  ✅ 可以从备份恢复数据库")
        logger.info("  ✅ 回滚后新字段被移除")
        logger.info("  ✅ 回滚后数据完整性保持")
        logger.info("\n回滚方法:")
        logger.info("  1. 停止应用程序")
        logger.info("  2. 复制备份文件覆盖当前数据库:")
        logger.info(f"     Copy-Item {backup_db_path} {migrated_db_path} -Force")
        logger.info("  3. 重启应用程序")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ 回滚能力测试失败: {str(e)}")
        logger.exception("详细错误信息:")
        
        # 清理测试文件
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        return False


if __name__ == "__main__":
    success = test_rollback()
    sys.exit(0 if success else 1)
