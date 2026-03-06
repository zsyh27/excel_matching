#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：将价格字段从Float转换为Integer

执行步骤：
1. 读取所有设备的价格
2. 将浮点数价格转换为整数（四舍五入）
3. 更新数据库表结构
4. 更新所有设备的价格为整数
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, Integer, Float, Column, MetaData, Table, text
from sqlalchemy.orm import sessionmaker
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_price_to_integer():
    """将价格字段从Float转换为Integer"""
    
    # 创建数据库连接
    engine = create_engine(Config.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        logger.info("开始迁移价格字段...")
        
        # 1. 读取所有设备并转换价格
        result = session.execute(text("SELECT device_id, unit_price FROM devices"))
        devices = result.fetchall()
        
        logger.info(f"找到 {len(devices)} 个设备")
        
        # 2. 更新每个设备的价格为整数
        updated_count = 0
        for device_id, unit_price in devices:
            if unit_price is not None:
                # 四舍五入转换为整数
                new_price = int(round(unit_price))
                session.execute(
                    text("UPDATE devices SET unit_price = :new_price WHERE device_id = :device_id"),
                    {"new_price": new_price, "device_id": device_id}
                )
                updated_count += 1
                
                if updated_count % 100 == 0:
                    logger.info(f"已更新 {updated_count} 个设备...")
        
        session.commit()
        logger.info(f"✓ 成功更新 {updated_count} 个设备的价格")
        
        # 3. 修改表结构（SQLite不支持直接修改列类型，需要重建表）
        logger.info("开始修改表结构...")
        
        # 对于SQLite，我们需要：
        # a. 创建新表
        # b. 复制数据
        # c. 删除旧表
        # d. 重命名新表
        
        # 检查数据库类型
        if 'sqlite' in Config.DATABASE_URL.lower():
            logger.info("检测到SQLite数据库，使用表重建方式...")
            
            # 创建临时表
            session.execute(text("""
                CREATE TABLE devices_new (
                    device_id VARCHAR(100) PRIMARY KEY,
                    brand VARCHAR(50) NOT NULL,
                    device_name VARCHAR(100) NOT NULL,
                    spec_model VARCHAR(200) NOT NULL,
                    device_type VARCHAR(50),
                    detailed_params TEXT,
                    unit_price INTEGER NOT NULL,
                    raw_description TEXT,
                    key_params JSON,
                    confidence_score FLOAT,
                    input_method VARCHAR(20) DEFAULT 'manual',
                    created_at DATETIME,
                    updated_at DATETIME
                )
            """))
            
            # 复制数据
            session.execute(text("""
                INSERT INTO devices_new 
                SELECT device_id, brand, device_name, spec_model, device_type,
                       detailed_params, unit_price, raw_description, key_params,
                       confidence_score, input_method, created_at, updated_at
                FROM devices
            """))
            
            # 删除旧表
            session.execute(text("DROP TABLE devices"))
            
            # 重命名新表
            session.execute(text("ALTER TABLE devices_new RENAME TO devices"))
            
            # 重建索引
            session.execute(text("CREATE INDEX idx_devices_brand ON devices(brand)"))
            session.execute(text("CREATE INDEX idx_devices_device_name ON devices(device_name)"))
            session.execute(text("CREATE INDEX idx_devices_device_type ON devices(device_type)"))
            session.execute(text("CREATE INDEX idx_devices_confidence_score ON devices(confidence_score)"))
            session.execute(text("CREATE INDEX idx_devices_input_method ON devices(input_method)"))
            
            session.commit()
            logger.info("✓ 表结构修改完成")
        else:
            # 对于其他数据库（如PostgreSQL、MySQL），可以直接修改列类型
            logger.info("使用ALTER TABLE修改列类型...")
            session.execute(text("ALTER TABLE devices ALTER COLUMN unit_price TYPE INTEGER"))
            session.commit()
            logger.info("✓ 表结构修改完成")
        
        logger.info("✓ 价格字段迁移完成！")
        
    except Exception as e:
        logger.error(f"迁移失败: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("价格字段迁移脚本")
    logger.info("=" * 60)
    
    # 确认执行
    response = input("此操作将修改数据库表结构，是否继续？(yes/no): ")
    if response.lower() != 'yes':
        logger.info("操作已取消")
        sys.exit(0)
    
    try:
        migrate_price_to_integer()
        logger.info("\n迁移成功完成！")
    except Exception as e:
        logger.error(f"\n迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
