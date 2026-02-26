"""
备份管理器测试

测试备份创建、恢复和列表功能。
"""

import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from organize_docs.backup_manager import BackupManager
from organize_docs.models import Document, BackupInfo


@pytest.fixture
def temp_project_dir():
    """创建临时项目目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def backup_manager(temp_project_dir):
    """创建备份管理器实例"""
    backup_root = os.path.join(temp_project_dir, ".backup", "docs")
    return BackupManager(backup_root=backup_root)


@pytest.fixture
def sample_documents(temp_project_dir):
    """创建示例文档"""
    documents = []
    
    # 创建几个测试文档
    test_files = [
        ("README.md", "# Test README\n\nThis is a test."),
        ("docs/guide.md", "# Guide\n\nTest guide content."),
        ("SUMMARY.md", "# Summary\n\nTest summary.")
    ]
    
    for rel_path, content in test_files:
        file_path = os.path.join(temp_project_dir, rel_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        doc = Document(
            file_name=os.path.basename(rel_path),
            file_path=file_path,
            relative_path=rel_path,
            size=len(content),
            modified_time=datetime.now(),
            content_preview=content[:200]
        )
        documents.append(doc)
    
    return documents


def test_create_backup(backup_manager, sample_documents, temp_project_dir):
    """测试创建备份"""
    # 创建备份
    backup_info = backup_manager.create_backup(sample_documents, temp_project_dir)
    
    # 验证备份信息
    assert backup_info.backup_id.startswith("backup_")
    assert backup_info.document_count == len(sample_documents)
    assert len(backup_info.manifest) == len(sample_documents)
    assert os.path.exists(backup_info.backup_path)
    
    # 验证备份文件存在
    for doc in sample_documents:
        backup_file = os.path.join(backup_info.backup_path, doc.relative_path)
        assert os.path.exists(backup_file), f"备份文件不存在: {backup_file}"
    
    # 验证清单文件存在
    manifest_path = os.path.join(backup_info.backup_path, "manifest.json")
    assert os.path.exists(manifest_path)


def test_backup_preserves_content(backup_manager, sample_documents, temp_project_dir):
    """测试备份保留文件内容"""
    # 创建备份
    backup_info = backup_manager.create_backup(sample_documents, temp_project_dir)
    
    # 验证每个文件的内容相同
    for doc in sample_documents:
        original_path = doc.file_path
        backup_file = os.path.join(backup_info.backup_path, doc.relative_path)
        
        with open(original_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        
        assert original_content == backup_content


def test_list_backups(backup_manager, sample_documents, temp_project_dir):
    """测试列出备份"""
    # 创建多个备份
    backup1 = backup_manager.create_backup(sample_documents, temp_project_dir)
    backup2 = backup_manager.create_backup(sample_documents[:2], temp_project_dir)
    
    # 列出备份
    backups = backup_manager.list_backups()
    
    # 验证
    assert len(backups) >= 2
    backup_ids = [b.backup_id for b in backups]
    assert backup1.backup_id in backup_ids
    assert backup2.backup_id in backup_ids
    
    # 验证按时间排序（最新的在前）
    for i in range(len(backups) - 1):
        assert backups[i].timestamp >= backups[i + 1].timestamp


def test_restore_from_backup(backup_manager, sample_documents, temp_project_dir):
    """测试从备份恢复"""
    # 创建备份
    backup_info = backup_manager.create_backup(sample_documents, temp_project_dir)
    
    # 删除原始文件
    for doc in sample_documents:
        os.remove(doc.file_path)
        assert not os.path.exists(doc.file_path)
    
    # 恢复备份
    restore_result = backup_manager.restore_from_backup(backup_info, temp_project_dir)
    
    # 验证恢复结果
    assert restore_result.success
    assert restore_result.restored_count == len(sample_documents)
    assert len(restore_result.failed_documents) == 0
    
    # 验证文件已恢复
    for doc in sample_documents:
        assert os.path.exists(doc.file_path), f"文件未恢复: {doc.file_path}"


def test_backup_manifest_records_paths(backup_manager, sample_documents, temp_project_dir):
    """测试备份清单记录路径映射"""
    # 创建备份
    backup_info = backup_manager.create_backup(sample_documents, temp_project_dir)
    
    # 验证清单包含所有文档
    assert len(backup_info.manifest) == len(sample_documents)
    
    # 验证每个清单项包含必要信息
    for manifest_item in backup_info.manifest:
        assert "original_path" in manifest_item
        assert "relative_path" in manifest_item
        assert "backup_path" in manifest_item
        assert "file_name" in manifest_item
        
        # 验证路径映射正确
        if manifest_item.get("backup_path"):
            assert os.path.exists(manifest_item["backup_path"])


def test_empty_backup_list_when_no_backups(backup_manager):
    """测试没有备份时返回空列表"""
    backups = backup_manager.list_backups()
    assert backups == []


def test_backup_id_format(backup_manager, sample_documents, temp_project_dir):
    """测试备份 ID 格式"""
    backup_info = backup_manager.create_backup(sample_documents, temp_project_dir)
    
    # 验证 ID 格式: backup_YYYYMMDD_HHMMSS_UUID
    parts = backup_info.backup_id.split("_")
    assert len(parts) == 4
    assert parts[0] == "backup"
    assert len(parts[1]) == 8  # YYYYMMDD
    assert len(parts[2]) == 6  # HHMMSS
    assert len(parts[3]) == 8  # UUID (前8位)


def test_restore_reads_backup_manifest(backup_manager, sample_documents, temp_project_dir):
    """
    测试恢复功能读取备份清单
    
    验证需求 11.3: 读取备份清单
    """
    # 创建备份
    backup_info = backup_manager.create_backup(sample_documents, temp_project_dir)
    
    # 验证清单文件存在
    manifest_path = os.path.join(backup_info.backup_path, "manifest.json")
    assert os.path.exists(manifest_path)
    
    # 删除原始文件
    for doc in sample_documents:
        os.remove(doc.file_path)
    
    # 恢复备份（内部会读取清单）
    restore_result = backup_manager.restore_from_backup(backup_info, temp_project_dir)
    
    # 验证恢复成功
    assert restore_result.success
    assert restore_result.restored_count == len(sample_documents)


def test_restore_moves_documents_to_original_location(backup_manager, sample_documents, temp_project_dir):
    """
    测试恢复功能将文档移回原位置
    
    验证需求 11.3: 将文档从备份位置移回原位置
    """
    # 记录原始路径
    original_paths = {doc.file_path for doc in sample_documents}
    
    # 创建备份
    backup_info = backup_manager.create_backup(sample_documents, temp_project_dir)
    
    # 删除原始文件
    for doc in sample_documents:
        os.remove(doc.file_path)
        assert not os.path.exists(doc.file_path)
    
    # 恢复备份
    restore_result = backup_manager.restore_from_backup(backup_info, temp_project_dir)
    
    # 验证所有文件都回到原位置
    assert restore_result.success
    for original_path in original_paths:
        assert os.path.exists(original_path), f"文件未恢复到原位置: {original_path}"


def test_restore_verifies_integrity(backup_manager, sample_documents, temp_project_dir):
    """
    测试恢复功能验证恢复完整性
    
    验证需求 11.3: 验证恢复完整性
    验证需求 11.4: 恢复后文档内容不变
    """
    # 记录原始内容
    original_contents = {}
    for doc in sample_documents:
        with open(doc.file_path, 'r', encoding='utf-8') as f:
            original_contents[doc.file_path] = f.read()
    
    # 创建备份
    backup_info = backup_manager.create_backup(sample_documents, temp_project_dir)
    
    # 删除原始文件
    for doc in sample_documents:
        os.remove(doc.file_path)
    
    # 恢复备份
    restore_result = backup_manager.restore_from_backup(backup_info, temp_project_dir)
    
    # 验证恢复完整性
    assert restore_result.success
    assert restore_result.restored_count == len(sample_documents)
    assert len(restore_result.failed_documents) == 0
    
    # 验证所有文件内容不变
    for file_path, original_content in original_contents.items():
        assert os.path.exists(file_path), f"文件未恢复: {file_path}"
        with open(file_path, 'r', encoding='utf-8') as f:
            restored_content = f.read()
        assert restored_content == original_content, f"文件内容已改变: {file_path}"


def test_restore_handles_missing_manifest(backup_manager, temp_project_dir):
    """测试恢复功能处理缺失的清单文件"""
    # 创建一个没有清单的备份信息
    fake_backup_path = os.path.join(temp_project_dir, ".backup", "docs", "fake_backup")
    os.makedirs(fake_backup_path, exist_ok=True)
    
    fake_backup_info = BackupInfo(
        backup_id="fake_backup",
        backup_path=fake_backup_path,
        timestamp=datetime.now(),
        document_count=0,
        manifest=[]
    )
    
    # 尝试恢复
    restore_result = backup_manager.restore_from_backup(fake_backup_info, temp_project_dir)
    
    # 验证失败并有错误信息
    assert not restore_result.success
    assert restore_result.error_message is not None
    assert "清单文件不存在" in restore_result.error_message


def test_restore_handles_partial_failures(backup_manager, sample_documents, temp_project_dir):
    """测试恢复功能处理部分失败的情况"""
    # 创建备份
    backup_info = backup_manager.create_backup(sample_documents, temp_project_dir)
    
    # 删除原始文件
    for doc in sample_documents:
        os.remove(doc.file_path)
    
    # 删除备份中的一个文件以模拟部分失败
    first_doc = sample_documents[0]
    backup_file = os.path.join(backup_info.backup_path, first_doc.relative_path)
    os.remove(backup_file)
    
    # 恢复备份
    restore_result = backup_manager.restore_from_backup(backup_info, temp_project_dir)
    
    # 验证部分成功
    assert not restore_result.success  # 因为有失败
    assert restore_result.restored_count == len(sample_documents) - 1
    assert len(restore_result.failed_documents) > 0
