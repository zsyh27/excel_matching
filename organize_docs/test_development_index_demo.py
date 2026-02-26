"""
开发文档索引生成演示

演示如何使用 IndexGenerator 生成开发文档索引。
"""

from datetime import datetime
from organize_docs.index_generator import IndexGenerator
from organize_docs.models import Document, IndexGenerationConfig


def demo_generate_development_indexes():
    """演示生成各类开发文档索引"""
    
    # 配置
    config = IndexGenerationConfig(
        include_file_size=True,
        include_modified_date=True,
        include_description=True,
        max_description_length=100
    )
    
    generator = IndexGenerator(config)
    
    # 示例：通用开发文档
    print("=" * 60)
    print("通用开发文档索引示例")
    print("=" * 60)
    
    general_dev_docs = [
        Document(
            file_name="CODING_STANDARDS.md",
            file_path="/project/docs/development/CODING_STANDARDS.md",
            relative_path="docs/development/CODING_STANDARDS.md",
            size=2048,
            modified_time=datetime(2024, 1, 15),
            content_preview="项目编码规范和最佳实践指南"
        ),
        Document(
            file_name="TESTING_GUIDE.md",
            file_path="/project/docs/development/TESTING_GUIDE.md",
            relative_path="docs/development/TESTING_GUIDE.md",
            size=3072,
            modified_time=datetime(2024, 2, 10),
            content_preview="测试策略和测试编写指南"
        )
    ]
    
    index = generator.generate_development_index(general_dev_docs, "docs/development")
    print(index)
    print()
    
    # 示例：后端开发文档
    print("=" * 60)
    print("后端开发文档索引示例")
    print("=" * 60)
    
    backend_docs = [
        Document(
            file_name="API_DESIGN.md",
            file_path="/project/backend/docs/API_DESIGN.md",
            relative_path="backend/docs/API_DESIGN.md",
            size=4096,
            modified_time=datetime(2024, 3, 1),
            content_preview="后端 API 设计文档和接口规范"
        ),
        Document(
            file_name="DATABASE_SCHEMA.md",
            file_path="/project/backend/docs/DATABASE_SCHEMA.md",
            relative_path="backend/docs/DATABASE_SCHEMA.md",
            size=5120,
            modified_time=datetime(2024, 3, 5),
            content_preview="数据库表结构设计和关系说明"
        )
    ]
    
    index = generator.generate_development_index(backend_docs, "backend/docs")
    print(index)
    print()
    
    # 示例：前端开发文档
    print("=" * 60)
    print("前端开发文档索引示例")
    print("=" * 60)
    
    frontend_docs = [
        Document(
            file_name="COMPONENT_LIBRARY.md",
            file_path="/project/frontend/docs/COMPONENT_LIBRARY.md",
            relative_path="frontend/docs/COMPONENT_LIBRARY.md",
            size=3584,
            modified_time=datetime(2024, 3, 10),
            content_preview="前端组件库使用指南和组件文档"
        ),
        Document(
            file_name="STATE_MANAGEMENT.md",
            file_path="/project/frontend/docs/STATE_MANAGEMENT.md",
            relative_path="frontend/docs/STATE_MANAGEMENT.md",
            size=2560,
            modified_time=datetime(2024, 3, 15),
            content_preview="前端状态管理架构和最佳实践"
        )
    ]
    
    index = generator.generate_development_index(frontend_docs, "frontend/docs")
    print(index)


if __name__ == "__main__":
    demo_generate_development_indexes()
