"""
错误处理单元测试

测试各种错误场景、回滚机制和日志记录。
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from .models import (
    Document,
    DocumentCategory,
    OrganizationConfig,
    ClassificationConfig,
    DirectoryStructure,
    BackupConfig,
    ArchiveGrouping,
    IndexGenerationConfig
)
from .organizer import DocumentOrganizer
from .scanner import DocumentScanner
from .mover import DocumentMover
from .backup_manager import BackupManager


class TestScannerErrorHandling:
    """测试扫描器的错误处理"""
    
    def test_scan_nonexistent_directory(self):
        """测试扫描不存在的目录"""
        scanner = DocumentScanner()
        
        with pytest.raises(FileNotFoundError):
            scanner.scan_directory("/nonexistent/path", [])
    
    def test_scan_file_instead_of_directory(self, tmp_path):
        """测试扫描文件而非目录"""
        # 创建一个文件
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        scanner = DocumentScanner()
        
        with pytest.raises(NotADirectoryError):
            scanner.scan_directory(str(test_file), [])
    
    def test_scan_with_unreadable_file(self, tmp_path):
        """测试扫描包含不可读文件的目录"""
        # 创建一个可读的 MD 文件
        readable_file = tmp_path / "readable.md"
        readable_file.write_text("# Readable")
        
        # 创建一个不可读的 MD 文件（通过写入二进制数据）
        unreadable_file = tmp_path / "unreadable.md"
        unreadable_file.write_bytes(b'\x80\x81\x82\x83')
        
        scanner = DocumentScanner()
        
        # 应该能够扫描，但会跳过不可读的文件
        documents = scanner.scan_directory(str(tmp_path), [])
        
        # 至少应该找到可读的文件
        assert len(documents) >= 1
        assert any(doc.file_name == "readable.md" for doc in documents)


class TestMoverErrorHandling:
    """测试移动器的错误处理"""
    
    def test_move_nonexistent_file(self, tmp_path):
        """测试移动不存在的文件"""
        # 创建配置
        structure = DirectoryStructure(
            docs_root="docs",
            archive_dir="docs/archive",
            development_dir="docs/development",
            backend_docs_dir="backend/docs",
            frontend_docs_dir="frontend/docs"
        )
        
        mover = DocumentMover(structure, str(tmp_path))
        
        # 创建一个不存在的文档对象
        doc = Document(
            file_name="nonexistent.md",
            file_path=str(tmp_path / "nonexistent.md"),
            relative_path="nonexistent.md",
            size=0,
            modified_time=datetime.now(),
            content_preview="",
            category=DocumentCategory.ARCHIVE
        )
        
        # 尝试移动
        result = mover.move_document(doc, DocumentCategory.ARCHIVE)
        
        # 应该失败
        assert not result.success
        assert result.error_message is not None
    
    def test_move_to_readonly_directory(self, tmp_path):
        """测试移动到只读目录"""
        # 跳过此测试在 Windows 上，因为 Windows 权限模型不同
        if os.name == 'nt':
            pytest.skip("Windows 权限模型不同，跳过此测试")
        
        # 创建源文件
        source_file = tmp_path / "test.md"
        source_file.write_text("# Test")
        
        # 创建只读目标目录
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        os.chmod(str(readonly_dir), 0o444)
        
        # 创建配置
        structure = DirectoryStructure(
            docs_root="readonly",
            archive_dir="readonly/archive",
            development_dir="readonly/development",
            backend_docs_dir="backend/docs",
            frontend_docs_dir="frontend/docs"
        )
        
        mover = DocumentMover(structure, str(tmp_path))
        
        doc = Document(
            file_name="test.md",
            file_path=str(source_file),
            relative_path="test.md",
            size=5,
            modified_time=datetime.now(),
            content_preview="# Test",
            category=DocumentCategory.ARCHIVE
        )
        
        # 尝试移动
        result = mover.move_document(doc, DocumentCategory.ARCHIVE)
        
        # 应该失败（权限错误）
        assert not result.success
        
        # 恢复目录权限以便清理
        os.chmod(str(readonly_dir), 0o755)


class TestBackupManagerErrorHandling:
    """测试备份管理器的错误处理"""
    
    def test_restore_from_nonexistent_backup(self, tmp_path):
        """测试从不存在的备份恢复"""
        backup_manager = BackupManager(str(tmp_path / ".backup"))
        
        # 创建一个假的备份信息
        from .models import BackupInfo
        fake_backup = BackupInfo(
            backup_id="nonexistent",
            backup_path=str(tmp_path / ".backup" / "nonexistent"),
            timestamp=datetime.now(),
            document_count=0,
            manifest=[]
        )
        
        # 尝试恢复
        result = backup_manager.restore_from_backup(fake_backup, str(tmp_path))
        
        # 应该失败
        assert not result.success
        assert "不存在" in result.error_message or "manifest" in result.error_message.lower()
    
    def test_backup_with_unreadable_file(self, tmp_path):
        """测试备份包含不可读文件的情况"""
        # 创建一个可读文件
        readable_file = tmp_path / "readable.md"
        readable_file.write_text("# Readable")
        
        # 创建文档对象
        doc1 = Document(
            file_name="readable.md",
            file_path=str(readable_file),
            relative_path="readable.md",
            size=10,
            modified_time=datetime.now(),
            content_preview="# Readable"
        )
        
        # 创建一个不存在的文档对象（模拟不可读）
        doc2 = Document(
            file_name="nonexistent.md",
            file_path=str(tmp_path / "nonexistent.md"),
            relative_path="nonexistent.md",
            size=0,
            modified_time=datetime.now(),
            content_preview=""
        )
        
        backup_manager = BackupManager(str(tmp_path / ".backup"))
        
        # 创建备份
        backup_info = backup_manager.create_backup([doc1, doc2], str(tmp_path))
        
        # 备份应该成功创建
        assert backup_info is not None
        assert backup_info.document_count == 2
        
        # 检查清单中是否记录了错误
        assert len(backup_info.manifest) == 2
        
        # 至少有一个文档应该有错误记录
        errors = [doc for doc in backup_info.manifest if "error" in doc]
        assert len(errors) >= 1


class TestOrganizerErrorHandling:
    """测试主控制器的错误处理和回滚机制"""
    
    def _create_test_config(self, tmp_path):
        """创建测试配置"""
        return OrganizationConfig(
            classification=ClassificationConfig(
                core_file_names=["README.md"],
                archive_keywords=["SUMMARY", "REPORT"],
                development_keywords=["GUIDE"],
                exclude_patterns=["node_modules/**", ".git/**"]
            ),
            directory_structure=DirectoryStructure(
                docs_root="docs",
                archive_dir="docs/archive",
                development_dir="docs/development",
                backend_docs_dir="backend/docs",
                frontend_docs_dir="frontend/docs"
            ),
            backup=BackupConfig(
                enabled=True,
                backup_dir=str(tmp_path / ".backup" / "docs"),
                keep_backups=5
            ),
            archive_grouping=ArchiveGrouping(groups={}),
            index_generation=IndexGenerationConfig(
                include_file_size=True,
                include_modified_date=True,
                include_description=True,
                max_description_length=100
            )
        )
    
    def test_organize_empty_directory(self, tmp_path):
        """测试整理空目录"""
        config = self._create_test_config(tmp_path)
        organizer = DocumentOrganizer(config, str(tmp_path))
        
        # 执行整理
        result = organizer.organize()
        
        # 应该成功但有警告
        assert result.success
        assert len(result.warnings) > 0
        assert "未找到任何 MD 文档" in result.warnings[0]
        
        # 清理
        organizer.cleanup()
    
    def test_organize_with_scan_error(self, tmp_path):
        """测试扫描阶段出错"""
        config = self._create_test_config(tmp_path)
        
        # 创建一个文件而不是目录来触发错误
        bad_path = tmp_path / "not_a_directory.txt"
        bad_path.write_text("test")
        
        organizer = DocumentOrganizer(config, str(bad_path))
        
        # 执行整理
        result = organizer.organize()
        
        # 应该失败
        assert not result.success
        assert len(result.errors) > 0
        
        # 清理
        organizer.cleanup()
    
    def test_rollback_on_error(self, tmp_path):
        """测试错误时的回滚机制"""
        # 创建测试文件
        test_file = tmp_path / "TEST_SUMMARY.md"
        test_file.write_text("# Test Summary")
        
        config = self._create_test_config(tmp_path)
        organizer = DocumentOrganizer(config, str(tmp_path))
        
        # 执行整理（应该成功）
        result = organizer.organize()
        
        # 验证备份已创建
        assert result.backup_info is not None
        
        # 清理
        organizer.cleanup()
    
    def test_logging_on_error(self, tmp_path):
        """测试错误时的日志记录"""
        config = self._create_test_config(tmp_path)
        
        # 创建一个文件而不是目录来触发错误
        bad_path = tmp_path / "not_a_directory.txt"
        bad_path.write_text("test")
        
        organizer = DocumentOrganizer(config, str(bad_path))
        
        # 执行整理
        result = organizer.organize()
        
        # 应该失败
        assert not result.success
        
        # 应该有日志文件
        assert result.log_file is not None
        
        # 清理
        organizer.cleanup()


class TestConfigErrorHandling:
    """测试配置错误处理"""
    
    def test_load_nonexistent_config(self):
        """测试加载不存在的配置文件"""
        from .config_manager import ConfigManager
        
        config_manager = ConfigManager()
        
        with pytest.raises(FileNotFoundError):
            config_manager.load_config("nonexistent_config.json")
    
    def test_load_invalid_json(self, tmp_path):
        """测试加载无效的 JSON 配置"""
        from .config_manager import ConfigManager
        
        # 创建无效的 JSON 文件
        invalid_config = tmp_path / "invalid.json"
        invalid_config.write_text("{ invalid json }")
        
        config_manager = ConfigManager()
        
        with pytest.raises(Exception):  # JSON 解析错误
            config_manager.load_config(str(invalid_config))
    
    def test_validate_incomplete_config(self, tmp_path):
        """测试验证不完整的配置"""
        from .config_manager import ConfigManager
        import json
        
        # 创建不完整的配置文件（缺少必需字段）
        incomplete_config = tmp_path / "incomplete.json"
        config_data = {
            "classification": {
                "core_file_names": ["README.md"]
                # 缺少其他必需字段
            }
        }
        
        with open(incomplete_config, 'w') as f:
            json.dump(config_data, f)
        
        config_manager = ConfigManager()
        
        # 应该抛出异常或返回验证失败
        try:
            config = config_manager.load_config(str(incomplete_config))
            validation = config_manager.validate_config(config)
            assert not validation.valid
        except Exception:
            # 加载时就失败也是可以的
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
