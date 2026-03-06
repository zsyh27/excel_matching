#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
为旧设备数据推断device_type
根据设备名称中的关键词匹配设备类型

验证需求: 37.1-37.5
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import logging
import yaml

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.database import DatabaseManager
from modules.models import Device as DeviceModel

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_device_type_keywords(config_path: str = None) -> dict:
    """
    加载设备类型关键词配置
    
    Args:
        config_path: 配置文件路径，默认为 backend/config/device_params.yaml
        
    Returns:
        设备类型关键词映射字典 {device_type: [keywords]}
        
    验证需求: 37.1
    """
    if config_path is None:
        config_path = project_root / 'config' / 'device_params.yaml'
    
    logger.info(f"加载设备类型配置: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 构建关键词映射
        keywords_map = {}
        device_types = config.get('device_types', {})
        
        for device_type, type_config in device_types.items():
            keywords = type_config.get('keywords', [])
            if keywords:
                keywords_map[device_type] = keywords
                logger.debug(f"  {device_type}: {len(keywords)} 个关键词")
        
        logger.info(f"✅ 成功加载 {len(keywords_map)} 种设备类型配置")
        return keywords_map
        
    except FileNotFoundError:
        logger.error(f"❌ 配置文件不存在: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"❌ 配置文件格式错误: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ 加载配置文件失败: {e}")
        raise


def infer_device_type(device_name: str, keywords_map: dict) -> str:
    """
    根据设备名称推断设备类型
    
    Args:
        device_name: 设备名称
        keywords_map: 设备类型关键词映射
        
    Returns:
        推断的设备类型，如果无法推断则返回 None
        
    验证需求: 37.2
    """
    if not device_name:
        return None
    
    # 遍历所有设备类型，检查关键词是否在设备名称中
    for device_type, keywords in keywords_map.items():
        for keyword in keywords:
            if keyword in device_name:
                return device_type
    
    return None


def infer_device_types(database_url: str = None, batch_size: int = 100) -> dict:
    """
    为旧设备批量推断device_type
    
    Args:
        database_url: 数据库连接URL，默认为 sqlite:///data/devices.db
        batch_size: 批量更新大小
        
    Returns:
        统计信息字典 {
            'total': 总设备数,
            'success': 推断成功数,
            'failed': 推断失败数,
            'failed_devices': 推断失败的设备列表
        }
        
    验证需求: 37.1-37.5
    """
    if database_url is None:
        database_url = f"sqlite:///{project_root / 'data' / 'devices.db'}"
    
    logger.info("=" * 60)
    logger.info("开始为旧设备推断device_type")
    logger.info("=" * 60)
    
    # 加载设备类型关键词配置
    keywords_map = load_device_type_keywords()
    
    # 初始化数据库管理器
    db_manager = DatabaseManager(database_url)
    
    # 统计信息
    stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'failed_devices': []
    }
    
    try:
        with db_manager.session_scope() as session:
            # 查询所有device_type为空的设备
            logger.info("\n查询需要推断device_type的设备...")
            old_devices = session.query(DeviceModel).filter(
                DeviceModel.device_type == None
            ).all()
            
            stats['total'] = len(old_devices)
            logger.info(f"找到 {stats['total']} 个需要推断device_type的设备\n")
            
            if stats['total'] == 0:
                logger.info("✅ 所有设备都已有device_type，无需推断")
                return stats
            
            # 批量推断和更新
            logger.info("开始推断device_type...")
            logger.info("-" * 60)
            
            for i, device in enumerate(old_devices, 1):
                # 根据device_name推断device_type
                device_type = infer_device_type(device.device_name, keywords_map)
                
                if device_type:
                    # 推断成功，更新设备
                    device.device_type = device_type
                    device.updated_at = datetime.utcnow()
                    stats['success'] += 1
                    logger.info(f"  [{i}/{stats['total']}] ✅ {device.device_id}: {device.device_name} -> {device_type}")
                else:
                    # 推断失败
                    stats['failed'] += 1
                    stats['failed_devices'].append({
                        'device_id': device.device_id,
                        'device_name': device.device_name,
                        'brand': device.brand
                    })
                    logger.warning(f"  [{i}/{stats['total']}] ⚠️  {device.device_id}: {device.device_name} -> 无法推断")
                
                # 批量提交
                if i % batch_size == 0:
                    session.commit()
                    logger.info(f"  已提交 {i} 个设备的更新")
            
            # 提交剩余的更新
            session.commit()
            
        logger.info("-" * 60)
        logger.info("\n✅ device_type推断完成")
        logger.info("=" * 60)
        logger.info("推断统计信息:")
        logger.info(f"  - 总设备数: {stats['total']}")
        logger.info(f"  - 推断成功: {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
        logger.info(f"  - 推断失败: {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)")
        logger.info("=" * 60)
        
        # 输出推断失败的设备列表
        if stats['failed'] > 0:
            logger.info("\n推断失败的设备列表:")
            logger.info("-" * 60)
            for device in stats['failed_devices']:
                logger.info(f"  - {device['device_id']}: {device['device_name']} ({device['brand']})")
            logger.info("-" * 60)
            logger.info("\n💡 提示: 这些设备需要手动设置device_type")
        
        return stats
        
    except Exception as e:
        logger.error(f"\n❌ device_type推断失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None
    finally:
        db_manager.close()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='为旧设备推断device_type')
    parser.add_argument(
        '--database-url',
        type=str,
        default=None,
        help='数据库连接URL (默认: sqlite:///data/devices.db)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='批量更新大小 (默认: 100)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='仅显示推断结果，不更新数据库'
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("⚠️  DRY RUN 模式: 仅显示推断结果，不更新数据库\n")
        # TODO: 实现 dry-run 模式
        logger.warning("DRY RUN 模式尚未实现")
        return 1
    
    # 执行推断
    stats = infer_device_types(
        database_url=args.database_url,
        batch_size=args.batch_size
    )
    
    if stats is None:
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
