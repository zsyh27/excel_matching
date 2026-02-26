"""
备份管理器

负责创建文档备份、恢复备份和管理备份列表。
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import List
from uuid import uuid4

from .models import Document, BackupInfo, RestoreResult


class BackupManager:
    """备份管理器"""
    
    def __init__(self, backup_root: str = ".backup/docs"):
        """
        初始化备份管理器
        
        参数:
            backup_root: 备份根目录路径
        """
        self.backup_root = backup_root
    
    def create_backup(self, documents: List[Document], project_root: str = ".") -> BackupInfo:
        """
        创建文档备份
        
        参数:
            documents: 待备份的文档列表
            project_root: 项目根目录路径
        
        返回:
            备份信息，包含备份路径、时间戳、文档清单
        """
        # 生成备份 ID 和时间戳
        backup_id = self._generate_backup_id()
        timestamp = datetime.now()
        
        # 创建备份目录
        backup_path = os.path.join(self.backup_root, backup_id)
        os.makedirs(backup_path, exist_ok=True)
        
        # 复制文档到备份目录并记录清单
        manifest = []
        for doc in documents:
            try:
                # 计算备份文件的相对路径
                backup_file_path = os.path.join(backup_path, doc.relative_path)
                
                # 创建备份文件的父目录
                os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
                
                # 复制文件
                shutil.copy2(doc.file_path, backup_file_path)
                
                # 记录到清单
                manifest.append({
                    "original_path": doc.file_path,
                    "relative_path": doc.relative_path,
                    "backup_path": backup_file_path,
                    "file_name": doc.file_name,
                    "size": doc.size,
                    "modified_time": doc.modified_time.isoformat()
                })
            except Exception as e:
                # 记录失败的文件
                manifest.append({
                    "original_path": doc.file_path,
                    "relative_path": doc.relative_path,
                    "backup_path": None,
                    "file_name": doc.file_name,
                    "error": str(e)
                })
        
        # 保存备份清单到 JSON 文件
        manifest_path = os.path.join(backup_path, "manifest.json")
        manifest_data = {
            "backup_id": backup_id,
            "timestamp": timestamp.isoformat(),
            "document_count": len(documents),
            "project_root": os.path.abspath(project_root),
            "documents": manifest
        }
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
        
        # 创建 BackupInfo 对象
        backup_info = BackupInfo(
            backup_id=backup_id,
            backup_path=backup_path,
            timestamp=timestamp,
            document_count=len(documents),
            manifest=manifest
        )
        
        return backup_info
    
    def restore_from_backup(self, backup_info: BackupInfo, project_root: str = ".") -> RestoreResult:
        """
        从备份恢复
        
        实现需求 11.3 和 11.4:
        - 读取备份清单 (manifest.json)
        - 将文档从备份位置移回原位置
        - 验证恢复完整性（检查成功/失败的文档数量）
        
        参数:
            backup_info: 备份信息，包含备份路径和清单
            project_root: 项目根目录路径
        
        返回:
            恢复结果，包含:
            - success: 是否所有文档都成功恢复
            - restored_count: 成功恢复的文档数量
            - failed_documents: 失败的文档列表
            - error_message: 错误信息（如果有）
        """
        restored_count = 0
        failed_documents = []
        
        try:
            # 读取备份清单
            manifest_path = os.path.join(backup_info.backup_path, "manifest.json")
            if not os.path.exists(manifest_path):
                return RestoreResult(
                    success=False,
                    restored_count=0,
                    failed_documents=[],
                    error_message=f"备份清单文件不存在: {manifest_path}"
                )
            
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            
            # 恢复每个文档
            for doc_info in manifest_data.get("documents", []):
                if "error" in doc_info:
                    # 跳过备份时失败的文档
                    failed_documents.append(doc_info["original_path"])
                    continue
                
                try:
                    backup_file = doc_info["backup_path"]
                    original_path = doc_info["original_path"]
                    
                    # 确保原始路径的父目录存在
                    os.makedirs(os.path.dirname(original_path), exist_ok=True)
                    
                    # 复制文件回原位置
                    shutil.copy2(backup_file, original_path)
                    restored_count += 1
                except Exception as e:
                    failed_documents.append(f"{doc_info['original_path']}: {str(e)}")
            
            success = len(failed_documents) == 0
            return RestoreResult(
                success=success,
                restored_count=restored_count,
                failed_documents=failed_documents,
                error_message=None if success else f"部分文档恢复失败: {len(failed_documents)} 个"
            )
        
        except Exception as e:
            return RestoreResult(
                success=False,
                restored_count=restored_count,
                failed_documents=failed_documents,
                error_message=f"恢复操作失败: {str(e)}"
            )
    
    def list_backups(self) -> List[BackupInfo]:
        """
        列出所有可用备份
        
        返回:
            备份信息列表
        """
        backups = []
        
        if not os.path.exists(self.backup_root):
            return backups
        
        # 遍历备份根目录
        for backup_id in os.listdir(self.backup_root):
            backup_path = os.path.join(self.backup_root, backup_id)
            
            # 跳过非目录项
            if not os.path.isdir(backup_path):
                continue
            
            # 读取备份清单
            manifest_path = os.path.join(backup_path, "manifest.json")
            if not os.path.exists(manifest_path):
                continue
            
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest_data = json.load(f)
                
                # 创建 BackupInfo 对象
                backup_info = BackupInfo(
                    backup_id=manifest_data["backup_id"],
                    backup_path=backup_path,
                    timestamp=datetime.fromisoformat(manifest_data["timestamp"]),
                    document_count=manifest_data["document_count"],
                    manifest=manifest_data["documents"]
                )
                backups.append(backup_info)
            except Exception:
                # 跳过无效的备份
                continue
        
        # 按时间戳排序（最新的在前）
        backups.sort(key=lambda b: b.timestamp, reverse=True)
        
        return backups
    
    def _generate_backup_id(self) -> str:
        """
        生成备份 ID
        
        返回:
            格式为 backup_YYYYMMDD_HHMMSS_UUID 的备份 ID
        """
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        uuid_str = str(uuid4())[:8]
        return f"backup_{timestamp_str}_{uuid_str}"
