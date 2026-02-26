"""
索引生成器

负责生成文档索引和导航链接。
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
from organize_docs.models import Document, DocumentCategory, IndexGenerationConfig, ArchiveGrouping


class IndexGenerator:
    """索引生成器类"""
    
    def __init__(self, config: IndexGenerationConfig, 
                 archive_grouping: Optional[ArchiveGrouping] = None):
        """
        初始化索引生成器
        
        参数:
            config: 索引生成配置
            archive_grouping: 归档分组配置（可选）
        """
        self.config = config
        self.archive_grouping = archive_grouping or ArchiveGrouping()
    
    def generate_main_index(self, documents: Dict[DocumentCategory, List[Document]], 
                           project_root: str = ".") -> str:
        """
        生成主文档索引
        
        参数:
            documents: 按分类分组的文档字典
            project_root: 项目根目录路径
        
        返回:
            索引 Markdown 内容
        """
        lines = []
        
        # 标题
        lines.append("# 文档索引")
        lines.append("")
        lines.append("本文档提供项目所有文档的导航和快速查找。")
        lines.append("")
        
        # 核心文档部分
        lines.append("## 核心文档")
        lines.append("")
        core_docs = documents.get(DocumentCategory.CORE, [])
        if core_docs:
            for doc in sorted(core_docs, key=lambda d: d.file_name):
                link = self._generate_relative_link(doc, project_root, "docs")
                description = self._get_document_description(doc)
                lines.append(f"- [{doc.file_name}]({link}) - {description}")
        else:
            lines.append("暂无核心文档")
        lines.append("")
        
        # 归档文档部分
        lines.append("## 归档文档")
        lines.append("")
        archive_docs = documents.get(DocumentCategory.ARCHIVE, [])
        if archive_docs:
            lines.append(f"共 {len(archive_docs)} 个归档文档")
            lines.append("")
            lines.append("详见 [归档文档索引](archive/README.md)")
        else:
            lines.append("暂无归档文档")
        lines.append("")
        
        # 开发文档部分
        lines.append("## 开发文档")
        lines.append("")
        dev_docs = documents.get(DocumentCategory.DEVELOPMENT, [])
        if dev_docs:
            lines.append(f"共 {len(dev_docs)} 个开发文档")
            lines.append("")
            lines.append("详见 [开发文档索引](development/README.md)")
        else:
            lines.append("暂无开发文档")
        lines.append("")
        
        # 页脚
        lines.append("---")
        lines.append("")
        lines.append(f"**最后更新**: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("**维护者**: 开发团队")
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_relative_link(self, doc: Document, project_root: str, 
                                from_dir: str) -> str:
        """
        生成相对路径链接
        
        参数:
            doc: 文档对象
            project_root: 项目根目录
            from_dir: 链接所在目录（相对于项目根目录）
        
        返回:
            相对路径链接
        """
        # 使用相对路径
        # 从 docs/ 目录链接到项目根目录的文件需要使用 ../
        if doc.relative_path.startswith(from_dir):
            # 文档在同一目录或子目录下
            rel_path = os.path.relpath(doc.relative_path, from_dir)
        else:
            # 文档在上级目录
            rel_path = os.path.join("..", doc.relative_path)
        
        # 转换为 URL 格式（使用正斜杠）
        return rel_path.replace(os.sep, "/")
    
    def _get_document_description(self, doc: Document) -> str:
        """
        获取文档描述
        
        参数:
            doc: 文档对象
        
        返回:
            文档描述文本
        """
        # 根据文件名生成描述
        descriptions = {
            "README.md": "项目概述和快速开始",
            "SETUP.md": "安装和配置指南",
            "MAINTENANCE.md": "维护和故障排查指南",
            "CHANGELOG.md": "版本变更历史",
            ".kiro/PROJECT.md": "项目配置文件"
        }
        
        if doc.relative_path in descriptions:
            return descriptions[doc.relative_path]
        
        # 使用内容预览作为描述
        if self.config.include_description and doc.content_preview:
            preview = doc.content_preview.strip().replace("\n", " ")
            if len(preview) > self.config.max_description_length:
                preview = preview[:self.config.max_description_length] + "..."
            return preview
        
        return "文档"
    
    def generate_archive_index(self, archive_docs: List[Document], 
                               project_root: str = ".") -> str:
        """
        生成归档文档索引
        
        参数:
            archive_docs: 归档文档列表
            project_root: 项目根目录路径
        
        返回:
            归档索引 Markdown 内容
        """
        lines = []
        
        # 标题
        lines.append("# 归档文档索引")
        lines.append("")
        lines.append("本目录包含项目历史开发过程中的文档，按功能模块分组。")
        lines.append("")
        
        if not archive_docs:
            lines.append("暂无归档文档")
            lines.append("")
            return "\n".join(lines)
        
        # 按功能模块分组文档
        grouped_docs = self._group_archive_documents(archive_docs)
        
        # 生成统计信息
        lines.append(f"**文档总数**: {len(archive_docs)}")
        lines.append(f"**功能模块数**: {len(grouped_docs)}")
        lines.append("")
        
        # 为每个分组生成内容
        for group_name in sorted(grouped_docs.keys()):
            docs = grouped_docs[group_name]
            
            # 分组标题
            group_title = self._format_group_title(group_name)
            lines.append(f"## {group_title}")
            lines.append("")
            
            # 列出该分组的文档
            for doc in sorted(docs, key=lambda d: d.file_name):
                # 生成相对链接（从 docs/archive/ 到文档位置）
                link = self._generate_archive_link(doc, project_root)
                
                # 获取文档描述
                description = self._get_document_description(doc)
                
                # 构建文档条目
                line_parts = [f"- [{doc.file_name}]({link})"]
                
                # 添加描述
                if description and description != "文档":
                    line_parts.append(f" - {description}")
                
                # 添加归档日期标记
                if self.config.include_modified_date:
                    archive_date = doc.modified_time.strftime('%Y-%m-%d')
                    line_parts.append(f" *(归档于: {archive_date})*")
                
                # 添加文件大小
                if self.config.include_file_size:
                    size_kb = doc.size / 1024
                    line_parts.append(f" `{size_kb:.1f} KB`")
                
                lines.append("".join(line_parts))
            
            lines.append("")
        
        # 页脚
        lines.append("---")
        lines.append("")
        lines.append(f"**最后更新**: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("**维护者**: 开发团队")
        lines.append("")
        
        return "\n".join(lines)
    
    def _group_archive_documents(self, archive_docs: List[Document]) -> Dict[str, List[Document]]:
        """
        按功能模块分组归档文档
        
        参数:
            archive_docs: 归档文档列表
        
        返回:
            分组后的文档字典 {分组名: [文档列表]}
        """
        grouped = {}
        
        for doc in archive_docs:
            group_name = self._determine_group(doc)
            if group_name not in grouped:
                grouped[group_name] = []
            grouped[group_name].append(doc)
        
        return grouped
    
    def _determine_group(self, doc: Document) -> str:
        """
        确定文档所属的功能模块分组
        
        参数:
            doc: 文档对象
        
        返回:
            分组名称
        """
        file_name_upper = doc.file_name.upper()
        
        # 检查每个分组的关键词
        for group_name, keywords in self.archive_grouping.groups.items():
            for keyword in keywords:
                if keyword.upper() in file_name_upper:
                    return group_name
        
        # 如果没有匹配的分组，返回默认分组
        return "其他"
    
    def _format_group_title(self, group_name: str) -> str:
        """
        格式化分组标题
        
        参数:
            group_name: 分组名称（kebab-case）
        
        返回:
            格式化的标题
        """
        # 将 kebab-case 转换为标题格式
        # 例如: "device-row-recognition" -> "Device Row Recognition"
        words = group_name.split("-")
        title = " ".join(word.capitalize() for word in words)
        
        # 特殊处理一些常见的缩写和术语
        replacements = {
            "Ui": "UI",
            "Api": "API",
            "Db": "DB",
            "Id": "ID"
        }
        
        for old, new in replacements.items():
            title = title.replace(old, new)
        
        return title
    
    def _generate_archive_link(self, doc: Document, project_root: str) -> str:
        """
        生成归档文档的相对链接
        
        参数:
            doc: 文档对象
            project_root: 项目根目录
        
        返回:
            相对路径链接
        """
        # 从 docs/archive/ 目录链接到文档
        # 如果文档在 docs/archive/ 下，使用相对路径
        # 如果文档在 docs/archive/subdir/ 下，使用 subdir/filename.md
        
        archive_prefix = "docs/archive/"
        if doc.relative_path.startswith(archive_prefix):
            # 获取相对于 archive/ 目录的路径
            rel_path = doc.relative_path[len(archive_prefix):]
        else:
            # 文档不在预期位置，使用完整相对路径
            rel_path = doc.relative_path
        
        # 转换为 URL 格式（使用正斜杠）
        return rel_path.replace(os.sep, "/")
    
    def generate_development_index(self, dev_docs: List[Document], 
                                   dev_dir: str,
                                   project_root: str = ".") -> str:
        """
        生成开发文档索引
        
        参数:
            dev_docs: 开发文档列表（该目录下的文档）
            dev_dir: 开发文档目录路径（如 "docs/development", "backend/docs", "frontend/docs"）
            project_root: 项目根目录路径
        
        返回:
            开发文档索引 Markdown 内容
        """
        lines = []
        
        # 确定目录类型和标题
        dir_titles = {
            "docs/development": "开发文档",
            "backend/docs": "后端开发文档",
            "frontend/docs": "前端开发文档"
        }
        
        title = dir_titles.get(dev_dir, "开发文档")
        
        # 标题
        lines.append(f"# {title}索引")
        lines.append("")
        
        # 添加说明
        if dev_dir == "backend/docs":
            lines.append("本目录包含后端技术实现细节和开发指南。")
        elif dev_dir == "frontend/docs":
            lines.append("本目录包含前端技术实现细节和开发指南。")
        else:
            lines.append("本目录包含通用开发指南和技术文档。")
        lines.append("")
        
        if not dev_docs:
            lines.append("暂无开发文档")
            lines.append("")
            return "\n".join(lines)
        
        # 生成统计信息
        lines.append(f"**文档总数**: {len(dev_docs)}")
        lines.append("")
        
        # 列出所有文档
        lines.append("## 文档列表")
        lines.append("")
        
        for doc in sorted(dev_docs, key=lambda d: d.file_name):
            # 生成相对链接（从当前目录到文档位置）
            link = self._generate_development_link(doc, dev_dir)
            
            # 获取文档描述
            description = self._get_document_description(doc)
            
            # 构建文档条目
            line_parts = [f"- [{doc.file_name}]({link})"]
            
            # 添加描述
            if description and description != "文档":
                line_parts.append(f" - {description}")
            
            # 添加文件大小
            if self.config.include_file_size:
                size_kb = doc.size / 1024
                line_parts.append(f" `{size_kb:.1f} KB`")
            
            lines.append("".join(line_parts))
        
        lines.append("")
        
        # 页脚
        lines.append("---")
        lines.append("")
        lines.append(f"**最后更新**: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append("**维护者**: 开发团队")
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_development_link(self, doc: Document, dev_dir: str) -> str:
        """
        生成开发文档的相对链接
        
        参数:
            doc: 文档对象
            dev_dir: 开发文档目录路径（如 "docs/development", "backend/docs"）
        
        返回:
            相对路径链接
        """
        # 从开发文档目录链接到文档
        # 如果文档在该目录下，使用相对路径
        
        dev_prefix = dev_dir + "/"
        if doc.relative_path.startswith(dev_prefix):
            # 获取相对于开发文档目录的路径
            rel_path = doc.relative_path[len(dev_prefix):]
        else:
            # 文档不在预期位置，使用文件名
            rel_path = doc.file_name
        
        # 转换为 URL 格式（使用正斜杠）
        return rel_path.replace(os.sep, "/")
