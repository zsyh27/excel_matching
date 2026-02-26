# 设计文档 - 文档整理功能

## 概述

文档整理功能旨在系统化地整理项目中的 MD 文档，建立清晰的文档层次结构。系统将自动识别文档类型，按照预定义规则进行分类、归档和索引，同时保持核心文档的可访问性。

### 设计目标

1. **自动化**: 最小化手动操作，自动识别和分类文档
2. **可配置**: 通过配置文件灵活调整整理规则
3. **可逆性**: 支持备份和恢复，确保操作安全
4. **可维护性**: 生成清晰的索引和导航，便于长期维护

## 架构

### 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                   文档整理系统                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐ │
│  │ 文档扫描器    │───>│ 文档分类器    │───>│ 文档移动器│ │
│  │ Scanner      │    │ Classifier   │    │ Mover    │ │
│  └──────────────┘    └──────────────┘    └──────────┘ │
│         │                    │                   │     │
│         v                    v                   v     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐ │
│  │ 配置管理器    │    │ 索引生成器    │    │ 备份管理器│ │
│  │ Config Mgr   │    │ Index Gen    │    │ Backup   │ │
│  └──────────────┘    └──────────────┘    └──────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 数据流

```
原始文档 → 扫描 → 分类 → 备份 → 移动 → 索引生成 → 验证 → 完成
```

## 组件和接口

### 1. 文档扫描器 (DocumentScanner)

**职责**: 扫描项目目录，识别所有 MD 文档

**接口**:
```python
class DocumentScanner:
    def scan_directory(self, root_path: str, exclude_dirs: List[str]) -> List[Document]:
        """
        扫描目录，返回文档列表
        
        参数:
            root_path: 项目根目录路径
            exclude_dirs: 排除的目录列表（如 node_modules, .git）
        
        返回:
            Document 对象列表
        """
        pass
    
    def get_document_info(self, file_path: str) -> Document:
        """
        获取单个文档的信息
        
        参数:
            file_path: 文档文件路径
        
        返回:
            Document 对象，包含文件名、路径、大小、修改时间等
        """
        pass
```

### 2. 文档分类器 (DocumentClassifier)

**职责**: 根据规则将文档分类为核心文档、归档文档或开发文档

**接口**:
```python
class DocumentClassifier:
    def __init__(self, config: ClassificationConfig):
        """
        初始化分类器
        
        参数:
            config: 分类配置，包含关键词规则、文件名规则等
        """
        pass
    
    def classify(self, document: Document) -> DocumentCategory:
        """
        分类单个文档
        
        参数:
            document: 待分类的文档对象
        
        返回:
            文档分类（CORE, ARCHIVE, DEVELOPMENT）
        """
        pass
    
    def classify_batch(self, documents: List[Document]) -> Dict[DocumentCategory, List[Document]]:
        """
        批量分类文档
        
        参数:
            documents: 文档列表
        
        返回:
            按分类分组的文档字典
        """
        pass
```

**分类规则**:

1. **核心文档识别**:
   - 文件名匹配: README.md, SETUP.md, MAINTENANCE.md, CHANGELOG.md
   - 路径匹配: .kiro/PROJECT.md

2. **归档文档识别**:
   - 文件名包含关键词: SUMMARY, REPORT, COMPLETION, FIX, TROUBLESHOOTING
   - 文件名包含: TASK_*, FINAL_*, INTEGRATION_TEST_*

3. **开发文档识别**:
   - 文件名包含: GUIDE, SETUP, DATABASE_, MIGRATION_
   - 位于 backend/ 或 frontend/ 目录下的 MD 文档

### 3. 文档移动器 (DocumentMover)

**职责**: 根据分类结果移动文档到目标目录

**接口**:
```python
class DocumentMover:
    def __init__(self, target_structure: DirectoryStructure):
        """
        初始化移动器
        
        参数:
            target_structure: 目标目录结构配置
        """
        pass
    
    def move_document(self, document: Document, target_category: DocumentCategory) -> MoveResult:
        """
        移动单个文档
        
        参数:
            document: 待移动的文档
            target_category: 目标分类
        
        返回:
            移动结果，包含原路径、新路径、状态
        """
        pass
    
    def create_directory_structure(self) -> None:
        """
        创建目标目录结构
        """
        pass
```

**目录结构**:
```
项目根目录/
├── README.md                    # 核心文档（保持不动）
├── SETUP.md                     # 核心文档（保持不动）
├── MAINTENANCE.md               # 核心文档（保持不动）
├── CHANGELOG.md                 # 核心文档（保持不动）
├── docs/                        # 文档根目录（新建）
│   ├── README.md               # 文档索引（生成）
│   ├── archive/                # 归档文档目录（新建）
│   │   ├── README.md          # 归档索引（生成）
│   │   ├── device-row-recognition/  # 按功能分组
│   │   │   ├── DEVICE_ROW_RECOGNITION_FINAL_SUMMARY.md
│   │   │   ├── TASK_9_FINAL_CHECKPOINT_REPORT.md
│   │   │   └── ...
│   │   ├── device-library/
│   │   │   ├── DEVICE_LIBRARY_EXPANSION_REPORT.md
│   │   │   └── ...
│   │   ├── ui-optimization/
│   │   │   ├── UI_OPTIMIZATION_SUMMARY.md
│   │   │   └── ...
│   │   └── troubleshooting/
│   │       ├── MANUAL_ADJUST_TROUBLESHOOTING_V2.md
│   │       └── ...
│   └── development/            # 开发文档目录（新建）
│       └── README.md          # 开发文档索引（生成）
├── backend/
│   └── docs/                   # 后端开发文档（新建）
│       └── README.md          # 后端文档索引（生成）
└── frontend/
    └── docs/                   # 前端开发文档（新建）
        └── README.md          # 前端文档索引（生成）
```

### 4. 索引生成器 (IndexGenerator)

**职责**: 生成文档索引和导航链接

**接口**:
```python
class IndexGenerator:
    def generate_main_index(self, documents: Dict[DocumentCategory, List[Document]]) -> str:
        """
        生成主文档索引
        
        参数:
            documents: 按分类分组的文档字典
        
        返回:
            索引 Markdown 内容
        """
        pass
    
    def generate_archive_index(self, archive_docs: List[Document]) -> str:
        """
        生成归档文档索引
        
        参数:
            archive_docs: 归档文档列表
        
        返回:
            归档索引 Markdown 内容
        """
        pass
    
    def update_readme_navigation(self, readme_path: str, doc_index_path: str) -> None:
        """
        更新 README.md 中的文档导航链接
        
        参数:
            readme_path: README.md 文件路径
            doc_index_path: 文档索引路径
        """
        pass
```

**索引格式**:
```markdown
# 文档索引

## 核心文档

- [README.md](../README.md) - 项目概述和快速开始
- [SETUP.md](../SETUP.md) - 安装和配置指南
- [MAINTENANCE.md](../MAINTENANCE.md) - 维护和故障排查指南
- [CHANGELOG.md](../CHANGELOG.md) - 版本变更历史

## 归档文档

详见 [归档文档索引](archive/README.md)

## 开发文档

详见 [开发文档索引](development/README.md)

---

**最后更新**: 2026-02-12  
**维护者**: 开发团队
```

### 5. 备份管理器 (BackupManager)

**职责**: 创建备份和支持恢复操作

**接口**:
```python
class BackupManager:
    def create_backup(self, documents: List[Document]) -> BackupInfo:
        """
        创建文档备份
        
        参数:
            documents: 待备份的文档列表
        
        返回:
            备份信息，包含备份路径、时间戳、文档清单
        """
        pass
    
    def restore_from_backup(self, backup_info: BackupInfo) -> RestoreResult:
        """
        从备份恢复
        
        参数:
            backup_info: 备份信息
        
        返回:
            恢复结果，包含成功/失败的文档列表
        """
        pass
    
    def list_backups(self) -> List[BackupInfo]:
        """
        列出所有可用备份
        
        返回:
            备份信息列表
        """
        pass
```

### 6. 配置管理器 (ConfigManager)

**职责**: 加载和验证配置文件

**接口**:
```python
class ConfigManager:
    def load_config(self, config_path: str) -> OrganizationConfig:
        """
        加载配置文件
        
        参数:
            config_path: 配置文件路径
        
        返回:
            配置对象
        """
        pass
    
    def validate_config(self, config: OrganizationConfig) -> ValidationResult:
        """
        验证配置有效性
        
        参数:
            config: 配置对象
        
        返回:
            验证结果
        """
        pass
    
    def get_default_config(self) -> OrganizationConfig:
        """
        获取默认配置
        
        返回:
            默认配置对象
        """
        pass
```

## 数据模型

### Document

```python
@dataclass
class Document:
    """文档数据模型"""
    file_name: str          # 文件名
    file_path: str          # 完整路径
    relative_path: str      # 相对于项目根目录的路径
    size: int               # 文件大小（字节）
    modified_time: datetime # 最后修改时间
    content_preview: str    # 内容预览（前200字符）
    category: Optional[DocumentCategory] = None  # 文档分类
```

### DocumentCategory

```python
class DocumentCategory(Enum):
    """文档分类枚举"""
    CORE = "core"           # 核心文档
    ARCHIVE = "archive"     # 归档文档
    DEVELOPMENT = "development"  # 开发文档
    UNKNOWN = "unknown"     # 未分类
```

### ClassificationConfig

```python
@dataclass
class ClassificationConfig:
    """分类配置"""
    core_file_names: List[str]      # 核心文档文件名列表
    archive_keywords: List[str]     # 归档文档关键词列表
    development_keywords: List[str] # 开发文档关键词列表
    exclude_patterns: List[str]     # 排除的文件模式
```

### DirectoryStructure

```python
@dataclass
class DirectoryStructure:
    """目录结构配置"""
    docs_root: str          # 文档根目录
    archive_dir: str        # 归档目录
    development_dir: str    # 开发文档目录
    backend_docs_dir: str   # 后端文档目录
    frontend_docs_dir: str  # 前端文档目录
```

### MoveResult

```python
@dataclass
class MoveResult:
    """移动操作结果"""
    document: Document      # 文档对象
    original_path: str      # 原始路径
    new_path: str          # 新路径
    success: bool          # 是否成功
    error_message: Optional[str] = None  # 错误信息
```

### BackupInfo

```python
@dataclass
class BackupInfo:
    """备份信息"""
    backup_id: str         # 备份ID
    backup_path: str       # 备份路径
    timestamp: datetime    # 备份时间
    document_count: int    # 文档数量
    manifest: List[Dict]   # 文档清单（原路径 -> 备份路径映射）
```

## 配置文件格式

### organization_config.json

```json
{
  "classification": {
    "core_documents": [
      "README.md",
      "SETUP.md",
      "MAINTENANCE.md",
      "CHANGELOG.md",
      ".kiro/PROJECT.md"
    ],
    "archive_keywords": [
      "SUMMARY",
      "REPORT",
      "COMPLETION",
      "FIX",
      "TROUBLESHOOTING",
      "TASK_",
      "FINAL_",
      "INTEGRATION_TEST_"
    ],
    "development_keywords": [
      "GUIDE",
      "SETUP",
      "DATABASE_",
      "MIGRATION_",
      "IMPORT_",
      "RULE_GENERATION"
    ],
    "exclude_patterns": [
      "node_modules/**",
      ".git/**",
      "**/__pycache__/**",
      "**/venv/**"
    ]
  },
  "directory_structure": {
    "docs_root": "docs",
    "archive_dir": "docs/archive",
    "development_dir": "docs/development",
    "backend_docs_dir": "backend/docs",
    "frontend_docs_dir": "frontend/docs"
  },
  "archive_grouping": {
    "device-row-recognition": [
      "DEVICE_ROW_RECOGNITION",
      "TASK_9"
    ],
    "device-library": [
      "DEVICE_LIBRARY_EXPANSION"
    ],
    "ui-optimization": [
      "UI_OPTIMIZATION",
      "UI_TOOLTIP"
    ],
    "troubleshooting": [
      "TROUBLESHOOTING",
      "MANUAL_ADJUST"
    ],
    "testing": [
      "TEST_REPORT",
      "INTEGRATION_TEST",
      "ACCEPTANCE_REPORT"
    ],
    "tasks": [
      "TASK_7",
      "TASK_12"
    ]
  },
  "backup": {
    "enabled": true,
    "backup_dir": ".backup/docs",
    "keep_backups": 5
  },
  "index_generation": {
    "include_file_size": true,
    "include_modified_date": true,
    "include_description": true,
    "max_description_length": 100
  }
}
```

## 工作流程

### 主流程

1. **初始化**
   - 加载配置文件
   - 验证配置有效性
   - 创建备份目录

2. **扫描阶段**
   - 扫描项目根目录
   - 识别所有 MD 文档
   - 排除指定目录

3. **分类阶段**
   - 应用分类规则
   - 标记文档类别
   - 生成分类报告

4. **备份阶段**
   - 创建文档备份
   - 记录原始位置
   - 生成备份清单

5. **移动阶段**
   - 创建目标目录结构
   - 移动归档文档
   - 移动开发文档
   - 保持核心文档不动

6. **索引生成阶段**
   - 生成主文档索引
   - 生成归档索引
   - 生成开发文档索引
   - 更新 README 导航

7. **验证阶段**
   - 验证所有文档已处理
   - 验证链接有效性
   - 生成操作日志

8. **完成**
   - 输出整理报告
   - 提供恢复脚本

### 错误处理流程

```
错误发生 → 记录错误 → 停止操作 → 提示用户 → 提供恢复选项
```

## 正确性属性

*属性是系统应该满足的特征或行为，适用于所有有效执行。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*


### 属性 1: 文档扫描完整性

*对于任何*包含 MD 文档的项目目录，扫描器应该识别所有 MD 文件（排除配置的排除目录）。

**验证**: 需求 1.1

### 属性 2: 文档分类完备性

*对于任何*文档，分类器应该将其分配到一个有效的分类（CORE、ARCHIVE、DEVELOPMENT 或 UNKNOWN），不应该有文档没有分类。

**验证**: 需求 1.2

### 属性 3: 归档关键词识别

*对于任何*文件名包含归档关键词（SUMMARY、REPORT、COMPLETION 等）的文档，分类器应该将其标记为归档文档。

**验证**: 需求 1.3

### 属性 4: 核心文档位置不变性

*对于任何*被标记为核心文档的文件，整理操作前后其路径应该保持不变。

**验证**: 需求 2.4, 5.1, 5.2, 5.3, 5.4, 5.5

### 属性 5: 目录层次约束

*对于任何*创建的目录结构，从文档根目录到任何文档的路径深度不应超过3层。

**验证**: 需求 2.5

### 属性 6: 归档文档移动正确性

*对于任何*被标记为归档文档的文件，它应该被移动到 docs/archive/ 目录或其子目录中。

**验证**: 需求 3.1

### 属性 7: 文件名不变性

*对于任何*被移动的文档，移动前后的文件名（不包括路径）应该保持不变。

**验证**: 需求 3.2

### 属性 8: 功能模块分组一致性

*对于任何*属于同一功能模块的归档文档集合，它们应该被放置在同一个子目录中。

**验证**: 需求 3.3

### 属性 9: 文档内容完整性

*对于任何*被移动的文档，移动前后的文件内容应该完全相同（字节级别相同）。

**验证**: 需求 3.5

### 属性 10: 文档不删除保证

*对于任何*原始文档，系统不应该删除它，只能移动到新位置或保持原位置。

**验证**: 需求 4.5

### 属性 11: 索引包含所有分类

*对于任何*生成的主文档索引，它应该包含所有有效的文档分类（CORE、ARCHIVE、DEVELOPMENT）。

**验证**: 需求 6.2

### 属性 12: 索引文档元数据完整性

*对于任何*在索引中列出的文档，索引应该包含该文档的基本元数据（文件名、链接、描述、类型、状态）。

**验证**: 需求 6.3, 6.4, 9.1, 9.2, 9.3, 9.5

### 属性 13: 导航链接相对路径

*对于任何*生成的导航链接，它应该使用相对路径而非绝对路径。

**验证**: 需求 7.2

### 属性 14: 导航文档分组

*对于任何*生成的导航内容，同一类型的文档应该被分组在一起。

**验证**: 需求 7.3

### 属性 15: 导航链接有效性

*对于任何*导航或索引中的文档链接，链接指向的文件应该存在。

**验证**: 需求 7.5, 10.4

### 属性 16: 开发目录索引生成

*对于任何*包含文档的开发文档目录（backend/docs、frontend/docs、docs/development），应该存在对应的索引文件。

**验证**: 需求 8.4

### 属性 17: 归档日期标记

*对于任何*归档文档，其内容或元数据中应该包含归档日期标记。

**验证**: 需求 9.4

### 属性 18: 文档处理完整性

*对于任何*原始文档集合，整理完成后，所有文档都应该被处理（移动或保持原位），不应该有遗漏的文档。

**验证**: 需求 10.1

### 属性 19: 备份路径记录

*对于任何*被备份的文档，备份清单中应该记录其原始路径和备份路径的映射关系。

**验证**: 需求 11.2

### 属性 20: 恢复操作往返性

*对于任何*文档集合，执行整理操作然后执行恢复操作，应该回到原始状态（所有文档回到原位置，内容不变）。

**验证**: 需求 11.4

### 属性 21: 配置规则应用

*对于任何*有效的配置文件，修改配置后重新运行系统，系统行为应该反映新的配置规则。

**验证**: 需求 12.3

### 属性 22: 配置格式验证

*对于任何*配置文件，系统应该能够检测并报告格式错误（如缺少必需字段、类型不匹配等）。

**验证**: 需求 12.5

## 错误处理

### 错误类型

1. **文件系统错误**
   - 文件不存在
   - 权限不足
   - 磁盘空间不足
   - 文件被占用

2. **配置错误**
   - 配置文件格式错误
   - 缺少必需字段
   - 无效的路径配置

3. **操作错误**
   - 文档移动失败
   - 索引生成失败
   - 备份创建失败

### 错误处理策略

1. **验证阶段错误**
   - 配置验证失败 → 输出详细错误信息，终止操作
   - 目录不存在 → 尝试创建，失败则终止

2. **扫描阶段错误**
   - 文件读取失败 → 记录警告，跳过该文件，继续处理其他文件
   - 权限不足 → 记录警告，跳过该文件

3. **移动阶段错误**
   - 文件移动失败 → 记录错误，尝试回滚已移动的文件
   - 目标目录创建失败 → 终止操作，保持原状

4. **索引生成错误**
   - 索引文件写入失败 → 记录错误，但不影响文档移动结果

5. **备份错误**
   - 备份创建失败 → 询问用户是否继续（不建议）

### 错误恢复

1. **自动回滚**: 如果移动阶段发生错误，自动将已移动的文档移回原位置
2. **手动恢复**: 提供恢复脚本，用户可以手动执行恢复操作
3. **错误日志**: 记录所有错误和警告，便于排查问题

## 测试策略

### 单元测试

**测试范围**:
- 文档扫描器：测试不同目录结构的扫描
- 文档分类器：测试各种文件名和内容的分类
- 文档移动器：测试文件移动操作
- 索引生成器：测试索引内容生成
- 备份管理器：测试备份和恢复操作
- 配置管理器：测试配置加载和验证

**测试工具**: pytest

**示例测试**:
```python
def test_scanner_finds_all_md_files():
    """测试扫描器能找到所有 MD 文件"""
    # 创建测试目录结构
    test_dir = create_test_directory_with_md_files(count=5)
    
    # 扫描
    scanner = DocumentScanner()
    documents = scanner.scan_directory(test_dir, exclude_dirs=[])
    
    # 验证
    assert len(documents) == 5
    assert all(doc.file_name.endswith('.md') for doc in documents)

def test_classifier_marks_summary_as_archive():
    """测试分类器将包含 SUMMARY 的文档标记为归档"""
    # 创建测试文档
    doc = Document(
        file_name="FEATURE_SUMMARY.md",
        file_path="/path/to/FEATURE_SUMMARY.md",
        relative_path="FEATURE_SUMMARY.md",
        size=1000,
        modified_time=datetime.now(),
        content_preview="This is a summary..."
    )
    
    # 分类
    config = ClassificationConfig(
        core_file_names=["README.md"],
        archive_keywords=["SUMMARY", "REPORT"],
        development_keywords=["GUIDE"],
        exclude_patterns=[]
    )
    classifier = DocumentClassifier(config)
    category = classifier.classify(doc)
    
    # 验证
    assert category == DocumentCategory.ARCHIVE
```

### 属性测试

**测试范围**:
- 文档扫描完整性
- 文档分类完备性
- 文件名和内容不变性
- 链接有效性
- 往返性（整理 + 恢复 = 原状）

**测试工具**: pytest + hypothesis

**配置**: 每个属性测试至少运行 100 次迭代

**示例属性测试**:
```python
from hypothesis import given, strategies as st

@given(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=20))
def test_property_all_documents_classified(file_names):
    """
    属性测试：所有文档都应该被分类
    
    Feature: documentation-organization, Property 2: 文档分类完备性
    """
    # 创建测试文档
    documents = [
        Document(
            file_name=f"{name}.md",
            file_path=f"/test/{name}.md",
            relative_path=f"{name}.md",
            size=100,
            modified_time=datetime.now(),
            content_preview="test content"
        )
        for name in file_names
    ]
    
    # 分类
    config = get_default_classification_config()
    classifier = DocumentClassifier(config)
    results = classifier.classify_batch(documents)
    
    # 验证：所有文档都被分类
    total_classified = sum(len(docs) for docs in results.values())
    assert total_classified == len(documents)
    
    # 验证：每个文档都有分类
    for doc in documents:
        assert doc.category is not None
        assert doc.category in DocumentCategory

@given(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10))
def test_property_file_content_unchanged_after_move(file_names):
    """
    属性测试：文档移动后内容不变
    
    Feature: documentation-organization, Property 9: 文档内容完整性
    """
    # 创建测试文件
    test_dir = create_temp_directory()
    original_contents = {}
    
    for name in file_names:
        file_path = os.path.join(test_dir, f"{name}.md")
        content = f"Test content for {name}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        original_contents[name] = content
    
    # 执行整理操作
    organizer = DocumentOrganizer(config)
    organizer.organize(test_dir)
    
    # 验证：所有文件内容不变
    for name, original_content in original_contents.items():
        # 查找文件新位置
        new_path = find_document_new_path(test_dir, f"{name}.md")
        assert new_path is not None
        
        # 读取新位置的内容
        with open(new_path, 'r', encoding='utf-8') as f:
            new_content = f.read()
        
        # 验证内容相同
        assert new_content == original_content

def test_property_organize_then_restore_is_identity():
    """
    属性测试：整理然后恢复应该回到原状
    
    Feature: documentation-organization, Property 20: 恢复操作往返性
    """
    # 创建测试目录和文档
    test_dir = create_test_directory_with_documents()
    original_structure = capture_directory_structure(test_dir)
    
    # 执行整理
    organizer = DocumentOrganizer(config)
    backup_info = organizer.organize(test_dir)
    
    # 执行恢复
    backup_manager = BackupManager()
    backup_manager.restore_from_backup(backup_info)
    
    # 验证：目录结构回到原状
    restored_structure = capture_directory_structure(test_dir)
    assert restored_structure == original_structure
```

### 集成测试

**测试场景**:
1. 完整流程测试：从扫描到索引生成
2. 错误恢复测试：模拟各种错误情况
3. 大规模测试：测试处理大量文档的性能

**示例集成测试**:
```python
def test_full_organization_workflow():
    """测试完整的文档整理流程"""
    # 准备：创建模拟项目结构
    project_dir = create_mock_project_structure()
    
    # 执行：运行整理系统
    config = load_config('test_config.json')
    organizer = DocumentOrganizer(config)
    result = organizer.organize(project_dir)
    
    # 验证：核心文档保持不动
    assert os.path.exists(os.path.join(project_dir, 'README.md'))
    assert os.path.exists(os.path.join(project_dir, 'SETUP.md'))
    
    # 验证：归档文档被移动
    assert os.path.exists(os.path.join(project_dir, 'docs/archive'))
    assert not os.path.exists(os.path.join(project_dir, 'TASK_1_SUMMARY.md'))
    assert os.path.exists(os.path.join(project_dir, 'docs/archive/tasks/TASK_1_SUMMARY.md'))
    
    # 验证：索引文件生成
    assert os.path.exists(os.path.join(project_dir, 'docs/README.md'))
    assert os.path.exists(os.path.join(project_dir, 'docs/archive/README.md'))
    
    # 验证：所有链接有效
    verify_all_links_valid(project_dir)
    
    # 验证：备份创建
    assert result.backup_info is not None
    assert os.path.exists(result.backup_info.backup_path)
```

### 测试覆盖率目标

- 单元测试覆盖率：≥ 80%
- 属性测试：覆盖所有关键属性（至少 15 个属性）
- 集成测试：覆盖主要使用场景（至少 5 个场景）

## 性能考虑

### 性能目标

- 扫描 1000 个文件：≤ 2 秒
- 分类 1000 个文档：≤ 1 秒
- 移动 100 个文档：≤ 5 秒
- 生成索引：≤ 1 秒

### 优化策略

1. **并行处理**: 使用多线程并行扫描和分类
2. **增量更新**: 只处理变更的文档
3. **缓存机制**: 缓存文档元数据，避免重复读取
4. **批量操作**: 批量移动文件，减少 I/O 操作

## 安全考虑

1. **路径验证**: 验证所有路径，防止路径遍历攻击
2. **权限检查**: 操作前检查文件和目录权限
3. **备份保护**: 备份文件使用只读权限
4. **原子操作**: 使用原子操作确保文件移动的一致性

## 扩展性

### 未来扩展方向

1. **智能分类**: 使用机器学习自动识别文档类型
2. **内容分析**: 分析文档内容，自动生成摘要
3. **版本控制集成**: 与 Git 集成，自动提交整理结果
4. **Web 界面**: 提供 Web 界面进行可视化管理
5. **多语言支持**: 支持多语言文档的整理

### 插件系统

设计插件接口，允许用户自定义：
- 分类规则
- 索引格式
- 文档处理逻辑

```python
class DocumentOrganizerPlugin:
    """文档整理插件基类"""
    
    def on_document_scanned(self, document: Document) -> None:
        """文档扫描后的钩子"""
        pass
    
    def on_document_classified(self, document: Document, category: DocumentCategory) -> None:
        """文档分类后的钩子"""
        pass
    
    def on_document_moved(self, document: Document, old_path: str, new_path: str) -> None:
        """文档移动后的钩子"""
        pass
    
    def on_index_generated(self, index_path: str, content: str) -> str:
        """索引生成后的钩子，可以修改索引内容"""
        return content
```

## 总结

本设计提供了一个完整的文档整理系统，具有以下特点：

1. **模块化设计**: 各组件职责清晰，易于测试和维护
2. **配置驱动**: 通过配置文件灵活调整整理规则
3. **安全可靠**: 支持备份和恢复，确保操作安全
4. **可测试性**: 提供完整的测试策略，包括单元测试和属性测试
5. **可扩展性**: 预留扩展接口，支持未来功能增强

系统通过 22 个正确性属性确保整理操作的正确性，通过完善的错误处理机制确保系统的健壮性。
