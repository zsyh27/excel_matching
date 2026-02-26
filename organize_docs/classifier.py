"""
文档分类器

负责根据规则将文档分类为核心文档、归档文档或开发文档。
"""

from typing import List, Dict
from pathlib import Path

from .models import Document, DocumentCategory, ClassificationConfig


class DocumentClassifier:
    """文档分类器"""
    
    def __init__(self, config: ClassificationConfig):
        """
        初始化分类器
        
        参数:
            config: 分类配置，包含关键词规则、文件名规则等
        """
        self.config = config
    
    def classify(self, document: Document) -> DocumentCategory:
        """
        分类单个文档
        
        参数:
            document: 待分类的文档对象
        
        返回:
            文档分类（CORE, ARCHIVE, DEVELOPMENT）
        """
        # 优先检查核心文档（需求 1.4, 5.1-5.5）
        if self._is_core_document(document):
            return DocumentCategory.CORE
        
        # 检查归档文档
        if self._is_archive_document(document):
            return DocumentCategory.ARCHIVE
        
        # 检查开发文档
        if self._is_development_document(document):
            return DocumentCategory.DEVELOPMENT
        
        # 默认为未知
        return DocumentCategory.UNKNOWN
    
    def classify_batch(self, documents: List[Document]) -> Dict[DocumentCategory, List[Document]]:
        """
        批量分类文档
        
        参数:
            documents: 文档列表
        
        返回:
            按分类分组的文档字典
        """
        result = {
            DocumentCategory.CORE: [],
            DocumentCategory.ARCHIVE: [],
            DocumentCategory.DEVELOPMENT: [],
            DocumentCategory.UNKNOWN: []
        }
        
        for doc in documents:
            category = self.classify(doc)
            doc.category = category
            result[category].append(doc)
        
        return result
    
    def _is_core_document(self, document: Document) -> bool:
        """
        判断是否为核心文档
        
        核心文档识别规则（需求 1.4, 5.1-5.5）:
        1. 文件名匹配: README.md, SETUP.md, MAINTENANCE.md, CHANGELOG.md
        2. 路径匹配: .kiro/PROJECT.md
        3. 核心目录匹配: .kiro/specs/** 等配置的核心目录
        
        参数:
            document: 文档对象
        
        返回:
            是否为核心文档
        """
        # 检查是否在核心目录中
        if self._is_in_core_directory(document):
            return True
        
        # 检查文件名是否在核心文档列表中
        for core_name in self.config.core_file_names:
            # 处理简单文件名匹配（如 README.md）
            if '/' not in core_name and '\\' not in core_name:
                if document.file_name == core_name:
                    return True
            else:
                # 处理路径匹配（如 .kiro/PROJECT.md）
                # 规范化路径分隔符
                core_path = core_name.replace('\\', '/')
                doc_relative_path = document.relative_path.replace('\\', '/')
                
                # 检查相对路径是否匹配
                if doc_relative_path == core_path:
                    return True
                
                # 检查是否以该路径结尾（处理不同根目录的情况）
                if doc_relative_path.endswith('/' + core_path) or doc_relative_path.endswith(core_path):
                    return True
        
        return False
    
    def _is_in_core_directory(self, document: Document) -> bool:
        """
        判断文档是否在核心目录中
        
        参数:
            document: 文档对象
        
        返回:
            是否在核心目录中
        """
        doc_relative_path = document.relative_path.replace('\\', '/')
        
        for core_dir_pattern in self.config.core_directories:
            # 规范化路径分隔符
            pattern = core_dir_pattern.replace('\\', '/')
            
            # 处理通配符模式（如 .kiro/specs/**）
            if pattern.endswith('/**'):
                # 移除 /** 后缀
                base_dir = pattern[:-3]
                # 检查文档路径是否以该目录开头
                if doc_relative_path.startswith(base_dir + '/') or doc_relative_path.startswith(base_dir):
                    return True
            elif pattern.endswith('/*'):
                # 处理单层通配符（如 .kiro/specs/*）
                base_dir = pattern[:-2]
                # 检查文档是否直接在该目录下（不包括子目录）
                if doc_relative_path.startswith(base_dir + '/'):
                    # 确保没有更深的子目录
                    remaining_path = doc_relative_path[len(base_dir) + 1:]
                    if '/' not in remaining_path:
                        return True
            else:
                # 精确匹配目录
                if doc_relative_path.startswith(pattern + '/') or doc_relative_path == pattern:
                    return True
        
        return False
    
    def _is_archive_document(self, document: Document) -> bool:
        """
        判断是否为归档文档
        
        归档文档识别规则（需求 1.3）:
        - 文件名包含关键词: SUMMARY, REPORT, COMPLETION, FIX, TROUBLESHOOTING
        - 文件名包含: TASK_*, FINAL_*, INTEGRATION_TEST_*
        
        参数:
            document: 文档对象
        
        返回:
            是否为归档文档
        """
        file_name_upper = document.file_name.upper()
        
        # 检查是否包含归档关键词
        for keyword in self.config.archive_keywords:
            keyword_upper = keyword.upper()
            if keyword_upper in file_name_upper:
                return True
        
        return False
    
    def _is_development_document(self, document: Document) -> bool:
        """
        判断是否为开发文档
        
        开发文档识别规则（需求 1.5, 8.1-8.3）:
        - 文件名包含关键词: GUIDE, SETUP, DATABASE_, MIGRATION_, IMPORT_, RULE_GENERATION
        - 位于 backend/ 或 frontend/ 目录下的 MD 文档
        
        参数:
            document: 文档对象
        
        返回:
            是否为开发文档
        """
        file_name_upper = document.file_name.upper()
        relative_path = document.relative_path.replace('\\', '/')
        
        # 检查是否包含开发文档关键词
        for keyword in self.config.development_keywords:
            keyword_upper = keyword.upper()
            if keyword_upper in file_name_upper:
                return True
        
        # 检查是否在 backend/ 或 frontend/ 目录下
        if relative_path.startswith('backend/') or relative_path.startswith('frontend/'):
            return True
        
        return False
