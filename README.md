# DDC 设备清单匹配报价系统

## 项目简介

DDC 设备清单匹配报价系统是一个轻量化的 Web 应用，专为 DDC 自控领域的设备清单报价流程设计。系统通过智能匹配算法，自动识别 Excel 设备清单中的设备信息，并生成标准化的报价单，大幅提升报价效率和准确性。

### 核心特性

- ✅ **多格式支持**: 支持 xls、xlsm、xlsx 三种 Excel 格式
- ✅ **智能匹配**: 基于特征权重的匹配算法，准确率≥85%
- ✅ **格式保留**: 导出时完整保留原 Excel 文件的格式和结构
- ✅ **人工兜底**: 匹配失败时支持手动选择设备
- ✅ **配置驱动**: 所有归一化规则和匹配参数可配置
- ✅ **轻量化设计**: 无需数据库，基于静态 JSON 文件

### 技术亮点

1. **三层归一化处理**: 精准映射 → 通用归一化 → 模糊兼容
2. **统一预处理器**: Excel 解析、规则生成、匹配引擎使用相同的文本处理逻辑
3. **标准化返回格式**: 前后端接口统一，易于维护和扩展
4. **自动特征生成**: 新增设备时自动生成匹配规则

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
- 静态 JSON 文件（无数据库依赖）

## 项目结构

```
.
├── backend/                    # 后端代码
│   ├── app.py                 # Flask 应用入口
│   ├── config.py              # 配置管理
│   ├── requirements.txt       # Python 依赖
│   ├── modules/               # 业务模块
│   │   ├── excel_parser.py   # Excel 解析模块
│   │   ├── text_preprocessor.py  # 文本预处理模块
│   │   ├── match_engine.py   # 匹配引擎模块
│   │   ├── excel_exporter.py # Excel 导出模块
│   │   └── data_loader.py    # 数据加载模块
│   ├── tests/                 # 测试文件
│   └── temp/                  # 临时文件目录
├── frontend/                   # 前端代码
│   ├── src/                   # 源代码
│   │   ├── components/       # Vue 组件
│   │   ├── api/              # API 接口
│   │   └── main.js           # 应用入口
│   ├── package.json          # npm 依赖
│   └── vite.config.js        # Vite 配置
├── data/                       # 静态数据文件
│   ├── static_device.json    # 设备表（25个示例设备）
│   ├── static_rule.json      # 规则表（自动生成）
│   ├── static_config.json    # 配置文件
│   └── 示例设备清单.xlsx      # 示例 Excel 文件
├── README.md                   # 项目说明（本文件）
├── MAINTENANCE.md              # 数据维护指南
└── SETUP.md                    # 详细安装指南
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
2. **访问应用**: 在浏览器中打开 `http://localhost:3000`
3. **上传文件**: 点击上传按钮或拖拽 Excel 文件到上传区域
4. **查看结果**: 系统自动解析并匹配设备，显示匹配结果
5. **人工调整**: 对匹配失败的设备，从下拉框中手动选择正确的设备
6. **导出报价**: 点击导出按钮，下载包含匹配结果的报价清单

### 示例数据

系统提供了完整的示例数据，包括：

- **25 个设备**: 涵盖 DDC 控制器、传感器、阀门、执行器、控制柜等
- **25 条匹配规则**: 与设备一一对应，自动生成
- **示例 Excel 文件**: `data/示例设备清单.xlsx`，包含标准和非标准格式的设备描述

您可以直接使用示例 Excel 文件测试系统功能。

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

- ✅ **匹配准确率**: ≥85%（标准和非标准格式）
- ✅ **解析性能**: 1000 行 Excel 在 5 秒内完成
- ✅ **匹配性能**: 1000 个设备描述在 10 秒内完成
- ✅ **文件大小**: 支持最大 10MB 的 Excel 文件

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
