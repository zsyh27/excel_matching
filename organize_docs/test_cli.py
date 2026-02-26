"""
CLI 测试

测试命令行接口的基本功能
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from io import StringIO
from unittest.mock import patch

import pytest

from .cli import cmd_validate, cmd_list_backups, cmd_organize, cmd_restore
from .config_manager import ConfigManager


class Args:
    """模拟命令行参数对象"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def test_cmd_validate_with_valid_config(tmp_path):
    """测试验证有效配置"""
    # 创建配置文件
    config_manager = ConfigManager()
    config_path = tmp_path / "test_config.json"
    config_manager.save_default_config(str(config_path))
    
    # 创建参数对象
    args = Args(
        config=str(config_path),
        verbose=False
    )
    
    # 执行验证命令
    exit_code = cmd_validate(args)
    
    # 验证返回码
    assert exit_code == 0


def test_cmd_validate_with_invalid_config(tmp_path):
    """测试验证无效配置"""
    # 创建无效的配置文件（路径格式错误）
    config_path = tmp_path / "invalid_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        # 使用无效的路径格式（包含非法字符）
        f.write('''{
            "classification": {
                "core_documents": [],
                "archive_keywords": [],
                "development_keywords": [],
                "exclude_patterns": []
            },
            "directory_structure": {
                "docs_root": "",
                "archive_dir": "docs/archive",
                "development_dir": "docs/development"
            }
        }''')
    
    # 创建参数对象
    args = Args(
        config=str(config_path),
        verbose=False
    )
    
    # 执行验证命令
    exit_code = cmd_validate(args)
    
    # 验证返回码（应该失败，因为 docs_root 为空）
    assert exit_code == 1


def test_cmd_validate_with_nonexistent_config(tmp_path):
    """测试验证不存在的配置文件"""
    # 创建参数对象
    args = Args(
        config=str(tmp_path / "nonexistent.json"),
        verbose=False
    )
    
    # 执行验证命令
    exit_code = cmd_validate(args)
    
    # 验证返回码（应该失败）
    assert exit_code == 1


def test_cmd_list_backups_with_no_backups(tmp_path):
    """测试列出备份（没有备份）"""
    # 创建配置文件
    config_manager = ConfigManager()
    config_path = tmp_path / "test_config.json"
    config_manager.save_default_config(str(config_path))
    
    # 修改备份目录为临时目录
    import json
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    config_data['backup']['backup_dir'] = str(tmp_path / "backups")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f)
    
    # 创建参数对象
    args = Args(
        config=str(config_path),
        verbose=False
    )
    
    # 执行列出备份命令
    exit_code = cmd_list_backups(args)
    
    # 验证返回码
    assert exit_code == 0


def test_cmd_organize_dry_run(tmp_path):
    """测试整理命令（试运行模式）"""
    # 创建测试项目结构
    project_root = tmp_path / "project"
    project_root.mkdir()
    
    # 创建一些测试文档
    (project_root / "README.md").write_text("# README", encoding='utf-8')
    (project_root / "TASK_1_SUMMARY.md").write_text("# Task 1", encoding='utf-8')
    
    # 创建配置文件
    config_manager = ConfigManager()
    config_path = project_root / "config.json"
    config_manager.save_default_config(str(config_path))
    
    # 修改备份目录为相对路径
    import json
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    config_data['backup']['backup_dir'] = ".backup/docs"  # 使用相对路径
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f)
    
    # 创建参数对象
    args = Args(
        config=str(config_path),
        project_root=str(project_root),
        dry_run=True,
        yes=True
    )
    
    # 执行整理命令
    exit_code = cmd_organize(args)
    
    # 验证返回码
    assert exit_code == 0
    
    # 验证文件没有被移动（试运行模式）
    assert (project_root / "README.md").exists()
    assert (project_root / "TASK_1_SUMMARY.md").exists()


def test_cmd_restore_without_backup_id(tmp_path):
    """测试恢复命令（不指定备份 ID）"""
    # 创建配置文件
    config_manager = ConfigManager()
    config_path = tmp_path / "test_config.json"
    config_manager.save_default_config(str(config_path))
    
    # 修改备份目录
    import json
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    config_data['backup']['backup_dir'] = str(tmp_path / "backups")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f)
    
    # 创建参数对象
    args = Args(
        config=str(config_path),
        project_root=str(tmp_path),
        backup_id=None,
        yes=True
    )
    
    # 执行恢复命令
    exit_code = cmd_restore(args)
    
    # 验证返回码（没有备份时应该返回 1）
    assert exit_code == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
