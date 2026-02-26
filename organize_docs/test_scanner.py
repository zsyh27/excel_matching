"""
文档扫描器测试

测试文档扫描功能。
"""

import os
import tempfile
from pathlib import Path
from datetime import datetime

from .scanner import DocumentScanner
from .models import Document


def test_scanner_finds_md_files():
    """测试扫描器能找到 MD 文件"""
    # 创建临时测试目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件
        test_file = Path(temp_dir) / "test.md"
        test_file.write_text("# Test Document\n\nThis is a test.", encoding='utf-8')
        
        # 扫描
        scanner = DocumentScanner()
        documents = scanner.scan_directory(temp_dir, exclude_dirs=[])
        
        # 验证
        assert len(documents) == 1
        assert documents[0].file_name == "test.md"
        assert documents[0].size > 0
        assert "Test Document" in documents[0].content_preview


def test_scanner_excludes_directories():
    """测试扫描器排除指定目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件结构
        Path(temp_dir, "root.md").write_text("Root doc", encoding='utf-8')
        
        # 创建应该被排除的目录
        node_modules = Path(temp_dir) / "node_modules"
        node_modules.mkdir()
        (node_modules / "excluded.md").write_text("Should be excluded", encoding='utf-8')
        
        git_dir = Path(temp_dir) / ".git"
        git_dir.mkdir()
        (git_dir / "config.md").write_text("Git config", encoding='utf-8')
        
        # 扫描，排除 node_modules 和 .git
        scanner = DocumentScanner()
        documents = scanner.scan_directory(
            temp_dir,
            exclude_dirs=["node_modules/**", ".git/**"]
        )
        
        # 验证：只找到根目录的文件
        assert len(documents) == 1
        assert documents[0].file_name == "root.md"


def test_scanner_recursive_scan():
    """测试扫描器递归扫描子目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建多层目录结构
        Path(temp_dir, "root.md").write_text("Root", encoding='utf-8')
        
        subdir = Path(temp_dir) / "subdir"
        subdir.mkdir()
        (subdir / "sub.md").write_text("Sub", encoding='utf-8')
        
        subsubdir = subdir / "subsubdir"
        subsubdir.mkdir()
        (subsubdir / "subsub.md").write_text("SubSub", encoding='utf-8')
        
        # 扫描
        scanner = DocumentScanner()
        documents = scanner.scan_directory(temp_dir, exclude_dirs=[])
        
        # 验证：找到所有 3 个文件
        assert len(documents) == 3
        file_names = {doc.file_name for doc in documents}
        assert file_names == {"root.md", "sub.md", "subsub.md"}


def test_get_document_info():
    """测试获取单个文档信息"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文件
        test_file = Path(temp_dir) / "info_test.md"
        content = "# Info Test\n\nThis is a test document for info extraction."
        test_file.write_text(content, encoding='utf-8')
        
        # 获取文档信息
        scanner = DocumentScanner()
        doc = scanner.get_document_info(str(test_file), temp_dir)
        
        # 验证
        assert doc.file_name == "info_test.md"
        assert doc.size > 0  # 文件大小应该大于 0（不检查精确值，因为不同系统行尾符不同）
        assert isinstance(doc.modified_time, datetime)
        assert "Info Test" in doc.content_preview
        assert doc.relative_path == "info_test.md"


def test_scanner_handles_non_utf8_files():
    """测试扫描器处理非 UTF-8 编码的文件"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建 GBK 编码的文件
        test_file = Path(temp_dir) / "gbk_test.md"
        content = "# 中文测试\n\n这是一个测试文档。"
        test_file.write_text(content, encoding='gbk')
        
        # 扫描
        scanner = DocumentScanner()
        documents = scanner.scan_directory(temp_dir, exclude_dirs=[])
        
        # 验证：应该能够读取文件（即使编码不同）
        assert len(documents) == 1
        assert documents[0].file_name == "gbk_test.md"
        # 内容预览可能包含中文或错误信息
        assert documents[0].content_preview is not None


def test_scanner_empty_directory():
    """测试扫描空目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 扫描空目录
        scanner = DocumentScanner()
        documents = scanner.scan_directory(temp_dir, exclude_dirs=[])
        
        # 验证：返回空列表
        assert len(documents) == 0


def test_scanner_only_non_md_files():
    """测试目录只包含非 MD 文件"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建非 MD 文件
        Path(temp_dir, "test.txt").write_text("Text file", encoding='utf-8')
        Path(temp_dir, "test.py").write_text("# Python file", encoding='utf-8')
        
        # 扫描
        scanner = DocumentScanner()
        documents = scanner.scan_directory(temp_dir, exclude_dirs=[])
        
        # 验证：不应该找到任何文件
        assert len(documents) == 0


if __name__ == '__main__':
    # 运行测试
    test_scanner_finds_md_files()
    print("✓ test_scanner_finds_md_files")
    
    test_scanner_excludes_directories()
    print("✓ test_scanner_excludes_directories")
    
    test_scanner_recursive_scan()
    print("✓ test_scanner_recursive_scan")
    
    test_get_document_info()
    print("✓ test_get_document_info")
    
    test_scanner_handles_non_utf8_files()
    print("✓ test_scanner_handles_non_utf8_files")
    
    test_scanner_empty_directory()
    print("✓ test_scanner_empty_directory")
    
    test_scanner_only_non_md_files()
    print("✓ test_scanner_only_non_md_files")
    
    print("\n所有测试通过！")
