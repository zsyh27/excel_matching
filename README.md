# DDC 设备清单匹配报价系统

## 项目简介

DDC 设备清单匹配报价系统是一个轻量化的 Web 应用，专为 DDC 自控领域的设备清单报价流程设计。系统通过**设备行智能识别**和**智能匹配算法**，自动识别 Excel 设备清单中的设备行并匹配设备信息，生成标准化的报价单，大幅提升报价效率和准确性。

### 核心特性

- ✅ **多格式支持**: 支持 xls、xlsm、xlsx 三种 Excel 格式
- ✅ **智能识别设备行**: 三维度加权评分模型，自动识别准确率 98.04%
- ✅ **手动调整功能**: 支持单行和批量调整，确保 100% 准确率
- ✅ **智能匹配设备**: 基于特征权重的匹配算法，准确率 91.30%
- ✅ **格式保留**: 导出时完整保留原 Excel 文件的格式和结构
- ✅ **人机协作**: 识别和匹配失败时支持手动调整
- ✅ **配置驱动**: 所有归一化规则和匹配参数可配置
- ✅ **轻量化设计**: 无需数据库，基于静态 JSON 文件

### 技术亮点

1. **设备行智能识别** (新增核心功能)
   - 三维度加权评分: 数据类型组合、结构关联性、行业通用特征
   - 自动识别准确率: 98.04%（超过 95% 目标）
   - 手动调整后准确率: 100%
   - 5 种颜色编码视觉反馈
   - 支持单行和批量调整
   - 多维度筛选功能

2. **设备智能匹配**
   - 三层归一化处理: 精准映射 → 通用归一化 → 模糊兼容
   - 统一预处理器: Excel 解析、规则生成、匹配引擎使用相同的文本处理逻辑
   - 标准化返回格式: 前后端接口统一，易于维护和扩展
   - 自动特征生成: 新增设备时自动生成匹配规则

## 技术栈

**后端:**
- Python 3.8+
- Flask (轻量级 Web 框架)
- openpyxl (处理 xlsx/xlsm 格式)
- xlrd (处理 xls 格式)
- pytest (单元测试)
- hypothesis (属性测试)

**前端:**
- Vue 3 (渐进式框架)
- Element Plus (UI 组件库)
- Axios (HTTP 客户端)
- Vite (构建工具)

**数据存储:**
- JSON 文件 (设备库、规则库、配置)
- 支持两大类设备：
  - 楼宇自控设备（25个）：传感器、控制器、执行器等
  - 能源管理系统设备（34个）：数据采集器、服务器、软件系统等
- 静态 JSON 文件（无数据库依赖）

## 项目结构

```
.
├── backend/                    # 后端代码
│   ├── app.py                 # Flask 应用入口（包含设备行识别 API）
│   ├── config.py              # 配置管理
│   ├── requirements.txt       # Python 依赖
│   ├── modules/               # 业务模块
│   │   ├── device_row_classifier.py  # 设备行分类器（新增）
│   │   ├── excel_parser.py   # Excel 解析模块
│   │   ├── text_preprocessor.py  # 文本预处理模块
│   │   ├── match_engine.py   # 匹配引擎模块
│   │   ├── excel_exporter.py # Excel 导出模块
│   │   └── data_loader.py    # 数据加载模块
│   ├── tests/                 # 测试文件（76 个测试全部通过）
│   └── temp/                  # 临时文件目录
├── frontend/                   # 前端代码
│   ├── src/                   # 源代码
│   │   ├── components/       # Vue 组件
│   │   │   ├── FileUpload.vue
│   │   │   ├── ResultTable.vue
│   │   │   ├── ExportButton.vue
│   │   │   └── DeviceRowAdjustment.vue  # 设备行调整组件（新增）
│   │   ├── views/            # 页面视图
│   │   │   ├── FileUploadView.vue
│   │   │   ├── DeviceRowAdjustmentView.vue  # 设备行调整页面（新增）
│   │   │   └── MatchingView.vue
│   │   ├── api/              # API 接口
│   │   └── main.js           # 应用入口
│   ├── package.json          # npm 依赖
│   └── vite.config.js        # Vite 配置
├── data/                       # 静态数据文件
│   ├── static_device.json    # 设备表（25个示例设备）
│   ├── static_rule.json      # 规则表（自动生成）
│   ├── static_config.json    # 配置文件（包含设备行识别配置）
│   └── 示例设备清单.xlsx      # 示例 Excel 文件
├── .kiro/                      # Kiro 规格文档
│   ├── specs/
│   │   ├── ddc-device-matching/  # 设备匹配功能规格
│   │   └── device-row-intelligent-recognition/  # 设备行识别功能规格
│   └── PROJECT.md             # 项目概述
├── README.md                   # 项目说明（本文件）
├── SETUP.md                    # 详细安装指南
├── QUICK_START_GUIDE.md        # 快速启动指南
├── MAINTENANCE.md              # 数据维护指南
├── DEVICE_ROW_RECOGNITION_FINAL_SUMMARY.md  # 设备行识别功能总结
└── TASK_9_FINAL_CHECKPOINT_REPORT.md  # 最终检查点报告
```

## 快速开始

### 环境要求

- Python 3.8 或更高版本
- Node.js 14 或更高版本
- npm 或 yarn 包管理器

### 后端安装

1. **创建 Python 虚拟环境**:
```bash
cd backend
python -m venv venv
```

2. **激活虚拟环境**:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. **安装依赖**:
```bash
pip install -r requirements.txt
```

4. **运行后端服务**:
```bash
python app.py
```

后端服务将运行在 `http://localhost:5000`

### 前端安装

1. **安装依赖**:
```bash
cd frontend
npm install
```

2. **运行开发服务器**:
```bash
npm run dev
```

前端应用将运行在 `http://localhost:3000`

### 运行测试

**后端测试**:
```bash
cd backend
pytest tests/ -v
```

**属性测试**:
```bash
cd backend
pytest tests/ -v -k "property"
```

## 使用指南

### 基本流程

1. **启动服务**: 分别启动后端和前端服务
2. **访问应用**: 在浏览器中打开 `http://localhost:5173`
3. **上传文件**: 点击上传按钮或拖拽 Excel 文件到上传区域
4. **智能识别**: 系统自动识别设备行（三维度评分，准确率 98%+）
5. **手动调整**: 查看识别结果，可选择性调整（单行或批量）
6. **确认设备行**: 点击"确认调整并进入匹配"
7. **查看匹配**: 系统自动匹配设备，显示匹配结果
8. **人工调整**: 对匹配失败的设备，从下拉框中手动选择正确的设备
9. **导出报价**: 点击导出按钮，下载包含匹配结果的报价清单

### 设备行智能识别功能

#### 三维度评分模型

系统采用三维度加权评分模型自动识别设备行：

1. **数据类型组合分析（权重 30%）**
   - 统计文本、数值、空单元格数量
   - 理想比例（文本:数值 = 1:1 到 3:1）得高分
   - 纯文本或纯数值得低分

2. **结构关联性分析（权重 35%）**
   - 检测列标题行并判断数据类型对应关系
   - 比较与周边行的格式相似度
   - 评估行位置合理性

3. **行业通用特征分析（权重 35%）**
   - 匹配 DDC 领域设备类型词库
   - 匹配参数词库（PPM、℃、Pa 等）
   - 匹配品牌词库（霍尼韦尔、西门子等）
   - 匹配型号模式

#### 概率等级划分

- **高概率（≥70分）**: 浅蓝色背景，自动标记为设备行
- **中概率（40-69分）**: 浅黄色背景，需要人工确认
- **低概率（<40分）**: 浅灰色背景，通常为表头或备注

#### 手动调整功能

1. **单行调整**: 使用每行右侧的下拉框
   - 标记为设备行（深绿色）
   - 取消设备行（深红色）
   - 恢复自动判断

2. **批量调整**: 
   - 勾选多行
   - 点击"批量标记为设备行"或"批量取消设备行"

3. **筛选功能**:
   - 按行号搜索
   - 按内容关键词搜索
   - 按概率等级筛选（高/中/低）

### 示例数据

系统提供了完整的示例数据，包括：

- **25 个设备**: 涵盖 DDC 控制器、传感器、阀门、执行器、控制柜等
- **25 条匹配规则**: 与设备一一对应，自动生成
- **示例 Excel 文件**: 
  - `data/示例设备清单.xlsx` - 标准格式示例
  - `data/(原始表格)建筑设备监控及能源管理报价清单(2).xlsx` - 真实场景测试文件

#### 真实测试文件说明

`(原始表格)建筑设备监控及能源管理报价清单(2).xlsx`:
- **总行数**: 66 行
- **真实设备行**: 第 6-21 行、第 23-57 行（共 51 行）
- **包含**: 表头、合计、备注等无关行
- **测试结果**: 
  - 自动识别准确率: 98.04%
  - 手动调整后准确率: 100%

您可以直接使用这些示例文件测试系统功能。

### 匹配算法说明

系统采用**特征权重匹配算法**：

1. **文本预处理**: 
   - 删除无关关键词（如"施工要求"、"验收"等）
   - 应用归一化映射（如 "～" → "-"，"℃" → "摄氏度"）
   - 统一格式（全角转半角、大小写统一、去空格）
   - 拆分特征（按逗号、分号等分隔符）

2. **特征匹配**:
   - 将 Excel 描述的特征与规则表中的特征进行比对
   - 匹配成功的特征累加权重得分
   - 品牌和型号权重较高（3.0），其他特征权重较低（1.0-2.5）

3. **阈值判定**:
   - 权重得分 ≥ 规则阈值：匹配成功
   - 权重得分 < 规则阈值：尝试使用默认阈值（2.0）
   - 仍未达到阈值：匹配失败，需要人工选择

4. **最佳匹配**:
   - 如果多条规则匹配成功，选择权重得分最高的规则

### 配置说明

系统的所有配置都在 `data/static_config.json` 文件中：

#### 设备行识别配置（新增）
```json
"device_row_recognition": {
  "scoring_weights": {
    "data_type": 0.30,    // 数据类型组合权重
    "structure": 0.35,    // 结构关联性权重
    "industry": 0.35      // 行业特征权重
  },
  "probability_thresholds": {
    "high": 70.0,         // 高概率阈值
    "medium": 40.0        // 中概率阈值
  },
  "industry_keywords": {
    "device_types": [...],  // 设备类型词库
    "parameters": [...],    // 参数词库
    "brands": [...],        // 品牌词库
    "model_patterns": [...]  // 型号模式
  }
}
```

#### 设备匹配配置
- **normalization_map**: 字符归一化映射表
- **feature_split_chars**: 特征拆分符号
- **ignore_keywords**: 需要过滤的关键词
- **default_match_threshold**: 默认匹配阈值（2.0）
- **unify_lowercase**: 是否统一小写（true）

详细的配置说明请参考 [MAINTENANCE.md](MAINTENANCE.md)。

## 数据维护

### 添加新设备

1. 编辑 `data/static_device.json`，添加新设备信息
2. 运行自动规则生成脚本：
```bash
python generate_rules.py
```
3. 系统会自动为新设备生成匹配规则

### 调整匹配规则

编辑 `data/static_rule.json`，可以调整：
- 特征权重（feature_weights）
- 匹配阈值（match_threshold）
- 特征列表（auto_extracted_features）

### 更新配置

编辑 `data/static_config.json`，可以添加：
- 新的归一化映射
- 新的过滤关键词
- 调整匹配阈值

详细的维护指南请参考 [MAINTENANCE.md](MAINTENANCE.md)。

## 性能指标

- ✅ **设备行识别准确率**: 自动识别 98.04%，手动调整后 100%
- ✅ **设备匹配准确率**: 91.30%（标准和非标准格式）
- ✅ **解析性能**: 1000 行 Excel 在 5 秒内完成（实际 0.032 秒/29 行）
- ✅ **匹配性能**: 1000 个设备描述在 10 秒内完成（实际 0.008 秒/100 个）
- ✅ **识别性能**: 100 行以内在 2 秒内完成（实际 <1 秒/66 行）
- ✅ **文件大小**: 支持最大 10MB 的 Excel 文件
- ✅ **测试覆盖**: 76 个单元测试全部通过

## 故障排查

### 常见问题

**Q: 上传文件失败**
- 检查文件格式是否为 xls/xlsm/xlsx
- 检查文件大小是否超过 10MB
- 检查文件是否损坏

**Q: 匹配准确率低**
- 检查设备描述是否包含足够的特征信息
- 调整规则表中的特征权重
- 添加更多归一化映射到配置文件

**Q: 导出文件格式错误**
- 检查原文件是否包含合并单元格
- 检查原文件是否有特殊格式
- 查看后端日志获取详细错误信息

更多故障排查信息请参考 [MAINTENANCE.md](MAINTENANCE.md)。

## 开发指南

### 运行测试

```bash
# 运行所有测试
cd backend
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_match_engine.py -v

# 运行属性测试
pytest tests/ -v -k "property"

# 查看测试覆盖率
pytest tests/ --cov=modules --cov-report=html
```

### 代码规范

- Python 代码遵循 PEP 8 规范
- 使用类型注解提高代码可读性
- 所有公共方法需要添加文档字符串
- 测试覆盖率目标：≥80%

### 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 版本历史

### v1.2.2 (2026-02-08)
- 🔧 **故障排查**: 手动调整功能400错误排查
  - 修复测试脚本中的API路径错误
  - 添加详细的后端调试日志
  - 创建完整的故障排查指南
  - 提供用户操作指南
- 📄 详细说明: [MANUAL_ADJUST_TROUBLESHOOTING_V2.md](MANUAL_ADJUST_TROUBLESHOOTING_V2.md)
- 📄 用户指南: [MANUAL_ADJUST_USER_GUIDE.md](MANUAL_ADJUST_USER_GUIDE.md)

### v1.2.1 (2026-02-08)
- ✅ **UI优化**: 设备行内容显示优化
  - 行内容限制在150字符以内，避免过长影响布局
  - 使用自定义Tooltip，鼠标悬停显示完整原始内容（不带省略号）
  - 短内容（≤150字符）不显示Tooltip，提升性能
  - 提升表格浏览体验和页面性能
- 📄 详细说明: [UI_OPTIMIZATION_SUMMARY.md](UI_OPTIMIZATION_SUMMARY.md)
- 📄 修复说明: [UI_TOOLTIP_FIX_SUMMARY.md](UI_TOOLTIP_FIX_SUMMARY.md)

### v1.2.0 (2026-02-08)
- ✅ **扩充设备库**: 从25个设备增加到59个设备
  - 新增34个能源管理系统设备
  - 支持能耗数据采集器、多联机采集器、服务器、软件系统等
  - 真实Excel文件匹配率从0%提升到90%
- ✅ **自动化工具**: 提供设备提取和合并脚本
- ✅ **规则优化**: 自动生成34条新匹配规则
- 📄 详细报告: [DEVICE_LIBRARY_EXPANSION_REPORT.md](DEVICE_LIBRARY_EXPANSION_REPORT.md)

### v1.1.0 (2026-02)
- ✅ **新增设备行智能识别功能**
  - 三维度加权评分模型
  - 自动识别准确率 98.04%
  - 手动调整功能（单行+批量）
  - 多维度筛选功能
  - 5 种颜色编码视觉反馈
- ✅ 完整的前后端实现
- ✅ 76 个单元测试全部通过
- ✅ 完整的文档和使用指南

### v1.0.0 (2024-02)
- ✅ 完成核心功能开发
- ✅ 实现 Excel 多格式支持
- ✅ 实现智能匹配算法
- ✅ 实现格式保留导出
- ✅ 添加完整的测试套件
- ✅ 提供示例数据和文档

## 许可证

MIT License

Copyright (c) 2024 DDC Device Matching System

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 查看文档

## 致谢

感谢所有为本项目做出贡献的开发者和用户。
