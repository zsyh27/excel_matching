"""
文档移动器

负责创建目录结构和移动文档到目标位置。
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict

from .models import (
    Document,
    DocumentCategory,
    DirectoryStructure,
    MoveResult
)


class DocumentMover:
    """文档移动器"""
    
    def __init__(self, target_structure: DirectoryStructure, project_root: str = ".", archive_grouping: Optional[dict] = None):
        """
        初始化移动器
        
        参数:
            target_structure: 目标目录结构配置
            project_root: 项目根目录路径，默认为当前目录
            archive_grouping: 归档分组配置，字典格式 {分组名: [关键词列表]}
        """
        self.target_structure = target_structure
        self.project_root = Path(project_root).resolve()
        self.archive_grouping = archive_grouping or {}
    
    def create_directory_structure(self) -> None:
        """
        创建目标目录结构
        
        创建以下目录:
        - docs/ 根目录
        - docs/archive/ 子目录
        - docs/archive/<group>/ 分组子目录（根据配置）
        - docs/development/ 子目录
        - backend/docs/ 目录
        - frontend/docs/ 目录
        
        异常:
            OSError: 目录创建失败
        """
        # 创建 docs/ 根目录
        docs_root_path = self.project_root / self.target_structure.docs_root
        docs_root_path.mkdir(parents=True, exist_ok=True)
        
        # 创建 docs/archive/ 子目录
        archive_path = self.project_root / self.target_structure.archive_dir
        archive_path.mkdir(parents=True, exist_ok=True)
        
        # 创建归档分组子目录
        for group_name in self.archive_grouping.keys():
            group_path = archive_path / group_name
            group_path.mkdir(parents=True, exist_ok=True)
        
        # 创建 docs/development/ 子目录
        development_path = self.project_root / self.target_structure.development_dir
        development_path.mkdir(parents=True, exist_ok=True)
        
        # 创建 backend/docs/ 目录
        if self.target_structure.backend_docs_dir:
            backend_docs_path = self.project_root / self.target_structure.backend_docs_dir
            backend_docs_path.mkdir(parents=True, exist_ok=True)
        
        # 创建 frontend/docs/ 目录
        if self.target_structure.frontend_docs_dir:
            frontend_docs_path = self.project_root / self.target_structure.frontend_docs_dir
            frontend_docs_path.mkdir(parents=True, exist_ok=True)
    
    def move_document(self, document: Document, target_category: DocumentCategory) -> MoveResult:
        """
        移动单个文档
        
        参数:
            document: 待移动的文档
            target_category: 目标分类
        
        返回:
            移动结果，包含原路径、新路径、状态
        """
        original_path = self.project_root / document.relative_path
        
        # 获取目标路径
        target_path = self.get_target_path(document, target_category)
        
        # 如果是核心文档，不移动
        if target_path is None:
            return MoveResult(
                document=document,
                original_path=str(original_path),
                new_path=str(original_path),
                success=True,
                error_message=None
            )
        
        try:
            # 确保目标目录存在
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 移动文件
            shutil.move(str(original_path), str(target_path))
            
            # 更新文档的相对路径以反映新位置
            document.relative_path = str(target_path.relative_to(self.project_root)).replace(os.sep, "/")
            
            return MoveResult(
                document=document,
                original_path=str(original_path),
                new_path=str(target_path),
                success=True,
                error_message=None
            )
        except Exception as e:
            return MoveResult(
                document=document,
                original_path=str(original_path),
                new_path=str(target_path),
                success=False,
                error_message=str(e)
            )
    
    def get_target_path(self, document: Document, category: DocumentCategory) -> Optional[Path]:
        """
        获取文档的目标路径
        
        参数:
            document: 文档对象
            category: 文档分类
        
        返回:
            目标路径，如果是核心文档则返回 None（保持原位置）
        """
        # 核心文档保持原位置
        if category == DocumentCategory.CORE:
            return None
        
        # 归档文档
        if category == DocumentCategory.ARCHIVE:
            # 检查是否属于某个分组
            group = self.get_archive_group(document)
            if group:
                # 移动到分组子目录
                return self.project_root / self.target_structure.archive_dir / group / document.file_name
            else:
                # 移动到归档根目录
                return self.project_root / self.target_structure.archive_dir / document.file_name
        
        # 开发文档
        if category == DocumentCategory.DEVELOPMENT:
            # 检查文档是否在 backend/ 或 frontend/ 目录下
            relative_path_lower = document.relative_path.lower()
            
            if relative_path_lower.startswith("backend/") or relative_path_lower.startswith("backend\\"):
                # 后端开发文档
                if self.target_structure.backend_docs_dir:
                    return self.project_root / self.target_structure.backend_docs_dir / document.file_name
            elif relative_path_lower.startswith("frontend/") or relative_path_lower.startswith("frontend\\"):
                # 前端开发文档
                if self.target_structure.frontend_docs_dir:
                    return self.project_root / self.target_structure.frontend_docs_dir / document.file_name
            
            # 通用开发文档
            return self.project_root / self.target_structure.development_dir / document.file_name
        
        # 未知分类，移动到开发文档目录
        return self.project_root / self.target_structure.development_dir / document.file_name
    
    def get_archive_group(self, document: Document) -> Optional[str]:
        """
        确定归档文档所属的分组
        
        根据配置的分组规则，检查文档文件名是否包含分组关键词。
        如果文档匹配多个分组，返回第一个匹配的分组。
        
        参数:
            document: 文档对象
        
        返回:
            分组名称，如果不属于任何分组则返回 None
        """
        if not self.archive_grouping:
            return None
        
        file_name_upper = document.file_name.upper()
        
        # 遍历所有分组，检查文件名是否包含分组关键词
        for group_name, keywords in self.archive_grouping.items():
            for keyword in keywords:
                if keyword.upper() in file_name_upper:
                    return group_name
        
        return None
