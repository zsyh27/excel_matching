# 核心目录配置

## 概述

核心目录是指那些包含重要项目文件、不应该被文档整理系统移动的目录。通过在配置文件中指定核心目录，可以确保这些目录中的所有文档都被标记为核心文档，从而保持在原位置。

## 配置方式

在 `organization_config.json` 配置文件的 `classification` 部分添加 `core_directories` 字段：

```json
{
  "classification": {
    "core_documents": [
      "README.md",
      "SETUP.md",
      ...
    ],
    "core_directories": [
      ".kiro/specs/**"
    ],
    ...
  }
}
```

## 支持的模式

核心目录配置支持以下模式：

### 1. 递归通配符 (`**`)

匹配目录及其所有子目录：

```json
"core_directories": [
  ".kiro/specs/**"
]
```

这将匹配：
- `.kiro/specs/feature-a/requirements.md`
- `.kiro/specs/feature-b/sub-feature/design.md`
- `.kiro/specs/any/nested/path/tasks.md`

### 2. 单层通配符 (`*`)

仅匹配直接子目录，不包括更深层的子目录：

```json
"core_directories": [
  ".kiro/specs/*"
]
```

这将匹配：
- `.kiro/specs/feature-a/requirements.md`

但不匹配：
- `.kiro/specs/feature-a/sub-feature/design.md`（太深）

### 3. 精确匹配

匹配特定目录：

```json
"core_directories": [
  ".kiro/specs/important-feature"
]
```

这将匹配：
- `.kiro/specs/important-feature/requirements.md`
- `.kiro/specs/important-feature/design.md`

但不匹配：
- `.kiro/specs/other-feature/requirements.md`

## 优先级

核心目录的优先级最高，即使文档的文件名包含归档或开发关键词，只要它位于核心目录中，就会被标记为核心文档。

优先级顺序：
1. **核心目录** - 最高优先级
2. **核心文档名称** - 如 README.md, SETUP.md
3. **归档关键词** - 如 SUMMARY, REPORT
4. **开发关键词** - 如 GUIDE, MIGRATION

## 示例

### 保护规格文件

```json
"core_directories": [
  ".kiro/specs/**"
]
```

这确保所有规格文件（requirements.md, design.md, tasks.md）都不会被移动。

### 保护多个目录

```json
"core_directories": [
  ".kiro/specs/**",
  ".kiro/workflows/**",
  "config/**"
]
```

### 保护特定功能的规格

```json
"core_directories": [
  ".kiro/specs/critical-feature/**",
  ".kiro/specs/production-ready/**"
]
```

## 测试

可以使用以下命令测试核心目录配置是否正确：

```bash
python -m pytest organize_docs/test_classifier.py::TestCoreDirectories -v
```

## 注意事项

1. 路径使用正斜杠 (`/`)，系统会自动处理 Windows 的反斜杠
2. 路径是相对于项目根目录的
3. 不要在路径末尾添加斜杠
4. 使用 `**` 进行递归匹配时，会匹配所有子目录
5. 核心目录中的文档永远不会被移动，即使它们的文件名符合归档或开发文档的规则

## 相关文件

- `organize_docs/models.py` - ClassificationConfig 数据模型
- `organize_docs/classifier.py` - 文档分类器实现
- `organize_docs/config_manager.py` - 配置管理器
- `organization_config.json` - 项目配置文件
