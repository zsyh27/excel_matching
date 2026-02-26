"""
核心数据模型

定义文档整理系统使用的数据结构。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict


class DocumentCategory(Enum):
    """文档分类枚举"""
    CORE = "core"           # 核心文档
    ARCHIVE = "archive"     # 归档文档
    DEVELOPMENT = "development"  # 开发文档
    UNKNOWN = "unknown"     # 未分类


@dataclass
class Document:
    """文档数据模型"""
    file_name: str          # 文件名
    file_path: str          # 完整路径
    relative_path: str      # 相对于项目根目录的路径
    size: int               # 文件大小（字节）
    modified_time: datetime # 最后修改时间
    content_preview: str    # 内容预览（前200字符）
    category: Optional[DocumentCategory] = None  # 文档分类


@dataclass
class ClassificationConfig:
    """分类配置"""
    core_file_names: List[str]      # 核心文档文件名列表
    core_directories: List[str] = field(default_factory=list)  # 核心目录模式列表（不应被移动）
    archive_keywords: List[str] = field(default_factory=list)     # 归档文档关键词列表
    development_keywords: List[str] = field(default_factory=list) # 开发文档关键词列表
    exclude_patterns: List[str] = field(default_factory=list)     # 排除的文件模式


@dataclass
class DirectoryStructure:
    """目录结构配置"""
    docs_root: str          # 文档根目录
    archive_dir: str        # 归档目录
    development_dir: str    # 开发文档目录
    backend_docs_dir: str   # 后端文档目录
    frontend_docs_dir: str  # 前端文档目录


@dataclass
class MoveResult:
    """移动操作结果"""
    document: Document      # 文档对象
    original_path: str      # 原始路径
    new_path: str          # 新路径
    success: bool          # 是否成功
    error_message: Optional[str] = None  # 错误信息


@dataclass
class BackupInfo:
    """备份信息"""
    backup_id: str         # 备份ID
    backup_path: str       # 备份路径
    timestamp: datetime    # 备份时间
    document_count: int    # 文档数量
    manifest: List[Dict]   # 文档清单（原路径 -> 备份路径映射）


@dataclass
class ArchiveGrouping:
    """归档分组配置"""
    groups: Dict[str, List[str]] = field(default_factory=dict)  # 分组名 -> 关键词列表


@dataclass
class BackupConfig:
    """备份配置"""
    enabled: bool = True
    backup_dir: str = ".backup/docs"
    keep_backups: int = 5


@dataclass
class IndexGenerationConfig:
    """索引生成配置"""
    include_file_size: bool = True
    include_modified_date: bool = True
    include_description: bool = True
    max_description_length: int = 100


@dataclass
class OrganizationConfig:
    """文档整理配置"""
    classification: ClassificationConfig
    directory_structure: DirectoryStructure
    archive_grouping: ArchiveGrouping = field(default_factory=ArchiveGrouping)
    backup: BackupConfig = field(default_factory=BackupConfig)
    index_generation: IndexGenerationConfig = field(default_factory=IndexGenerationConfig)


@dataclass
class ValidationResult:
    """配置验证结果"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class RestoreResult:
    """恢复操作结果"""
    success: bool
    restored_count: int
    failed_documents: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
