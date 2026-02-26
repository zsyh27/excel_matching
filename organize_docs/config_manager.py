"""
配置管理器

负责加载、验证和管理文档整理配置。
"""

import json
from pathlib import Path
from typing import Optional

from .models import (
    OrganizationConfig,
    ClassificationConfig,
    DirectoryStructure,
    ArchiveGrouping,
    BackupConfig,
    IndexGenerationConfig,
    ValidationResult
)


class ConfigManager:
    """配置管理器"""
    
    def load_config(self, config_path: str) -> OrganizationConfig:
        """
        加载配置文件
        
        参数:
            config_path: 配置文件路径
        
        返回:
            配置对象
        
        异常:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: JSON 格式错误
            ValueError: 配置格式不正确
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        return self._parse_config(config_data)
    
    def _parse_config(self, config_data: dict) -> OrganizationConfig:
        """
        解析配置数据
        
        参数:
            config_data: 配置字典
        
        返回:
            配置对象
        """
        # 解析分类配置
        classification_data = config_data.get('classification', {})
        classification = ClassificationConfig(
            core_file_names=classification_data.get('core_documents', []),
            core_directories=classification_data.get('core_directories', []),
            archive_keywords=classification_data.get('archive_keywords', []),
            development_keywords=classification_data.get('development_keywords', []),
            exclude_patterns=classification_data.get('exclude_patterns', [])
        )
        
        # 解析目录结构配置
        dir_structure_data = config_data.get('directory_structure', {})
        directory_structure = DirectoryStructure(
            docs_root=dir_structure_data.get('docs_root', 'docs'),
            archive_dir=dir_structure_data.get('archive_dir', 'docs/archive'),
            development_dir=dir_structure_data.get('development_dir', 'docs/development'),
            backend_docs_dir=dir_structure_data.get('backend_docs_dir', 'backend/docs'),
            frontend_docs_dir=dir_structure_data.get('frontend_docs_dir', 'frontend/docs')
        )
        
        # 解析归档分组配置
        archive_grouping_data = config_data.get('archive_grouping', {})
        archive_grouping = ArchiveGrouping(groups=archive_grouping_data)
        
        # 解析备份配置
        backup_data = config_data.get('backup', {})
        backup = BackupConfig(
            enabled=backup_data.get('enabled', True),
            backup_dir=backup_data.get('backup_dir', '.backup/docs'),
            keep_backups=backup_data.get('keep_backups', 5)
        )
        
        # 解析索引生成配置
        index_gen_data = config_data.get('index_generation', {})
        index_generation = IndexGenerationConfig(
            include_file_size=index_gen_data.get('include_file_size', True),
            include_modified_date=index_gen_data.get('include_modified_date', True),
            include_description=index_gen_data.get('include_description', True),
            max_description_length=index_gen_data.get('max_description_length', 100)
        )
        
        return OrganizationConfig(
            classification=classification,
            directory_structure=directory_structure,
            archive_grouping=archive_grouping,
            backup=backup,
            index_generation=index_generation
        )
    
    def validate_config(self, config: OrganizationConfig) -> ValidationResult:
        """
        验证配置有效性
        
        参数:
            config: 配置对象
        
        返回:
            验证结果
        """
        errors = []
        warnings = []
        
        # 验证必需字段存在
        if not hasattr(config, 'classification') or config.classification is None:
            errors.append("缺少必需字段: classification")
            return ValidationResult(valid=False, errors=errors, warnings=warnings)
        
        if not hasattr(config, 'directory_structure') or config.directory_structure is None:
            errors.append("缺少必需字段: directory_structure")
            return ValidationResult(valid=False, errors=errors, warnings=warnings)
        
        # 验证字段类型正确
        if not isinstance(config.classification.core_file_names, list):
            errors.append("core_file_names 必须是列表类型")
        
        if not isinstance(config.classification.archive_keywords, list):
            errors.append("archive_keywords 必须是列表类型")
        
        if not isinstance(config.classification.development_keywords, list):
            errors.append("development_keywords 必须是列表类型")
        
        if not isinstance(config.classification.exclude_patterns, list):
            errors.append("exclude_patterns 必须是列表类型")
        
        if not isinstance(config.backup.enabled, bool):
            errors.append("backup.enabled 必须是布尔类型")
        
        if not isinstance(config.backup.keep_backups, int):
            errors.append("backup.keep_backups 必须是整数类型")
        
        if not isinstance(config.index_generation.max_description_length, int):
            errors.append("index_generation.max_description_length 必须是整数类型")
        
        # 验证分类配置
        if not config.classification.core_file_names:
            warnings.append("核心文档列表为空")
        
        if not config.classification.archive_keywords:
            warnings.append("归档关键词列表为空")
        
        if not config.classification.development_keywords:
            warnings.append("开发文档关键词列表为空")
        
        # 验证目录结构配置 - 必需字段
        if not config.directory_structure.docs_root:
            errors.append("文档根目录不能为空")
        
        if not config.directory_structure.archive_dir:
            errors.append("归档目录不能为空")
        
        if not config.directory_structure.development_dir:
            errors.append("开发文档目录不能为空")
        
        # 验证路径格式有效
        if config.directory_structure.docs_root:
            if not self._is_valid_path_format(config.directory_structure.docs_root):
                errors.append(f"文档根目录路径格式无效: {config.directory_structure.docs_root}")
        
        if config.directory_structure.archive_dir:
            if not self._is_valid_path_format(config.directory_structure.archive_dir):
                errors.append(f"归档目录路径格式无效: {config.directory_structure.archive_dir}")
        
        if config.directory_structure.development_dir:
            if not self._is_valid_path_format(config.directory_structure.development_dir):
                errors.append(f"开发文档目录路径格式无效: {config.directory_structure.development_dir}")
        
        if config.directory_structure.backend_docs_dir:
            if not self._is_valid_path_format(config.directory_structure.backend_docs_dir):
                errors.append(f"后端文档目录路径格式无效: {config.directory_structure.backend_docs_dir}")
        
        if config.directory_structure.frontend_docs_dir:
            if not self._is_valid_path_format(config.directory_structure.frontend_docs_dir):
                errors.append(f"前端文档目录路径格式无效: {config.directory_structure.frontend_docs_dir}")
        
        if config.backup.backup_dir:
            if not self._is_valid_path_format(config.backup.backup_dir):
                errors.append(f"备份目录路径格式无效: {config.backup.backup_dir}")
        
        # 验证备份配置
        if config.backup.enabled and not config.backup.backup_dir:
            errors.append("备份已启用但备份目录为空")
        
        if isinstance(config.backup.keep_backups, int) and config.backup.keep_backups < 1:
            errors.append("保留备份数量必须至少为 1")
        
        # 验证索引生成配置
        if config.index_generation.max_description_length < 10:
            warnings.append("描述最大长度过短，建议至少 10 个字符")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _is_valid_path_format(self, path: str) -> bool:
        """
        验证路径格式是否有效
        
        参数:
            path: 路径字符串
        
        返回:
            路径格式是否有效
        """
        if not path or not isinstance(path, str):
            return False
        
        # 检查路径中是否包含非法字符
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        if any(char in path for char in invalid_chars):
            return False
        
        # 检查是否为绝对路径（不允许）
        if path.startswith('/') or (len(path) > 1 and path[1] == ':'):
            return False
        
        # 检查路径是否包含父目录引用（安全考虑）
        if '..' in path:
            return False
        
        # 检查路径是否以斜杠结尾（不推荐）
        if path.endswith('/') or path.endswith('\\'):
            return False
        
        return True
    
    def get_default_config(self) -> OrganizationConfig:
        """
        获取默认配置
        
        返回:
            默认配置对象
        """
        classification = ClassificationConfig(
            core_file_names=[
                "README.md",
                "SETUP.md",
                "MAINTENANCE.md",
                "CHANGELOG.md",
                ".kiro/PROJECT.md"
            ],
            core_directories=[
                ".kiro/specs/**"
            ],
            archive_keywords=[
                "SUMMARY",
                "REPORT",
                "COMPLETION",
                "FIX",
                "TROUBLESHOOTING",
                "TASK_",
                "FINAL_",
                "INTEGRATION_TEST_"
            ],
            development_keywords=[
                "GUIDE",
                "SETUP",
                "DATABASE_",
                "MIGRATION_",
                "IMPORT_",
                "RULE_GENERATION"
            ],
            exclude_patterns=[
                "node_modules/**",
                ".git/**",
                "**/__pycache__/**",
                "**/venv/**"
            ]
        )
        
        directory_structure = DirectoryStructure(
            docs_root="docs",
            archive_dir="docs/archive",
            development_dir="docs/development",
            backend_docs_dir="backend/docs",
            frontend_docs_dir="frontend/docs"
        )
        
        archive_grouping = ArchiveGrouping(
            groups={
                "device-row-recognition": [
                    "DEVICE_ROW_RECOGNITION",
                    "TASK_9"
                ],
                "device-library": [
                    "DEVICE_LIBRARY_EXPANSION"
                ],
                "ui-optimization": [
                    "UI_OPTIMIZATION",
                    "UI_TOOLTIP"
                ],
                "troubleshooting": [
                    "TROUBLESHOOTING",
                    "MANUAL_ADJUST"
                ],
                "testing": [
                    "TEST_REPORT",
                    "INTEGRATION_TEST",
                    "ACCEPTANCE_REPORT"
                ],
                "tasks": [
                    "TASK_7",
                    "TASK_12"
                ]
            }
        )
        
        backup = BackupConfig(
            enabled=True,
            backup_dir=".backup/docs",
            keep_backups=5
        )
        
        index_generation = IndexGenerationConfig(
            include_file_size=True,
            include_modified_date=True,
            include_description=True,
            max_description_length=100
        )
        
        return OrganizationConfig(
            classification=classification,
            directory_structure=directory_structure,
            archive_grouping=archive_grouping,
            backup=backup,
            index_generation=index_generation
        )
    
    def save_default_config(self, config_path: str) -> None:
        """
        生成并保存默认配置到指定路径
        
        参数:
            config_path: 配置文件保存路径
        
        异常:
            OSError: 文件写入失败
        """
        # 获取默认配置
        config = self.get_default_config()
        
        # 转换为字典格式
        config_dict = {
            "classification": {
                "core_documents": config.classification.core_file_names,
                "core_directories": config.classification.core_directories,
                "archive_keywords": config.classification.archive_keywords,
                "development_keywords": config.classification.development_keywords,
                "exclude_patterns": config.classification.exclude_patterns
            },
            "directory_structure": {
                "docs_root": config.directory_structure.docs_root,
                "archive_dir": config.directory_structure.archive_dir,
                "development_dir": config.directory_structure.development_dir,
                "backend_docs_dir": config.directory_structure.backend_docs_dir,
                "frontend_docs_dir": config.directory_structure.frontend_docs_dir
            },
            "archive_grouping": config.archive_grouping.groups,
            "backup": {
                "enabled": config.backup.enabled,
                "backup_dir": config.backup.backup_dir,
                "keep_backups": config.backup.keep_backups
            },
            "index_generation": {
                "include_file_size": config.index_generation.include_file_size,
                "include_modified_date": config.index_generation.include_modified_date,
                "include_description": config.index_generation.include_description,
                "max_description_length": config.index_generation.max_description_length
            }
        }
        
        # 确保目标目录存在
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入配置文件
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    def _config_to_dict(self, config: OrganizationConfig) -> dict:
        """
        将配置对象转换为字典
        
        参数:
            config: 配置对象
        
        返回:
            配置字典
        """
        return {
            "classification": {
                "core_documents": config.classification.core_file_names,
                "core_directories": config.classification.core_directories,
                "archive_keywords": config.classification.archive_keywords,
                "development_keywords": config.classification.development_keywords,
                "exclude_patterns": config.classification.exclude_patterns
            },
            "directory_structure": {
                "docs_root": config.directory_structure.docs_root,
                "archive_dir": config.directory_structure.archive_dir,
                "development_dir": config.directory_structure.development_dir,
                "backend_docs_dir": config.directory_structure.backend_docs_dir,
                "frontend_docs_dir": config.directory_structure.frontend_docs_dir
            },
            "archive_grouping": config.archive_grouping.groups,
            "backup": {
                "enabled": config.backup.enabled,
                "backup_dir": config.backup.backup_dir,
                "keep_backups": config.backup.keep_backups
            },
            "index_generation": {
                "include_file_size": config.index_generation.include_file_size,
                "include_modified_date": config.index_generation.include_modified_date,
                "include_description": config.index_generation.include_description,
                "max_description_length": config.index_generation.max_description_length
            }
        }
