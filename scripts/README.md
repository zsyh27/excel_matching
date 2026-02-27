# 项目管理脚本

本目录包含用于项目维护和管理的脚本。

## 脚本列表

### 1. cleanup_project.py - 项目文件清理工具

自动识别并清理临时文件、整理项目结构。

**功能**：
- 识别临时测试文件
- 归档过时文件
- 移动诊断工具到tools目录
- 移动运维脚本到scripts目录
- 生成清理报告

**使用方法**：

```bash
# 预览模式（推荐先运行）
python scripts/cleanup_project.py --dry-run

# 执行清理
python scripts/cleanup_project.py --execute
```

**输出示例**：

```
项目文件清理工具
================================================================================
模式: 预览模式

扫描 backend 目录...
  找到 15 个临时文件
  找到 5 个诊断工具
  找到 8 个运维脚本

清理报告
================================================================================
统计信息:
  临时文件: 15 个
  诊断工具: 5 个
  运维脚本: 8 个
  重复文档: 12 个
```

### 2. organize_docs.py - 文档整理工具

分析和整理项目文档结构。

**功能**：
- 分析文档结构
- 识别重复文档
- 生成文档索引
- 提供合并建议

**使用方法**：

```bash
# 分析文档结构
python scripts/organize_docs.py --analyze

# 生成文档索引
python scripts/organize_docs.py --execute
```

**输出示例**：

```
文档整理工具
================================================================================
模式: analyze

扫描 docs 目录...
  找到 35 个文档

文档分析报告
================================================================================
按主题分组:
  CONFIG_MANAGEMENT (8 个文档)
  DEVICE_MANAGEMENT (5 个文档)
  ...

整理建议:
  CONFIG_MANAGEMENT 有 8 个文档，建议合并
```

## 使用场景

### 场景1：每次修改后

```bash
# 删除临时测试文件
rm backend/test_*_fix.py
rm backend/test_*_debug.py
```

### 场景2：每周维护

```bash
# 运行清理脚本（预览）
python scripts/cleanup_project.py --dry-run

# 确认后执行
python scripts/cleanup_project.py --execute
```

### 场景3：每月整理

```bash
# 分析文档结构
python scripts/organize_docs.py --analyze

# 生成文档索引
python scripts/organize_docs.py --execute

# 运行完整清理
python scripts/cleanup_project.py --execute
```

## 文件分类规则

### 临时文件（应该删除）

- `test_*_fix.py` - 修复验证脚本
- `test_*_debug.py` - 调试脚本
- `fix_*.py` - 一次性修复脚本
- `check_temp_*.py` - 临时检查脚本
- `demo_*.py` - 演示脚本

### 诊断工具（移动到tools/）

- `diagnose_*.py` - 诊断工具
- `verify_*.py` - 验证工具

### 运维脚本（移动到scripts/）

- `init_*.py` - 初始化脚本
- `migrate_*.py` - 迁移脚本
- `sync_*.py` - 同步脚本
- `regenerate_*.py` - 重新生成脚本

## 安全提示

1. **先预览再执行**：始终先运行 `--dry-run` 模式
2. **提交代码**：清理前先提交重要更改到Git
3. **备份重要文件**：如果不确定，先备份
4. **检查结果**：清理后运行测试确保功能正常

## 常见问题

### Q: 脚本会删除重要文件吗？

A: 不会。脚本只处理明确标记为临时的文件（如test_*_fix.py）。核心代码、正式测试和文档都不会被删除。

### Q: 如果误删了文件怎么办？

A: 
1. 使用Git恢复：`git checkout -- <file>`
2. 从归档目录恢复：`.archive/`

### Q: 可以自定义清理规则吗？

A: 可以。编辑脚本中的 `TEMP_FILE_PATTERNS` 和 `TOOL_PATTERNS` 变量。

## 相关文档

- [文件管理指南](../docs/FILE_MANAGEMENT_GUIDE.md) - 完整的文件管理策略
- [快速清理指南](../docs/QUICK_CLEANUP_GUIDE.md) - 快速参考指南

## 贡献

如果你有改进建议或发现问题，请：
1. 提交Issue
2. 或直接提交Pull Request

## 许可

与项目主许可证相同。
