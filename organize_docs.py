"""
文档整理脚本
将开发过程中的临时文档归档，保留核心文档
"""

import os
import shutil
from pathlib import Path

# 需要归档的文档（移到 docs/archive/）
ARCHIVE_DOCS = [
    # 开发总结文档
    "DEVICE_ROW_RECOGNITION_FINAL_SUMMARY.md",
    "TASK_12_COMPLETION_SUMMARY.md",
    "TASK_7_FINAL_REPORT.md",
    "TASK_9_FINAL_CHECKPOINT_REPORT.md",
    
    # 测试报告
    "FINAL_ACCEPTANCE_REPORT.md",
    "INTEGRATION_TEST_REPORT.md",
    
    # 设备库扩充文档
    "DEVICE_LIBRARY_EXPANSION_REPORT.md",
    "DEVICE_LIBRARY_EXPANSION_SUMMARY.md",
    
    # 问题修复文档
    "DEVICE_ROW_DETECTION_FIX_REPORT.md",
    "CRITICAL_DEVICE_ROW_DETECTION_ISSUE.md",
    "MATCH_API_FIX_SUMMARY.md",
    
    # 手动调整相关（已整合到 MAINTENANCE.md）
    "MANUAL_ADJUST_DEBUG_SUMMARY.md",
    "MANUAL_ADJUST_TROUBLESHOOTING.md",
    "MANUAL_ADJUST_TROUBLESHOOTING_V2.md",
    "MANUAL_ADJUST_USER_GUIDE.md",
    
    # UI 优化文档
    "UI_OPTIMIZATION_SUMMARY.md",
    "UI_TOOLTIP_FIX_SUMMARY.md",
    
    # 故障排查（已整合到 MAINTENANCE.md）
    "TROUBLESHOOTING_QUICK_REFERENCE.md",
]

# 需要删除的重复文档
DELETE_DOCS = [
    "PROJECT_STATUS.md",  # 内容已整合到 README.md 和 .kiro/PROJECT.md
    "PROJECT_OVERVIEW.md",  # 与 README.md 重复
    "QUICK_START_GUIDE.md",  # 已整合到 README.md
]

# 保留的核心文档
KEEP_DOCS = [
    "README.md",  # 项目入口
    "SETUP.md",  # 安装指南
    "MAINTENANCE.md",  # 维护指南
    "CHANGELOG.md",  # 版本历史（新建）
]

def organize_docs():
    """整理文档"""
    
    print("="*60)
    print("文档整理脚本")
    print("="*60)
    
    # 创建归档目录
    archive_dir = Path("docs/archive")
    archive_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n✅ 创建归档目录: {archive_dir}")
    
    # 归档文档
    print(f"\n📦 归档文档 ({len(ARCHIVE_DOCS)} 个):")
    archived_count = 0
    for doc in ARCHIVE_DOCS:
        if os.path.exists(doc):
            dest = archive_dir / doc
            shutil.move(doc, dest)
            print(f"  ✓ {doc} -> docs/archive/")
            archived_count += 1
        else:
            print(f"  ⚠ {doc} (不存在)")
    
    print(f"\n✅ 已归档 {archived_count} 个文档")
    
    # 删除重复文档
    print(f"\n🗑️  删除重复文档 ({len(DELETE_DOCS)} 个):")
    deleted_count = 0
    for doc in DELETE_DOCS:
        if os.path.exists(doc):
            os.remove(doc)
            print(f"  ✓ 删除 {doc}")
            deleted_count += 1
        else:
            print(f"  ⚠ {doc} (不存在)")
    
    print(f"\n✅ 已删除 {deleted_count} 个重复文档")
    
    # 显示保留的核心文档
    print(f"\n📄 保留的核心文档 ({len(KEEP_DOCS)} 个):")
    for doc in KEEP_DOCS:
        if os.path.exists(doc):
            size = os.path.getsize(doc)
            print(f"  ✓ {doc} ({size:,} bytes)")
        else:
            print(f"  ⚠ {doc} (不存在)")
    
    # 创建归档索引
    create_archive_index(archive_dir)
    
    print("\n" + "="*60)
    print("✅ 文档整理完成！")
    print("="*60)
    print(f"\n核心文档: 根目录")
    print(f"历史文档: docs/archive/")
    print(f"规格文档: .kiro/specs/")
    print(f"后端文档: backend/*.md")

def create_archive_index(archive_dir):
    """创建归档索引"""
    index_content = """# 归档文档索引

本目录包含项目开发过程中的历史文档，这些文档记录了功能开发、问题修复和测试的详细过程。

## 📁 文档分类

### 开发总结
- `DEVICE_ROW_RECOGNITION_FINAL_SUMMARY.md` - 设备行识别功能总结
- `TASK_12_COMPLETION_SUMMARY.md` - 任务12完成总结
- `TASK_7_FINAL_REPORT.md` - 任务7最终报告
- `TASK_9_FINAL_CHECKPOINT_REPORT.md` - 任务9检查点报告

### 测试报告
- `FINAL_ACCEPTANCE_REPORT.md` - 最终验收报告
- `INTEGRATION_TEST_REPORT.md` - 集成测试报告

### 功能扩展
- `DEVICE_LIBRARY_EXPANSION_REPORT.md` - 设备库扩充详细报告
- `DEVICE_LIBRARY_EXPANSION_SUMMARY.md` - 设备库扩充总结

### 问题修复
- `DEVICE_ROW_DETECTION_FIX_REPORT.md` - 设备行检测修复报告
- `CRITICAL_DEVICE_ROW_DETECTION_ISSUE.md` - 关键问题记录
- `MATCH_API_FIX_SUMMARY.md` - 匹配API修复总结

### 手动调整功能
- `MANUAL_ADJUST_DEBUG_SUMMARY.md` - 调试总结
- `MANUAL_ADJUST_TROUBLESHOOTING.md` - 故障排查v1
- `MANUAL_ADJUST_TROUBLESHOOTING_V2.md` - 故障排查v2
- `MANUAL_ADJUST_USER_GUIDE.md` - 用户指南

### UI 优化
- `UI_OPTIMIZATION_SUMMARY.md` - UI优化说明
- `UI_TOOLTIP_FIX_SUMMARY.md` - Tooltip修复说明

### 故障排查
- `TROUBLESHOOTING_QUICK_REFERENCE.md` - 快速参考

## 📝 说明

这些文档已经归档，相关内容已整合到以下核心文档中：

- **README.md** - 项目概述和快速开始
- **MAINTENANCE.md** - 维护指南（包含故障排查）
- **CHANGELOG.md** - 版本变更历史
- **.kiro/PROJECT.md** - 项目详细信息

如需查看历史开发过程，可以参考本目录中的文档。

---

**归档日期**: 2026-02-12  
**维护者**: DDC 系统开发团队
"""
    
    index_file = archive_dir / "README.md"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"\n✅ 创建归档索引: {index_file}")

if __name__ == '__main__':
    # 确认操作
    print("\n⚠️  此操作将:")
    print(f"  1. 归档 {len(ARCHIVE_DOCS)} 个历史文档到 docs/archive/")
    print(f"  2. 删除 {len(DELETE_DOCS)} 个重复文档")
    print(f"  3. 保留 {len(KEEP_DOCS)} 个核心文档")
    
    confirm = input("\n确认执行？(yes/no): ").strip().lower()
    
    if confirm == 'yes':
        organize_docs()
    else:
        print("\n❌ 取消操作")
