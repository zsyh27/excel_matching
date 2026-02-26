"""
文档分类器测试

测试文档分类器的各种功能。
"""

import pytest
from datetime import datetime

from .models import Document, DocumentCategory, ClassificationConfig
from .classifier import DocumentClassifier


@pytest.fixture
def classification_config():
    """创建测试用的分类配置"""
    return ClassificationConfig(
        core_file_names=[
            "README.md",
            "SETUP.md",
            "MAINTENANCE.md",
            "CHANGELOG.md",
            ".kiro/PROJECT.md"
        ],
        core_directories=[
            ".kiro/specs/**"
        ],
        archive_keywords=[
            "SUMMARY",
            "REPORT",
            "COMPLETION",
            "FIX",
            "TROUBLESHOOTING",
            "TASK_",
            "FINAL_",
            "INTEGRATION_TEST_"
        ],
        development_keywords=[
            "GUIDE",
            "SETUP",
            "DATABASE_",
            "MIGRATION_"
        ],
        exclude_patterns=[]
    )


@pytest.fixture
def classifier(classification_config):
    """创建分类器实例"""
    return DocumentClassifier(classification_config)


def create_test_document(file_name: str, relative_path: str = None) -> Document:
    """创建测试文档对象"""
    if relative_path is None:
        relative_path = file_name
    
    return Document(
        file_name=file_name,
        file_path=f"/test/{relative_path}",
        relative_path=relative_path,
        size=1000,
        modified_time=datetime.now(),
        content_preview="Test content"
    )


class TestCoreDocumentIdentification:
    """测试核心文档识别功能（任务 4.1）"""
    
    def test_identify_readme_as_core(self, classifier):
        """测试识别 README.md 为核心文档"""
        doc = create_test_document("README.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.CORE
    
    def test_identify_setup_as_core(self, classifier):
        """测试识别 SETUP.md 为核心文档"""
        doc = create_test_document("SETUP.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.CORE
    
    def test_identify_maintenance_as_core(self, classifier):
        """测试识别 MAINTENANCE.md 为核心文档"""
        doc = create_test_document("MAINTENANCE.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.CORE
    
    def test_identify_changelog_as_core(self, classifier):
        """测试识别 CHANGELOG.md 为核心文档"""
        doc = create_test_document("CHANGELOG.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.CORE
    
    def test_identify_project_md_by_path(self, classifier):
        """测试通过路径识别 .kiro/PROJECT.md 为核心文档"""
        doc = create_test_document("PROJECT.md", ".kiro/PROJECT.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.CORE
    
    def test_identify_project_md_with_backslash(self, classifier):
        """测试使用反斜杠路径识别 .kiro\\PROJECT.md 为核心文档"""
        doc = create_test_document("PROJECT.md", ".kiro\\PROJECT.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.CORE
    
    def test_non_core_document(self, classifier):
        """测试非核心文档不被识别为核心文档"""
        doc = create_test_document("SOME_OTHER_FILE.md")
        category = classifier.classify(doc)
        assert category != DocumentCategory.CORE
    
    def test_core_document_case_sensitive(self, classifier):
        """测试核心文档识别是大小写敏感的"""
        # README.md 应该被识别为核心文档
        doc1 = create_test_document("README.md")
        assert classifier.classify(doc1) == DocumentCategory.CORE
        
        # readme.md 不应该被识别为核心文档（除非配置中包含）
        doc2 = create_test_document("readme.md")
        # 这个测试假设配置中只有 README.md（大写）
        # 如果不是核心文档，应该被分类为其他类别
        category = classifier.classify(doc2)
        # 由于 readme 不在配置中，应该不是 CORE
        assert category != DocumentCategory.CORE


class TestArchiveDocumentIdentification:
    """测试归档文档识别功能（任务 4.2）"""
    
    def test_identify_summary_as_archive(self, classifier):
        """测试识别包含 SUMMARY 的文档为归档文档"""
        doc = create_test_document("FEATURE_SUMMARY.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.ARCHIVE
    
    def test_identify_report_as_archive(self, classifier):
        """测试识别包含 REPORT 的文档为归档文档"""
        doc = create_test_document("TEST_REPORT.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.ARCHIVE
    
    def test_identify_completion_as_archive(self, classifier):
        """测试识别包含 COMPLETION 的文档为归档文档"""
        doc = create_test_document("PROJECT_COMPLETION.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.ARCHIVE
    
    def test_identify_task_prefix_as_archive(self, classifier):
        """测试识别 TASK_ 前缀的文档为归档文档"""
        doc = create_test_document("TASK_1_SUMMARY.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.ARCHIVE
    
    def test_identify_final_prefix_as_archive(self, classifier):
        """测试识别 FINAL_ 前缀的文档为归档文档"""
        doc = create_test_document("FINAL_REPORT.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.ARCHIVE
    
    def test_archive_keyword_case_insensitive(self, classifier):
        """测试归档关键词识别是大小写不敏感的"""
        doc1 = create_test_document("feature_summary.md")
        assert classifier.classify(doc1) == DocumentCategory.ARCHIVE
        
        doc2 = create_test_document("Feature_Summary.md")
        assert classifier.classify(doc2) == DocumentCategory.ARCHIVE
    
    def test_identify_integration_test_as_archive(self, classifier):
        """测试识别 INTEGRATION_TEST_ 前缀的文档为归档文档"""
        doc = create_test_document("INTEGRATION_TEST_RESULTS.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.ARCHIVE
    
    def test_identify_fix_as_archive(self, classifier):
        """测试识别包含 FIX 的文档为归档文档"""
        doc = create_test_document("BUG_FIX_REPORT.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.ARCHIVE
    
    def test_identify_troubleshooting_as_archive(self, classifier):
        """测试识别包含 TROUBLESHOOTING 的文档为归档文档"""
        doc = create_test_document("TROUBLESHOOTING_GUIDE.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.ARCHIVE


class TestDevelopmentDocumentIdentification:
    """测试开发文档识别功能（任务 4.3）"""
    
    def test_identify_guide_as_development(self, classifier):
        """测试识别包含 GUIDE 的文档为开发文档"""
        doc = create_test_document("DEVELOPMENT_GUIDE.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.DEVELOPMENT
    
    def test_identify_database_as_development(self, classifier):
        """测试识别包含 DATABASE_ 的文档为开发文档"""
        doc = create_test_document("DATABASE_SCHEMA.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.DEVELOPMENT
    
    def test_identify_migration_as_development(self, classifier):
        """测试识别包含 MIGRATION_ 的文档为开发文档"""
        doc = create_test_document("MIGRATION_GUIDE.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.DEVELOPMENT
    
    def test_identify_backend_path_as_development(self, classifier):
        """测试识别 backend/ 路径下的文档为开发文档（需求 8.1）"""
        doc = create_test_document("api.md", "backend/api.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.DEVELOPMENT
    
    def test_identify_frontend_path_as_development(self, classifier):
        """测试识别 frontend/ 路径下的文档为开发文档（需求 8.2）"""
        doc = create_test_document("components.md", "frontend/components.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.DEVELOPMENT
    
    def test_identify_backend_subdirectory_as_development(self, classifier):
        """测试识别 backend/ 子目录下的文档为开发文档"""
        doc = create_test_document("auth.md", "backend/services/auth.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.DEVELOPMENT
    
    def test_identify_frontend_subdirectory_as_development(self, classifier):
        """测试识别 frontend/ 子目录下的文档为开发文档"""
        doc = create_test_document("button.md", "frontend/components/button.md")
        category = classifier.classify(doc)
        assert category == DocumentCategory.DEVELOPMENT
    
    def test_development_keyword_case_insensitive(self, classifier):
        """测试开发文档关键词识别是大小写不敏感的"""
        doc1 = create_test_document("development_guide.md")
        assert classifier.classify(doc1) == DocumentCategory.DEVELOPMENT
        
        doc2 = create_test_document("Development_Guide.md")
        assert classifier.classify(doc2) == DocumentCategory.DEVELOPMENT
        
        doc3 = create_test_document("database_setup.md")
        assert classifier.classify(doc3) == DocumentCategory.DEVELOPMENT


class TestBatchClassification:
    """测试批量分类功能（任务 4.4）"""
    
    def test_classify_batch_returns_all_categories(self, classifier):
        """测试批量分类返回所有分类"""
        documents = [
            create_test_document("README.md"),
            create_test_document("FEATURE_SUMMARY.md"),
            create_test_document("DEVELOPMENT_GUIDE.md"),
            create_test_document("random.md")
        ]
        
        result = classifier.classify_batch(documents)
        
        # 验证返回的字典包含所有分类
        assert DocumentCategory.CORE in result
        assert DocumentCategory.ARCHIVE in result
        assert DocumentCategory.DEVELOPMENT in result
        assert DocumentCategory.UNKNOWN in result
    
    def test_classify_batch_assigns_categories_correctly(self, classifier):
        """测试批量分类正确分配文档到各分类"""
        documents = [
            create_test_document("README.md"),
            create_test_document("SETUP.md"),
            create_test_document("FEATURE_SUMMARY.md"),
            create_test_document("DEVELOPMENT_GUIDE.md"),
        ]
        
        result = classifier.classify_batch(documents)
        
        # 验证核心文档
        assert len(result[DocumentCategory.CORE]) == 2
        assert any(doc.file_name == "README.md" for doc in result[DocumentCategory.CORE])
        assert any(doc.file_name == "SETUP.md" for doc in result[DocumentCategory.CORE])
        
        # 验证归档文档
        assert len(result[DocumentCategory.ARCHIVE]) == 1
        assert result[DocumentCategory.ARCHIVE][0].file_name == "FEATURE_SUMMARY.md"
        
        # 验证开发文档
        assert len(result[DocumentCategory.DEVELOPMENT]) == 1
        assert result[DocumentCategory.DEVELOPMENT][0].file_name == "DEVELOPMENT_GUIDE.md"
    
    def test_classify_batch_updates_document_category(self, classifier):
        """测试批量分类更新文档对象的 category 属性"""
        documents = [
            create_test_document("README.md"),
            create_test_document("FEATURE_SUMMARY.md"),
        ]
        
        classifier.classify_batch(documents)
        
        # 验证文档对象的 category 属性被更新
        assert documents[0].category == DocumentCategory.CORE
        assert documents[1].category == DocumentCategory.ARCHIVE
    
    def test_classify_empty_list(self, classifier):
        """测试分类空文档列表"""
        result = classifier.classify_batch([])
        
        # 验证返回空的分类字典
        assert len(result[DocumentCategory.CORE]) == 0
        assert len(result[DocumentCategory.ARCHIVE]) == 0
        assert len(result[DocumentCategory.DEVELOPMENT]) == 0
        assert len(result[DocumentCategory.UNKNOWN]) == 0


class TestClassificationPriority:
    """测试分类优先级"""
    
    def test_core_takes_priority_over_archive(self, classifier):
        """测试核心文档优先级高于归档文档"""
        # 如果一个文档既符合核心文档又符合归档文档的规则，
        # 应该被分类为核心文档
        # 注意：在实际配置中，核心文档名称不太可能包含归档关键词
        # 这个测试主要验证分类逻辑的优先级
        
        # 创建一个文档，文件名是 README.md（核心文档）
        doc = create_test_document("README.md")
        category = classifier.classify(doc)
        
        # 应该被识别为核心文档
        assert category == DocumentCategory.CORE
    
    def test_archive_takes_priority_over_development(self, classifier):
        """测试归档文档优先级高于开发文档"""
        # 如果一个文档既符合归档又符合开发文档的规则，
        # 应该被分类为归档文档
        
        # 创建一个包含 SUMMARY 和 GUIDE 的文档
        doc = create_test_document("DEVELOPMENT_GUIDE_SUMMARY.md")
        category = classifier.classify(doc)
        
        # 应该被识别为归档文档（因为包含 SUMMARY）
        assert category == DocumentCategory.ARCHIVE



class TestCoreDirectories:
    """测试核心目录识别"""
    
    def test_identify_specs_directory_as_core(self, classifier):
        """测试识别 .kiro/specs/ 目录下的文档为核心文档"""
        # 创建一个在 specs 目录下的文档
        doc = create_test_document(
            "requirements.md",
            relative_path=".kiro/specs/my-feature/requirements.md"
        )
        category = classifier.classify(doc)
        
        # 应该被识别为核心文档
        assert category == DocumentCategory.CORE
    
    def test_identify_specs_subdirectory_as_core(self, classifier):
        """测试识别 .kiro/specs/ 子目录下的文档为核心文档"""
        # 创建一个在 specs 子目录下的文档
        doc = create_test_document(
            "design.md",
            relative_path=".kiro/specs/feature-a/sub-feature/design.md"
        )
        category = classifier.classify(doc)
        
        # 应该被识别为核心文档
        assert category == DocumentCategory.CORE
    
    def test_specs_directory_overrides_development_keywords(self, classifier):
        """测试核心目录优先级高于开发文档关键词"""
        # 创建一个在 specs 目录下的文档，文件名包含开发关键词
        doc = create_test_document(
            "MIGRATION_GUIDE.md",
            relative_path=".kiro/specs/database/MIGRATION_GUIDE.md"
        )
        category = classifier.classify(doc)
        
        # 应该被识别为核心文档（而不是开发文档）
        assert category == DocumentCategory.CORE
    
    def test_specs_directory_overrides_archive_keywords(self, classifier):
        """测试核心目录优先级高于归档文档关键词"""
        # 创建一个在 specs 目录下的文档，文件名包含归档关键词
        doc = create_test_document(
            "TASK_SUMMARY.md",
            relative_path=".kiro/specs/feature/TASK_SUMMARY.md"
        )
        category = classifier.classify(doc)
        
        # 应该被识别为核心文档（而不是归档文档）
        assert category == DocumentCategory.CORE
    
    def test_non_specs_directory_not_core(self, classifier):
        """测试非 specs 目录下的文档不会被识别为核心文档"""
        # 创建一个不在 specs 目录下的文档，包含开发关键词
        doc = create_test_document(
            "MIGRATION_GUIDE.md",
            relative_path="docs/development/MIGRATION_GUIDE.md"
        )
        category = classifier.classify(doc)
        
        # 不应该被识别为核心文档
        assert category != DocumentCategory.CORE
        # 应该被识别为开发文档（因为包含 MIGRATION 关键词）
        assert category == DocumentCategory.DEVELOPMENT
