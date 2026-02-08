# DDC 设备清单匹配报价系统

## 项目概述

这是一个轻量化的 DDC 设备清单匹配报价系统，旨在解决 DDC 自控领域空调机房、末端设备清单报价过程中的效率和准确性问题。系统实现从 Excel 设备清单上传到报价单导出的全流程自动化处理。

## 核心目标

1. **多格式支持**: 兼容 xls/xlsm/xlsx 格式 Excel 文件上传和解析
2. **智能识别**: 三维度加权评分模型，自动识别设备行准确率≥95%
3. **智能匹配**: 基于权重的特征匹配算法，匹配准确率≥85%
4. **格式保留**: 导出时精准保留原 Excel 的合并单元格、行列顺序
5. **人工兜底**: 支持手动调整设备行识别结果和匹配失败时手动选择设备
6. **轻量化架构**: 基于静态 JSON 文件，无数据库依赖，不使用大模型

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

**阶段一: 核心验证阶段 - 已完成 ✅**

已完成完整链路的实现和验证：
- ✅ Excel 多格式上传与解析
- ✅ 设备行智能识别（三维度评分模型）
- ✅ 手动调整功能（单行+批量）
- ✅ 不规范描述归一化
- ✅ 静态规则匹配
- ✅ 表格展示与人工调整
- ✅ Excel 格式还原导出

**已实现的两大核心功能模块：**

1. **设备行智能识别与手动调整** ✅
   - 自动识别准确率: 98.04%
   - 手动调整后准确率: 100%
   - 完整的前后端实现
   - 76个单元测试全部通过

2. **设备匹配与报价导出** ✅
   - 匹配准确率: 91.30%
   - 完整的匹配引擎
   - Excel格式完美保留
   - 性能表现优秀

## 项目结构

```
ddc-device-matching/
├── .kiro/
│   ├── specs/
│   │   ├── ddc-device-matching/
│   │   │   ├── requirements.md    # 需求文档（9个需求，52个验收标准）
│   │   │   ├── design.md          # 设计文档（架构、接口、数据模型、20个正确性属性）
│   │   │   └── tasks.md           # 任务清单（13个主要任务）
│   │   └── device-row-intelligent-recognition/
│   │       ├── requirements.md    # 设备行识别需求文档（15个需求）
│   │       ├── design.md          # 设备行识别设计文档（三维度评分模型）
│   │       └── tasks.md           # 设备行识别任务清单（9个任务，已完成）
│   └── PROJECT.md                 # 本文件
├── backend/                       # 后端代码（已实现）
│   ├── app.py                     # Flask应用，包含设备行识别API
│   ├── modules/
│   │   ├── text_preprocessor.py  # 文本预处理
│   │   ├── data_loader.py        # 数据加载
│   │   ├── excel_parser.py       # Excel解析
│   │   ├── match_engine.py       # 匹配引擎
│   │   ├── excel_exporter.py     # Excel导出
│   │   └── device_row_classifier.py  # 设备行分类器（新增）
│   ├── tests/                    # 单元测试
│   └── temp/                     # 临时文件目录
├── frontend/                      # 前端代码（已实现）
│   └── src/
│       ├── components/
│       │   ├── FileUpload.vue
│       │   ├── ResultTable.vue
│       │   ├── ExportButton.vue
│       │   └── DeviceRowAdjustment.vue  # 设备行调整组件（新增）
│       └── views/
│           ├── FileUploadView.vue
│           ├── DeviceRowAdjustmentView.vue  # 设备行调整页面（新增）
│           └── MatchingView.vue
├── data/                          # 数据文件
│   ├── static_device.json        # 设备数据
│   ├── static_rule.json          # 匹配规则
│   └── static_config.json        # 配置文件（包含设备行识别配置）
└── README.md                      # 项目说明
```

## 核心工作流程

### 完整流程（包含设备行智能识别）

1. **上传**: 用户上传 xls/xlsm/xlsx 格式的设备清单
2. **智能识别**: 系统自动识别设备行（三维度评分，准确率98%+）
   - 数据类型组合分析（权重30%）
   - 结构关联性分析（权重35%）
   - 行业通用特征分析（权重35%）
3. **手动调整**: 用户可选择性调整识别结果（确保100%准确率）
   - 单行调整或批量调整
   - 多维度筛选功能
   - 实时视觉反馈
4. **解析**: 系统解析最终确认的设备行
5. **预处理**: 对设备描述进行归一化和特征提取
6. **匹配**: 基于权重的特征匹配，计算得分并选择最佳匹配
7. **展示**: 前端表格展示匹配结果，支持人工调整
8. **导出**: 保留原格式，新增"匹配设备"和"单价"列，生成报价清单

## 关键特性

### 设备行智能识别（新增功能）
- **三维度评分**: 数据类型、结构关联、行业特征综合评估
- **高准确率**: 自动识别准确率98.04%，手动调整后100%
- **视觉直观**: 5种颜色编码概率等级（高/中/低/手动标记/手动取消）
- **灵活调整**: 支持单行调整和批量调整
- **智能筛选**: 多维度筛选（行号、内容、概率等级）
- **配置驱动**: 评分权重、阈值、行业词库均可配置

### 设备匹配与导出
- **三层归一化**: 精准映射 → 通用归一化 → 模糊兼容
- **权重匹配**: 核心特征高权重，累计得分超过阈值即匹配成功
- **自动特征生成**: 新增设备时自动生成匹配规则
- **格式往返保留**: 导出文件保持原 Excel 的合并单元格和行列顺序
- **配置热加载**: 修改配置文件无需重启服务

## 性能指标

- **设备行识别准确率**: 自动识别≥95%（实际98.04%），手动调整后100%
- **匹配准确率**: ≥85%（实际91.30%）
- **解析性能**: 1000行 Excel ≤5秒（实际0.032秒/29行）
- **匹配性能**: 1000个设备描述 ≤10秒（实际0.008秒/100个）
- **识别性能**: 100行以内 ≤2秒（实际<1秒/66行）

## 下一步行动

### 查看和执行任务

**设备匹配功能（主要功能）:**
- 查看 `.kiro/specs/ddc-device-matching/tasks.md` 了解设备匹配相关任务

**设备行识别功能（已完成）:**
- 查看 `.kiro/specs/device-row-intelligent-recognition/tasks.md` 了解已完成的任务
- 查看 `DEVICE_ROW_RECOGNITION_FINAL_SUMMARY.md` 了解功能详情

### 如何开始
1. 打开 tasks.md 文件
2. 点击任务旁边的 "Start task" 按钮
3. Kiro 将引导你完成该任务的实施

### 快速启动系统

**后端:**
```bash
cd backend
python app.py
```

**前端:**
```bash
cd frontend
npm run dev
```

访问: `http://localhost:5173`

## 文档索引

### 规格文档

**设备匹配功能:**
- **需求文档**: `.kiro/specs/ddc-device-matching/requirements.md`
- **设计文档**: `.kiro/specs/ddc-device-matching/design.md`
- **任务清单**: `.kiro/specs/ddc-device-matching/tasks.md`

**设备行识别功能:**
- **需求文档**: `.kiro/specs/device-row-intelligent-recognition/requirements.md`
- **设计文档**: `.kiro/specs/device-row-intelligent-recognition/design.md`
- **任务清单**: `.kiro/specs/device-row-intelligent-recognition/tasks.md`

### 项目文档
- **项目说明**: `.kiro/PROJECT.md` (本文件)
- **README**: `README.md`
- **维护指南**: `MAINTENANCE.md`
- **快速开始**: `QUICK_START_GUIDE.md`

### 故障排查文档（新增）
- **完整故障排查指南**: `MANUAL_ADJUST_TROUBLESHOOTING_V2.md`
- **用户操作指南**: `MANUAL_ADJUST_USER_GUIDE.md`
- **快速参考卡片**: `TROUBLESHOOTING_QUICK_REFERENCE.md`
- **测试脚本**: `backend/test_manual_adjust_debug.py`

### 实现总结文档

**设备行识别:**
- `DEVICE_ROW_RECOGNITION_FINAL_SUMMARY.md` - 功能完整总结
- `TASK_9_FINAL_CHECKPOINT_REPORT.md` - 最终检查点报告
- `backend/TASK2_COMPLETION_SUMMARY.md` - 三维度评分算法
- `backend/TASK3_API_IMPLEMENTATION_SUMMARY.md` - API接口实现
- `backend/TASK5_ACCURACY_VERIFICATION_SUMMARY.md` - 准确率验证
- `backend/E2E_TEST_REPORT.md` - 端到端测试报告
- `frontend/TASK_6_COMPLETION_SUMMARY.md` - 前端组件实现
- `frontend/TASK_7_INTEGRATION_SUMMARY.md` - 前端集成

**设备匹配:**
- `TASK_12_COMPLETION_SUMMARY.md` - 任务12完成总结
- `FINAL_ACCEPTANCE_REPORT.md` - 最终验收报告

**设备库扩充:**
- `DEVICE_LIBRARY_EXPANSION_REPORT.md` - 设备库扩充详细报告
- `DEVICE_LIBRARY_EXPANSION_SUMMARY.md` - 设备库扩充快速总结

**UI优化:**
- `UI_OPTIMIZATION_SUMMARY.md` - UI优化说明
- `UI_TOOLTIP_FIX_SUMMARY.md` - Tooltip修复说明

**故障排查:**
- `MANUAL_ADJUST_TROUBLESHOOTING_V2.md` - 手动调整功能故障排查指南v2.0
- `MANUAL_ADJUST_USER_GUIDE.md` - 用户操作指南
- `TROUBLESHOOTING_QUICK_REFERENCE.md` - 快速参考卡片

## 注意事项

### 通用规范
1. 所有模块都应该复用统一的 TextPreprocessor 进行文本预处理
2. 所有 API 返回的匹配结果都应该使用标准化的 match_result 格式
3. 系统启动时会自动校验规则表与设备表的关联完整性
4. 配置文件修改后会自动热加载，无需重启服务
5. 测试任务标记为可选（*），可以先实现核心功能，后续补充测试

### 设备行识别功能
1. 评分权重和阈值可在 `data/static_config.json` 中配置
2. 行业词库（设备类型、参数、品牌、型号）可持续扩充
3. 手动调整记录基于 excel_id 管理，存储在内存中
4. 前端颜色编码：浅蓝（高概率）、浅黄（中概率）、浅灰（低概率）、深绿（手动标记）、深红（手动取消）
5. API 端到端测试需要启动 Flask 服务器

### 故障排查（新增）
1. **手动调整功能400错误**: 通常是后端缓存为空导致，重启后端并重新上传文件即可解决
2. **测试脚本**: 使用 `backend/test_manual_adjust_debug.py` 快速验证后端API是否正常
3. **调试日志**: 后端已添加详细的调试日志，可查看 excel_id 匹配情况
4. **预防措施**: 使用期间不要重启后端服务，避免内存缓存清空
5. **详细文档**: 查看 `MANUAL_ADJUST_TROUBLESHOOTING_V2.md` 获取完整的故障排查指南

## 联系与支持

如有问题或需要调整，请随时与开发团队沟通。
