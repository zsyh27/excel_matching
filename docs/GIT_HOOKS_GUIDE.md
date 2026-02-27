# Git Hooks 使用指南

## 概述

Git Hooks 是一个自动化工具，在每次提交代码前自动检查是否包含临时文件，防止将不应该提交的文件加入版本控制。

## 安装状态

✅ **Git Hooks 已成功安装并配置**

- 配置路径: `.githooks`
- Hook 文件: `.githooks/pre-commit`
- 状态: 已激活

## 功能说明

### 自动检查的文件类型

每次执行 `git commit` 时，Hook 会自动检查以下文件：

1. **临时测试文件**
   - `backend/test_*_fix.py` - 修复验证脚本
   - `backend/test_*_debug.py` - 调试脚本
   - `backend/check_temp_*.py` - 临时检查脚本
   - `backend/demo_*.py` - 演示脚本

2. **临时修复脚本**
   - `backend/fix_*.py` - 修复脚本

3. **根目录Python文件**
   - 除 `setup.py` 外的所有根目录 `.py` 文件

### 检查结果

如果检测到上述文件，Hook 会：
- ❌ **阻止提交**
- 📋 **显示文件列表**
- 💡 **提供处理建议**

## 使用示例

### 正常提交（无临时文件）

```bash
git add .
git commit -m "添加新功能"
```

输出：
```
检查临时文件...
✅ 文件检查通过
[main abc1234] 添加新功能
```

### 检测到临时文件

```bash
git add backend/test_fix_something.py
git commit -m "提交修复"
```

输出：
```
检查临时文件...
❌ 警告：检测到临时文件即将被提交：
backend/test_fix_something.py

这些文件看起来是临时测试/修复文件。
建议：
  1. 如果已验证完成，请删除这些文件
  2. 如果是诊断工具，请移动到 backend/tools/
  3. 如果确实需要提交，使用 git commit --no-verify
```

### 跳过检查（不推荐）

如果确实需要提交这些文件，可以使用 `--no-verify` 参数：

```bash
git commit -m "提交临时文件" --no-verify
```

⚠️ **注意**: 只在确实需要时使用此选项。

## 处理建议

### 场景1: 临时测试文件验证完成

```bash
# 删除临时文件
del backend\test_fix_something.py

# 正常提交其他文件
git add .
git commit -m "完成功能开发"
```

### 场景2: 诊断工具需要保留

```bash
# 移动到tools目录
move backend\diagnose_something.py backend\tools\

# 提交
git add backend\tools\diagnose_something.py
git commit -m "添加诊断工具"
```

### 场景3: 根目录脚本需要整理

```bash
# 移动到scripts目录
move create_something.py scripts\

# 提交
git add scripts\create_something.py
git commit -m "添加项目脚本"
```

## 维护命令

### 验证安装

```bash
# Windows
scripts\verify_hooks.bat

# 或手动检查
git config core.hooksPath
```

应该输出: `.githooks`

### 重新安装

```bash
# Windows
scripts\install_hooks.bat

# 或手动配置
git config core.hooksPath .githooks
```

### 卸载

```bash
git config --unset core.hooksPath
```

## 常见问题

### Q: Hook 没有运行？

**A**: 检查配置是否正确：
```bash
git config core.hooksPath
```

如果输出为空或不是 `.githooks`，重新运行安装脚本。

### Q: 中文显示乱码？

**A**: 这是 Git Bash 在 Windows 上的编码问题，不影响功能。Hook 仍然能正确检测和阻止提交。

### Q: 如何临时禁用 Hook？

**A**: 使用 `--no-verify` 参数：
```bash
git commit -m "消息" --no-verify
```

### Q: 如何永久禁用 Hook？

**A**: 卸载 Hook 配置：
```bash
git config --unset core.hooksPath
```

### Q: Hook 检查哪些文件？

**A**: 只检查暂存区（staged）的文件，即通过 `git add` 添加的文件。

## 最佳实践

### ✅ 推荐做法

1. **验证后立即删除临时文件**
   ```bash
   # 测试完成后
   del backend\test_fix_*.py
   ```

2. **使用清理脚本定期清理**
   ```bash
   python scripts\cleanup_project.py --dry-run
   python scripts\cleanup_project.py --execute
   ```

3. **提交前检查文件列表**
   ```bash
   git status
   ```

4. **遵循文件命名规范**
   - 正式测试: `backend/tests/test_*.py`
   - 诊断工具: `backend/tools/diagnose_*.py`
   - 运维脚本: `backend/scripts/*.py`

### ❌ 避免做法

1. 不要频繁使用 `--no-verify`
2. 不要在根目录创建 Python 脚本
3. 不要保留已完成功能的临时测试文件
4. 不要提交带有 `_fix`、`_debug` 后缀的文件

## 工作流程

```
1. 开发功能
   ↓
2. 创建临时测试文件验证
   ↓
3. 验证完成后删除临时文件
   ↓
4. git add .
   ↓
5. git commit -m "..."
   ↓
6. Hook 自动检查
   ↓
7. 检查通过 → 提交成功
   检查失败 → 处理文件后重新提交
```

## 相关文档

- [文件管理指南](FILE_MANAGEMENT_GUIDE.md) - 完整的文件管理策略
- [Kiro工作流程](KIRO_WORKFLOW_GUIDE.md) - 与Kiro协作的最佳实践
- [快速清理指南](QUICK_CLEANUP_GUIDE.md) - 项目清理快速参考

## 技术细节

### Hook 脚本位置

- 主脚本: `.githooks/pre-commit` (Shell脚本，兼容Git Bash)
- PowerShell版本: `.githooks/pre-commit.ps1` (备用)

### 检查逻辑

1. 获取暂存区文件列表: `git diff --cached --name-only`
2. 使用模式匹配检查文件名
3. 如果匹配到临时文件模式，返回错误码1（阻止提交）
4. 如果未匹配到，返回错误码0（允许提交）

### 文件模式

```bash
# 临时文件模式
backend/test_*_fix.py
backend/test_*_debug.py
backend/fix_*.py
backend/check_temp_*.py
backend/demo_*.py

# 根目录Python文件（排除setup.py）
*.py (在根目录)
```

## 总结

Git Hooks 是保持项目整洁的第一道防线，它能：

- ✅ 自动检测临时文件
- ✅ 防止误提交
- ✅ 提供处理建议
- ✅ 保持项目结构清晰

配合定期运行清理脚本，可以有效管理项目文件，避免文件堆积。
