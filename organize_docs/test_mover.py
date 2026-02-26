"""
文档移动器测试

测试文档移动器的目录创建和文档移动功能。
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest

from .mover import DocumentMover
from .models import DirectoryStructure, Document, DocumentCategory
from datetime import datetime


class TestDocumentMover:
    """测试 DocumentMover 类"""
    
    @pytest.fixture
    def temp_project_dir(self):
        """创建临时项目目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # 清理
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def directory_structure(self):
        """创建测试用的目录结构配置"""
        return DirectoryStructure(
            docs_root="docs",
            archive_dir="docs/archive",
            development_dir="docs/development",
            backend_docs_dir="backend/docs",
            frontend_docs_dir="frontend/docs"
        )
    
    def test_create_directory_structure_creates_all_directories(self, temp_project_dir, directory_structure):
        """测试创建目录结构时创建所有必需的目录"""
        # 创建移动器
        mover = DocumentMover(directory_structure, temp_project_dir)
        
        # 执行目录创建
        mover.create_directory_structure()
        
        # 验证 docs/ 根目录存在
        docs_root = Path(temp_project_dir) / "docs"
        assert docs_root.exists()
        assert docs_root.is_dir()
        
        # 验证 docs/archive/ 子目录存在
        archive_dir = Path(temp_project_dir) / "docs" / "archive"
        assert archive_dir.exists()
        assert archive_dir.is_dir()
        
        # 验证 docs/development/ 子目录存在
        development_dir = Path(temp_project_dir) / "docs" / "development"
        assert development_dir.exists()
        assert development_dir.is_dir()
        
        # 验证 backend/docs/ 目录存在
        backend_docs = Path(temp_project_dir) / "backend" / "docs"
        assert backend_docs.exists()
        assert backend_docs.is_dir()
        
        # 验证 frontend/docs/ 目录存在
        frontend_docs = Path(temp_project_dir) / "frontend" / "docs"
        assert frontend_docs.exists()
        assert frontend_docs.is_dir()
    
    def test_create_directory_structure_idempotent(self, temp_project_dir, directory_structure):
        """测试多次调用创建目录结构是幂等的（不会报错）"""
        mover = DocumentMover(directory_structure, temp_project_dir)
        
        # 第一次创建
        mover.create_directory_structure()
        
        # 第二次创建（应该不会报错）
        mover.create_directory_structure()
        
        # 验证目录仍然存在
        docs_root = Path(temp_project_dir) / "docs"
        assert docs_root.exists()
    
    def test_create_directory_structure_with_existing_parent(self, temp_project_dir, directory_structure):
        """测试当父目录已存在时创建子目录"""
        # 预先创建 docs/ 目录
        docs_root = Path(temp_project_dir) / "docs"
        docs_root.mkdir()
        
        # 创建移动器并执行
        mover = DocumentMover(directory_structure, temp_project_dir)
        mover.create_directory_structure()
        
        # 验证子目录被创建
        archive_dir = Path(temp_project_dir) / "docs" / "archive"
        assert archive_dir.exists()
        
        development_dir = Path(temp_project_dir) / "docs" / "development"
        assert development_dir.exists()
    
    def test_create_directory_structure_with_custom_paths(self, temp_project_dir):
        """测试使用自定义路径创建目录结构"""
        custom_structure = DirectoryStructure(
            docs_root="documentation",
            archive_dir="documentation/old",
            development_dir="documentation/dev",
            backend_docs_dir="server/documentation",
            frontend_docs_dir="client/documentation"
        )
        
        mover = DocumentMover(custom_structure, temp_project_dir)
        mover.create_directory_structure()
        
        # 验证自定义路径的目录被创建
        assert (Path(temp_project_dir) / "documentation").exists()
        assert (Path(temp_project_dir) / "documentation" / "old").exists()
        assert (Path(temp_project_dir) / "documentation" / "dev").exists()
        assert (Path(temp_project_dir) / "server" / "documentation").exists()
        assert (Path(temp_project_dir) / "client" / "documentation").exists()
    
    def test_create_directory_structure_with_empty_backend_frontend(self, temp_project_dir):
        """测试当 backend/frontend 目录配置为空时不创建"""
        structure = DirectoryStructure(
            docs_root="docs",
            archive_dir="docs/archive",
            development_dir="docs/development",
            backend_docs_dir="",
            frontend_docs_dir=""
        )
        
        mover = DocumentMover(structure, temp_project_dir)
        mover.create_directory_structure()
        
        # 验证 docs 相关目录被创建
        assert (Path(temp_project_dir) / "docs").exists()
        assert (Path(temp_project_dir) / "docs" / "archive").exists()
        
        # 验证 backend/frontend 目录不存在
        assert not (Path(temp_project_dir) / "backend").exists()
        assert not (Path(temp_project_dir) / "frontend").exists()
    
    def test_create_directory_structure_with_archive_grouping(self, temp_project_dir, directory_structure):
        """测试创建归档分组子目录"""
        archive_grouping = {
            "device-row-recognition": ["DEVICE_ROW_RECOGNITION", "TASK_9"],
            "device-library": ["DEVICE_LIBRARY_EXPANSION"],
            "ui-optimization": ["UI_OPTIMIZATION", "UI_TOOLTIP"]
        }
        
        mover = DocumentMover(directory_structure, temp_project_dir, archive_grouping)
        mover.create_directory_structure()
        
        # 验证归档分组子目录被创建
        archive_base = Path(temp_project_dir) / "docs" / "archive"
        assert (archive_base / "device-row-recognition").exists()
        assert (archive_base / "device-library").exists()
        assert (archive_base / "ui-optimization").exists()
    
    def test_get_archive_group_matches_keyword(self, temp_project_dir, directory_structure):
        """测试根据关键词匹配归档分组"""
        archive_grouping = {
            "device-row-recognition": ["DEVICE_ROW_RECOGNITION", "TASK_9"],
            "ui-optimization": ["UI_OPTIMIZATION", "UI_TOOLTIP"],
            "troubleshooting": ["TROUBLESHOOTING", "MANUAL_ADJUST"]
        }
        
        mover = DocumentMover(directory_structure, temp_project_dir, archive_grouping)
        
        # 测试匹配 DEVICE_ROW_RECOGNITION 关键词
        doc1 = Document(
            file_name="DEVICE_ROW_RECOGNITION_FINAL_SUMMARY.md",
            file_path="/test/DEVICE_ROW_RECOGNITION_FINAL_SUMMARY.md",
            relative_path="DEVICE_ROW_RECOGNITION_FINAL_SUMMARY.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="Test content"
        )
        assert mover.get_archive_group(doc1) == "device-row-recognition"
        
        # 测试匹配 UI_OPTIMIZATION 关键词
        doc2 = Document(
            file_name="UI_OPTIMIZATION_SUMMARY.md",
            file_path="/test/UI_OPTIMIZATION_SUMMARY.md",
            relative_path="UI_OPTIMIZATION_SUMMARY.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="Test content"
        )
        assert mover.get_archive_group(doc2) == "ui-optimization"
        
        # 测试匹配 TASK_9 关键词
        doc3 = Document(
            file_name="TASK_9_FINAL_CHECKPOINT_REPORT.md",
            file_path="/test/TASK_9_FINAL_CHECKPOINT_REPORT.md",
            relative_path="TASK_9_FINAL_CHECKPOINT_REPORT.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="Test content"
        )
        assert mover.get_archive_group(doc3) == "device-row-recognition"
    
    def test_get_archive_group_case_insensitive(self, temp_project_dir, directory_structure):
        """测试归档分组匹配不区分大小写"""
        archive_grouping = {
            "testing": ["TEST_REPORT", "INTEGRATION_TEST"]
        }
        
        mover = DocumentMover(directory_structure, temp_project_dir, archive_grouping)
        
        # 测试小写文件名
        doc = Document(
            file_name="integration_test_results.md",
            file_path="/test/integration_test_results.md",
            relative_path="integration_test_results.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="Test content"
        )
        assert mover.get_archive_group(doc) == "testing"
    
    def test_get_archive_group_no_match(self, temp_project_dir, directory_structure):
        """测试文档不匹配任何分组时返回 None"""
        archive_grouping = {
            "device-row-recognition": ["DEVICE_ROW_RECOGNITION"],
            "ui-optimization": ["UI_OPTIMIZATION"]
        }
        
        mover = DocumentMover(directory_structure, temp_project_dir, archive_grouping)
        
        doc = Document(
            file_name="RANDOM_DOCUMENT.md",
            file_path="/test/RANDOM_DOCUMENT.md",
            relative_path="RANDOM_DOCUMENT.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="Test content"
        )
        assert mover.get_archive_group(doc) is None
    
    def test_get_archive_group_no_grouping_config(self, temp_project_dir, directory_structure):
        """测试没有分组配置时返回 None"""
        mover = DocumentMover(directory_structure, temp_project_dir)
        
        doc = Document(
            file_name="DEVICE_ROW_RECOGNITION_SUMMARY.md",
            file_path="/test/DEVICE_ROW_RECOGNITION_SUMMARY.md",
            relative_path="DEVICE_ROW_RECOGNITION_SUMMARY.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="Test content"
        )
        assert mover.get_archive_group(doc) is None
    
    def test_get_archive_group_first_match_wins(self, temp_project_dir, directory_structure):
        """测试当文档匹配多个分组时，返回第一个匹配的分组"""
        # 注意：Python 3.7+ 字典保持插入顺序
        archive_grouping = {
            "tasks": ["TASK_"],
            "device-row-recognition": ["TASK_9"]
        }
        
        mover = DocumentMover(directory_structure, temp_project_dir, archive_grouping)
        
        doc = Document(
            file_name="TASK_9_REPORT.md",
            file_path="/test/TASK_9_REPORT.md",
            relative_path="TASK_9_REPORT.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="Test content"
        )
        # 应该匹配第一个分组 "tasks"（因为 TASK_ 先匹配）
        assert mover.get_archive_group(doc) == "tasks"
    
    def test_get_target_path_core_document_returns_none(self, temp_project_dir, directory_structure):
        """测试核心文档的目标路径返回 None"""
        mover = DocumentMover(directory_structure, temp_project_dir)
        
        doc = Document(
            file_name="README.md",
            file_path=str(Path(temp_project_dir) / "README.md"),
            relative_path="README.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="Test content"
        )
        
        target_path = mover.get_target_path(doc, DocumentCategory.CORE)
        assert target_path is None
    
    def test_get_target_path_archive_document_without_group(self, temp_project_dir, directory_structure):
        """测试归档文档（无分组）的目标路径"""
        mover = DocumentMover(directory_structure, temp_project_dir)
        
        doc = Document(
            file_name="RANDOM_SUMMARY.md",
            file_path=str(Path(temp_project_dir) / "RANDOM_SUMMARY.md"),
            relative_path="RANDOM_SUMMARY.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="Test content"
        )
        
        target_path = mover.get_target_path(doc, DocumentCategory.ARCHIVE)
        expected_path = Path(temp_project_dir) / "docs" / "archive" / "RANDOM_SUMMARY.md"
        assert target_path == expected_path
    
    def test_get_target_path_archive_document_with_group(self, temp_project_dir, directory_structure):
        """测试归档文档（有分组）的目标路径"""
        archive_grouping = {
            "device-row-recognition": ["DEVICE_ROW_RECOGNITION"],
            "ui-optimization": ["UI_OPTIMIZATION"]
        }
        mover = DocumentMover(directory_structure, temp_project_dir, archive_grouping)
        
        doc = Document(
            file_name="DEVICE_ROW_RECOGNITION_SUMMARY.md",
            file_path=str(Path(temp_project_dir) / "DEVICE_ROW_RECOGNITION_SUMMARY.md"),
            relative_path="DEVICE_ROW_RECOGNITION_SUMMARY.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="Test content"
        )
        
        target_path = mover.get_target_path(doc, DocumentCategory.ARCHIVE)
        expected_path = Path(temp_project_dir) / "docs" / "archive" / "device-row-recognition" / "DEVICE_ROW_RECOGNITION_SUMMARY.md"
        assert target_path == expected_path
    
    def test_get_target_path_development_document_general(self, temp_project_dir, directory_structure):
        """测试通用开发文档的目标路径"""
        mover = DocumentMover(directory_structure, temp_project_dir)
        
        doc = Document(
            file_name="DEVELOPMENT_GUIDE.md",
            file_path=str(Path(temp_project_dir) / "DEVELOPMENT_GUIDE.md"),
            relative_path="DEVELOPMENT_GUIDE.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="Test content"
        )
        
        target_path = mover.get_target_path(doc, DocumentCategory.DEVELOPMENT)
        expected_path = Path(temp_project_dir) / "docs" / "development" / "DEVELOPMENT_GUIDE.md"
        assert target_path == expected_path
    
    def test_get_target_path_development_document_backend(self, temp_project_dir, directory_structure):
        """测试后端开发文档的目标路径"""
        mover = DocumentMover(directory_structure, temp_project_dir)
        
        doc = Document(
            file_name="API_GUIDE.md",
            file_path=str(Path(temp_project_dir) / "backend" / "API_GUIDE.md"),
            relative_path="backend/API_GUIDE.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="Test content"
        )
        
        target_path = mover.get_target_path(doc, DocumentCategory.DEVELOPMENT)
        expected_path = Path(temp_project_dir) / "backend" / "docs" / "API_GUIDE.md"
        assert target_path == expected_path
    
    def test_get_target_path_development_document_frontend(self, temp_project_dir, directory_structure):
        """测试前端开发文档的目标路径"""
        mover = DocumentMover(directory_structure, temp_project_dir)
        
        doc = Document(
            file_name="COMPONENT_GUIDE.md",
            file_path=str(Path(temp_project_dir) / "frontend" / "COMPONENT_GUIDE.md"),
            relative_path="frontend/COMPONENT_GUIDE.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="Test content"
        )
        
        target_path = mover.get_target_path(doc, DocumentCategory.DEVELOPMENT)
        expected_path = Path(temp_project_dir) / "frontend" / "docs" / "COMPONENT_GUIDE.md"
        assert target_path == expected_path
    
    def test_get_target_path_unknown_document(self, temp_project_dir, directory_structure):
        """测试未知分类文档的目标路径（默认移动到开发文档目录）"""
        mover = DocumentMover(directory_structure, temp_project_dir)
        
        doc = Document(
            file_name="UNKNOWN.md",
            file_path=str(Path(temp_project_dir) / "UNKNOWN.md"),
            relative_path="UNKNOWN.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="Test content"
        )
        
        target_path = mover.get_target_path(doc, DocumentCategory.UNKNOWN)
        expected_path = Path(temp_project_dir) / "docs" / "development" / "UNKNOWN.md"
        assert target_path == expected_path
    
    def test_move_document_core_stays_in_place(self, temp_project_dir, directory_structure):
        """测试核心文档保持原位置不动"""
        # 创建测试文件
        test_file = Path(temp_project_dir) / "README.md"
        test_file.write_text("# Test README", encoding="utf-8")
        
        doc = Document(
            file_name="README.md",
            file_path=str(test_file),
            relative_path="README.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="# Test README"
        )
        
        mover = DocumentMover(directory_structure, temp_project_dir)
        result = mover.move_document(doc, DocumentCategory.CORE)
        
        # 验证移动结果
        assert result.success is True
        assert result.original_path == str(test_file)
        assert result.new_path == str(test_file)
        assert result.error_message is None
        
        # 验证文件仍在原位置
        assert test_file.exists()
        assert test_file.read_text(encoding="utf-8") == "# Test README"
    
    def test_move_document_archive_without_group(self, temp_project_dir, directory_structure):
        """测试移动归档文档（无分组）"""
        # 创建测试文件
        test_file = Path(temp_project_dir) / "TEST_SUMMARY.md"
        test_file.write_text("# Test Summary", encoding="utf-8")
        
        doc = Document(
            file_name="TEST_SUMMARY.md",
            file_path=str(test_file),
            relative_path="TEST_SUMMARY.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="# Test Summary"
        )
        
        mover = DocumentMover(directory_structure, temp_project_dir)
        mover.create_directory_structure()
        result = mover.move_document(doc, DocumentCategory.ARCHIVE)
        
        # 验证移动结果
        assert result.success is True
        assert result.original_path == str(test_file)
        expected_new_path = Path(temp_project_dir) / "docs" / "archive" / "TEST_SUMMARY.md"
        assert result.new_path == str(expected_new_path)
        assert result.error_message is None
        
        # 验证文件已移动
        assert not test_file.exists()
        assert expected_new_path.exists()
        assert expected_new_path.read_text(encoding="utf-8") == "# Test Summary"
    
    def test_move_document_archive_with_group(self, temp_project_dir, directory_structure):
        """测试移动归档文档（有分组）"""
        archive_grouping = {
            "ui-optimization": ["UI_OPTIMIZATION"]
        }
        
        # 创建测试文件
        test_file = Path(temp_project_dir) / "UI_OPTIMIZATION_SUMMARY.md"
        test_file.write_text("# UI Optimization", encoding="utf-8")
        
        doc = Document(
            file_name="UI_OPTIMIZATION_SUMMARY.md",
            file_path=str(test_file),
            relative_path="UI_OPTIMIZATION_SUMMARY.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="# UI Optimization"
        )
        
        mover = DocumentMover(directory_structure, temp_project_dir, archive_grouping)
        mover.create_directory_structure()
        result = mover.move_document(doc, DocumentCategory.ARCHIVE)
        
        # 验证移动结果
        assert result.success is True
        expected_new_path = Path(temp_project_dir) / "docs" / "archive" / "ui-optimization" / "UI_OPTIMIZATION_SUMMARY.md"
        assert result.new_path == str(expected_new_path)
        
        # 验证文件已移动到分组目录
        assert not test_file.exists()
        assert expected_new_path.exists()
        assert expected_new_path.read_text(encoding="utf-8") == "# UI Optimization"
    
    def test_move_document_development_general(self, temp_project_dir, directory_structure):
        """测试移动通用开发文档"""
        # 创建测试文件
        test_file = Path(temp_project_dir) / "DEVELOPMENT_GUIDE.md"
        test_file.write_text("# Development Guide", encoding="utf-8")
        
        doc = Document(
            file_name="DEVELOPMENT_GUIDE.md",
            file_path=str(test_file),
            relative_path="DEVELOPMENT_GUIDE.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="# Development Guide"
        )
        
        mover = DocumentMover(directory_structure, temp_project_dir)
        mover.create_directory_structure()
        result = mover.move_document(doc, DocumentCategory.DEVELOPMENT)
        
        # 验证移动结果
        assert result.success is True
        expected_new_path = Path(temp_project_dir) / "docs" / "development" / "DEVELOPMENT_GUIDE.md"
        assert result.new_path == str(expected_new_path)
        
        # 验证文件已移动
        assert not test_file.exists()
        assert expected_new_path.exists()
        assert expected_new_path.read_text(encoding="utf-8") == "# Development Guide"
    
    def test_move_document_development_backend(self, temp_project_dir, directory_structure):
        """测试移动后端开发文档"""
        # 创建测试文件
        backend_dir = Path(temp_project_dir) / "backend"
        backend_dir.mkdir()
        test_file = backend_dir / "API_GUIDE.md"
        test_file.write_text("# API Guide", encoding="utf-8")
        
        doc = Document(
            file_name="API_GUIDE.md",
            file_path=str(test_file),
            relative_path="backend/API_GUIDE.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="# API Guide"
        )
        
        mover = DocumentMover(directory_structure, temp_project_dir)
        mover.create_directory_structure()
        result = mover.move_document(doc, DocumentCategory.DEVELOPMENT)
        
        # 验证移动结果
        assert result.success is True
        expected_new_path = Path(temp_project_dir) / "backend" / "docs" / "API_GUIDE.md"
        assert result.new_path == str(expected_new_path)
        
        # 验证文件已移动
        assert not test_file.exists()
        assert expected_new_path.exists()
        assert expected_new_path.read_text(encoding="utf-8") == "# API Guide"
    
    def test_move_document_creates_target_directory(self, temp_project_dir, directory_structure):
        """测试移动文档时自动创建目标目录"""
        # 创建测试文件（不预先创建目标目录）
        test_file = Path(temp_project_dir) / "TEST_DOC.md"
        test_file.write_text("# Test", encoding="utf-8")
        
        doc = Document(
            file_name="TEST_DOC.md",
            file_path=str(test_file),
            relative_path="TEST_DOC.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="# Test"
        )
        
        mover = DocumentMover(directory_structure, temp_project_dir)
        # 不调用 create_directory_structure()
        result = mover.move_document(doc, DocumentCategory.ARCHIVE)
        
        # 验证移动成功（目录自动创建）
        assert result.success is True
        expected_new_path = Path(temp_project_dir) / "docs" / "archive" / "TEST_DOC.md"
        assert expected_new_path.exists()
    
    def test_move_document_file_not_exists_fails(self, temp_project_dir, directory_structure):
        """测试移动不存在的文件时失败"""
        doc = Document(
            file_name="NONEXISTENT.md",
            file_path=str(Path(temp_project_dir) / "NONEXISTENT.md"),
            relative_path="NONEXISTENT.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="Test"
        )
        
        mover = DocumentMover(directory_structure, temp_project_dir)
        mover.create_directory_structure()
        result = mover.move_document(doc, DocumentCategory.ARCHIVE)
        
        # 验证移动失败
        assert result.success is False
        assert result.error_message is not None
    
    def test_move_document_preserves_file_content(self, temp_project_dir, directory_structure):
        """测试移动文档后内容保持不变"""
        # 创建测试文件，包含多行内容
        test_content = """# Test Document

This is a test document with multiple lines.

## Section 1
Content here.

## Section 2
More content.
"""
        test_file = Path(temp_project_dir) / "TEST_DOC.md"
        test_file.write_text(test_content, encoding="utf-8")
        
        doc = Document(
            file_name="TEST_DOC.md",
            file_path=str(test_file),
            relative_path="TEST_DOC.md",
            size=len(test_content),
            modified_time=datetime.now(),
            content_preview=test_content[:200]
        )
        
        mover = DocumentMover(directory_structure, temp_project_dir)
        mover.create_directory_structure()
        result = mover.move_document(doc, DocumentCategory.ARCHIVE)
        
        # 验证内容完全相同
        assert result.success is True
        new_file = Path(result.new_path)
        assert new_file.read_text(encoding="utf-8") == test_content
    
    def test_move_document_preserves_file_name(self, temp_project_dir, directory_structure):
        """测试移动文档后文件名保持不变"""
        test_file = Path(temp_project_dir) / "ORIGINAL_NAME.md"
        test_file.write_text("# Test", encoding="utf-8")
        
        doc = Document(
            file_name="ORIGINAL_NAME.md",
            file_path=str(test_file),
            relative_path="ORIGINAL_NAME.md",
            size=1000,
            modified_time=datetime.now(),
            content_preview="# Test"
        )
        
        mover = DocumentMover(directory_structure, temp_project_dir)
        mover.create_directory_structure()
        result = mover.move_document(doc, DocumentCategory.ARCHIVE)
        
        # 验证文件名不变
        assert result.success is True
        new_file = Path(result.new_path)
        assert new_file.name == "ORIGINAL_NAME.md"
