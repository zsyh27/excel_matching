#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：添加智能设备录入系统字段

为 devices 表添加以下字段：
- raw_description: TEXT - 用户输入的原始设备描述文本
- key_params: JSON - 根据设备类型提取的关键参数（JSON格式）
- confidence_score: FLOAT - 解析结果的置信度评分（0.0-1.0）

同时创建相应的索引以优化查询性能。

验证需求: 8.1, 8.2, 8.3, 8.5
"""

import sys
import os
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_database_path():
    """获取数据库文件路径"""
    # 脚本所在目录的父目录的父目录是项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    db_path = project_root / 'data' / 'devices.db'
    return db_path


def check_column_exists(cursor, table_name, column_name):
    """检查列是否已存在"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    return column_name in column_names


def check_index_exists(cursor, index_name):
    """检查索引是否已存在"""
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name=?",
        (index_name,)
    )
    return cursor.fetchone() is not None


def backup_database(db_path):
    """备份数据库"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = db_path.parent / f"devices_backup_{timestamp}.db"
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        logger.info(f"✅ 数据库备份成功: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"❌ 数据库备份失败: {e}")
        raise


def add_columns(cursor):
    """添加新字段"""
    columns_to_add = [
        {
            'name': 'raw_description',
            'type': 'TEXT',
            'comment': '用户输入的原始设备描述文本'
        },
        {
            'name': 'key_params',
            'type': 'TEXT',  # SQLite 使用 TEXT 存储 JSON
            'comment': '根据设备类型提取的关键参数（JSON格式）'
        },
        {
            'name': 'confidence_score',
            'type': 'REAL',  # SQLite 使用 REAL 存储浮点数
            'comment': '解析结果的置信度评分（0.0-1.0）'
        }
    ]
    
    added_columns = []
    
    for column in columns_to_add:
        column_name = column['name']
        column_type = column['type']
        comment = column['comment']
        
        # 检查列是否已存在
        if check_column_exists(cursor, 'devices', column_name):
            logger.info(f"⚠️  列 '{column_name}' 已存在，跳过")
            continue
        
        # 添加列
        try:
            sql = f"ALTER TABLE devices ADD COLUMN {column_name} {column_type}"
            cursor.execute(sql)
            logger.info(f"✅ 添加列: {column_name} ({column_type}) - {comment}")
            added_columns.append(column_name)
        except sqlite3.OperationalError as e:
            logger.error(f"❌ 添加列 '{column_name}' 失败: {e}")
            raise
    
    return added_columns


def create_indexes(cursor):
    """创建索引"""
    indexes_to_create = [
        {
            'name': 'idx_devices_device_type',
            'table': 'devices',
            'column': 'device_name',  # 使用 device_name 作为设备类型的代理
            'comment': '设备类型索引（使用device_name）'
        },
        {
            'name': 'idx_devices_brand',
            'table': 'devices',
            'column': 'brand',
            'comment': '品牌索引'
        },
        {
            'name': 'idx_devices_confidence_score',
            'table': 'devices',
            'column': 'confidence_score',
            'comment': '置信度评分索引'
        }
    ]
    
    created_indexes = []
    
    for index in indexes_to_create:
        index_name = index['name']
        table = index['table']
        column = index['column']
        comment = index['comment']
        
        # 检查索引是否已存在
        if check_index_exists(cursor, index_name):
            logger.info(f"⚠️  索引 '{index_name}' 已存在，跳过")
            continue
        
        # 创建索引
        try:
            sql = f"CREATE INDEX {index_name} ON {table}({column})"
            cursor.execute(sql)
            logger.info(f"✅ 创建索引: {index_name} ON {table}({column}) - {comment}")
            created_indexes.append(index_name)
        except sqlite3.OperationalError as e:
            logger.error(f"❌ 创建索引 '{index_name}' 失败: {e}")
            raise
    
    # 注意：SQLite 不支持 GIN 索引（PostgreSQL 特性）
    # key_params 字段的 JSON 查询在 SQLite 中需要使用 JSON 函数
    logger.info("ℹ️  注意: SQLite 不支持 GIN 索引，key_params 的 JSON 查询需使用 JSON 函数")
    
    return created_indexes


def verify_migration(cursor):
    """验证迁移结果"""
    logger.info("\n" + "="*60)
    logger.info("验证迁移结果")
    logger.info("="*60)
    
    # 检查表结构
    cursor.execute("PRAGMA table_info(devices)")
    columns = cursor.fetchall()
    
    logger.info("\n当前 devices 表结构:")
    for col in columns:
        col_id, name, col_type, not_null, default_val, pk = col
        logger.info(f"  - {name}: {col_type} (NOT NULL: {bool(not_null)}, PK: {bool(pk)})")
    
    # 检查新字段是否存在
    column_names = [col[1] for col in columns]
    required_columns = ['raw_description', 'key_params', 'confidence_score']
    
    missing_columns = [col for col in required_columns if col not in column_names]
    if missing_columns:
        logger.error(f"❌ 缺少字段: {', '.join(missing_columns)}")
        return False
    else:
        logger.info(f"✅ 所有必需字段已存在: {', '.join(required_columns)}")
    
    # 检查索引
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='devices'")
    indexes = cursor.fetchall()
    
    logger.info("\n当前 devices 表索引:")
    for idx in indexes:
        logger.info(f"  - {idx[0]}")
    
    # 检查数据完整性
    cursor.execute("SELECT COUNT(*) FROM devices")
    device_count = cursor.fetchone()[0]
    logger.info(f"\n设备总数: {device_count}")
    
    # 检查新字段的数据
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(raw_description) as has_raw_desc,
            COUNT(key_params) as has_key_params,
            COUNT(confidence_score) as has_confidence
        FROM devices
    """)
    stats = cursor.fetchone()
    logger.info(f"\n新字段数据统计:")
    logger.info(f"  - 总记录数: {stats[0]}")
    logger.info(f"  - 有 raw_description: {stats[1]}")
    logger.info(f"  - 有 key_params: {stats[2]}")
    logger.info(f"  - 有 confidence_score: {stats[3]}")
    
    logger.info("\n" + "="*60)
    logger.info("✅ 迁移验证完成")
    logger.info("="*60)
    
    return True


def main():
    """主函数"""
    logger.info("="*60)
    logger.info("数据库迁移：添加智能设备录入系统字段")
    logger.info("="*60)
    
    # 获取数据库路径
    db_path = get_database_path()
    
    if not db_path.exists():
        logger.error(f"❌ 数据库文件不存在: {db_path}")
        logger.info("提示: 请先运行 init_database.py 初始化数据库")
        sys.exit(1)
    
    logger.info(f"\n数据库路径: {db_path}")
    
    # 备份数据库
    logger.info("\n步骤 1: 备份数据库")
    try:
        backup_path = backup_database(db_path)
    except Exception as e:
        logger.error(f"备份失败，迁移中止: {e}")
        sys.exit(1)
    
    # 连接数据库
    logger.info("\n步骤 2: 连接数据库")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        logger.info("✅ 数据库连接成功")
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        sys.exit(1)
    
    try:
        # 添加字段
        logger.info("\n步骤 3: 添加新字段")
        added_columns = add_columns(cursor)
        
        # 创建索引
        logger.info("\n步骤 4: 创建索引")
        created_indexes = create_indexes(cursor)
        
        # 提交事务
        logger.info("\n步骤 5: 提交事务")
        conn.commit()
        logger.info("✅ 事务提交成功")
        
        # 验证迁移
        logger.info("\n步骤 6: 验证迁移结果")
        if verify_migration(cursor):
            logger.info("\n" + "="*60)
            logger.info("🎉 迁移成功完成！")
            logger.info("="*60)
            logger.info(f"\n添加的字段: {', '.join(added_columns) if added_columns else '无（已存在）'}")
            logger.info(f"创建的索引: {', '.join(created_indexes) if created_indexes else '无（已存在）'}")
            logger.info(f"\n备份文件: {backup_path}")
        else:
            logger.error("\n❌ 迁移验证失败")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"\n❌ 迁移失败: {e}")
        logger.info("正在回滚事务...")
        conn.rollback()
        logger.info("✅ 事务已回滚")
        logger.info(f"\n可以从备份恢复: {backup_path}")
        sys.exit(1)
    
    finally:
        # 关闭连接
        cursor.close()
        conn.close()
        logger.info("\n数据库连接已关闭")


if __name__ == '__main__':
    main()
