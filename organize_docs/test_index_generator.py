"""
索引生成器测试
"""

import pytest
from datetime import datetime
from organize_docs.index_generator import IndexGenerator
from organize_docs.models import Document, DocumentCategory, IndexGenerationConfig


@pytest.fixture
def index_config():
    """索引生成配置"""
    return IndexGenerationConfig(
        include_file_size=True,
        include_modified_date=True,
        include_description=True,
        max_description_length=100
    )


@pytest.fixture
def sample_documents():
    """示例文档集合"""
    return {
        DocumentCategory.CORE: [
            Document(
                file_name="README.md",
                file_path="/project/README.md",
                relative_path="README.md",
                size=1000,
                modified_time=datetime(2024, 1, 1),
                content_preview="This is the main README"
            ),
            Document(
                file_name="SETUP.md",
                file_path="/project/SETUP.md",
                relative_path="SETUP.md",
                size=500,
                modified_time=datetime(2024, 1, 2),
                content_preview="Setup instructions"
            )
        ],
        DocumentCategory.ARCHIVE: [
            Document(
                file_name="TASK_1_SUMMARY.md",
                file_path="/project/docs/archive/TASK_1_SUMMARY.md",
                relative_path="docs/archive/TASK_1_SUMMARY.md",
                size=2000,
                modified_time=datetime(2024, 1, 3),
                content_preview="Task 1 completion summary"
            )
        ],
        DocumentCategory.DEVELOPMENT: [
            Document(
                file_name="DEV_GUIDE.md",
                file_path="/project/docs/development/DEV_GUIDE.md",
                relative_path="docs/development/DEV_GUIDE.md",
                size=1500,
                modified_time=datetime(2024, 1, 4),
                content_preview="Development guide"
            )
        ]
    }


def test_generate_main_index_structure(index_config, sample_documents):
    """测试主索引生成的基本结构"""
    generator = IndexGenerator(index_config)
    index_content = generator.generate_main_index(sample_documents)
    
    # 验证包含标题
    assert "# 文档索引" in index_content
    
    # 验证包含所有分类
    assert "## 核心文档" in index_content
    assert "## 归档文档" in index_content
    assert "## 开发文档" in index_content
    
    # 验证包含页脚
    assert "**最后更新**" in index_content
    assert "**维护者**" in index_content


def test_generate_main_index_core_documents(index_config, sample_documents):
    """测试核心文档列表生成"""
    generator = IndexGenerator(index_config)
    index_content = generator.generate_main_index(sample_documents)
    
    # 验证核心文档链接
    assert "[README.md]" in index_content
    assert "[SETUP.md]" in index_content
    
    # 验证描述
    assert "项目概述和快速开始" in index_content
    assert "安装和配置指南" in index_content


def test_generate_main_index_archive_summary(index_config, sample_documents):
    """测试归档文档摘要"""
    generator = IndexGenerator(index_config)
    index_content = generator.generate_main_index(sample_documents)
    
    # 验证归档文档数量
    assert "共 1 个归档文档" in index_content
    
    # 验证归档索引链接
    assert "[归档文档索引](archive/README.md)" in index_content


def test_generate_main_index_development_summary(index_config, sample_documents):
    """测试开发文档摘要"""
    generator = IndexGenerator(index_config)
    index_content = generator.generate_main_index(sample_documents)
    
    # 验证开发文档数量
    assert "共 1 个开发文档" in index_content
    
    # 验证开发文档索引链接
    assert "[开发文档索引](development/README.md)" in index_content


def test_generate_main_index_empty_categories(index_config):
    """测试空分类的处理"""
    generator = IndexGenerator(index_config)
    empty_docs = {
        DocumentCategory.CORE: [],
        DocumentCategory.ARCHIVE: [],
        DocumentCategory.DEVELOPMENT: []
    }
    index_content = generator.generate_main_index(empty_docs)
    
    # 验证空分类提示
    assert "暂无核心文档" in index_content
    assert "暂无归档文档" in index_content
    assert "暂无开发文档" in index_content


def test_generate_relative_link_for_core_docs(index_config):
    """测试核心文档的相对链接生成"""
    generator = IndexGenerator(index_config)
    doc = Document(
        file_name="README.md",
        file_path="/project/README.md",
        relative_path="README.md",
        size=1000,
        modified_time=datetime.now(),
        content_preview="Test"
    )
    
    link = generator._generate_relative_link(doc, "/project", "docs")
    
    # 从 docs/ 链接到根目录的文件应该使用 ../
    assert link == "../README.md"


def test_get_document_description_predefined(index_config):
    """测试预定义文档描述"""
    generator = IndexGenerator(index_config)
    doc = Document(
        file_name="README.md",
        file_path="/project/README.md",
        relative_path="README.md",
        size=1000,
        modified_time=datetime.now(),
        content_preview="Some content"
    )
    
    description = generator._get_document_description(doc)
    assert description == "项目概述和快速开始"


def test_get_document_description_from_preview(index_config):
    """测试从内容预览生成描述"""
    generator = IndexGenerator(index_config)
    doc = Document(
        file_name="CUSTOM.md",
        file_path="/project/CUSTOM.md",
        relative_path="CUSTOM.md",
        size=1000,
        modified_time=datetime.now(),
        content_preview="This is a custom document with some content"
    )
    
    description = generator._get_document_description(doc)
    assert description == "This is a custom document with some content"


def test_get_document_description_truncation(index_config):
    """测试描述截断"""
    generator = IndexGenerator(index_config)
    long_content = "A" * 150  # 超过最大长度
    doc = Document(
        file_name="LONG.md",
        file_path="/project/LONG.md",
        relative_path="LONG.md",
        size=1000,
        modified_time=datetime.now(),
        content_preview=long_content
    )
    
    description = generator._get_document_description(doc)
    assert len(description) <= index_config.max_description_length + 3  # +3 for "..."
    assert description.endswith("...")


def test_generate_archive_index_basic_structure(index_config):
    """测试归档索引的基本结构"""
    from organize_docs.models import ArchiveGrouping
    
    archive_grouping = ArchiveGrouping(groups={
        "device-row-recognition": ["DEVICE_ROW_RECOGNITION", "TASK_9"],
        "ui-optimization": ["UI_OPTIMIZATION"]
    })
    
    generator = IndexGenerator(index_config, archive_grouping)
    
    archive_docs = [
        Document(
            file_name="DEVICE_ROW_RECOGNITION_SUMMARY.md",
            file_path="/project/docs/archive/device-row-recognition/DEVICE_ROW_RECOGNITION_SUMMARY.md",
            relative_path="docs/archive/device-row-recognition/DEVICE_ROW_RECOGNITION_SUMMARY.md",
            size=2048,
            modified_time=datetime(2024, 1, 15),
            content_preview="Device row recognition feature summary"
        ),
        Document(
            file_name="UI_OPTIMIZATION_REPORT.md",
            file_path="/project/docs/archive/ui-optimization/UI_OPTIMIZATION_REPORT.md",
            relative_path="docs/archive/ui-optimization/UI_OPTIMIZATION_REPORT.md",
            size=1536,
            modified_time=datetime(2024, 2, 10),
            content_preview="UI optimization completion report"
        )
    ]
    
    index_content = generator.generate_archive_index(archive_docs)
    
    # 验证标题
    assert "# 归档文档索引" in index_content
    
    # 验证统计信息
    assert "**文档总数**: 2" in index_content
    assert "**功能模块数**: 2" in index_content
    
    # 验证分组标题
    assert "## Device Row Recognition" in index_content
    assert "## UI Optimization" in index_content
    
    # 验证页脚
    assert "**最后更新**" in index_content
    assert "**维护者**" in index_content


def test_generate_archive_index_with_metadata(index_config):
    """测试归档索引包含元数据"""
    from organize_docs.models import ArchiveGrouping
    
    archive_grouping = ArchiveGrouping(groups={
        "testing": ["TEST_REPORT"]
    })
    
    generator = IndexGenerator(index_config, archive_grouping)
    
    archive_docs = [
        Document(
            file_name="TEST_REPORT_FINAL.md",
            file_path="/project/docs/archive/testing/TEST_REPORT_FINAL.md",
            relative_path="docs/archive/testing/TEST_REPORT_FINAL.md",
            size=3072,
            modified_time=datetime(2024, 3, 20),
            content_preview="Final test report for the project"
        )
    ]
    
    index_content = generator.generate_archive_index(archive_docs)
    
    # 验证归档日期标记
    assert "*(归档于: 2024-03-20)*" in index_content
    
    # 验证文件大小
    assert "3.0 KB" in index_content
    
    # 验证描述
    assert "Final test report for the project" in index_content


def test_generate_archive_index_empty_list(index_config):
    """测试空归档文档列表"""
    generator = IndexGenerator(index_config)
    
    index_content = generator.generate_archive_index([])
    
    # 验证包含标题
    assert "# 归档文档索引" in index_content
    
    # 验证空列表提示
    assert "暂无归档文档" in index_content


def test_generate_archive_index_grouping(index_config):
    """测试归档文档按功能模块分组"""
    from organize_docs.models import ArchiveGrouping
    
    archive_grouping = ArchiveGrouping(groups={
        "tasks": ["TASK_7", "TASK_12"]
    })
    
    generator = IndexGenerator(index_config, archive_grouping)
    
    archive_docs = [
        Document(
            file_name="TASK_7_SUMMARY.md",
            file_path="/project/docs/archive/tasks/TASK_7_SUMMARY.md",
            relative_path="docs/archive/tasks/TASK_7_SUMMARY.md",
            size=1024,
            modified_time=datetime(2024, 1, 10),
            content_preview="Task 7 completion"
        ),
        Document(
            file_name="TASK_12_REPORT.md",
            file_path="/project/docs/archive/tasks/TASK_12_REPORT.md",
            relative_path="docs/archive/tasks/TASK_12_REPORT.md",
            size=2048,
            modified_time=datetime(2024, 1, 20),
            content_preview="Task 12 report"
        )
    ]
    
    index_content = generator.generate_archive_index(archive_docs)
    
    # 验证分组
    assert "## Tasks" in index_content
    
    # 验证两个文档都在同一分组下
    assert "[TASK_7_SUMMARY.md]" in index_content
    assert "[TASK_12_REPORT.md]" in index_content


def test_generate_archive_index_default_group(index_config):
    """测试未匹配分组的文档归入默认分组"""
    from organize_docs.models import ArchiveGrouping
    
    archive_grouping = ArchiveGrouping(groups={
        "testing": ["TEST_REPORT"]
    })
    
    generator = IndexGenerator(index_config, archive_grouping)
    
    archive_docs = [
        Document(
            file_name="RANDOM_DOCUMENT.md",
            file_path="/project/docs/archive/RANDOM_DOCUMENT.md",
            relative_path="docs/archive/RANDOM_DOCUMENT.md",
            size=512,
            modified_time=datetime(2024, 1, 5),
            content_preview="Some random document"
        )
    ]
    
    index_content = generator.generate_archive_index(archive_docs)
    
    # 验证默认分组
    assert "## 其他" in index_content
    assert "[RANDOM_DOCUMENT.md]" in index_content


def test_determine_group(index_config):
    """测试文档分组判断"""
    from organize_docs.models import ArchiveGrouping
    
    archive_grouping = ArchiveGrouping(groups={
        "device-library": ["DEVICE_LIBRARY_EXPANSION"],
        "troubleshooting": ["TROUBLESHOOTING", "MANUAL_ADJUST"]
    })
    
    generator = IndexGenerator(index_config, archive_grouping)
    
    # 测试匹配第一个分组
    doc1 = Document(
        file_name="DEVICE_LIBRARY_EXPANSION_REPORT.md",
        file_path="/project/docs/archive/DEVICE_LIBRARY_EXPANSION_REPORT.md",
        relative_path="docs/archive/DEVICE_LIBRARY_EXPANSION_REPORT.md",
        size=1024,
        modified_time=datetime.now(),
        content_preview="Test"
    )
    assert generator._determine_group(doc1) == "device-library"
    
    # 测试匹配第二个分组
    doc2 = Document(
        file_name="MANUAL_ADJUST_TROUBLESHOOTING.md",
        file_path="/project/docs/archive/MANUAL_ADJUST_TROUBLESHOOTING.md",
        relative_path="docs/archive/MANUAL_ADJUST_TROUBLESHOOTING.md",
        size=1024,
        modified_time=datetime.now(),
        content_preview="Test"
    )
    assert generator._determine_group(doc2) == "troubleshooting"
    
    # 测试不匹配任何分组
    doc3 = Document(
        file_name="UNKNOWN_DOC.md",
        file_path="/project/docs/archive/UNKNOWN_DOC.md",
        relative_path="docs/archive/UNKNOWN_DOC.md",
        size=1024,
        modified_time=datetime.now(),
        content_preview="Test"
    )
    assert generator._determine_group(doc3) == "其他"


def test_format_group_title(index_config):
    """测试分组标题格式化"""
    generator = IndexGenerator(index_config)
    
    # 测试基本格式化
    assert generator._format_group_title("device-row-recognition") == "Device Row Recognition"
    assert generator._format_group_title("ui-optimization") == "UI Optimization"
    assert generator._format_group_title("tasks") == "Tasks"
    
    # 测试特殊缩写
    assert generator._format_group_title("api-documentation") == "API Documentation"


def test_generate_archive_link(index_config):
    """测试归档文档链接生成"""
    generator = IndexGenerator(index_config)
    
    # 测试子目录中的文档
    doc = Document(
        file_name="TEST.md",
        file_path="/project/docs/archive/testing/TEST.md",
        relative_path="docs/archive/testing/TEST.md",
        size=1024,
        modified_time=datetime.now(),
        content_preview="Test"
    )
    
    link = generator._generate_archive_link(doc, "/project")
    assert link == "testing/TEST.md"
    
    # 测试直接在 archive 目录下的文档
    doc2 = Document(
        file_name="DIRECT.md",
        file_path="/project/docs/archive/DIRECT.md",
        relative_path="docs/archive/DIRECT.md",
        size=1024,
        modified_time=datetime.now(),
        content_preview="Test"
    )
    
    link2 = generator._generate_archive_link(doc2, "/project")
    assert link2 == "DIRECT.md"


def test_generate_development_index_basic_structure(index_config):
    """测试开发文档索引的基本结构"""
    generator = IndexGenerator(index_config)
    
    dev_docs = [
        Document(
            file_name="SETUP_GUIDE.md",
            file_path="/project/docs/development/SETUP_GUIDE.md",
            relative_path="docs/development/SETUP_GUIDE.md",
            size=2048,
            modified_time=datetime(2024, 1, 15),
            content_preview="Development environment setup guide"
        ),
        Document(
            file_name="CODING_STANDARDS.md",
            file_path="/project/docs/development/CODING_STANDARDS.md",
            relative_path="docs/development/CODING_STANDARDS.md",
            size=1536,
            modified_time=datetime(2024, 2, 10),
            content_preview="Coding standards and best practices"
        )
    ]
    
    index_content = generator.generate_development_index(dev_docs, "docs/development")
    
    # 验证标题
    assert "# 开发文档索引" in index_content
    
    # 验证说明
    assert "本目录包含通用开发指南和技术文档" in index_content
    
    # 验证统计信息
    assert "**文档总数**: 2" in index_content
    
    # 验证文档列表标题
    assert "## 文档列表" in index_content
    
    # 验证文档链接
    assert "[SETUP_GUIDE.md]" in index_content
    assert "[CODING_STANDARDS.md]" in index_content
    
    # 验证页脚
    assert "**最后更新**" in index_content
    assert "**维护者**" in index_content


def test_generate_development_index_backend(index_config):
    """测试后端开发文档索引"""
    generator = IndexGenerator(index_config)
    
    backend_docs = [
        Document(
            file_name="API_DESIGN.md",
            file_path="/project/backend/docs/API_DESIGN.md",
            relative_path="backend/docs/API_DESIGN.md",
            size=3072,
            modified_time=datetime(2024, 3, 1),
            content_preview="Backend API design documentation"
        )
    ]
    
    index_content = generator.generate_development_index(backend_docs, "backend/docs")
    
    # 验证标题
    assert "# 后端开发文档索引" in index_content
    
    # 验证说明
    assert "本目录包含后端技术实现细节和开发指南" in index_content
    
    # 验证文档
    assert "[API_DESIGN.md]" in index_content


def test_generate_development_index_frontend(index_config):
    """测试前端开发文档索引"""
    generator = IndexGenerator(index_config)
    
    frontend_docs = [
        Document(
            file_name="COMPONENT_GUIDE.md",
            file_path="/project/frontend/docs/COMPONENT_GUIDE.md",
            relative_path="frontend/docs/COMPONENT_GUIDE.md",
            size=2560,
            modified_time=datetime(2024, 3, 5),
            content_preview="Frontend component development guide"
        )
    ]
    
    index_content = generator.generate_development_index(frontend_docs, "frontend/docs")
    
    # 验证标题
    assert "# 前端开发文档索引" in index_content
    
    # 验证说明
    assert "本目录包含前端技术实现细节和开发指南" in index_content
    
    # 验证文档
    assert "[COMPONENT_GUIDE.md]" in index_content


def test_generate_development_index_empty_list(index_config):
    """测试空开发文档列表"""
    generator = IndexGenerator(index_config)
    
    index_content = generator.generate_development_index([], "docs/development")
    
    # 验证包含标题
    assert "# 开发文档索引" in index_content
    
    # 验证空列表提示
    assert "暂无开发文档" in index_content


def test_generate_development_index_with_metadata(index_config):
    """测试开发文档索引包含元数据"""
    generator = IndexGenerator(index_config)
    
    dev_docs = [
        Document(
            file_name="DATABASE_GUIDE.md",
            file_path="/project/docs/development/DATABASE_GUIDE.md",
            relative_path="docs/development/DATABASE_GUIDE.md",
            size=4096,
            modified_time=datetime(2024, 4, 1),
            content_preview="Database design and migration guide"
        )
    ]
    
    index_content = generator.generate_development_index(dev_docs, "docs/development")
    
    # 验证文件大小
    assert "4.0 KB" in index_content
    
    # 验证描述
    assert "Database design and migration guide" in index_content


def test_generate_development_link(index_config):
    """测试开发文档链接生成"""
    generator = IndexGenerator(index_config)
    
    # 测试 docs/development 目录下的文档
    doc1 = Document(
        file_name="GUIDE.md",
        file_path="/project/docs/development/GUIDE.md",
        relative_path="docs/development/GUIDE.md",
        size=1024,
        modified_time=datetime.now(),
        content_preview="Test"
    )
    
    link1 = generator._generate_development_link(doc1, "docs/development")
    assert link1 == "GUIDE.md"
    
    # 测试 backend/docs 目录下的文档
    doc2 = Document(
        file_name="API.md",
        file_path="/project/backend/docs/API.md",
        relative_path="backend/docs/API.md",
        size=1024,
        modified_time=datetime.now(),
        content_preview="Test"
    )
    
    link2 = generator._generate_development_link(doc2, "backend/docs")
    assert link2 == "API.md"
    
    # 测试子目录中的文档
    doc3 = Document(
        file_name="ADVANCED.md",
        file_path="/project/docs/development/advanced/ADVANCED.md",
        relative_path="docs/development/advanced/ADVANCED.md",
        size=1024,
        modified_time=datetime.now(),
        content_preview="Test"
    )
    
    link3 = generator._generate_development_link(doc3, "docs/development")
    assert link3 == "advanced/ADVANCED.md"


def test_generate_development_index_sorted_by_filename(index_config):
    """测试开发文档按文件名排序"""
    generator = IndexGenerator(index_config)
    
    dev_docs = [
        Document(
            file_name="Z_LAST.md",
            file_path="/project/docs/development/Z_LAST.md",
            relative_path="docs/development/Z_LAST.md",
            size=1024,
            modified_time=datetime.now(),
            content_preview="Last document"
        ),
        Document(
            file_name="A_FIRST.md",
            file_path="/project/docs/development/A_FIRST.md",
            relative_path="docs/development/A_FIRST.md",
            size=1024,
            modified_time=datetime.now(),
            content_preview="First document"
        ),
        Document(
            file_name="M_MIDDLE.md",
            file_path="/project/docs/development/M_MIDDLE.md",
            relative_path="docs/development/M_MIDDLE.md",
            size=1024,
            modified_time=datetime.now(),
            content_preview="Middle document"
        )
    ]
    
    index_content = generator.generate_development_index(dev_docs, "docs/development")
    
    # 验证排序：A_FIRST 应该在 M_MIDDLE 之前，M_MIDDLE 应该在 Z_LAST 之前
    a_pos = index_content.find("A_FIRST.md")
    m_pos = index_content.find("M_MIDDLE.md")
    z_pos = index_content.find("Z_LAST.md")
    
    assert a_pos < m_pos < z_pos
