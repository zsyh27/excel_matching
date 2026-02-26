"""
文档扫描器

负责扫描项目目录，识别所有 MD 文档。
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List
import fnmatch

from .models import Document


class DocumentScanner:
    """文档扫描器"""
    
    def scan_directory(self, root_path: str, exclude_dirs: List[str]) -> List[Document]:
        """
        扫描目录，返回文档列表
        
        参数:
            root_path: 项目根目录路径
            exclude_dirs: 排除的目录列表（如 node_modules, .git）
        
        返回:
            Document 对象列表
        """
        documents = []
        root = Path(root_path).resolve()
        
        if not root.exists():
            raise FileNotFoundError(f"目录不存在: {root_path}")
        
        if not root.is_dir():
            raise NotADirectoryError(f"路径不是目录: {root_path}")
        
        # 遍历目录树
        for dirpath, dirnames, filenames in os.walk(root):
            # 转换为 Path 对象
            current_dir = Path(dirpath)
            
            # 过滤排除的目录
            dirnames[:] = [d for d in dirnames if not self._should_exclude(
                current_dir / d, root, exclude_dirs
            )]
            
            # 处理当前目录下的所有文件
            for filename in filenames:
                if filename.endswith('.md'):
                    file_path = current_dir / filename
                    try:
                        document = self.get_document_info(str(file_path), str(root))
                        documents.append(document)
                    except Exception as e:
                        # 记录警告但继续处理其他文件
                        print(f"警告: 无法读取文件 {file_path}: {e}")
                        continue
        
        return documents
    
    def get_document_info(self, file_path: str, root_path: str = None) -> Document:
        """
        获取单个文档的信息
        
        参数:
            file_path: 文档文件路径
            root_path: 项目根目录路径（用于计算相对路径）
        
        返回:
            Document 对象，包含文件名、路径、大小、修改时间等
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 获取文件统计信息
        stat = path.stat()
        
        # 读取文件内容预览
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read(200)
                content_preview = content[:200]
        except UnicodeDecodeError:
            # 如果 UTF-8 解码失败，尝试其他编码
            try:
                with open(path, 'r', encoding='gbk') as f:
                    content = f.read(200)
                    content_preview = content[:200]
            except Exception:
                content_preview = "[无法读取内容]"
        except Exception as e:
            content_preview = f"[读取错误: {e}]"
        
        # 计算相对路径
        if root_path:
            try:
                relative_path = str(path.relative_to(Path(root_path)))
            except ValueError:
                # 如果文件不在根目录下，使用绝对路径
                relative_path = str(path)
        else:
            relative_path = path.name
        
        return Document(
            file_name=path.name,
            file_path=str(path.resolve()),
            relative_path=relative_path,
            size=stat.st_size,
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            content_preview=content_preview
        )
    
    def _should_exclude(self, dir_path: Path, root_path: Path, exclude_patterns: List[str]) -> bool:
        """
        判断目录是否应该被排除
        
        参数:
            dir_path: 目录路径
            root_path: 项目根目录路径
            exclude_patterns: 排除模式列表
        
        返回:
            是否应该排除该目录
        """
        try:
            # 计算相对路径
            relative_path = str(dir_path.relative_to(root_path))
        except ValueError:
            # 如果不在根目录下，不排除
            return False
        
        # 检查是否匹配任何排除模式
        for pattern in exclude_patterns:
            # 移除 ** 通配符，因为我们只检查目录名
            pattern_clean = pattern.replace('**/', '').replace('/**', '')
            
            # 检查完整路径匹配
            if fnmatch.fnmatch(relative_path, pattern_clean):
                return True
            
            # 检查目录名匹配
            if fnmatch.fnmatch(dir_path.name, pattern_clean):
                return True
            
            # 检查路径中是否包含排除的目录
            if pattern_clean in relative_path.split(os.sep):
                return True
        
        return False
