#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本：批量解析现有设备数据

使用批量解析服务从 detailed_params 字段提取信息并更新 key_params 字段。
生成详细的迁移报告，包括成功率、失败案例等统计信息。

验证需求: 10.2, 10.3, 10.4

使用方法:
    python migrate_device_data.py [--dry-run] [--device-ids ID1,ID2,ID3]
    
参数:
    --dry-run: 测试模式，只解析不更新数据库
    --device-ids: 指定要处理的设备ID列表（逗号分隔），不指定则处理所有设备
    
示例:
    # 测试模式，处理所有设备
    python migrate_device_data.py --dry-run
    
    # 正式迁移所有设备
    python migrate_device_data.py
    
    # 只处理指定的设备
    python migrate_device_data.py --device-ids DEV001,DEV002,DEV003
"""

import sys
import os
import argparse
import logging
import json
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# 导入必要的模块
from modules.intelligent_device.device_description_parser import DeviceDescriptionParser
from modules.intelligent_device.configuration_manager import ConfigurationManager
from modules.intelligent_device.batch_parser import BatchParser
from modules.database import DatabaseManager
from config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='批量解析现有设备数据，从 detailed_params 提取信息并更新 key_params 字段',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 测试模式，处理所有设备
  python migrate_device_data.py --dry-run
  
  # 正式迁移所有设备
  python migrate_device_data.py
  
  # 只处理指定的设备
  python migrate_device_data.py --device-ids DEV001,DEV002,DEV003
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='测试模式：只解析不更新数据库'
    )
    
    parser.add_argument(
        '--device-ids',
        type=str,
        help='要处理的设备ID列表（逗号分隔），不指定则处理所有设备'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='migration_report.json',
        help='迁移报告输出文件名（默认: migration_report.json）'
    )
    
    return parser.parse_args()


def initialize_components():
    """初始化系统组件"""
    logger.info("初始化系统组件...")
    
    try:
        # 1. 初始化配置管理器
        config_path = project_root / 'config' / 'device_params.yaml'
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        config_manager = ConfigurationManager(str(config_path))
        logger.info(f"✅ 配置管理器初始化成功: {config_path}")
        
        # 2. 初始化设备描述解析器
        parser = DeviceDescriptionParser(config_manager)
        logger.info("✅ 设备描述解析器初始化成功")
        
        # 3. 初始化数据库管理器
        database_url = Config.DATABASE_URL
        db_manager = DatabaseManager(database_url, echo=False)
        logger.info(f"✅ 数据库管理器初始化成功: {database_url}")
        
        # 4. 初始化批量解析服务
        batch_parser = BatchParser(parser, db_manager)
        logger.info("✅ 批量解析服务初始化成功")
        
        return batch_parser, db_manager
        
    except Exception as e:
        logger.error(f"❌ 系统组件初始化失败: {e}")
        raise


def generate_report(result, output_file, dry_run, device_ids):
    """生成迁移报告"""
    logger.info("\n" + "="*80)
    logger.info("生成迁移报告")
    logger.info("="*80)
    
    # 构建报告数据
    report = {
        'migration_info': {
            'timestamp': datetime.now().isoformat(),
            'dry_run': dry_run,
            'device_ids_filter': device_ids.split(',') if device_ids else None,
            'start_time': result.start_time.isoformat() if result.start_time else None,
            'end_time': result.end_time.isoformat() if result.end_time else None,
            'duration_seconds': result.duration_seconds
        },
        'statistics': {
            'total_devices': result.total,
            'processed': result.processed,
            'successful': result.successful,
            'failed': result.failed,
            'success_rate': result.success_rate,
            'success_rate_percentage': f"{result.success_rate * 100:.2f}%"
        },
        'failed_devices': result.failed_devices
    }
    
    # 保存为 JSON 文件
    output_path = project_root / 'scripts' / output_file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ 迁移报告已保存: {output_path}")
    except Exception as e:
        logger.error(f"❌ 保存迁移报告失败: {e}")
    
    # 打印报告摘要
    logger.info("\n" + "="*80)
    logger.info("迁移报告摘要")
    logger.info("="*80)
    logger.info(f"\n模式: {'测试模式（不更新数据库）' if dry_run else '正式迁移'}")
    logger.info(f"开始时间: {result.start_time}")
    logger.info(f"结束时间: {result.end_time}")
    logger.info(f"总耗时: {result.duration_seconds:.2f} 秒")
    
    logger.info(f"\n统计信息:")
    logger.info(f"  - 设备总数: {result.total}")
    logger.info(f"  - 已处理: {result.processed}")
    logger.info(f"  - 成功: {result.successful}")
    logger.info(f"  - 失败: {result.failed}")
    logger.info(f"  - 成功率: {result.success_rate * 100:.2f}%")
    
    if result.failed_devices:
        logger.info(f"\n失败案例 (共 {len(result.failed_devices)} 个):")
        for idx, failed in enumerate(result.failed_devices[:10], 1):  # 只显示前10个
            logger.info(f"  {idx}. 设备ID: {failed.get('device_id')}")
            logger.info(f"     品牌: {failed.get('brand')}")
            logger.info(f"     名称: {failed.get('device_name')}")
            logger.info(f"     错误: {failed.get('error')}")
        
        if len(result.failed_devices) > 10:
            logger.info(f"  ... 还有 {len(result.failed_devices) - 10} 个失败案例")
        logger.info(f"\n完整失败案例列表请查看报告文件: {output_path}")
    else:
        logger.info("\n✅ 所有设备解析成功！")
    
    logger.info("\n" + "="*80)
    
    return output_path


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    logger.info("="*80)
    logger.info("数据迁移：批量解析现有设备数据")
    logger.info("="*80)
    logger.info(f"\n模式: {'测试模式（不更新数据库）' if args.dry_run else '正式迁移'}")
    
    if args.device_ids:
        logger.info(f"处理设备: {args.device_ids}")
    else:
        logger.info("处理范围: 所有设备")
    
    # 初始化组件
    try:
        batch_parser, db_manager = initialize_components()
    except Exception as e:
        logger.error(f"初始化失败，迁移中止: {e}")
        sys.exit(1)
    
    # 解析设备ID列表
    device_ids_list = None
    if args.device_ids:
        device_ids_list = [id.strip() for id in args.device_ids.split(',')]
        logger.info(f"\n将处理 {len(device_ids_list)} 个指定设备")
    
    # 执行批量解析
    logger.info("\n" + "="*80)
    logger.info("开始批量解析")
    logger.info("="*80)
    
    try:
        result = batch_parser.batch_parse(
            device_ids=device_ids_list,
            dry_run=args.dry_run
        )
        
        logger.info("\n" + "="*80)
        logger.info("✅ 批量解析完成")
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"\n❌ 批量解析失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
    
    finally:
        # 关闭数据库连接
        try:
            db_manager.close()
            logger.info("\n数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {e}")
    
    # 生成迁移报告
    try:
        report_path = generate_report(result, args.output, args.dry_run, args.device_ids)
        
        # 最终提示
        logger.info("\n" + "="*80)
        if args.dry_run:
            logger.info("🎉 测试完成！")
            logger.info("="*80)
            logger.info("\n这是测试模式，数据库未被修改。")
            logger.info("如果结果满意，请去掉 --dry-run 参数执行正式迁移。")
        else:
            logger.info("🎉 迁移成功完成！")
            logger.info("="*80)
            logger.info(f"\n成功迁移 {result.successful} 个设备")
            if result.failed > 0:
                logger.info(f"失败 {result.failed} 个设备，请查看报告了解详情")
        
        logger.info(f"\n详细报告: {report_path}")
        logger.info("\n" + "="*80)
        
    except Exception as e:
        logger.error(f"生成报告失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
