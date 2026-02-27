# 快速清理指南

## 问题

项目中积累了太多临时文件和文档，导致混乱。

## 快速解决方案

### 方案1：使用自动化脚本（推荐）

```bash
# 1. 预览将要清理的文件
python scripts/cleanup_project.py --dry-run

# 2. 确认无误后执行清理
python scripts/cleanup_project.py --execute

# 3. 分析文档结构
python scripts/organize_docs.py --analyze

# 4. 生成文档索引
python scripts/organize_docs.py --execute
```

### 方案2：手动清理

#### 第一步：删除临时测试文件

```bash
# 进入backend目录
cd backend

# 删除修复验证脚本
rm test_*_fix.py
rm test_*_debug.py
rm fix_*.py

# 删除临时检查脚本
rm check_temp_*.py
rm check_db_*.py

# 删除演示脚本
rm demo_*.py
```

#### 第二步：整理诊断工具

```bash
# 创建tools目录
mkdir -p backend/tools

# 移动诊断工具
mv diagnose_*.py backend/tools/
mv verify_*.py backend/tools/
```

#### 第三步：整理运维脚本

```bash
# 创建scripts目录
mkdir -p backend/scripts

# 移动运维脚本
mv init_*.py backend/scripts/
mv migrate_*.py backend/scripts/
mv sync_*.py backend/scripts/
mv regenerate_*.py backend/scripts/
```

#### 第四步：整理文档

```bash
# 创建文档目录
mkdir -p docs/user
mkdir -p docs/development
mkdir -p docs/maintenance
mkdir -p docs/archive

# 移动用户文档
mv docs/*_USER_GUIDE.md docs/user/
mv docs/*_MANUAL.md docs/user/

# 移动开发文档
mv docs/*_API.md docs/development/
mv docs/*_DESIGN.md docs/development/

# 移动维护文档
mv docs/*_TROUBLESHOOTING.md docs/maintenance/
mv docs/*_FIX.md docs/maintenance/

# 归档历史文档
mv docs/*_SUMMARY.md docs/archive/
mv docs/*_COMPLETION.md docs/archive/
```

## 清理规则

### 立即删除

完成验证后立即删除这些文件：

- ❌ `test_*_fix.py` - 修复验证脚本
- ❌ `test_*_debug.py` - 调试脚本
- ❌ `fix_*.py` - 一次性修复脚本
- ❌ `check_temp_*.py` - 临时检查脚本

### 保留并整理

这些文件应该保留但需要整理：

- ✅ `diagnose_*.py` → 移动到 `backend/tools/`
- ✅ `verify_*.py` → 移动到 `backend/tools/`
- ✅ `init_*.py` → 移动到 `backend/scripts/`
- ✅ `migrate_*.py` → 移动到 `backend/scripts/`

### 文档合并

将多个相关文档合并为一份：

**配置管理文档** → `docs/user/CONFIG_MANAGEMENT.md`
- ❌ CONFIG_MANAGEMENT_SUMMARY.md
- ❌ CONFIG_MANAGEMENT_COMPLETION_SUMMARY.md
- ❌ CONFIG_MANAGEMENT_FINAL_IMPLEMENTATION.md
- ❌ CONFIG_MANAGEMENT_IMPLEMENTATION_SUMMARY.md
- ✅ 合并为一份完整文档

**设备管理文档** → `docs/user/DEVICE_MANAGEMENT.md`
- ❌ DEVICE_PAGINATION_FIX.md
- ❌ DEVICE_CRUD_API_FIX.md
- ❌ DEVICE_MANAGEMENT_COMPLETE_FIX.md
- ✅ 合并为一份完整文档

## 维护建议

### 每次修改后

1. ✅ 验证完成后立即删除临时测试脚本
2. ✅ 更新现有文档而不是创建新文档
3. ✅ 提交代码前检查是否有临时文件

### 每周

1. ✅ 检查是否有未删除的临时文件
2. ✅ 整理文档结构

### 每月

1. ✅ 运行清理脚本
2. ✅ 归档过时文档
3. ✅ 更新文档索引

## 文件命名规范

### 推荐命名

- ✅ `test_feature.py` - 正式测试
- ✅ `diagnose_issue.py` - 诊断工具
- ✅ `FEATURE_GUIDE.md` - 功能指南

### 避免命名

- ❌ `test_feature_fix.py` - 表明是临时文件
- ❌ `test_feature_debug.py` - 表明是调试文件
- ❌ `FEATURE_FIX_SUMMARY.md` - 表明是临时文档

## 目录结构

### 推荐结构

```
project/
├── backend/
│   ├── modules/          # 核心模块
│   ├── tests/            # 正式测试
│   ├── tools/            # 诊断工具
│   ├── scripts/          # 运维脚本
│   └── app.py
│
├── docs/
│   ├── user/             # 用户文档
│   ├── development/      # 开发文档
│   ├── maintenance/      # 维护文档
│   ├── archive/          # 历史文档
│   └── README.md
│
└── scripts/              # 项目脚本
    ├── cleanup_project.py
    └── organize_docs.py
```

## 常见问题

### Q: 如何判断文件是否应该删除？

A: 问自己三个问题：
1. 这个文件是一次性使用的吗？
2. 功能已经验证完成了吗？
3. 有没有更好的替代方案？

如果三个问题都是"是"，那就可以删除。

### Q: 删除文件会不会影响功能？

A: 不会。我们只删除临时测试和验证脚本，不删除：
- 核心代码（modules/）
- 正式测试（tests/）
- 运维脚本（scripts/）

### Q: 如果误删了重要文件怎么办？

A: 
1. 使用 Git 恢复：`git checkout -- <file>`
2. 从归档目录恢复：`.archive/`
3. 从备份恢复

### Q: 多久清理一次？

A: 建议：
- 每次修改后：立即删除临时文件
- 每周：检查一次
- 每月：运行清理脚本

## 检查清单

清理前检查：

- [ ] 已经运行预览模式查看将要删除的文件
- [ ] 确认没有重要文件会被删除
- [ ] 已经提交了所有重要更改到Git
- [ ] 已经备份了重要文件

清理后检查：

- [ ] 项目仍然可以正常运行
- [ ] 测试仍然可以通过
- [ ] 文档结构更清晰了
- [ ] 找文件更容易了

## 总结

记住三个原则：

1. **及时清理** - 不要等到文件堆积如山
2. **分类整理** - 不同类型的文件放在不同目录
3. **定期维护** - 每月运行一次清理脚本

好的项目不是文件越多越好，而是结构越清晰越好！
