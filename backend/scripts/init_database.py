#!/usr/bin/env python3
"""
数据库初始化脚本

功能:
1. 创建数据库表结构（devices, rules, configs）
2. 创建索引以提高查询性能
3. 初始化默认配置数据
4. 支持命令行参数指定数据库类型和URL

使用方式:
    # 使用默认配置（SQLite）
    python init_database.py
    
    # 指定数据库类型和URL
    python init_database.py --db-type sqlite --db-url "sqlite:///data/devices.db"
    python init_database.py --db-type mysql --db-url "mysql://user:pass@localhost/dbname"
    
    # 强制重新创建表（会删除现有数据）
    python init_database.py --force
"""

import argparse
import logging
import sys
import os
from pathlib import Path

# 添加项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.database import DatabaseManager
from modules.models import Base, Device, Rule, Config
from sqlalchemy import inspect

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='初始化DDC设备匹配系统数据库',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s
  %(prog)s --db-type sqlite --db-url "sqlite:///data/devices.db"
  %(prog)s --db-type mysql --db-url "mysql://user:pass@localhost/dbname"
  %(prog)s --force
        """
    )
    
    parser.add_argument(
        '--db-type',
        type=str,
        choices=['sqlite', 'mysql'],
        default='sqlite',
        help='数据库类型 (默认: sqlite)'
    )
    
    parser.add_argument(
        '--db-url',
        type=str,
        default=None,
        help='数据库连接URL (默认: sqlite:///data/devices.db)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制重新创建表（警告：会删除现有数据）'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='显示详细的SQL语句'
    )
    
    return parser.parse_args()


def get_database_url(db_type, db_url):
    """
    获取数据库连接URL
    
    Args:
        db_type: 数据库类型
        db_url: 用户指定的数据库URL
    
    Returns:
        数据库连接URL字符串
    """
    if db_url:
        return db_url
    
    # 使用默认URL
    if db_type == 'sqlite':
        # 确保data目录存在
        base_dir = Path(__file__).parent.parent
        data_dir = base_dir / 'data'
        data_dir.mkdir(exist_ok=True)
        
        db_path = data_dir / 'devices.db'
        return f'sqlite:///{db_path}'
    elif db_type == 'mysql':
        logger.error("使用MySQL时必须指定--db-url参数")
        sys.exit(1)
    
    return None


def check_existing_tables(db_manager):
    """
    检查数据库中是否已存在表
    
    Args:
        db_manager: DatabaseManager实例
    
    Returns:
        dict: 表名到是否存在的映射
    """
    inspector = inspect(db_manager.engine)
    existing_tables = inspector.get_table_names()
    
    tables_status = {
        'devices': 'devices' in existing_tables,
        'rules': 'rules' in existing_tables,
        'configs': 'configs' in existing_tables
    }
    
    return tables_status


def create_tables(db_manager, force=False):
    """
    创建数据库表结构
    
    Args:
        db_manager: DatabaseManager实例
        force: 是否强制重新创建表
    """
    logger.info("=" * 60)
    logger.info("开始创建数据库表结构")
    logger.info("=" * 60)
    
    # 检查现有表
    tables_status = check_existing_tables(db_manager)
    existing_count = sum(tables_status.values())
    
    if existing_count > 0 and not force:
        logger.info(f"检测到 {existing_count} 个表已存在:")
        for table, exists in tables_status.items():
            if exists:
                logger.info(f"  ✓ {table}")
        logger.info("跳过表创建（使用 --force 参数强制重新创建）")
        return
    
    if force and existing_count > 0:
        logger.warning("⚠️  强制模式：将删除现有表并重新创建")
        logger.warning("⚠️  所有现有数据将丢失！")
        Base.metadata.drop_all(db_manager.engine)
        logger.info("已删除现有表")
    
    # 创建所有表
    try:
        db_manager.create_tables()
        logger.info("✓ 成功创建以下表:")
        logger.info("  - devices (设备表)")
        logger.info("  - rules (匹配规则表)")
        logger.info("  - configs (配置表)")
    except Exception as e:
        logger.error(f"✗ 创建表失败: {e}")
        raise


def create_indexes(db_manager):
    """
    创建索引以提高查询性能
    
    注意: SQLAlchemy的模型定义中已经包含了index=True的字段，
    这些索引会在create_all时自动创建。
    此函数用于创建额外的复合索引或特殊索引。
    
    Args:
        db_manager: DatabaseManager实例
    """
    logger.info("=" * 60)
    logger.info("检查数据库索引")
    logger.info("=" * 60)
    
    # 检查索引是否已创建
    inspector = inspect(db_manager.engine)
    
    # 检查devices表的索引
    devices_indexes = inspector.get_indexes('devices')
    logger.info(f"✓ devices表索引: {len(devices_indexes)} 个")
    for idx in devices_indexes:
        logger.info(f"  - {idx['name']}: {idx['column_names']}")
    
    # 检查rules表的索引
    rules_indexes = inspector.get_indexes('rules')
    logger.info(f"✓ rules表索引: {len(rules_indexes)} 个")
    for idx in rules_indexes:
        logger.info(f"  - {idx['name']}: {idx['column_names']}")
    
    logger.info("索引检查完成")


def initialize_config_data(db_manager):
    """
    初始化默认配置数据
    
    Args:
        db_manager: DatabaseManager实例
    """
    logger.info("=" * 60)
    logger.info("初始化配置数据")
    logger.info("=" * 60)
    
    # 默认配置数据
    default_configs = [
        {
            'config_key': 'default_match_threshold',
            'config_value': {'value': 0.6},
            'description': '默认匹配阈值，用于判断设备是否匹配'
        },
        {
            'config_key': 'default_feature_weights',
            'config_value': {
                'brand': 0.3,
                'device_name': 0.3,
                'spec_model': 0.2,
                'detailed_params': 0.2
            },
            'description': '默认特征权重配置'
        },
        {
            'config_key': 'system_version',
            'config_value': {'version': '1.0.0'},
            'description': '系统版本信息'
        }
    ]
    
    try:
        with db_manager.session_scope() as session:
            # 检查配置是否已存在
            existing_configs = session.query(Config).all()
            existing_keys = {c.config_key for c in existing_configs}
            
            if existing_keys:
                logger.info(f"检测到 {len(existing_keys)} 个现有配置:")
                for key in existing_keys:
                    logger.info(f"  ✓ {key}")
            
            # 插入不存在的配置
            inserted_count = 0
            for config_data in default_configs:
                if config_data['config_key'] not in existing_keys:
                    config = Config(**config_data)
                    session.add(config)
                    inserted_count += 1
                    logger.info(f"  + 添加配置: {config_data['config_key']}")
            
            if inserted_count > 0:
                logger.info(f"✓ 成功添加 {inserted_count} 个配置项")
            else:
                logger.info("所有配置项已存在，无需添加")
                
    except Exception as e:
        logger.error(f"✗ 初始化配置数据失败: {e}")
        raise


def print_statistics(db_manager):
    """
    打印数据库统计信息
    
    Args:
        db_manager: DatabaseManager实例
    """
    logger.info("=" * 60)
    logger.info("数据库统计信息")
    logger.info("=" * 60)
    
    try:
        with db_manager.session_scope() as session:
            device_count = session.query(Device).count()
            rule_count = session.query(Rule).count()
            config_count = session.query(Config).count()
            
            logger.info(f"设备数量: {device_count}")
            logger.info(f"规则数量: {rule_count}")
            logger.info(f"配置数量: {config_count}")
            
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")


def main():
    """主函数"""
    args = parse_arguments()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    # 获取数据库URL
    database_url = get_database_url(args.db_type, args.db_url)
    
    logger.info("=" * 60)
    logger.info("DDC设备匹配系统 - 数据库初始化")
    logger.info("=" * 60)
    logger.info(f"数据库类型: {args.db_type}")
    logger.info(f"数据库URL: {database_url}")
    logger.info(f"强制模式: {'是' if args.force else '否'}")
    logger.info("=" * 60)
    
    # 初始化数据库管理器
    try:
        db_manager = DatabaseManager(database_url, echo=args.verbose)
    except Exception as e:
        logger.error(f"初始化数据库管理器失败: {e}")
        sys.exit(1)
    
    try:
        # 1. 创建表结构
        create_tables(db_manager, force=args.force)
        
        # 2. 检查索引
        create_indexes(db_manager)
        
        # 3. 初始化配置数据
        initialize_config_data(db_manager)
        
        # 4. 打印统计信息
        print_statistics(db_manager)
        
        logger.info("=" * 60)
        logger.info("✓ 数据库初始化完成！")
        logger.info("=" * 60)
        logger.info("下一步:")
        logger.info("  1. 运行 migrate_json_to_db.py 迁移现有JSON数据")
        logger.info("  2. 或运行 import_devices_from_excel.py 导入Excel设备数据")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        sys.exit(1)
    finally:
        # 关闭数据库连接
        db_manager.close()


if __name__ == '__main__':
    main()
