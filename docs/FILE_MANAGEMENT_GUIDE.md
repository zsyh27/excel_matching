# 项目文件管理指南

## 问题描述

随着项目迭代，产生了大量临时文件：
- 临时测试脚本（test_*.py, check_*.py, diagnose_*.py等）
- 修复验证脚本（fix_*.py, verify_*.py）
- 重复的文档（多个SUMMARY.md, FIX.md）
- 过时的文档和代码

这导致：
- 项目结构混乱
- 难以找到有用的文件
- 维护成本增加
- 新人难以理解项目

## 文件分类策略

### 1. 临时文件（应该删除）

**特征**：
- 一次性验证脚本
- 已完成功能的测试脚本
- 重复的文档

**命名模式**：
- `test_*_fix.py` - 修复验证脚本
- `test_*_debug.py` - 调试脚本
- `check_*.py` - 一次性检查脚本
- `*_SUMMARY.md` - 临时总结文档
- `*_FIX.md` - 修复说明文档

**处理方式**：
- 验证完成后立即删除
- 或移动到 `.archive/` 目录

### 2. 诊断工具（应该保留）

**特征**：
- 可重复使用的诊断工具
- 帮助排查问题的脚本
- 数据验证工具

**命名模式**：
- `diagnose_*.py` - 诊断工具
- `verify_*.py` - 验证工具（可重用）
- `check_*.py` - 检查工具（可重用）

**存放位置**：
- `backend/tools/` - 后端诊断工具
- `frontend/tools/` - 前端诊断工具

### 3. 正式测试（应该保留）

**特征**：
- 单元测试
- 集成测试
- E2E测试

**存放位置**：
- `backend/tests/` - 后端测试
- `frontend/src/**/__tests__/` - 前端测试

### 4. 文档（需要整理）

**分类**：
- **用户文档**：用户手册、使用指南
- **开发文档**：API文档、架构设计
- **维护文档**：故障排查、运维指南
- **历史文档**：已过时的文档

**存放位置**：
- `docs/user/` - 用户文档
- `docs/development/` - 开发文档
- `docs/maintenance/` - 维护文档
- `docs/archive/` - 历史文档

## 推荐的目录结构

```
project/
├── backend/
│   ├── modules/          # 核心模块
│   ├── tests/            # 正式测试
│   ├── tools/            # 诊断工具（保留）
│   │   ├── diagnose_*.py
│   │   ├── verify_*.py
│   │   └── README.md
│   ├── scripts/          # 运维脚本
│   │   ├── init_database.py
│   │   ├── migrate_*.py
│   │   └── README.md
│   └── app.py
│
├── frontend/
│   ├── src/
│   │   └── **/__tests__/  # 正式测试
│   └── tools/             # 前端工具
│
├── docs/
│   ├── user/              # 用户文档
│   │   ├── README.md
│   │   ├── QUICK_START.md
│   │   └── USER_GUIDE.md
│   ├── development/       # 开发文档
│   │   ├── API.md
│   │   ├── ARCHITECTURE.md
│   │   └── CONTRIBUTING.md
│   ├── maintenance/       # 维护文档
│   │   ├── TROUBLESHOOTING.md
│   │   ├── DEPLOYMENT.md
│   │   └── MONITORING.md
│   └── archive/           # 历史文档
│       └── YYYY-MM/       # 按月归档
│
└── .archive/              # 临时文件归档
    └── YYYY-MM-DD/        # 按日期归档
```

## 文件清理规则

### 规则1：立即删除

完成验证后立即删除：
- `test_*_fix.py`
- `test_*_debug.py`
- `fix_*.py`
- 一次性检查脚本

### 规则2：定期清理

每月清理一次：
- 超过30天未使用的临时文件
- 重复的文档
- 过时的文档

### 规则3：归档保存

移动到 `.archive/` 而不是删除：
- 可能需要参考的历史文档
- 重要的修复记录
- 性能测试结果

## 文档管理规则

### 规则1：避免重复

同一主题只保留一份文档：
- ❌ `CONFIG_MANAGEMENT_SUMMARY.md`
- ❌ `CONFIG_MANAGEMENT_COMPLETION_SUMMARY.md`
- ❌ `CONFIG_MANAGEMENT_FINAL_IMPLEMENTATION.md`
- ✅ `CONFIG_MANAGEMENT.md` （合并为一份）

### 规则2：文档合并

将多个小文档合并为一份完整文档：
- 修复文档 → 合并到主文档的"故障排查"章节
- 实现文档 → 合并到主文档的"实现细节"章节
- 测试文档 → 合并到主文档的"测试"章节

### 规则3：文档分层

- **README.md** - 概述和快速开始
- **USER_GUIDE.md** - 详细使用指南
- **API.md** - API参考文档
- **TROUBLESHOOTING.md** - 故障排查

### 规则4：文档更新

- 功能完成后，更新主文档
- 删除临时的修复/实现文档
- 保持文档与代码同步

## 实施步骤

### 第一步：创建新目录结构

```bash
# 创建工具目录
mkdir -p backend/tools
mkdir -p backend/scripts
mkdir -p frontend/tools

# 创建文档目录
mkdir -p docs/user
mkdir -p docs/development
mkdir -p docs/maintenance
mkdir -p docs/archive

# 创建归档目录
mkdir -p .archive
```

### 第二步：移动文件

```bash
# 移动诊断工具
mv backend/diagnose_*.py backend/tools/
mv backend/verify_*.py backend/tools/

# 移动运维脚本
mv backend/init_database.py backend/scripts/
mv backend/migrate_*.py backend/scripts/
mv backend/sync_*.py backend/scripts/

# 移动文档
mv docs/*_USER_GUIDE.md docs/user/
mv docs/*_API.md docs/development/
mv docs/*_TROUBLESHOOTING.md docs/maintenance/
```

### 第三步：删除临时文件

```bash
# 删除临时测试脚本
rm backend/test_*_fix.py
rm backend/test_*_debug.py
rm backend/fix_*.py

# 删除重复文档
# （需要手动审查后删除）
```

### 第四步：合并文档

将多个相关文档合并为一份：
- 配置管理相关文档 → `docs/user/CONFIG_MANAGEMENT.md`
- 设备管理相关文档 → `docs/user/DEVICE_MANAGEMENT.md`
- 规则管理相关文档 → `docs/user/RULE_MANAGEMENT.md`

### 第五步：创建索引

在每个目录创建 `README.md` 索引文件。

## 自动化清理脚本

创建一个清理脚本 `scripts/cleanup.py`：

```python
#!/usr/bin/env python3
"""
项目文件清理脚本
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# 配置
TEMP_FILE_PATTERNS = [
    'test_*_fix.py',
    'test_*_debug.py',
    'fix_*.py',
    'check_temp_*.py',
]

ARCHIVE_DIR = '.archive'
DAYS_TO_KEEP = 30

def should_delete(filepath):
    """判断文件是否应该删除"""
    filename = os.path.basename(filepath)
    
    # 检查文件名模式
    for pattern in TEMP_FILE_PATTERNS:
        if filename.startswith(pattern.replace('*', '')):
            return True
    
    return False

def archive_file(filepath):
    """归档文件"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    archive_path = os.path.join(ARCHIVE_DIR, date_str)
    os.makedirs(archive_path, exist_ok=True)
    
    filename = os.path.basename(filepath)
    dest = os.path.join(archive_path, filename)
    shutil.move(filepath, dest)
    print(f"归档: {filepath} -> {dest}")

def cleanup_backend():
    """清理backend目录"""
    backend_dir = 'backend'
    
    for filename in os.listdir(backend_dir):
        filepath = os.path.join(backend_dir, filename)
        
        if os.path.isfile(filepath) and should_delete(filepath):
            archive_file(filepath)

def main():
    print("开始清理项目文件...")
    cleanup_backend()
    print("清理完成！")

if __name__ == '__main__':
    main()
```

## 维护建议

### 每次修改后

1. 验证完成后立即删除临时测试脚本
2. 更新主文档而不是创建新文档
3. 提交代码前检查是否有临时文件

### 每周

1. 检查是否有未删除的临时文件
2. 整理文档结构

### 每月

1. 运行清理脚本
2. 归档过时文档
3. 更新文档索引

## Git 忽略规则

更新 `.gitignore`：

```gitignore
# 临时测试文件
backend/test_*_fix.py
backend/test_*_debug.py
backend/fix_*.py
backend/check_temp_*.py

# 临时文档
docs/*_TEMP.md
docs/*_DRAFT.md

# 归档目录
.archive/
```

## 最佳实践

### ✅ 推荐做法

1. **一次性脚本**：验证后立即删除
2. **可重用工具**：移动到 `tools/` 目录
3. **文档更新**：更新现有文档而不是创建新文档
4. **命名规范**：使用清晰的命名表明文件用途
5. **定期清理**：每月清理一次

### ❌ 避免做法

1. 不要保留已完成功能的临时测试脚本
2. 不要创建重复的文档
3. 不要在根目录堆积临时文件
4. 不要保留过时的文档
5. 不要使用模糊的文件名

## 文档模板

### 用户文档模板

```markdown
# 功能名称

## 概述
简要说明功能用途

## 快速开始
最简单的使用方式

## 详细说明
详细的使用说明

## 常见问题
FAQ

## 故障排查
常见问题的解决方法
```

### 开发文档模板

```markdown
# 模块名称

## 架构设计
模块的设计思路

## API参考
API接口说明

## 实现细节
关键实现说明

## 测试
测试策略和方法
```

## 总结

通过以上文件管理策略，可以：
- ✅ 保持项目结构清晰
- ✅ 快速找到需要的文件
- ✅ 降低维护成本
- ✅ 提高团队协作效率
- ✅ 方便新人理解项目

记住：**好的项目不是文件越多越好，而是结构越清晰越好**。
