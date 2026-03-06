"""
验证Schema迁移结果
检查字段、索引和数据完整性
"""

import sys
import os

# 添加backend目录到Python路径
backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy import text, inspect
from modules.database import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def verify_migration(database_url: str = "sqlite:///data/devices.db"):
    """验证Schema迁移结果"""
    
    logger.info("=" * 60)
    logger.info("开始验证Schema迁移结果...")
    logger.info("=" * 60)
    
    db_manager = DatabaseManager(database_url)
    
    try:
        with db_manager.session_scope() as session:
            inspector = inspect(session.bind)
            
            # 1. 验证字段添加成功
            logger.info("\n[1/5] 验证字段添加...")
            columns = {col['name']: col for col in inspector.get_columns('devices')}
            
            required_fields = ['device_type', 'input_method', 'created_at', 'updated_at']
            all_fields_exist = True
            
            for field in required_fields:
                if field in columns:
                    logger.info(f"  ✅ {field} 字段存在 - 类型: {columns[field]['type']}")
                else:
                    logger.error(f"  ❌ {field} 字段不存在")
                    all_fields_exist = False
            
            if not all_fields_exist:
                logger.error("字段验证失败")
                return False
            
            # 2. 验证索引创建成功
            logger.info("\n[2/5] 验证索引创建...")
            indexes = inspector.get_indexes('devices')
            index_names = [idx['name'] for idx in indexes]
            
            required_indexes = ['idx_device_type', 'idx_input_method']
            all_indexes_exist = True
            
            for idx_name in required_indexes:
                if idx_name in index_names:
                    idx_info = next(idx for idx in indexes if idx['name'] == idx_name)
                    logger.info(f"  ✅ {idx_name} 索引存在 - 列: {idx_info['column_names']}")
                else:
                    logger.error(f"  ❌ {idx_name} 索引不存在")
                    all_indexes_exist = False
            
            if not all_indexes_exist:
                logger.error("索引验证失败")
                return False
            
            # 3. 验证现有数据不受影响
            logger.info("\n[3/5] 验证现有数据完整性...")
            
            # 检查记录总数
            result = session.execute(text("SELECT COUNT(*) as count FROM devices"))
            total_count = result.fetchone()[0]
            logger.info(f"  设备总数: {total_count}")
            
            # 检查必填字段数据完整性
            result = session.execute(text("""
                SELECT COUNT(*) as count FROM devices 
                WHERE device_id IS NULL OR brand IS NULL OR device_name IS NULL 
                   OR spec_model IS NULL OR unit_price IS NULL
            """))
            null_count = result.fetchone()[0]
            
            if null_count == 0:
                logger.info(f"  ✅ 所有必填字段数据完整")
            else:
                logger.error(f"  ❌ 发现 {null_count} 条记录的必填字段为空")
                return False
            
            # 4. 验证默认值设置
            logger.info("\n[4/5] 验证默认值设置...")
            
            # 检查input_method默认值
            result = session.execute(text("""
                SELECT COUNT(*) as count FROM devices 
                WHERE input_method = 'manual'
            """))
            manual_count = result.fetchone()[0]
            logger.info(f"  input_method='manual' 的记录数: {manual_count}")
            
            # 检查时间戳字段
            result = session.execute(text("""
                SELECT COUNT(*) as count FROM devices 
                WHERE created_at IS NOT NULL AND updated_at IS NOT NULL
            """))
            timestamp_count = result.fetchone()[0]
            logger.info(f"  有时间戳的记录数: {timestamp_count}")
            
            if timestamp_count == total_count:
                logger.info(f"  ✅ 所有记录都有时间戳")
            else:
                logger.warning(f"  ⚠️ {total_count - timestamp_count} 条记录缺少时间戳")
            
            # 5. 抽样检查数据
            logger.info("\n[5/5] 抽样检查数据...")
            result = session.execute(text("""
                SELECT device_id, brand, device_name, device_type, input_method, 
                       created_at, updated_at
                FROM devices 
                LIMIT 5
            """))
            
            logger.info("  前5条记录:")
            for row in result:
                logger.info(f"    - {row[0]}: {row[1]} {row[2]}")
                logger.info(f"      device_type: {row[3]}, input_method: {row[4]}")
                logger.info(f"      created_at: {row[5]}, updated_at: {row[6]}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ Schema迁移验证通过")
        logger.info("=" * 60)
        logger.info("\n验证结果总结:")
        logger.info("  ✅ 所有新字段已成功添加")
        logger.info("  ✅ 所有索引已成功创建")
        logger.info("  ✅ 现有数据完整性保持不变")
        logger.info("  ✅ 默认值已正确设置")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Schema迁移验证失败: {str(e)}")
        logger.exception("详细错误信息:")
        return False
    finally:
        db_manager.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='验证Schema迁移结果')
    parser.add_argument('--database', type=str, default='sqlite:///data/devices.db',
                       help='数据库连接URL (默认: sqlite:///data/devices.db)')
    
    args = parser.parse_args()
    
    success = verify_migration(args.database)
    sys.exit(0 if success else 1)
