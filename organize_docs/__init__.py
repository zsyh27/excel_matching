"""
文档整理功能模块

本模块提供文档自动分类、归档和索引生成功能。
"""

from .models import (
    Document,
    DocumentCategory,
    ClassificationConfig,
    DirectoryStructure,
    MoveResult,
    BackupInfo,
    OrganizationConfig,
)
from .scanner import DocumentScanner
from .config_manager import ConfigManager
from .classifier import DocumentClassifier
from .backup_manager import BackupManager

__all__ = [
    'Document',
    'DocumentCategory',
    'ClassificationConfig',
    'DirectoryStructure',
    'MoveResult',
    'BackupInfo',
    'OrganizationConfig',
    'DocumentScanner',
    'ConfigManager',
    'DocumentClassifier',
    'BackupManager',
]

__version__ = '0.1.0'
