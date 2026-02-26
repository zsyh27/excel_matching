# 更新日志

本文档记录 DDC 设备清单匹配报价系统的所有重要变更。

---

## [2.0.0] - 2026-02-12

### 新增功能 🎉
- **数据库支持**: 新增 SQLite 和 MySQL 数据库支持
- **真实设备数据**: 导入 719 个真实设备数据
- **数据库管理工具**: 提供完整的数据导入、迁移和管理工具
- **自动回退机制**: 数据库不可用时自动切换到 JSON 模式

### 核心组件
- `backend/modules/database.py` - 数据库管理器
- `backend/modules/database_loader.py` - 数据库加载器
- `backend/modules/models.py` - ORM 数据模型
- `backend/init_database.py` - 数据库初始化脚本
- `backend/migrate_json_to_db.py` - 数据迁移脚本
- `backend/import_devices_from_excel.py` - Excel 设备导入
- `backend/generate_rules_for_devices.py` - 规则自动生成

### 改进
- 重构 DataLoader 支持双模式（数据库/JSON）
- 清理数据库中的模拟数据（删除 59 个 JSON 设备）
- 清理孤立规则（删除 84 条规则）
- 更新所有项目文档

### 文档
- 新增 `backend/DATABASE_SETUP.md` - 数据库设置指南
- 更新 `README.md` - 添加数据库相关说明
- 更新 `MAINTENANCE.md` - 添加数据库维护部分

---

## [1.2.2] - 2026-02-08

### 修复 🔧
- **手动调整功能 400 错误排查**
  - 修复测试脚本中的 API 路径错误
  - 添加详细的后端调试日志
  - 创建完整的故障排查指南

### 文档
- `MANUAL_ADJUST_TROUBLESHOOTING_V2.md` - 故障排查指南
- `MANUAL_ADJUST_USER_GUIDE.md` - 用户操作指南

---

## [1.2.1] - 2026-02-08

### 改进 ✨
- **UI 优化**: 设备行内容显示优化
  - 行内容限制在 150 字符以内
  - 使用自定义 Tooltip 显示完整内容
  - 短内容不显示 Tooltip，提升性能

### 文档
- `UI_OPTIMIZATION_SUMMARY.md` - UI 优化说明
- `UI_TOOLTIP_FIX_SUMMARY.md` - Tooltip 修复说明

---

## [1.2.0] - 2026-02-08

### 新增功能 🎉
- **扩充设备库**: 从 25 个设备增加到 59 个设备
  - 新增 34 个能源管理系统设备
  - 支持能耗数据采集器、多联机采集器、服务器、软件系统等
  - 真实 Excel 文件匹配率从 0% 提升到 90%

### 改进
- 自动化工具：提供设备提取和合并脚本
- 规则优化：自动生成 34 条新匹配规则

### 文档
- `DEVICE_LIBRARY_EXPANSION_REPORT.md` - 设备库扩充详细报告

---

## [1.1.0] - 2026-02

### 新增功能 🎉
- **设备行智能识别功能**
  - 三维度加权评分模型（数据类型 30% + 结构关联 35% + 行业特征 35%）
  - 自动识别准确率 98.04%
  - 手动调整功能（单行 + 批量）
  - 多维度筛选功能
  - 5 种颜色编码视觉反馈

### 核心组件
- `backend/modules/device_row_classifier.py` - 设备行分类器
- `frontend/src/components/DeviceRowAdjustment.vue` - 设备行调整组件
- `frontend/src/views/DeviceRowAdjustmentView.vue` - 调整页面

### 测试
- 76 个单元测试全部通过
- 端到端测试验证

### 文档
- `DEVICE_ROW_RECOGNITION_FINAL_SUMMARY.md` - 功能完整总结
- `TASK_9_FINAL_CHECKPOINT_REPORT.md` - 最终检查点报告

---

## [1.0.0] - 2024-02

### 新增功能 🎉
- **核心功能开发完成**
  - Excel 多格式支持（xls/xlsm/xlsx）
  - 智能匹配算法（基于权重的特征匹配）
  - 格式保留导出
  - 完整的测试套件

### 核心组件
- `backend/modules/excel_parser.py` - Excel 解析
- `backend/modules/text_preprocessor.py` - 文本预处理
- `backend/modules/match_engine.py` - 匹配引擎
- `backend/modules/excel_exporter.py` - Excel 导出
- `backend/modules/data_loader.py` - 数据加载

### 性能指标
- 匹配准确率: 91.30%
- 解析性能: 1000 行 ≤5 秒
- 匹配性能: 1000 个设备 ≤10 秒

### 文档
- 提供示例数据和完整文档
- 创建 README.md、SETUP.md、MAINTENANCE.md

---

## 版本说明

- **主版本号**: 重大功能变更或架构调整
- **次版本号**: 新功能添加
- **修订号**: Bug 修复和小改进

---

**维护者**: DDC 系统开发团队  
**最后更新**: 2026-02-12
