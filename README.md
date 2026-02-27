# DDC 设备清单匹配报价系统

> 智能化的 DDC 自控设备清单报价解决方案

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/vue-3.x-brightgreen.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

## 📖 项目简介

DDC 设备清单匹配报价系统是一个轻量化的 Web 应用，专为 DDC 自控领域的设备清单报价流程设计。系统通过**设备行智能识别**和**智能匹配算法**，自动识别 Excel 设备清单中的设备行并匹配设备信息，生成标准化的报价单，大幅提升报价效率和准确性。

### ✨ 核心特性

- 🎯 **智能识别设备行**: 三维度加权评分模型，自动识别准确率 98.04%
- 🤖 **智能匹配设备**: 基于特征权重的匹配算法，准确率 91.30%
- 📊 **多格式支持**: 支持 xls、xlsm、xlsx 三种 Excel 格式
- ✏️ **手动调整功能**: 支持单行和批量调整，确保 100% 准确率
- 💾 **数据库支持**: SQLite/MySQL 双模式，支持 720+ 真实设备数据
- 🎨 **格式保留**: 导出时完整保留原 Excel 文件的格式和结构
- ⚙️ **配置驱动**: 所有归一化规则和匹配参数可配置
- 🔧 **规则管理**: 可视化规则编辑和优化界面

### 📊 性能指标

- ✅ 设备行识别准确率: 98.04% (自动) / 100% (手动调整后)
- ✅ 设备匹配准确率: 91.30%
- ✅ 解析性能: 1000 行 ≤5 秒
- ✅ 匹配性能: 1000 个设备 ≤10 秒
- ✅ 测试覆盖: 76 个单元测试全部通过

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 14+
- npm 或 yarn

### 5分钟快速启动

```bash
# 1. 克隆项目
git clone <repository-url>
cd excel_matching

# 2. 启动后端
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
python app.py

# 3. 启动前端（新终端）
cd frontend
npm install
npm run dev

# 4. 访问应用
# 浏览器打开 http://localhost:5173
```

### 数据库初始化（可选）

```bash
cd backend

# 创建数据库
python scripts/init_database.py

# 导入真实设备数据（720+条）
python scripts/import_devices_from_excel.py

# 生成匹配规则
python scripts/generate_rules_for_devices.py
```

详细安装说明请参考 [docs/SETUP.md](docs/SETUP.md)

---

## 📁 项目结构

```
excel_matching/
├── README.md                   # 项目说明（本文件）
├── CHANGELOG.md                # 版本历史
├── .gitignore                  # Git 忽略规则
│
├── backend/                    # 后端服务
│   ├── app.py                 # Flask 应用入口
│   ├── config.py              # 配置管理
│   ├── requirements.txt       # Python 依赖
│   │
│   ├── modules/               # 核心业务模块
│   │   ├── device_row_classifier.py  # 设备行分类器
│   │   ├── excel_parser.py           # Excel 解析
│   │   ├── text_preprocessor.py      # 文本预处理
│   │   ├── match_engine.py           # 匹配引擎
│   │   ├── excel_exporter.py         # Excel 导出
│   │   ├── data_loader.py            # 数据加载（支持数据库/JSON）
│   │   ├── database.py               # 数据库管理
│   │   ├── database_loader.py        # 数据库加载器
│   │   └── models.py                 # ORM 数据模型
│   │
│   ├── tests/                 # 单元测试（76个测试）
│   ├── tools/                 # 诊断工具
│   │   ├── diagnose_*.py     # 问题诊断脚本
│   │   └── verify_*.py       # 验证脚本
│   │
│   └── scripts/               # 运维脚本
│       ├── init_database.py           # 数据库初始化
│       ├── import_devices_from_excel.py  # 设备导入
│       └── regenerate_all_rules.py    # 规则重新生成
│
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/       # Vue 组件
│   │   │   ├── FileUpload.vue
│   │   │   ├── ResultTable.vue
│   │   │   ├── ExportButton.vue
│   │   │   ├── DeviceRowAdjustment.vue
│   │   │   └── ConfigManagement/     # 配置管理组件
│   │   │
│   │   ├── views/            # 页面视图
│   │   │   ├── FileUploadView.vue
│   │   │   ├── DeviceRowAdjustmentView.vue
│   │   │   ├── MatchingView.vue
│   │   │   └── ConfigManagementView.vue
│   │   │
│   │   └── api/              # API 接口封装
│   │
│   ├── package.json          # npm 依赖
│   └── vite.config.js        # Vite 配置
│
├── data/                       # 数据文件
│   ├── devices.db            # SQLite 数据库（720+设备）
│   ├── static_device.json    # JSON 模式设备数据
│   ├── static_rule.json      # JSON 模式匹配规则
│   ├── static_config.json    # 系统配置
│   └── 真实设备价格例子.xlsx  # 真实设备数据源
│
├── docs/                       # 项目文档
│   ├── SETUP.md              # 详细安装指南
│   ├── MAINTENANCE.md        # 维护指南
│   ├── QUICK_START.md        # 快速开始
│   ├── TESTING_GUIDE.md      # 测试指南
│   ├── FILE_MANAGEMENT_GUIDE.md      # 文件管理指南
│   ├── GIT_HOOKS_GUIDE.md            # Git Hooks 使用指南
│   └── CONFIG_MANAGEMENT_USER_GUIDE.md  # 配置管理指南
│
├── scripts/                    # 项目管理脚本
│   ├── cleanup_project.py    # 项目清理工具
│   ├── organize_docs.py      # 文档整理工具
│   ├── install_hooks.bat     # Git Hooks 安装（Windows）
│   ├── install_hooks.sh      # Git Hooks 安装（Linux/Mac）
│   └── verify_hooks.bat      # Git Hooks 验证
│
├── .githooks/                  # Git Hooks
│   ├── pre-commit            # 提交前检查（Shell）
│   └── pre-commit.ps1        # 提交前检查（PowerShell）
│
├── .kiro/                      # Kiro 规格文档
│   ├── PROJECT.md            # 项目概述
│   └── specs/                # 功能规格
│       ├── ddc-device-matching/
│       ├── device-row-intelligent-recognition/
│       ├── database-migration/
│       └── config-management-ui/
│
└── .archive/                   # 临时文件归档（不提交到Git）
    └── 2026-02-27/            # 按日期归档
```

---

## 💡 使用指南

### 基本工作流程

1. **上传 Excel 文件** → 2. **智能识别设备行** → 3. **手动调整（可选）** → 4. **自动匹配设备** → 5. **导出报价单**

### 详细步骤

#### 1. 上传文件
- 支持拖拽或点击上传
- 支持 xls、xlsm、xlsx 格式
- 最大文件大小: 10MB

#### 2. 设备行识别
- 系统自动识别设备行（准确率 98%+）
- 5 种颜色编码：
  - 🟦 高概率（≥70分）- 自动标记为设备行
  - 🟨 中概率（40-69分）- 需要人工确认
  - ⬜ 低概率（<40分）- 通常为表头或备注
  - 🟩 手动标记为设备行
  - 🟥 手动取消设备行

#### 3. 手动调整（可选）
- 单行调整：使用每行右侧的下拉框
- 批量调整：勾选多行后批量操作
- 筛选功能：按行号、内容、概率等级筛选

#### 4. 设备匹配
- 系统自动匹配设备（准确率 91%+）
- 显示匹配结果和置信度
- 匹配失败时可手动选择

#### 5. 导出报价
- 完整保留原 Excel 格式
- 自动填充匹配的设备信息
- 下载包含价格的报价清单

---

## 🔧 配置管理

系统提供强大的配置管理界面，用于优化匹配规则和系统参数。

### 访问配置管理

在主界面导航栏点击"配置管理"进入。

### 主要功能

1. **设备类型管理** - 管理设备分类和关键词
2. **品牌关键词** - 配置品牌识别规则
3. **归一化规则** - 配置文本归一化映射
4. **同义词映射** - 配置同义词替换规则
5. **特征权重** - 调整匹配特征的权重
6. **设备行识别** - 配置设备行识别参数

详细说明请参考 [docs/CONFIG_MANAGEMENT_USER_GUIDE.md](docs/CONFIG_MANAGEMENT_USER_GUIDE.md)

---

## 🛠️ 项目维护

### 文件管理系统

项目配备完整的文件管理系统，保持项目结构清晰。

#### Git Hooks（自动检查）

每次提交代码前自动检查临时文件：

```bash
# 安装 Git Hooks
scripts\install_hooks.bat      # Windows
bash scripts/install_hooks.sh  # Linux/Mac

# 验证安装
scripts\verify_hooks.bat
```

**自动检查的文件**:
- ❌ `backend/test_*_fix.py` - 修复验证脚本
- ❌ `backend/test_*_debug.py` - 调试脚本
- ❌ `backend/fix_*.py` - 修复脚本
- ❌ `backend/demo_*.py` - 演示脚本
- ❌ 根目录的 Python 文件

#### 项目清理工具

定期清理临时文件，保持项目整洁：

```bash
# 预览将要清理的文件
python scripts/cleanup_project.py --dry-run

# 执行清理
python scripts/cleanup_project.py --execute
```

**清理内容**:
- 归档临时文件到 `.archive/`
- 移动诊断工具到 `backend/tools/`
- 移动运维脚本到 `backend/scripts/`
- 整理根目录文档到 `docs/`

#### 文档整理工具

自动整理和分类项目文档：

```bash
# 分析文档结构
python scripts/organize_docs.py --analyze

# 执行整理
python scripts/organize_docs.py --execute
```

### 维护建议

**每次开发后**:
```bash
# 删除临时测试文件
del backend\test_*_fix.py
del backend\test_*_debug.py
```

**每周维护**:
```bash
# 检查并清理临时文件
python scripts\cleanup_project.py --dry-run
python scripts\cleanup_project.py --execute
```

**每月维护**:
```bash
# 全面清理和整理
python scripts\cleanup_project.py --execute
python scripts\organize_docs.py --execute
```

详细说明请参考：
- [文件管理指南](docs/FILE_MANAGEMENT_GUIDE.md)
- [Git Hooks 使用指南](docs/GIT_HOOKS_GUIDE.md)
- [快速清理指南](docs/QUICK_CLEANUP_GUIDE.md)

---

## 🧪 测试

### 运行测试

```bash
cd backend

# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_match_engine.py -v

# 查看测试覆盖率
pytest tests/ --cov=modules --cov-report=html
```

### 测试覆盖

- ✅ 76 个单元测试全部通过
- ✅ 集成测试覆盖核心流程
- ✅ 端到端测试验证完整功能

详细说明请参考 [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md)

---

## 📚 技术栈

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 后端语言 |
| Flask | 2.x | Web 框架 |
| SQLAlchemy | 1.4+ | ORM 框架 |
| openpyxl | 3.x | Excel 处理（xlsx/xlsm） |
| xlrd | 2.x | Excel 处理（xls） |
| pytest | 7.x | 单元测试 |
| hypothesis | 6.x | 属性测试 |

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.x | 前端框架 |
| Element Plus | 2.x | UI 组件库 |
| Axios | 1.x | HTTP 客户端 |
| Vite | 4.x | 构建工具 |
| Vitest | 0.x | 单元测试 |

### 数据存储

| 技术 | 用途 |
|------|------|
| SQLite | 默认数据库（开发/小规模） |
| MySQL | 生产数据库（可选） |
| JSON | 向后兼容模式 |

---

## 📖 文档导航

### 快速开始
- [README.md](README.md) - 项目概述（本文件）
- [docs/QUICK_START.md](docs/QUICK_START.md) - 5分钟快速开始
- [docs/SETUP.md](docs/SETUP.md) - 详细安装指南

### 使用指南
- [docs/CONFIG_MANAGEMENT_USER_GUIDE.md](docs/CONFIG_MANAGEMENT_USER_GUIDE.md) - 配置管理
- [docs/MAINTENANCE.md](docs/MAINTENANCE.md) - 数据维护
- [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) - 测试指南

### 开发指南
- [docs/FILE_MANAGEMENT_GUIDE.md](docs/FILE_MANAGEMENT_GUIDE.md) - 文件管理
- [docs/GIT_HOOKS_GUIDE.md](docs/GIT_HOOKS_GUIDE.md) - Git Hooks
- [docs/KIRO_WORKFLOW_GUIDE.md](docs/KIRO_WORKFLOW_GUIDE.md) - Kiro 工作流程

### 技术文档
- [backend/docs/](backend/docs/) - 后端 API 文档
- [frontend/docs/](frontend/docs/) - 前端组件文档
- [.kiro/specs/](. kiro/specs/) - 功能规格文档

---

## 🔄 版本历史

### v2.1.0 (2026-02-27) - 最新版本

**新增功能**:
- 🎉 项目文件管理系统
- 🎉 Git Hooks 自动检查
- 🎉 项目清理工具
- 🎉 文档整理工具

**改进**:
- 项目结构规范化（清理 47 个文件）
- 根目录文件数量减少 77%
- 完整的文件管理指南

### v2.0.0 (2026-02-12)

**新增功能**:
- 🎉 数据库支持（SQLite/MySQL）
- 🎉 真实设备数据（720+条）
- 🎉 数据库管理工具

### v1.2.0 (2026-02-08)

**新增功能**:
- 🎉 设备库扩充（25 → 59 个设备）
- 🎉 能源管理系统设备支持

### v1.1.0 (2026-02)

**新增功能**:
- 🎉 设备行智能识别功能
- 🎉 三维度加权评分模型
- 🎉 手动调整功能

完整版本历史请参考 [CHANGELOG.md](CHANGELOG.md)

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- Python 代码遵循 PEP 8 规范
- 使用类型注解提高代码可读性
- 所有公共方法需要添加文档字符串
- 测试覆盖率目标：≥80%

---

## 📄 许可证

MIT License

Copyright (c) 2024-2026 DDC Device Matching System

---

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 📧 提交 Issue
- 📝 查看文档
- 💬 项目讨论

---

## 🙏 致谢

感谢所有为本项目做出贡献的开发者和用户！

---

**最后更新**: 2026-02-27  
**当前版本**: v2.1.0  
**维护状态**: ✅ 积极维护中
