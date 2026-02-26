"""
索引生成器集成测试

演示如何使用 IndexGenerator 生成实际的文档索引文件。
"""

import os
import tempfile
from datetime import datetime
from organize_docs.index_generator import IndexGenerator
from organize_docs.models import Document, DocumentCategory, IndexGenerationConfig


def test_generate_and_write_main_index():
    """测试生成并写入主索引文件"""
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 准备文档数据
        documents = {
            DocumentCategory.CORE: [
                Document(
                    file_name="README.md",
                    file_path=os.path.join(temp_dir, "README.md"),
                    relative_path="README.md",
                    size=1000,
                    modified_time=datetime.now(),
                    content_preview="Main project README"
                ),
                Document(
                    file_name="SETUP.md",
                    file_path=os.path.join(temp_dir, "SETUP.md"),
                    relative_path="SETUP.md",
                    size=500,
                    modified_time=datetime.now(),
                    content_preview="Setup guide"
                )
            ],
            DocumentCategory.ARCHIVE: [
                Document(
                    file_name="TASK_1_SUMMARY.md",
                    file_path=os.path.join(temp_dir, "docs/archive/TASK_1_SUMMARY.md"),
                    relative_path="docs/archive/TASK_1_SUMMARY.md",
                    size=2000,
                    modified_time=datetime.now(),
                    content_preview="Task 1 summary"
                )
            ],
            DocumentCategory.DEVELOPMENT: []
        }
        
        # 创建索引生成器
        config = IndexGenerationConfig(
            include_file_size=True,
            include_modified_date=True,
            include_description=True,
            max_description_length=100
        )
        generator = IndexGenerator(config)
        
        # 生成索引内容
        index_content = generator.generate_main_index(documents, temp_dir)
        
        # 创建 docs 目录
        docs_dir = os.path.join(temp_dir, "docs")
        os.makedirs(docs_dir, exist_ok=True)
        
        # 写入索引文件
        index_path = os.path.join(docs_dir, "README.md")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        # 验证文件创建成功
        assert os.path.exists(index_path)
        
        # 验证文件内容
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "# 文档索引" in content
        assert "[README.md]" in content
        assert "[SETUP.md]" in content
        assert "共 1 个归档文档" in content
        
        print(f"\n生成的索引文件位置: {index_path}")
        print("\n索引内容预览:")
        print("=" * 60)
        print(content)
        print("=" * 60)


if __name__ == "__main__":
    test_generate_and_write_main_index()


def test_generate_and_write_archive_index():
    """测试生成并写入归档索引文件"""
    from organize_docs.models import ArchiveGrouping
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 准备归档文档数据
        archive_docs = [
            Document(
                file_name="DEVICE_ROW_RECOGNITION_SUMMARY.md",
                file_path=os.path.join(temp_dir, "docs/archive/device-row-recognition/DEVICE_ROW_RECOGNITION_SUMMARY.md"),
                relative_path="docs/archive/device-row-recognition/DEVICE_ROW_RECOGNITION_SUMMARY.md",
                size=2048,
                modified_time=datetime(2024, 1, 15),
                content_preview="Device row recognition feature implementation summary"
            ),
            Document(
                file_name="TASK_9_FINAL_CHECKPOINT.md",
                file_path=os.path.join(temp_dir, "docs/archive/device-row-recognition/TASK_9_FINAL_CHECKPOINT.md"),
                relative_path="docs/archive/device-row-recognition/TASK_9_FINAL_CHECKPOINT.md",
                size=1536,
                modified_time=datetime(2024, 1, 20),
                content_preview="Task 9 final checkpoint report"
            ),
            Document(
                file_name="UI_OPTIMIZATION_SUMMARY.md",
                file_path=os.path.join(temp_dir, "docs/archive/ui-optimization/UI_OPTIMIZATION_SUMMARY.md"),
                relative_path="docs/archive/ui-optimization/UI_OPTIMIZATION_SUMMARY.md",
                size=3072,
                modified_time=datetime(2024, 2, 10),
                content_preview="UI optimization and tooltip improvements"
            ),
            Document(
                file_name="TEST_REPORT_FINAL.md",
                file_path=os.path.join(temp_dir, "docs/archive/testing/TEST_REPORT_FINAL.md"),
                relative_path="docs/archive/testing/TEST_REPORT_FINAL.md",
                size=2560,
                modified_time=datetime(2024, 3, 5),
                content_preview="Final integration test report"
            )
        ]
        
        # 创建归档分组配置
        archive_grouping = ArchiveGrouping(groups={
            "device-row-recognition": ["DEVICE_ROW_RECOGNITION", "TASK_9"],
            "ui-optimization": ["UI_OPTIMIZATION", "UI_TOOLTIP"],
            "testing": ["TEST_REPORT", "INTEGRATION_TEST"]
        })
        
        # 创建索引生成器
        config = IndexGenerationConfig(
            include_file_size=True,
            include_modified_date=True,
            include_description=True,
            max_description_length=100
        )
        generator = IndexGenerator(config, archive_grouping)
        
        # 生成归档索引内容
        archive_index_content = generator.generate_archive_index(archive_docs, temp_dir)
        
        # 创建 docs/archive 目录
        archive_dir = os.path.join(temp_dir, "docs", "archive")
        os.makedirs(archive_dir, exist_ok=True)
        
        # 写入归档索引文件
        archive_index_path = os.path.join(archive_dir, "README.md")
        with open(archive_index_path, 'w', encoding='utf-8') as f:
            f.write(archive_index_content)
        
        # 验证文件创建成功
        assert os.path.exists(archive_index_path)
        
        # 验证文件内容
        with open(archive_index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "# 归档文档索引" in content
        assert "**文档总数**: 4" in content
        assert "**功能模块数**: 3" in content
        assert "## Device Row Recognition" in content
        assert "## UI Optimization" in content
        assert "## Testing" in content
        assert "[DEVICE_ROW_RECOGNITION_SUMMARY.md]" in content
        assert "[TASK_9_FINAL_CHECKPOINT.md]" in content
        assert "[UI_OPTIMIZATION_SUMMARY.md]" in content
        assert "[TEST_REPORT_FINAL.md]" in content
        assert "*(归档于:" in content
        assert "KB`" in content
        
        print(f"\n生成的归档索引文件位置: {archive_index_path}")
        print("\n归档索引内容预览:")
        print("=" * 60)
        print(content)
        print("=" * 60)


if __name__ == "__main__":
    test_generate_and_write_main_index()
    print("\n" + "=" * 80 + "\n")
    test_generate_and_write_archive_index()
