# DDC 设备清单匹配报价系统

## 项目概述

这是一个轻量化的 DDC 设备清单匹配报价系统，旨在解决 DDC 自控领域空调机房、末端设备清单报价过程中的效率和准确性问题。系统实现从 Excel 设备清单上传到报价单导出的全流程自动化处理。

## 核心目标

1. **多格式支持**: 兼容 xls/xlsm/xlsx 格式 Excel 文件上传和解析
2. **智能匹配**: 基于权重的特征匹配算法，匹配准确率≥85%
3. **格式保留**: 导出时精准保留原 Excel 的合并单元格、行列顺序
4. **人工兜底**: 匹配失败时支持手动选择设备
5. **轻量化架构**: 基于静态 JSON 文件，无数据库依赖，不使用大模型

## 技术栈

**后端:**
- Python 3.8+ / Flask
- openpyxl (xlsx/xlsm)
- xlrd 2.0.1 (xls)

**前端:**
- Vue 3
- Element Plus
- Axios

**数据存储:**
- 静态 JSON 文件（static_device.json、static_rule.json、static_config.json）

## 四大标准化原则

1. **核心函数封装标准化**: 文本预处理封装为独立工具函数，所有阶段复用
2. **返回格式标准化**: 统一的 match_result 格式，前端和导出只需对接一个格式
3. **规则表与设备表联动标准化**: 自动校验和同步机制，避免关联失败
4. **全局配置参数化**: 配置热加载，支持前端配置界面修改

## 当前阶段

**阶段一: 核心验证阶段**

当前处于阶段一的实施阶段，目标是跑通完整链路：
- Excel 多格式上传 → 解析预处理 → 不规范描述归一化 → 静态规则匹配 → 表格展示 → Excel 格式还原导出

## 项目结构

```
ddc-device-matching/
├── .kiro/
│   ├── specs/
│   │   └── ddc-device-matching/
│   │       ├── requirements.md    # 需求文档（9个需求，52个验收标准）
│   │       ├── design.md          # 设计文档（架构、接口、数据模型、20个正确性属性）
│   │       └── tasks.md           # 任务清单（13个主要任务）
│   └── PROJECT.md                 # 本文件
├── backend/                       # 后端代码（待实现）
│   ├── app.py
│   ├── modules/
│   │   ├── text_preprocessor.py
│   │   ├── data_loader.py
│   │   ├── excel_parser.py
│   │   ├── match_engine.py
│   │   └── excel_exporter.py
│   ├── data/
│   │   ├── static_device.json
│   │   ├── static_rule.json
│   │   └── static_config.json
│   └── tests/
├── frontend/                      # 前端代码（待实现）
│   └── src/
│       └── components/
└── README.md                      # 项目说明（待创建）
```

## 核心工作流程

1. **上传**: 用户上传 xls/xlsm/xlsx 格式的设备清单
2. **解析**: 系统解析 Excel，过滤空行，识别行类型
3. **预处理**: 对设备描述进行归一化和特征提取
4. **匹配**: 基于权重的特征匹配，计算得分并选择最佳匹配
5. **展示**: 前端表格展示匹配结果，支持人工调整
6. **导出**: 保留原格式，新增"匹配设备"和"单价"列，生成报价清单

## 关键特性

- **三层归一化**: 精准映射 → 通用归一化 → 模糊兼容
- **权重匹配**: 核心特征高权重，累计得分超过阈值即匹配成功
- **自动特征生成**: 新增设备时自动生成匹配规则
- **格式往返保留**: 导出文件保持原 Excel 的合并单元格和行列顺序
- **配置热加载**: 修改配置文件无需重启服务

## 性能指标

- 匹配准确率: ≥85%
- 解析性能: 1000行 Excel ≤5秒
- 匹配性能: 1000个设备描述 ≤10秒

## 下一步行动

查看 `.kiro/specs/ddc-device-matching/tasks.md` 开始执行任务。

可以通过以下方式开始：
1. 打开 tasks.md 文件
2. 点击任务旁边的 "Start task" 按钮
3. Kiro 将引导你完成该任务的实施

## 文档索引

- **需求文档**: `.kiro/specs/ddc-device-matching/requirements.md`
- **设计文档**: `.kiro/specs/ddc-device-matching/design.md`
- **任务清单**: `.kiro/specs/ddc-device-matching/tasks.md`
- **项目说明**: `.kiro/PROJECT.md` (本文件)

## 注意事项

1. 所有模块都应该复用统一的 TextPreprocessor 进行文本预处理
2. 所有 API 返回的匹配结果都应该使用标准化的 match_result 格式
3. 系统启动时会自动校验规则表与设备表的关联完整性
4. 配置文件修改后会自动热加载，无需重启服务
5. 测试任务标记为可选（*），可以先实现核心功能，后续补充测试

## 联系与支持

如有问题或需要调整，请随时与开发团队沟通。
