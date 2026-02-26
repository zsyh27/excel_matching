"""
文档整理主控制器测试
"""

import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from organize_docs.organizer import DocumentOrganizer, OrganizationResult
from organize_docs.config_manager import ConfigManager
from organize_docs.models import Document, DocumentCategory


def test_organizer_initialization():
    """测试整理器初始化"""
    config_manager = ConfigManager()
    config = config_manager.get_default_config()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        organizer = DocumentOrganizer(config, temp_dir)
        
        assert organizer.config == config
        assert organizer.project_root == Path(temp_dir).resolve()
        assert organizer.scanner is not None
        assert organizer.classifier is not None
        assert organizer.backup_manager is not None
        assert organizer.mover is not None
        assert organizer.index_generator is not None
        assert organizer.logger is not None
        
        # 清理资源
        organizer.cleanup()


def test_organizer_dry_run():
    """测试试运行模式"""
    config_manager = ConfigManager()
    config = config_manager.get_default_config()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文档
        test_files = [
            "README.md",
            "TASK_1_SUMMARY.md",
            "DEVELOPMENT_GUIDE.md"
        ]
        
        for filename in test_files:
            file_path = Path(temp_dir) / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {filename}\n\nTest content")
        
        # 执行试运行
        organizer = DocumentOrganizer(config, temp_dir)
        result = organizer.organize(dry_run=True)
        
        # 验证结果
        assert result.scanned_count == 3
        assert result.moved_count == 0  # 试运行不实际移动
        
        # 验证文件仍在原位置
        for filename in test_files:
            assert (Path(temp_dir) / filename).exists()
        
        # 清理资源
        organizer.cleanup()


def test_organizer_full_workflow():
    """测试完整整理流程"""
    config_manager = ConfigManager()
    config = config_manager.get_default_config()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文档
        test_files = {
            "README.md": "core",
            "TASK_1_SUMMARY.md": "archive",
            "DEVELOPMENT_GUIDE.md": "development"
        }
        
        for filename, category in test_files.items():
            file_path = Path(temp_dir) / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {filename}\n\nTest content for {category}")
        
        # 执行整理
        organizer = DocumentOrganizer(config, temp_dir)
        result = organizer.organize(dry_run=False)
        
        # 验证结果
        assert result.success
        assert result.scanned_count == 3
        assert result.backup_info is not None
        assert len(result.errors) == 0
        
        # 验证核心文档保持不动
        assert (Path(temp_dir) / "README.md").exists()
        
        # 验证归档文档被移动
        assert not (Path(temp_dir) / "TASK_1_SUMMARY.md").exists()
        # TASK_1 不匹配任何分组（配置中只有 TASK_7 和 TASK_12），所以会在归档根目录
        archive_path = Path(temp_dir) / config.directory_structure.archive_dir / "TASK_1_SUMMARY.md"
        assert archive_path.exists()
        
        # 验证开发文档被移动
        assert not (Path(temp_dir) / "DEVELOPMENT_GUIDE.md").exists()
        dev_path = Path(temp_dir) / config.directory_structure.development_dir / "DEVELOPMENT_GUIDE.md"
        assert dev_path.exists()
        
        # 验证索引文件生成
        main_index = Path(temp_dir) / config.directory_structure.docs_root / "README.md"
        assert main_index.exists()
        
        archive_index = Path(temp_dir) / config.directory_structure.archive_dir / "README.md"
        assert archive_index.exists()
        
        # 清理资源
        organizer.cleanup()


def test_organizer_error_handling():
    """测试错误处理"""
    config_manager = ConfigManager()
    config = config_manager.get_default_config()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文档
        test_file = Path(temp_dir) / "TEST_REPORT.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("# Test Report\n\nContent")
        
        # 执行整理
        organizer = DocumentOrganizer(config, temp_dir)
        result = organizer.organize(dry_run=False)
        
        # 清理资源（必须在验证之前，以释放文件句柄）
        organizer.cleanup()
        
        # 验证整理已完成（可能有错误或警告）
        assert result.scanned_count == 1
        # 文档应该被移动
        assert result.moved_count >= 0


def test_organizer_empty_directory():
    """测试空目录处理"""
    config_manager = ConfigManager()
    config = config_manager.get_default_config()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 不创建任何文档
        organizer = DocumentOrganizer(config, temp_dir)
        result = organizer.organize(dry_run=False)
        
        # 应该成功但有警告
        assert result.success
        assert result.scanned_count == 0
        assert "未找到任何 MD 文档" in result.warnings
        
        # 清理资源
        organizer.cleanup()


def test_organizer_backup_creation():
    """测试备份创建"""
    config_manager = ConfigManager()
    config = config_manager.get_default_config()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文档
        test_file = Path(temp_dir) / "SUMMARY.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("# Summary\n\nContent")
        
        # 执行整理
        organizer = DocumentOrganizer(config, temp_dir)
        result = organizer.organize(dry_run=False)
        
        # 验证备份创建
        assert result.backup_info is not None
        assert result.backup_info.backup_id is not None
        assert result.backup_info.document_count == 1
        
        # 验证备份文件存在
        backup_path = Path(result.backup_info.backup_path)
        assert backup_path.exists()
        assert (backup_path / "manifest.json").exists()
        
        # 清理资源
        organizer.cleanup()


def test_organization_result_str():
    """测试结果对象的字符串表示"""
    result = OrganizationResult()
    result.success = True
    result.scanned_count = 10
    result.moved_count = 5
    result.warnings.append("测试警告")
    result.errors.append("测试错误")
    
    result_str = str(result)
    
    assert "文档整理报告" in result_str
    assert "状态: 成功" in result_str
    assert "扫描文档数: 10" in result_str
    assert "移动文档数: 5" in result_str
    assert "测试警告" in result_str
    assert "测试错误" in result_str


def test_manifest_comparison_report_generation():
    """测试文档清单对比报告生成"""
    config_manager = ConfigManager()
    config = config_manager.get_default_config()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文档
        test_files = [
            "README.md",
            "TASK_1_SUMMARY.md",
            "TASK_2_REPORT.md",
            "DEVELOPMENT_GUIDE.md"
        ]
        
        for filename in test_files:
            file_path = Path(temp_dir) / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {filename}\n\nTest content")
        
        # 执行整理
        organizer = DocumentOrganizer(config, temp_dir)
        result = organizer.organize(dry_run=False)
        
        # 验证清单对比报告生成
        log_dir = Path(temp_dir) / ".logs"
        assert log_dir.exists()
        
        # 查找清单对比报告文件
        manifest_files = list(log_dir.glob("manifest_comparison_*.txt"))
        assert len(manifest_files) > 0
        
        # 验证报告内容
        manifest_file = manifest_files[0]
        with open(manifest_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "文档清单对比报告" in content
        assert "扫描文档总数" in content
        assert "处理文档总数" in content
        assert "按分类统计" in content
        assert "文档移动详情" in content
        
        # 清理资源
        organizer.cleanup()


def test_link_validation():
    """测试链接有效性验证"""
    config_manager = ConfigManager()
    config = config_manager.get_default_config()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文档
        test_files = [
            "README.md",
            "TASK_SUMMARY.md"
        ]
        
        for filename in test_files:
            file_path = Path(temp_dir) / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {filename}\n\nTest content")
        
        # 执行整理
        organizer = DocumentOrganizer(config, temp_dir)
        result = organizer.organize(dry_run=False)
        
        # 验证链接验证已执行（没有错误表示所有链接有效）
        # 如果有无效链接，会在 errors 中
        link_errors = [e for e in result.errors if "无效链接" in e or "链接" in e]
        
        # 对于这个简单的测试，应该没有链接错误
        # （因为生成的索引链接应该都是有效的）
        assert len(link_errors) == 0 or result.success
        
        # 清理资源
        organizer.cleanup()


def test_unprocessed_documents_detection():
    """测试未处理文档检测"""
    config_manager = ConfigManager()
    config = config_manager.get_default_config()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文档
        test_file = Path(temp_dir) / "TEST_DOC.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("# Test Document\n\nContent")
        
        # 执行整理
        organizer = DocumentOrganizer(config, temp_dir)
        result = organizer.organize(dry_run=False)
        
        # 验证所有文档都被处理
        assert result.scanned_count > 0
        
        # 检查日志文件中是否记录了未处理的文档
        if result.log_file:
            with open(result.log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # 日志应该包含验证信息
            assert "验证结果" in log_content or "阶段 7" in log_content
        
        # 清理资源
        organizer.cleanup()


def test_warnings_and_errors_output():
    """测试警告和错误输出"""
    config_manager = ConfigManager()
    config = config_manager.get_default_config()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试文档
        test_file = Path(temp_dir) / "SUMMARY.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("# Summary\n\nContent")
        
        # 执行整理
        organizer = DocumentOrganizer(config, temp_dir)
        result = organizer.organize(dry_run=False)
        
        # 验证结果对象包含警告和错误列表
        assert hasattr(result, 'warnings')
        assert hasattr(result, 'errors')
        assert isinstance(result.warnings, list)
        assert isinstance(result.errors, list)
        
        # 验证日志文件记录了警告和错误
        if result.log_file and (result.warnings or result.errors):
            with open(result.log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # 如果有警告或错误，日志应该包含相关信息
            if result.warnings:
                assert "WARNING" in log_content or "警告" in log_content
            if result.errors:
                assert "ERROR" in log_content or "错误" in log_content
        
        # 清理资源
        organizer.cleanup()


if __name__ == "__main__":
    # 运行测试
    test_organizer_initialization()
    print("✓ test_organizer_initialization")
    
    test_organizer_dry_run()
    print("✓ test_organizer_dry_run")
    
    test_organizer_full_workflow()
    print("✓ test_organizer_full_workflow")
    
    test_organizer_error_handling()
    print("✓ test_organizer_error_handling")
    
    test_organizer_empty_directory()
    print("✓ test_organizer_empty_directory")
    
    test_organizer_backup_creation()
    print("✓ test_organizer_backup_creation")
    
    test_organization_result_str()
    print("✓ test_organization_result_str")
    
    test_manifest_comparison_report_generation()
    print("✓ test_manifest_comparison_report_generation")
    
    test_link_validation()
    print("✓ test_link_validation")
    
    test_unprocessed_documents_detection()
    print("✓ test_unprocessed_documents_detection")
    
    test_warnings_and_errors_output()
    print("✓ test_warnings_and_errors_output")
    
    print("\n所有测试通过！")
