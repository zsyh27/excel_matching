# Kiro 工作流程指南

## 如何让Kiro按规则管理文件

### 问题

Kiro本身不会自动将文件放到指定目录，但我们可以通过以下方法来规范文件管理。

## 解决方案

### 方案1：明确告诉Kiro文件应该放在哪里

在请求时明确指定文件位置：

```
❌ 不好的请求：
"创建一个测试脚本来验证配置保存功能"

✅ 好的请求：
"在 backend/tests/ 目录创建一个测试脚本来验证配置保存功能"
```

### 方案2：使用Git Hooks自动检查

我已经创建了Git pre-commit hook，会自动检查：

```bash
# 安装Git Hook
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit

# 现在每次提交时会自动检查临时文件
```

**Hook会检查**：
- ❌ 临时测试文件（test_*_fix.py）
- ❌ 调试脚本（test_*_debug.py）
- ❌ 根目录的Python文件

**如果检测到问题**：
```bash
❌ 警告：检测到临时文件即将被提交：
backend/test_config_fix.py

建议：
  1. 如果已验证完成，请删除这些文件
  2. 如果是诊断工具，请移动到 backend/tools/
  3. 如果确实需要提交，使用 git commit --no-verify
```

### 方案3：定期运行清理脚本

```bash
# 每周运行一次
python scripts/cleanup_project.py --dry-run
python scripts/cleanup_project.py --execute
```

### 方案4：在项目中添加规则文档

创建 `.kiro/steering/file-management.md`：

```markdown
# 文件管理规则

## 创建文件时的规则

### 测试文件
- 正式测试 → `backend/tests/test_*.py`
- 临时测试 → 验证后立即删除

### 工具脚本
- 诊断工具 → `backend/tools/diagnose_*.py`
- 运维脚本 → `backend/scripts/*.py`

### 文档
- 用户文档 → `docs/user/*.md`
- 开发文档 → `docs/development/*.md`
- 维护文档 → `docs/maintenance/*.md`

## 命名规范

### 避免的命名
- `test_*_fix.py` - 表明是临时文件
- `test_*_debug.py` - 表明是调试文件
- `*_SUMMARY.md` - 表明是临时文档

### 推荐的命名
- `test_feature.py` - 正式测试
- `diagnose_issue.py` - 诊断工具
- `FEATURE_GUIDE.md` - 功能指南
```

## 与Kiro协作的最佳实践

### 1. 明确指定文件位置

```
用户: "创建一个诊断工具来检查数据库连接"

Kiro: 我会创建 backend/tools/diagnose_db_connection.py
```

### 2. 验证后立即清理

```
用户: "创建一个测试脚本验证修复是否有效"

Kiro: 我会创建 backend/test_fix_verification.py
      验证完成后请删除此文件
```

### 3. 更新现有文档而不是创建新文档

```
❌ 不好的做法：
用户: "创建一个文档说明配置管理功能"
Kiro: 创建 docs/CONFIG_MANAGEMENT_SUMMARY.md

✅ 好的做法：
用户: "更新 docs/user/CONFIG_MANAGEMENT.md 添加新功能说明"
Kiro: 更新现有文档
```

### 4. 使用清理脚本

```
用户: "清理项目中的临时文件"

Kiro: 运行 python scripts/cleanup_project.py --dry-run
      显示将要清理的文件列表
```

## 根目录文件整理

### 当前根目录文件

```
.
├── create_example_excel.py      → 应移动到 scripts/
├── generate_rules.py             → 应移动到 scripts/
├── validate_task12.py            → 应移动到 scripts/
├── organize_docs.py              → 应移动到 scripts/
├── QUICK_START.md                → 应移动到 docs/
├── SETUP.md                      → 应移动到 docs/
├── TESTING_GUIDE.md              → 应移动到 docs/
├── MAINTENANCE.md                → 应移动到 docs/
├── SYSTEM_STATUS.md              → 应移动到 docs/
├── VERIFICATION_CHECKLIST.md     → 应移动到 docs/
├── MATCHING_OPTIMIZATION_SUMMARY.md → 应移动到 docs/
├── organization_config.json      → 需要审查
├── README.md                     → 保留
└── CHANGELOG.md                  → 保留
```

### 自动整理

```bash
# 预览将要移动的文件
python scripts/cleanup_project.py --dry-run

# 执行整理
python scripts/cleanup_project.py --execute
```

### 整理后的结构

```
.
├── README.md                     # 项目概述
├── CHANGELOG.md                  # 变更日志
├── .gitignore                    # Git忽略规则
│
├── docs/                         # 所有文档
│   ├── QUICK_START.md
│   ├── SETUP.md
│   ├── TESTING_GUIDE.md
│   ├── MAINTENANCE.md
│   └── ...
│
├── scripts/                      # 所有脚本
│   ├── create_example_excel.py
│   ├── generate_rules.py
│   ├── validate_task12.py
│   └── ...
│
├── backend/
│   ├── modules/                  # 核心模块
│   ├── tests/                    # 正式测试
│   ├── tools/                    # 诊断工具
│   └── scripts/                  # 运维脚本
│
└── frontend/
```

## 文件分类决策树

```
创建新文件时，问自己：

1. 这是什么类型的文件？
   ├─ Python脚本
   │  ├─ 是测试吗？
   │  │  ├─ 是正式测试 → backend/tests/
   │  │  └─ 是临时测试 → 验证后删除
   │  ├─ 是诊断工具吗？ → backend/tools/
   │  ├─ 是运维脚本吗？ → backend/scripts/
   │  └─ 是项目脚本吗？ → scripts/
   │
   └─ Markdown文档
      ├─ 是用户文档吗？ → docs/user/
      ├─ 是开发文档吗？ → docs/development/
      ├─ 是维护文档吗？ → docs/maintenance/
      └─ 是临时文档吗？ → 合并到现有文档

2. 这个文件会长期使用吗？
   ├─ 是 → 放到合适的目录
   └─ 否 → 验证后删除

3. 已经有类似的文件了吗？
   ├─ 是 → 更新现有文件
   └─ 否 → 创建新文件
```

## 与Kiro沟通的模板

### 创建测试

```
❌ 模糊的请求：
"创建一个测试"

✅ 清晰的请求：
"在 backend/tests/ 创建 test_config_validation.py 测试配置验证功能"
```

### 创建工具

```
❌ 模糊的请求：
"创建一个诊断脚本"

✅ 清晰的请求：
"在 backend/tools/ 创建 diagnose_matching_issue.py 诊断匹配问题"
```

### 创建文档

```
❌ 模糊的请求：
"写一个文档说明这个功能"

✅ 清晰的请求：
"更新 docs/user/DEVICE_MANAGEMENT.md 添加批量导入功能的说明"
```

### 临时验证

```
✅ 明确说明是临时的：
"创建一个临时测试脚本 backend/test_pagination_verify.py 验证分页功能，
验证完成后我会删除它"
```

## 自动化检查清单

### 提交代码前

```bash
# 1. 检查是否有临时文件
git status | grep "test_.*_fix.py"
git status | grep "test_.*_debug.py"

# 2. 运行清理脚本
python scripts/cleanup_project.py --dry-run

# 3. 提交代码（会自动运行Git Hook检查）
git add .
git commit -m "..."
```

### 每周维护

```bash
# 1. 清理临时文件
python scripts/cleanup_project.py --execute

# 2. 整理文档
python scripts/organize_docs.py --analyze

# 3. 检查根目录
ls -la | grep "\.py$"
ls -la | grep "\.md$"
```

### 每月维护

```bash
# 1. 全面清理
python scripts/cleanup_project.py --execute

# 2. 整理文档
python scripts/organize_docs.py --execute

# 3. 更新文档索引
# 4. 归档过时文档
```

## 常见问题

### Q: Kiro能自动把文件放到正确的目录吗？

A: Kiro本身不会自动分类，但你可以：
1. 在请求时明确指定目录
2. 使用Git Hook自动检查
3. 定期运行清理脚本

### Q: 如何防止临时文件被提交？

A: 
1. 安装Git Hook：`git config core.hooksPath .githooks`
2. 更新 `.gitignore` 忽略临时文件模式
3. 提交前运行清理脚本

### Q: 根目录的文件应该怎么处理？

A: 
1. 运行 `python scripts/cleanup_project.py --dry-run` 查看建议
2. 只保留必要的文件（README.md, CHANGELOG.md等）
3. 其他文件移动到 docs/ 或 scripts/

### Q: 如何让团队成员也遵守规则？

A: 
1. 在项目README中说明文件管理规则
2. 配置Git Hook（团队共享）
3. 在代码审查时检查文件位置
4. 定期运行清理脚本

## 总结

### 三个关键原则

1. **明确指定** - 告诉Kiro文件应该放在哪里
2. **及时清理** - 临时文件验证后立即删除
3. **定期维护** - 每周运行清理脚本

### 推荐工作流

```
1. 创建文件时 → 明确指定目录
2. 验证完成后 → 立即删除临时文件
3. 提交代码前 → Git Hook自动检查
4. 每周维护 → 运行清理脚本
5. 每月整理 → 全面清理和归档
```

### 记住

**好的项目管理不是依赖工具自动化，而是建立良好的习惯和流程！**
