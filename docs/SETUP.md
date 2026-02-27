# 项目环境搭建指南

本指南将帮助你完整搭建 DDC 设备清单匹配报价系统的开发环境。

## 系统功能概述

本系统包含两大核心功能：

1. **设备行智能识别与手动调整** ✅
   - 三维度加权评分模型
   - 自动识别准确率: 98.04%
   - 手动调整后准确率: 100%

2. **设备智能匹配与报价导出** ✅
   - 特征权重匹配算法
   - 匹配准确率: 91.30%
   - 完美保留 Excel 格式

## 前置要求

- Python 3.8 或更高版本
- Node.js 16 或更高版本
- npm 或 yarn

## 后端环境搭建

### 1. 创建 Python 虚拟环境

在项目根目录下执行:

**Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装 Python 依赖

激活虚拟环境后，安装依赖:

```bash
pip install -r requirements.txt
```

依赖包括:
- Flask 3.0.0 - Web 框架
- Flask-CORS 4.0.0 - 跨域支持
- openpyxl 3.1.2 - 处理 xlsx/xlsm 格式
- xlrd 2.0.1 - 处理 xls 格式
- pytest 7.4.3 - 单元测试框架
- hypothesis 6.92.1 - 属性测试框架

### 3. 验证后端安装

```bash
python app.py
```

如果看到以下信息，说明后端环境搭建成功：
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 4. 运行测试验证

```bash
# 运行所有单元测试
pytest tests/ -v

# 运行设备行识别测试
python test_device_row_recognition.py

# 查看测试覆盖率
pytest tests/ --cov=modules
```

预期结果: 76 个测试全部通过 ✅

## 前端环境搭建

### 1. 安装 Node.js 依赖

在项目根目录下执行:

```bash
cd frontend
npm install
```

依赖包括:
- Vue 3.3.4 - 前端框架
- Element Plus 2.4.4 - UI 组件库
- Axios 1.6.2 - HTTP 客户端
- Vite 5.0.7 - 构建工具

### 2. 验证前端安装

```bash
npm run dev
```

如果看到以下信息，说明前端环境搭建成功：
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

访问 `http://localhost:5173` 应该能看到文件上传页面。

## 数据文件说明

项目包含完整的数据文件，支持开箱即用：

### 1. data/static_device.json
存储设备基础信息，包含 25 个示例设备：
- CO 传感器、温度传感器、湿度传感器
- DDC 控制器（多种点位配置）
- 电动调节阀、执行器
- 控制柜、电源、继电器等

### 2. data/static_rule.json
存储匹配规则配置，包含 25 条规则，与设备一一对应。
每条规则包含：
- 特征列表和权重
- 匹配阈值
- 关联的设备 ID

### 3. data/static_config.json
存储全局配置，包括：

#### 设备行识别配置（新增）
```json
"device_row_recognition": {
  "scoring_weights": {
    "data_type": 0.30,
    "structure": 0.35,
    "industry": 0.35
  },
  "probability_thresholds": {
    "high": 70.0,
    "medium": 40.0
  },
  "industry_keywords": {
    "device_types": ["传感器", "控制器", "DDC", "阀门", ...],
    "parameters": ["PPM", "℃", "Pa", "%RH", ...],
    "brands": ["霍尼韦尔", "西门子", "江森自控", ...],
    "model_patterns": ["[A-Z]{2,}-[A-Z0-9]+", ...]
  }
}
```

#### 设备匹配配置
- 归一化映射规则
- 特征拆分字符
- 忽略关键词
- 全局配置参数
- UI 配置
- 性能配置

### 4. 测试文件
- `data/示例设备清单.xlsx` - 标准格式示例
- `data/(原始表格)建筑设备监控及能源管理报价清单(2).xlsx` - 真实场景测试文件（66 行，51 个设备行）

## 项目结构

```
.
├── backend/              # 后端代码（已完成）
│   ├── app.py           # Flask 应用入口（包含设备行识别 API）
│   ├── config.py        # 配置管理
│   ├── requirements.txt # Python 依赖
│   ├── modules/         # 业务模块
│   │   ├── device_row_classifier.py  # 设备行分类器（新增）
│   │   ├── text_preprocessor.py      # 文本预处理
│   │   ├── data_loader.py            # 数据加载
│   │   ├── excel_parser.py           # Excel 解析
│   │   ├── match_engine.py           # 匹配引擎
│   │   └── excel_exporter.py         # Excel 导出
│   ├── tests/           # 测试文件（76 个测试）
│   └── temp/            # 临时文件目录
├── frontend/            # 前端代码（已完成）
│   ├── src/
│   │   ├── main.js     # Vue 应用入口
│   │   ├── App.vue     # 根组件
│   │   ├── components/ # Vue 组件
│   │   │   ├── FileUpload.vue
│   │   │   ├── ResultTable.vue
│   │   │   ├── ExportButton.vue
│   │   │   └── DeviceRowAdjustment.vue  # 设备行调整组件（新增）
│   │   ├── views/      # 页面视图
│   │   │   ├── FileUploadView.vue
│   │   │   ├── DeviceRowAdjustmentView.vue  # 设备行调整页面（新增）
│   │   │   └── MatchingView.vue
│   │   └── api/        # API 请求封装
│   ├── index.html      # HTML 模板
│   ├── package.json    # npm 依赖
│   └── vite.config.js  # Vite 配置
├── data/               # 静态数据文件
│   ├── static_device.json  # 设备表（25 个设备）
│   ├── static_rule.json    # 规则表（25 条规则）
│   ├── static_config.json  # 配置文件（包含设备行识别配置）
│   ├── 示例设备清单.xlsx    # 示例文件
│   └── (原始表格)建筑设备监控及能源管理报价清单(2).xlsx  # 测试文件
├── .kiro/              # Kiro 规格文档
│   ├── specs/
│   │   ├── ddc-device-matching/  # 设备匹配功能规格
│   │   └── device-row-intelligent-recognition/  # 设备行识别功能规格
│   └── PROJECT.md      # 项目概述
├── .gitignore          # Git 忽略文件
├── README.md           # 项目说明
├── SETUP.md            # 本文件
├── QUICK_START_GUIDE.md  # 快速启动指南
├── MAINTENANCE.md      # 数据维护指南
├── DEVICE_ROW_RECOGNITION_FINAL_SUMMARY.md  # 设备行识别功能总结
└── TASK_9_FINAL_CHECKPOINT_REPORT.md  # 最终检查点报告
```

## 下一步

环境搭建完成后，你可以：

### 1. 快速体验系统
查看 `QUICK_START_GUIDE.md` 了解如何使用系统的完整功能。

### 2. 了解功能详情

**设备行智能识别功能**:
- 查看 `DEVICE_ROW_RECOGNITION_FINAL_SUMMARY.md` 了解功能详情
- 查看 `TASK_9_FINAL_CHECKPOINT_REPORT.md` 了解测试结果
- 查看 `.kiro/specs/device-row-intelligent-recognition/` 了解需求和设计

**设备匹配功能**:
- 查看 `MAINTENANCE.md` 了解数据维护
- 查看 `.kiro/specs/ddc-device-matching/` 了解需求和设计

### 3. 运行测试

```bash
# 后端单元测试
cd backend
pytest tests/ -v

# 设备行识别准确率测试
python test_device_row_recognition.py

# 设备匹配准确率测试
python check_real_accuracy.py
```

### 4. 开始开发

如果需要继续开发新功能：
1. 查看 `.kiro/specs/` 目录下的规格文档
2. 打开对应的 `tasks.md` 文件
3. 点击任务旁边的 "Start task" 按钮
4. Kiro 将引导你完成任务实施

## 常见问题

### Q: pip install 失败怎么办?
A: 尝试使用国内镜像源:
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: npm install 失败怎么办?
A: 尝试使用国内镜像源:
```bash
npm install --registry=https://registry.npmmirror.com
```

### Q: Python 虚拟环境激活失败?
A: Windows 用户可能需要修改执行策略:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 技术支持

如有问题，请参考项目文档或联系开发团队。
