# 文档整理功能使用指南

## 简介

文档整理功能是一个自动化工具，用于系统化地整理项目中的 MD 文档。它可以自动识别文档类型，按照预定义规则进行分类、归档和索引，同时保持核心文档的可访问性。

## 功能特性

- **自动文档分类**: 根据文件名和内容自动识别文档类型
- **智能归档**: 将历史文档归档到分组目录
- **核心文档保护**: 保持重要文档在项目根目录
- **自动备份**: 操作前自动创建备份，支持一键恢复
- **索引生成**: 自动生成文档索引和导航链接
- **配置驱动**: 通过配置文件灵活调整整理规则

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 验证配置

首次使用前，验证配置文件是否正确：

```bash
python -m organize_docs.cli validate --verbose
```

### 3. 试运行

使用试运行模式查看将要执行的操作：

```bash
python -m organize_docs.cli organize --dry-run
```

### 4. 执行整理

确认无误后，执行实际整理：

```bash
python -m organize_docs.cli organize --yes
```

## 文档分类规则

### 核心文档 (Core Documents)

保持在项目根目录，不会被移动：

- `README.md` - 项目概述和快速开始
- `SETUP.md` - 安装和配置指南
- `MAINTENANCE.md` - 维护和故障排查指南
- `CHANGELOG.md` - 版本变更历史
- `.kiro/PROJECT.md` - 项目元数据

### 归档文档 (Archive Documents)

移动到 `docs/archive/` 目录，按功能模块分组：

**识别规则**：文件名包含以下关键词
- `SUMMARY` - 总结文档
- `REPORT` - 报告文档
- `COMPLETION` - 完成文档
- `FIX` - 修复文档
- `TROUBLESHOOTING` - 故障排查文档
- `TASK_*` - 任务文档
- `FINAL_*` - 最终文档
- `INTEGRATION_TEST_*` - 集成测试文档

**分组示例**：
- `docs/archive/device-row-recognition/` - 设备行识别相关文档
- `docs/archive/device-library/` - 设备库相关文档
- `docs/archive/ui-optimization/` - UI 优化相关文档
- `docs/archive/troubleshooting/` - 故障排查相关文档
- `docs/archive/testing/` - 测试相关文档
- `docs/archive/tasks/` - 任务相关文档

### 开发文档 (Development Documents)

移动到相应的开发文档目录：

**识别规则**：文件名包含以下关键词
- `GUIDE` - 指南文档
- `SETUP` - 设置文档
- `DATABASE_*` - 数据库相关文档
- `MIGRATION_*` - 迁移相关文档
- `IMPORT_*` - 导入相关文档
- `RULE_GENERATION` - 规则生成相关文档

**目标目录**：
- `backend/docs/` - 后端技术文档
- `frontend/docs/` - 前端技术文档
- `docs/development/` - 通用开发文档

## 目录结构

整理后的目录结构：

```
项目根目录/
├── README.md                    # 核心文档
├── SETUP.md                     # 核心文档
├── MAINTENANCE.md               # 核心文档
├── CHANGELOG.md                 # 核心文档
├── docs/                        # 文档根目录
│   ├── README.md               # 文档索引
│   ├── archive/                # 归档文档
│   │   ├── README.md          # 归档索引
│   │   ├── device-row-recognition/
│   │   ├── device-library/
│   │   ├── ui-optimization/
│   │   ├── troubleshooting/
│   │   ├── testing/
│   │   └── tasks/
│   └── development/            # 开发文档
│       └── README.md          # 开发文档索引
├── backend/
│   └── docs/                   # 后端文档
│       └── README.md
├── frontend/
│   └── docs/                   # 前端文档
│       └── README.md
└── .backup/                    # 备份目录
    └── docs/
        └── backup_YYYYMMDD_HHMMSS_UUID/
```

## 自定义配置

### 配置文件位置

默认配置文件：`organization_config.json`

### 配置项说明

#### 1. 文档分类规则 (classification)

```json
{
  "classification": {
    "core_documents": ["README.md", "SETUP.md"],
    "archive_keywords": ["SUMMARY", "REPORT"],
    "development_keywords": ["GUIDE", "SETUP"],
    "exclude_patterns": ["node_modules/**", ".git/**"]
  }
}
```

- `core_documents`: 核心文档列表（文件名或路径）
- `archive_keywords`: 归档文档关键词
- `development_keywords`: 开发文档关键词
- `exclude_patterns`: 排除的目录模式（支持通配符）

#### 2. 目录结构 (directory_structure)

```json
{
  "directory_structure": {
    "docs_root": "docs",
    "archive_dir": "docs/archive",
    "development_dir": "docs/development",
    "backend_docs_dir": "backend/docs",
    "frontend_docs_dir": "frontend/docs"
  }
}
```

所有路径都是相对于项目根目录的相对路径。

#### 3. 归档分组 (archive_grouping)

```json
{
  "archive_grouping": {
    "device-row-recognition": ["DEVICE_ROW_RECOGNITION", "TASK_9"],
    "device-library": ["DEVICE_LIBRARY_EXPANSION"],
    "ui-optimization": ["UI_OPTIMIZATION", "UI_TOOLTIP"]
  }
}
```

定义归档文档的分组规则。键是分组目录名，值是匹配关键词列表。

#### 4. 备份配置 (backup)

```json
{
  "backup": {
    "enabled": true,
    "backup_dir": ".backup/docs",
    "keep_backups": 5
  }
}
```

- `enabled`: 是否启用备份（强烈建议保持启用）
- `backup_dir`: 备份目录路径
- `keep_backups`: 保留的备份数量（旧备份会被自动清理）

#### 5. 索引生成配置 (index_generation)

```json
{
  "index_generation": {
    "include_file_size": true,
    "include_modified_date": true,
    "include_description": true,
    "max_description_length": 100
  }
}
```

- `include_file_size`: 索引中是否包含文件大小
- `include_modified_date`: 索引中是否包含修改日期
- `include_description`: 索引中是否包含文档描述
- `max_description_length`: 描述的最大长度

### 修改配置

1. 编辑 `organization_config.json` 文件
2. 验证配置：`python -m organize_docs.cli validate`
3. 试运行测试：`python -m organize_docs.cli organize --dry-run`
4. 执行整理：`python -m organize_docs.cli organize --yes`

## 使用场景

### 场景 1: 项目初始整理

项目积累了大量文档，需要首次整理：

```bash
# 1. 验证配置
python -m organize_docs.cli validate --verbose

# 2. 试运行查看效果
python -m organize_docs.cli organize --dry-run

# 3. 确认无误后执行
python -m organize_docs.cli organize --yes

# 4. 查看生成的索引
cat docs/README.md
cat docs/archive/README.md
```

### 场景 2: 定期维护

定期整理新增的文档：

```bash
# 直接执行整理（已有配置）
python -m organize_docs.cli organize --yes

# 查看备份列表
python -m organize_docs.cli list-backups
```

### 场景 3: 自定义分类规则

需要根据项目特点调整分类规则：

```bash
# 1. 编辑配置文件
vim organization_config.json

# 2. 验证新配置
python -m organize_docs.cli validate --verbose

# 3. 试运行测试
python -m organize_docs.cli organize --dry-run

# 4. 执行整理
python -m organize_docs.cli organize --yes
```

### 场景 4: 恢复操作

整理后发现问题，需要恢复：

```bash
# 1. 列出所有备份
python -m organize_docs.cli list-backups

# 2. 选择最新备份恢复
python -m organize_docs.cli restore --backup-id backup_20240212_143022_abc123 --yes
```

## 最佳实践

### 1. 首次使用

- 使用 `--dry-run` 模式查看效果
- 仔细检查试运行输出
- 确认核心文档不会被移动
- 确认归档文档分组合理

### 2. 配置调整

- 根据项目特点自定义关键词
- 添加项目特定的归档分组
- 调整排除模式避免扫描不必要的目录

### 3. 定期维护

- 定期执行整理（如每周或每月）
- 定期清理旧备份
- 更新索引文件的描述信息

### 4. 团队协作

- 将配置文件纳入版本控制
- 在团队中统一整理规则
- 文档化项目特定的分类规则

## 故障排查

### 问题 1: 配置验证失败

**症状**: 运行 `validate` 命令报错

**解决方法**:
1. 检查 JSON 格式是否正确（使用 JSON 验证工具）
2. 确认所有必需字段都存在
3. 检查路径格式（使用相对路径，不包含非法字符）

### 问题 2: 文档分类不正确

**症状**: 文档被分类到错误的类别

**解决方法**:
1. 检查文件名是否包含分类关键词
2. 调整配置文件中的关键词列表
3. 使用 `--dry-run` 模式验证新配置

### 问题 3: 文档移动失败

**症状**: 部分文档移动失败

**解决方法**:
1. 检查文件权限
2. 确认目标目录可写
3. 关闭占用文件的程序
4. 查看日志文件获取详细错误信息

### 问题 4: 备份占用空间过大

**症状**: `.backup/` 目录占用大量磁盘空间

**解决方法**:
1. 调整 `keep_backups` 配置减少保留数量
2. 手动删除旧备份
3. 考虑使用外部备份工具

## 日志和报告

### 日志文件

位置：`.logs/organization_YYYYMMDD_HHMMSS.log`

内容包括：
- 扫描到的文档列表
- 分类结果详情
- 移动操作记录
- 错误和警告信息
- 验证结果

### 清单对比报告

位置：`.logs/manifest_comparison_YYYYMMDD_HHMMSS.txt`

内容包括：
- 文档统计信息
- 按分类的文档列表
- 移动操作详情
- 未处理的文档列表

## 安全注意事项

1. **备份**: 始终保持备份功能启用
2. **试运行**: 首次使用或修改配置后使用 `--dry-run`
3. **权限**: 确保有足够的文件系统权限
4. **版本控制**: 在执行整理前提交代码到版本控制系统
5. **恢复测试**: 定期测试备份恢复功能

## 高级功能

### 1. 批量处理多个项目

创建脚本批量处理：

```bash
#!/bin/bash
for project in project1 project2 project3; do
  cd $project
  python -m organize_docs.cli organize --yes
  cd ..
done
```

### 2. 集成到 CI/CD

在 CI/CD 流程中自动整理文档：

```yaml
# .github/workflows/organize-docs.yml
name: Organize Documentation
on:
  schedule:
    - cron: '0 0 * * 0'  # 每周日运行
jobs:
  organize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Organize docs
        run: python -m organize_docs.cli organize --yes
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add .
          git commit -m "Auto-organize documentation" || true
          git push
```

### 3. 自定义插件

扩展功能（未来版本）：

```python
from organize_docs.organizer import DocumentOrganizerPlugin

class MyCustomPlugin(DocumentOrganizerPlugin):
    def on_document_classified(self, document, category):
        # 自定义分类后的处理逻辑
        pass
```

## 常见问题 (FAQ)

**Q: 整理操作会删除文档吗？**  
A: 不会。系统只会移动文档到新位置，不会删除任何文档。

**Q: 可以恢复到整理前的状态吗？**  
A: 可以。使用 `restore` 命令从备份恢复。

**Q: 核心文档会被移动吗？**  
A: 不会。核心文档始终保持在原位置。

**Q: 如何添加新的分类规则？**  
A: 编辑 `organization_config.json` 文件，添加新的关键词或分组。

**Q: 支持哪些文件格式？**  
A: 目前只支持 Markdown (.md) 文件。

**Q: 可以在 Windows 上使用吗？**  
A: 可以。工具支持 Windows、Linux 和 macOS。

## 获取帮助

- **命令行帮助**: `python -m organize_docs.cli --help`
- **详细文档**: 查看 `organize_docs/CLI_USAGE.md`
- **问题反馈**: 提交 Issue 到项目仓库

## 版本历史

- **v0.1.0** (2026-02-13)
  - 初始版本
  - 支持文档扫描、分类、备份、移动和索引生成
  - 提供命令行接口
  - 支持配置驱动

---

**维护者**: 开发团队  
**最后更新**: 2026-02-14  
**许可证**: MIT

