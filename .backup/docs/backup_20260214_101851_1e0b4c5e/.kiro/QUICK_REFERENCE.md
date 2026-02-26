# Kiro 快速参考 - DDC 设备清单匹配报价系统

**用途**: 帮助 Kiro 快速了解项目状态和上下文

---

## 🎯 项目核心信息

**项目名称**: DDC 设备清单匹配报价系统  
**版本**: v2.0.0  
**状态**: 生产就绪 ✅  
**最后更新**: 2026-02-12

**核心功能**:
1. 设备行智能识别（98.04% 准确率）
2. 设备智能匹配（91.30% 准确率）
3. 数据库存储管理（719 个真实设备）

---

## 📁 三大功能模块（全部完成）

### 1. database-migration ✅
- **位置**: `.kiro/specs/database-migration/`
- **状态**: 14/14 任务完成
- **功能**: SQLite/MySQL 数据库支持，719个真实设备
- **关键文件**: 
  - `backend/modules/database.py`
  - `backend/modules/database_loader.py`
  - `backend/modules/models.py`

### 2. ddc-device-matching ✅
- **位置**: `.kiro/specs/ddc-device-matching/`
- **状态**: 13/13 任务完成
- **功能**: 基于权重的特征匹配，91.30% 准确率
- **关键文件**:
  - `backend/modules/match_engine.py`
  - `backend/modules/excel_parser.py`
  - `backend/modules/text_preprocessor.py`

### 3. device-row-intelligent-recognition ✅
- **位置**: `.kiro/specs/device-row-intelligent-recognition/`
- **状态**: 9/9 任务完成
- **功能**: 三维度评分模型，98.04% 准确率
- **关键文件**:
  - `backend/modules/device_row_classifier.py`
  - `frontend/src/components/DeviceRowAdjustment.vue`

---

## 🗄️ 当前数据状态

**存储模式**: 数据库模式（SQLite）  
**配置文件**: `backend/config.py`
```python
STORAGE_MODE = 'database'  # 当前使用数据库
DATABASE_TYPE = 'sqlite'
DATABASE_URL = 'sqlite:///data/devices.db'
```

**数据统计**:
- 设备: 719 个（真实数据，已清理59个JSON模拟数据）
- 规则: 719 条（已清理84条孤立规则）
- 配置: 10 项

**数据来源**: `data/真实设备价格例子.xlsx`

---

## 🚀 快速启动命令

```bash
# 后端
cd backend
python app.py

# 前端
cd frontend
npm run dev
```

**访问**: http://localhost:5173

---

## 📝 重要文档位置

### 项目概览
- `PROJECT_STATUS.md` - 完整项目状态（最重要）
- `.kiro/PROJECT.md` - 项目概述
- `README.md` - 用户文档

### 规格文档（Specs）
- `.kiro/specs/database-migration/` - 数据库迁移
- `.kiro/specs/ddc-device-matching/` - 设备匹配
- `.kiro/specs/device-row-intelligent-recognition/` - 设备行识别

### 维护文档
- `MAINTENANCE.md` - 数据维护指南（包含数据库部分）
- `backend/DATABASE_SETUP.md` - 数据库设置详细指南
- `TROUBLESHOOTING_QUICK_REFERENCE.md` - 故障排查

---

## 🔧 常用管理命令

### 数据库管理
```bash
# 查看数据
sqlite3 data/devices.db "SELECT COUNT(*) FROM devices;"

# 导入设备
python import_devices_from_excel.py --file devices.xlsx

# 生成规则
python generate_rules_for_devices.py

# 清理数据
python remove_json_devices_from_db.py
python cleanup_orphan_rules.py
```

### 测试
```bash
# 运行所有测试
cd backend
pytest tests/ -v

# 测试 API
python test_api_devices.py
```

---

## 🎨 系统架构简图

```
前端 (Vue 3)
    ↓ HTTP API
后端 (Flask)
    ↓
DataLoader (统一接口)
    ↓
DatabaseLoader (当前) / JSONLoader (备用)
    ↓
SQLite 数据库 (719设备+719规则)
```

---

## ⚠️ 重要注意事项

1. **当前使用数据库模式**，不再使用 JSON 文件中的模拟数据
2. **JSON 文件仅作为备用**，包含 59 个示例设备
3. **数据库包含 719 个真实设备**，来自 `data/真实设备价格例子.xlsx`
4. **所有三个功能模块已完成**，系统处于生产就绪状态
5. **测试覆盖**: 76 个单元测试全部通过

---

## 📊 性能指标

- 设备行识别准确率: 98.04% (自动) / 100% (手动调整后)
- 设备匹配准确率: 91.30%
- 解析性能: 1000行 ≤5秒
- 匹配性能: 1000个设备 ≤10秒
- 识别性能: 100行 ≤2秒

---

## 🔄 最近的重要更改

**2026-02-12**:
- ✅ 完成任务14：更新项目文档
- ✅ 清理数据库中的 JSON 模拟数据（删除59个设备）
- ✅ 清理孤立规则（删除84条规则）
- ✅ 更新 README.md、MAINTENANCE.md、PROJECT.md
- ✅ 创建 PROJECT_STATUS.md 完整状态文档
- ✅ 系统现在只使用 719 个真实设备数据

---

## 💡 Kiro 使用提示

当用户询问项目相关问题时：

1. **项目状态** → 参考 `PROJECT_STATUS.md`
2. **功能实现** → 查看对应的 `.kiro/specs/` 目录
3. **数据库问题** → 参考 `backend/DATABASE_SETUP.md` 和 `MAINTENANCE.md`
4. **代码位置** → 参考本文档的"关键文件"部分
5. **任务进度** → 查看各 spec 的 `tasks.md` 文件

**所有三个功能模块都已完成，系统可以正常使用！**

---

**文档版本**: 1.0  
**创建日期**: 2026-02-12  
**用途**: Kiro AI 助手快速参考
