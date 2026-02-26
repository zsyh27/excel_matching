# 文档整理工具 - CLI 使用指南

## 概述

文档整理工具提供命令行接口，用于自动整理项目中的 MD 文档。支持文档扫描、分类、备份、移动和索引生成。

## 安装

确保已安装 Python 3.8+ 和所需依赖：

```bash
pip install -r requirements.txt
```

## 基本用法

### 1. 验证配置文件

在执行整理操作前，建议先验证配置文件：

```bash
python -m organize_docs.cli validate
```

显示详细的配置摘要：

```bash
python -m organize_docs.cli validate --verbose
```

### 2. 执行文档整理

**试运行模式**（推荐首次使用）：

```bash
python -m organize_docs.cli organize --dry-run
```

试运行模式会显示将要执行的操作，但不会实际移动文件。

**实际执行整理**：

```bash
python -m organize_docs.cli organize
```

系统会提示确认，输入 `y` 继续。

**跳过确认提示**：

```bash
python -m organize_docs.cli organize --yes
```

### 3. 列出备份

查看所有可用的备份：

```bash
python -m organize_docs.cli list-backups
```

显示详细信息（包括文档列表）：

```bash
python -m organize_docs.cli list-backups --verbose
```

### 4. 从备份恢复

首先列出所有备份，找到要恢复的备份 ID：

```bash
python -m organize_docs.cli list-backups
```

然后使用备份 ID 恢复：

```bash
python -m organize_docs.cli restore --backup-id backup_20240212_143022_abc123
```

系统会提示确认，输入 `y` 继续。

跳过确认提示：

```bash
python -m organize_docs.cli restore --backup-id backup_20240212_143022_abc123 --yes
```

## 高级用法

### 使用自定义配置文件

```bash
python -m organize_docs.cli organize --config my_config.json
```

### 指定项目根目录

```bash
python -m organize_docs.cli organize --project-root /path/to/project
```

### 组合使用参数

```bash
python -m organize_docs.cli organize \
  --config custom_config.json \
  --project-root /path/to/project \
  --dry-run
```

## 命令参考

### 全局参数

- `--config CONFIG`: 配置文件路径（默认: `organization_config.json`）
- `--project-root PROJECT_ROOT`: 项目根目录路径（默认: 当前目录）

### organize 命令

执行文档整理操作。

**参数**:
- `--dry-run`: 试运行模式，不实际移动文件
- `--yes, -y`: 跳过确认提示，直接执行

**示例**:
```bash
# 试运行
python -m organize_docs.cli organize --dry-run

# 实际执行
python -m organize_docs.cli organize --yes
```

### restore 命令

从备份恢复文档。

**参数**:
- `--backup-id BACKUP_ID`: 备份 ID（如果不指定，将列出所有可用备份）
- `--yes, -y`: 跳过确认提示，直接执行

**示例**:
```bash
# 列出所有备份
python -m organize_docs.cli restore

# 恢复指定备份
python -m organize_docs.cli restore --backup-id backup_20240212_143022_abc123
```

### list-backups 命令

列出所有可用的备份。

**参数**:
- `--verbose, -v`: 显示详细信息（包括文档列表）

**示例**:
```bash
# 简单列表
python -m organize_docs.cli list-backups

# 详细信息
python -m organize_docs.cli list-backups --verbose
```

### validate 命令

验证配置文件的格式和内容。

**参数**:
- `--verbose, -v`: 显示详细的配置摘要

**示例**:
```bash
# 基本验证
python -m organize_docs.cli validate

# 详细验证
python -m organize_docs.cli validate --verbose
```

## 工作流程示例

### 首次使用

1. 验证配置文件：
   ```bash
   python -m organize_docs.cli validate --verbose
   ```

2. 试运行查看效果：
   ```bash
   python -m organize_docs.cli organize --dry-run
   ```

3. 确认无误后执行：
   ```bash
   python -m organize_docs.cli organize --yes
   ```

4. 查看备份：
   ```bash
   python -m organize_docs.cli list-backups
   ```

### 恢复操作

如果需要恢复到整理前的状态：

1. 列出所有备份：
   ```bash
   python -m organize_docs.cli list-backups
   ```

2. 选择最新的备份并恢复：
   ```bash
   python -m organize_docs.cli restore --backup-id <backup_id> --yes
   ```

## 配置文件

默认配置文件为 `organization_config.json`，包含以下配置项：

- **classification**: 文档分类规则
  - `core_documents`: 核心文档列表
  - `archive_keywords`: 归档文档关键词
  - `development_keywords`: 开发文档关键词
  - `exclude_patterns`: 排除的目录模式

- **directory_structure**: 目录结构
  - `docs_root`: 文档根目录
  - `archive_dir`: 归档目录
  - `development_dir`: 开发文档目录
  - `backend_docs_dir`: 后端文档目录
  - `frontend_docs_dir`: 前端文档目录

- **archive_grouping**: 归档文档分组规则

- **backup**: 备份配置
  - `enabled`: 是否启用备份
  - `backup_dir`: 备份目录
  - `keep_backups`: 保留备份数量

- **index_generation**: 索引生成配置
  - `include_file_size`: 是否包含文件大小
  - `include_modified_date`: 是否包含修改日期
  - `include_description`: 是否包含描述
  - `max_description_length`: 描述最大长度

## 日志

执行整理操作时，系统会在 `.logs/` 目录下生成详细的日志文件：

```
.logs/organization_YYYYMMDD_HHMMSS.log
```

日志包含：
- 扫描到的文档列表
- 分类结果
- 移动操作详情
- 错误和警告信息

## 故障排查

### 配置验证失败

如果配置验证失败，请检查：
1. 配置文件格式是否正确（有效的 JSON）
2. 必需字段是否存在
3. 路径格式是否有效（相对路径，不包含非法字符）

### 文档移动失败

如果文档移动失败，可能的原因：
1. 文件权限不足
2. 目标目录不可写
3. 文件被其他程序占用

查看日志文件获取详细错误信息。

### 恢复失败

如果恢复操作失败：
1. 确认备份 ID 正确
2. 确认备份文件完整
3. 确认有足够的磁盘空间

## 安全提示

1. **首次使用建议使用试运行模式**，确认操作符合预期
2. **备份功能默认启用**，每次整理前会自动创建备份
3. **恢复操作会覆盖当前文档**，请谨慎操作
4. **定期清理旧备份**，避免占用过多磁盘空间

## 获取帮助

查看命令帮助信息：

```bash
# 主帮助
python -m organize_docs.cli --help

# 子命令帮助
python -m organize_docs.cli organize --help
python -m organize_docs.cli restore --help
python -m organize_docs.cli list-backups --help
python -m organize_docs.cli validate --help
```

## 版本信息

当前版本: 0.1.0

---

**维护者**: 开发团队  
**最后更新**: 2026-02-13
