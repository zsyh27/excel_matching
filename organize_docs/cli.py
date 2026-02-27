"""
命令行接口

提供文档整理工具的命令行接口，支持以下命令：
- organize: 执行文档整理
- restore: 从备份恢复
- list-backups: 列出所有备份
- validate: 验证配置文件
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .config_manager import ConfigManager
from .organizer import DocumentOrganizer
from .backup_manager import BackupManager
from .models import BackupInfo


def cmd_organize(args) -> int:
    """
    执行文档整理命令
    
    参数:
        args: 命令行参数
    
    返回:
        退出码（0 表示成功，1 表示失败）
    """
    print("=" * 60)
    print("文档整理工具 - 整理模式")
    print("=" * 60)
    
    try:
        # 加载配置
        config_manager = ConfigManager()
        config = config_manager.load_config(args.config)
        
        # 验证配置
        validation = config_manager.validate_config(config)
        if not validation.valid:
            print("\n配置验证失败:")
            for error in validation.errors:
                print(f"  ✗ {error}")
            return 1
        
        if validation.warnings:
            print("\n配置警告:")
            for warning in validation.warnings:
                print(f"  ⚠ {warning}")
        
        # 创建整理器
        organizer = DocumentOrganizer(config, args.project_root)
        
        # 执行整理
        print(f"\n项目根目录: {args.project_root}")
        print(f"配置文件: {args.config}")
        print(f"试运行模式: {args.dry_run}")
        
        if args.dry_run:
            print("\n⚠ 试运行模式：不会实际移动文件，仅显示将要执行的操作")
        
        if not args.yes and not args.dry_run:
            response = input("\n是否继续执行整理操作？(y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("操作已取消")
                return 0
        
        print("\n开始整理...")
        result = organizer.organize(dry_run=args.dry_run)
        
        # 输出结果
        print("\n" + str(result))
        
        # 清理资源
        organizer.cleanup()
        
        return 0 if result.success else 1
        
    except FileNotFoundError as e:
        print(f"\n错误: {e}")
        return 1
    except Exception as e:
        print(f"\n未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_restore(args) -> int:
    """
    从备份恢复命令
    
    参数:
        args: 命令行参数
    
    返回:
        退出码（0 表示成功，1 表示失败）
    """
    print("=" * 60)
    print("文档整理工具 - 恢复模式")
    print("=" * 60)
    
    try:
        # 加载配置以获取备份目录
        config_manager = ConfigManager()
        config = config_manager.load_config(args.config)
        
        # 创建备份管理器
        backup_manager = BackupManager(config.backup.backup_dir)
        
        # 如果没有指定备份 ID，列出所有备份
        if not args.backup_id:
            backups = backup_manager.list_backups()
            if not backups:
                print("\n没有可用的备份")
                return 1
            
            print("\n可用的备份:")
            for i, backup in enumerate(backups, 1):
                print(f"\n{i}. 备份 ID: {backup.backup_id}")
                print(f"   时间: {backup.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   文档数量: {backup.document_count}")
                print(f"   路径: {backup.backup_path}")
            
            print("\n请使用 --backup-id 参数指定要恢复的备份 ID")
            return 0
        
        # 查找指定的备份
        backups = backup_manager.list_backups()
        backup_info = None
        for backup in backups:
            if backup.backup_id == args.backup_id:
                backup_info = backup
                break
        
        if not backup_info:
            print(f"\n错误: 找不到备份 ID: {args.backup_id}")
            return 1
        
        # 显示备份信息
        print(f"\n备份信息:")
        print(f"  ID: {backup_info.backup_id}")
        print(f"  时间: {backup_info.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  文档数量: {backup_info.document_count}")
        print(f"  路径: {backup_info.backup_path}")
        
        # 确认恢复
        if not args.yes:
            print("\n⚠ 警告: 恢复操作将覆盖当前文档")
            response = input("是否继续执行恢复操作？(y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("操作已取消")
                return 0
        
        # 执行恢复
        print("\n开始恢复...")
        restore_result = backup_manager.restore_from_backup(
            backup_info,
            args.project_root
        )
        
        # 输出结果
        print("\n" + "=" * 60)
        print("恢复结果")
        print("=" * 60)
        print(f"状态: {'成功' if restore_result.success else '失败'}")
        print(f"恢复文档数: {restore_result.restored_count}")
        
        if restore_result.failed_documents:
            print(f"\n失败的文档 ({len(restore_result.failed_documents)}):")
            for doc in restore_result.failed_documents:
                print(f"  - {doc}")
        
        if restore_result.error_message:
            print(f"\n错误: {restore_result.error_message}")
        
        print("=" * 60)
        
        return 0 if restore_result.success else 1
        
    except FileNotFoundError as e:
        print(f"\n错误: {e}")
        return 1
    except Exception as e:
        print(f"\n未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_list_backups(args) -> int:
    """
    列出所有备份命令
    
    参数:
        args: 命令行参数
    
    返回:
        退出码（0 表示成功，1 表示失败）
    """
    print("=" * 60)
    print("文档整理工具 - 备份列表")
    print("=" * 60)
    
    try:
        # 加载配置以获取备份目录
        config_manager = ConfigManager()
        config = config_manager.load_config(args.config)
        
        # 创建备份管理器
        backup_manager = BackupManager(config.backup.backup_dir)
        
        # 列出所有备份
        backups = backup_manager.list_backups()
        
        if not backups:
            print("\n没有可用的备份")
            return 0
        
        print(f"\n找到 {len(backups)} 个备份:\n")
        
        for i, backup in enumerate(backups, 1):
            print(f"{i}. 备份 ID: {backup.backup_id}")
            print(f"   时间: {backup.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   文档数量: {backup.document_count}")
            print(f"   路径: {backup.backup_path}")
            
            if args.verbose:
                print(f"   文档列表:")
                for doc in backup.manifest[:10]:  # 只显示前 10 个
                    if "error" in doc:
                        print(f"     - {doc['file_name']} (备份失败)")
                    else:
                        print(f"     - {doc['file_name']}")
                
                if len(backup.manifest) > 10:
                    print(f"     ... 还有 {len(backup.manifest) - 10} 个文档")
            
            print()
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n错误: {e}")
        return 1
    except Exception as e:
        print(f"\n未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_validate(args) -> int:
    """
    验证配置文件命令
    
    参数:
        args: 命令行参数
    
    返回:
        退出码（0 表示成功，1 表示失败）
    """
    print("=" * 60)
    print("文档整理工具 - 配置验证")
    print("=" * 60)
    
    try:
        # 加载配置
        config_manager = ConfigManager()
        print(f"\n加载配置文件: {args.config}")
        config = config_manager.load_config(args.config)
        print("✓ 配置文件加载成功")
        
        # 验证配置
        print("\n验证配置...")
        validation = config_manager.validate_config(config)
        
        # 输出验证结果
        print("\n" + "=" * 60)
        print("验证结果")
        print("=" * 60)
        print(f"状态: {'✓ 通过' if validation.valid else '✗ 失败'}")
        
        if validation.errors:
            print(f"\n错误 ({len(validation.errors)}):")
            for error in validation.errors:
                print(f"  ✗ {error}")
        
        if validation.warnings:
            print(f"\n警告 ({len(validation.warnings)}):")
            for warning in validation.warnings:
                print(f"  ⚠ {warning}")
        
        if validation.valid and not validation.warnings:
            print("\n配置文件完全有效，没有错误或警告")
        
        # 显示配置摘要
        if args.verbose:
            print("\n" + "=" * 60)
            print("配置摘要")
            print("=" * 60)
            print(f"\n核心文档 ({len(config.classification.core_file_names)}):")
            for name in config.classification.core_file_names:
                print(f"  - {name}")
            
            print(f"\n归档关键词 ({len(config.classification.archive_keywords)}):")
            for keyword in config.classification.archive_keywords[:10]:
                print(f"  - {keyword}")
            if len(config.classification.archive_keywords) > 10:
                print(f"  ... 还有 {len(config.classification.archive_keywords) - 10} 个")
            
            print(f"\n开发文档关键词 ({len(config.classification.development_keywords)}):")
            for keyword in config.classification.development_keywords:
                print(f"  - {keyword}")
            
            print(f"\n目录结构:")
            print(f"  文档根目录: {config.directory_structure.docs_root}")
            print(f"  归档目录: {config.directory_structure.archive_dir}")
            print(f"  开发文档目录: {config.directory_structure.development_dir}")
            print(f"  后端文档目录: {config.directory_structure.backend_docs_dir}")
            print(f"  前端文档目录: {config.directory_structure.frontend_docs_dir}")
            
            print(f"\n备份配置:")
            print(f"  启用: {config.backup.enabled}")
            print(f"  备份目录: {config.backup.backup_dir}")
            print(f"  保留备份数: {config.backup.keep_backups}")
        
        print("=" * 60)
        
        return 0 if validation.valid else 1
        
    except FileNotFoundError as e:
        print(f"\n错误: {e}")
        return 1
    except Exception as e:
        print(f"\n未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="文档整理工具 - 自动整理项目中的 MD 文档",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 执行文档整理（试运行）
  python -m organize_docs.cli organize --dry-run
  
  # 执行文档整理（实际操作）
  python -m organize_docs.cli organize --yes
  
  # 列出所有备份
  python -m organize_docs.cli list-backups
  
  # 从备份恢复
  python -m organize_docs.cli restore --backup-id backup_20240212_143022_abc123
  
  # 验证配置文件
  python -m organize_docs.cli validate
  
  # 使用自定义配置文件
  python -m organize_docs.cli organize --config my_config.json
        """
    )
    
    # 全局参数
    parser.add_argument(
        '--config',
        default='scripts/organization_config.json',
        help='配置文件路径（默认: scripts/organization_config.json）'
    )
    
    parser.add_argument(
        '--project-root',
        default='.',
        help='项目根目录路径（默认: 当前目录）'
    )
    
    # 子命令
    subparsers = parser.add_subparsers(
        title='命令',
        description='可用的命令',
        dest='command',
        required=True
    )
    
    # organize 命令
    organize_parser = subparsers.add_parser(
        'organize',
        help='执行文档整理',
        description='扫描、分类、备份和移动文档到目标目录'
    )
    organize_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行模式，不实际移动文件'
    )
    organize_parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='跳过确认提示，直接执行'
    )
    organize_parser.set_defaults(func=cmd_organize)
    
    # restore 命令
    restore_parser = subparsers.add_parser(
        'restore',
        help='从备份恢复',
        description='从指定的备份恢复文档到原始位置'
    )
    restore_parser.add_argument(
        '--backup-id',
        help='备份 ID（如果不指定，将列出所有可用备份）'
    )
    restore_parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='跳过确认提示，直接执行'
    )
    restore_parser.set_defaults(func=cmd_restore)
    
    # list-backups 命令
    list_backups_parser = subparsers.add_parser(
        'list-backups',
        help='列出所有备份',
        description='显示所有可用的备份及其详细信息'
    )
    list_backups_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细信息（包括文档列表）'
    )
    list_backups_parser.set_defaults(func=cmd_list_backups)
    
    # validate 命令
    validate_parser = subparsers.add_parser(
        'validate',
        help='验证配置文件',
        description='检查配置文件的格式和内容是否有效'
    )
    validate_parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细的配置摘要'
    )
    validate_parser.set_defaults(func=cmd_validate)
    
    # 解析参数
    args = parser.parse_args()
    
    # 执行对应的命令
    exit_code = args.func(args)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
